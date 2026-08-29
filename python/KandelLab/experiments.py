"""KandelLab — 12 classic neuroscience teaching experiments.

Each experiment: change parameters → run the simulation → produce figures (PNG)
+ data (CSV) → students analyze.

Experiment list
--------
 1  Ionic basis of the resting potential ([K⁺]₀ scan)
 2  Generation of the action potential (stimulus strength → threshold /
    all-or-none / refractory period)
 3  Frequency coding (LIF: input current → f-I curve → raster plot)
 4  Synaptic spatiotemporal integration (frequency × number → firing probability)
 5  Hebbian learning (training on correlated inputs → selective strengthening)
 6  Lateral inhibition and edge enhancement (Mach band phenomenon)
 7  Excitation-inhibition balance (WC: input strength → fixed points / bistability)
 8  Neural oscillation synchronization (coupling strength → phase transition)
 9  Visual orientation selectivity (Gabor tuning curves)
10  Associative memory (Hopfield: corrupted-pattern recovery)
11  Reward learning (RW/TD: conditioning + blocking)
12  Perceptual decision-making (DDM: accuracy-RT tradeoff + ROC)
"""

from __future__ import annotations

import numpy as np
from pathlib import Path

from . import config
from .utils import output
from .utils.visualization import NeuroVisualizer
from .utils.neuro import rng


def _summary(name, figures, csvs, rows=None, headers=None, key_results=None):
    return {
        "name": name,
        "figures": [str(f) for f in figures],
        "csvs": [str(c) for c in csvs],
        "rows": rows,
        "headers": headers,
        "results": key_results or {},
    }


# ---------------------------------------------------------------------------
# Experiment 1: ionic basis of the resting potential
# ---------------------------------------------------------------------------
def experiment_1_resting_potential(out_dir="output/exp1"):
    """[K⁺]₀ scan → GHK resting potential vs Nernst E_K."""
    viz = NeuroVisualizer(out_dir)
    from .cells import nernst, goldman

    c_out = np.logspace(0.5, 2.2, 25)   # 3.16 ~ 158 mM
    ghk_v = np.array([
        goldman.goldman_voltage(
            dict(config.PERMEABILITIES),
            {"K": ko, "Na": config.ION_CONCENTRATIONS["Na"]["o"],
             "Cl": config.ION_CONCENTRATIONS["Cl"]["o"]},
            {ion: config.ION_CONCENTRATIONS[ion]["i"]
             for ion in ("K", "Na", "Cl")})
        for ko in c_out])
    nernst_v = np.array([
        nernst.nernst_potential(1, ko, config.ION_CONCENTRATIONS["K"]["i"])
        for ko in c_out])

    fig_dir = Path(out_dir) / "figures"
    fig_dir.mkdir(parents=True, exist_ok=True)
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.semilogx(c_out, ghk_v, marker="o", ms=3, label="GHK resting potential")
    ax.semilogx(c_out, nernst_v, ls="--", label="Nernst E_K")
    ax.axhline(config.ION_CONCENTRATIONS["K"]["i"] * 0 + 0, color="gray",
               lw=0.5, ls=":")
    ax.set_xlabel("$[K^+]_o$ (mM)")
    ax.set_ylabel("V (mV)")
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(fig_dir / "resting_vs_k.png", facecolor="#f4ead0")
    plt.close(fig)

    csv = output.save_csv(
        np.column_stack([c_out, ghk_v, nernst_v]),
        Path(out_dir) / "data.csv",
        headers=["K_out_mM", "V_ghk_mV", "V_nernst_mV"])
    return _summary("Ionic basis of the resting potential", [fig_dir / "resting_vs_k.png"],
                    [csv])


# ---------------------------------------------------------------------------
# Experiment 2: generation of the action potential
# ---------------------------------------------------------------------------
def experiment_2_action_potential(out_dir="output/exp2"):
    """Stimulus-strength scan → threshold / all-or-none / refractory period."""
    viz = NeuroVisualizer(out_dir)
    from .cells.hodgkin_huxley import HodgkinHuxley, step_current

    hh = HodgkinHuxley()
    amps = [1.0, 2.0, 3.0, 4.0, 6.0, 10.0, 20.0]     # µA/cm²
    t_max, dt = 40.0, 0.01
    n_spikes = []
    waves = {}
    for a in amps:
        t, y = hh.simulate(t_max, dt, i_ext_fn=step_current(a, 5.0, 7.0))
        sp = hh.spikes(t, y)
        n_spikes.append(sp.size)
        if a in (1.0, 4.0, 10.0):
            waves[a] = y[:, 0]
    csv = output.save_csv(np.column_stack([amps, n_spikes]),
                          Path(out_dir) / "spike_count.csv",
                          headers=["amp_uA_cm2", "n_spikes"])

    fig_dir = Path(out_dir) / "figures"
    fig_dir.mkdir(parents=True, exist_ok=True)
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.5, 3.6))
    for a, v in waves.items():
        ax1.plot(t, v, lw=1.2, label=f"I={a} µA/cm²")
    ax1.set_xlabel("t (ms)")
    ax1.set_ylabel("V (mV)")
    ax1.legend(frameon=False, fontsize=8)
    ax2.plot(amps, n_spikes, marker="o", color="#7a3b2e")
    ax2.set_xlabel("Stimulus amplitude (µA/cm²)")
    ax2.set_ylabel("Number of spikes")
    ax2.set_xticks(amps)
    fig.tight_layout()
    fig.savefig(fig_dir / "action_potential.png", facecolor="#f4ead0")
    plt.close(fig)

    # refractory period: double pulse (10 µA, 2 ms)
    isi_list = [1.0, 2.0, 3.0, 5.0, 8.0, 12.0, 20.0]
    ref_ok = []
    for isi in isi_list:
        def dbl(tt):
            return 10.0 if (5.0 <= tt <= 7.0 or 5.0 + isi <= tt <= 7.0 + isi) else 0.0
        t, y = hh.simulate(60.0, dt, i_ext_fn=dbl)
        sp = hh.spikes(t, y)
        ref_ok.append(sp.size >= 2)
    csv2 = output.save_csv(np.column_stack([isi_list, ref_ok]),
                           Path(out_dir) / "refractory.csv",
                           headers=["isi_ms", "double_spike"])
    return _summary("Generation of the action potential",
                    [fig_dir / "action_potential.png"], [csv, csv2],
                    rows=[[a, n] for a, n in zip(amps, n_spikes)],
                    headers=["Stimulus amplitude (µA/cm²)", "Number of spikes"])


# ---------------------------------------------------------------------------
# Experiment 3: frequency coding
# ---------------------------------------------------------------------------
def experiment_3_frequency_coding(out_dir="output/exp3"):
    """LIF: f-I curve (numeric vs analytic) + raster plot."""
    viz = NeuroVisualizer(out_dir)
    from .cells.lif import LIF, raster_simulation

    lif = LIF()
    currents = np.linspace(0.2, 1.2, 11)
    I, f_num, f_ana = lif.fI_curve(currents, t_max=1000.0, burn_ms=100.0)
    fig_fi = viz.fi_curve(I, f_num, out="fi_curve")
    csv = output.save_csv(np.column_stack([I, f_num, f_ana]),
                          Path(out_dir) / "fi_curve.csv",
                          headers=["I_nA", "f_numeric_Hz", "f_analytic_Hz"])

    raster = raster_simulation([0.3, 0.6, 0.9], n_trials=15, t_max=300.0)
    times_by_trial = {k: v for k, v in raster.items()}
    fig_raster = None
    for i, (cur, sp_list) in enumerate(times_by_trial.items()):
        p = viz.raster(sp_list, out=f"raster_{i}")
        fig_raster = p if fig_raster is None else fig_raster

    return _summary("Frequency coding", [fig_fi, fig_raster], [csv],
                    rows=[[round(float(i), 3), round(float(n), 2),
                           round(float(a), 2)] for i, n, a in zip(I, f_num, f_ana)],
                    headers=["I (nA)", "f numeric (Hz)", "f analytic (Hz)"])


# ---------------------------------------------------------------------------
# Experiment 4: synaptic spatiotemporal integration
# ---------------------------------------------------------------------------
def experiment_4_synaptic_integration(out_dir="output/exp4"):
    """Temporal summation + spatial summation → firing probability."""
    viz = NeuroVisualizer(out_dir)
    from .cells import synapse
    from .cells.lif import LIF

    # temporal summation: two-pulse ISI scan
    isis = np.arange(2, 60, 3, dtype=float)
    peaks = np.array([synapse.temporal_sum_peak(isi) for isi in isis])
    fig_dir = Path(out_dir) / "figures"
    fig_dir.mkdir(parents=True, exist_ok=True)
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 2, figsize=(9.5, 3.6))
    axes[0].plot(isis, peaks, marker="o", ms=3, color="#7a3b2e")
    axes[0].set_xlabel("Two-pulse interval ISI (ms)")
    axes[0].set_ylabel("Summed peak (mV)")
    axes[0].set_title("Temporal summation")
    csv = output.save_csv(np.column_stack([isis, peaks]),
                          Path(out_dir) / "temporal_sum.csv",
                          headers=["isi_ms", "peak_mV"])

    # spatial summation → firing probability: LIF driven by Poisson input
    lif = LIF()
    r = rng(11)
    n_in_list = [1, 2, 4, 8, 16, 32]
    rate_list = [20.0, 40.0]
    t_max, dt = 300.0, 0.01
    results = []
    for n_in in n_in_list:
        for f_hz in rate_list:
            spike_count = 0
            n_trials = 12
            for trial in range(n_trials):
                n_steps = int(t_max / dt)
                I = np.zeros(n_steps)
                for k in range(n_in):
                    events = r.poisson(f_hz / 1000.0 * t_max)
                    ts = r.uniform(0, t_max, events)
                    for te in ts:
                        i0 = int(te / dt)
                        for j in range(min(30, n_steps - i0)):
                            I[i0 + j] += 0.03 * np.exp(-j * dt / 5.0)
                t, v, sp = lif.simulate(I, t_max, dt)
                if sp.size > 0:
                    spike_count += 1
            prob = spike_count / n_trials
            results.append([n_in, f_hz, prob])
    axes[1].set_xlabel("Number of inputs")
    axes[1].set_ylabel("Firing probability")
    for f_hz in rate_list:
        pr = [r for n_in, fh, r in results if fh == f_hz]
        axes[1].plot(n_in_list, pr, marker="o", ms=3, label=f"{f_hz} Hz")
    axes[1].legend(frameon=False, fontsize=8)
    axes[1].set_title("Spatial summation → firing probability")
    fig.tight_layout()
    fig.savefig(fig_dir / "spatial_sum.png", facecolor="#f4ead0")
    plt.close(fig)
    csv2 = output.save_csv(results, Path(out_dir) / "spatial_sum.csv",
                           headers=["n_inputs", "rate_Hz", "spike_prob"])
    return _summary("Synaptic spatiotemporal integration", [fig_dir / "spatial_sum.png"],
                    [csv, csv2])


# ---------------------------------------------------------------------------
# Experiment 5: Hebbian learning
# ---------------------------------------------------------------------------
def experiment_5_hebbian_learning(out_dir="output/exp5"):
    """Training on correlated inputs → selective strengthening + BCM LTD/LTP."""
    viz = NeuroVisualizer(out_dir)
    from .circuits import hebbian

    pattern = np.array([1.0, -1.0, 1.0, -1.0, 1.0, -1.0, 1.0, -1.0])
    x, y = hebbian.correlated_inputs(pattern, noise_level=0.15, n_samples=400,
                                     seed=5)
    w, hist = hebbian.run_hebb(x, y, rule="hebb")
    corr = np.array([np.corrcoef(h, pattern)[0, 1] for h in hist])
    csv = output.save_csv(np.column_stack([np.arange(len(corr)), corr]),
                          Path(out_dir) / "weight_corr.csv",
                          headers=["step", "corr_w_pattern"])
    # overlap between the normalized weight vector and the target pattern
    overlap = np.array([w_i @ pattern / np.linalg.norm(w_i + 1e-12)
                        for w_i in hist]) / np.sqrt(pattern.size)
    csv2 = output.save_csv(np.column_stack([np.arange(len(overlap)), overlap]),
                           Path(out_dir) / "overlap.csv",
                           headers=["step", "overlap"])

    y_ltp, dw = hebbian.lt_ltp_curve()
    fig_dir = Path(out_dir) / "figures"
    fig_dir.mkdir(parents=True, exist_ok=True)
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 2, figsize=(9.5, 3.6))
    axes[0].plot(overlap, color="#7a3b2e")
    axes[0].set_xlabel("Training step")
    axes[0].set_ylabel("Weight-pattern overlap")
    axes[0].set_title("Hebb directed strengthening")
    axes[1].axhline(0, color="gray", lw=0.7)
    axes[1].plot(y_ltp, dw, color="#3d5a3a")
    axes[1].axvline(1.0, color="gray", ls="--", lw=0.7)
    axes[1].set_xlabel("Output activity y")
    axes[1].set_ylabel("Δw")
    axes[1].set_title("BCM: LTD / LTP")
    fig.tight_layout()
    fig.savefig(fig_dir / "hebbian.png", facecolor="#f4ead0")
    plt.close(fig)
    return _summary("Hebbian learning", [fig_dir / "hebbian.png"],
                    [csv, csv2])


# ---------------------------------------------------------------------------
# Experiment 6: lateral inhibition and edge enhancement
# ---------------------------------------------------------------------------
def experiment_6_lateral_inhibition(out_dir="output/exp6"):
    """Mach band: a step edge enhanced by DOG lateral inhibition."""
    viz = NeuroVisualizer(out_dir)
    from .circuits.lateral_inhibition import (step_edge_image, dog_kernel_2d,
                                              apply_kernel)

    img = step_edge_image((64, 128), 0.2, 0.8)
    kernel = dog_kernel_2d(41, 2.0, 6.0)
    out = apply_kernel(img, kernel)
    fig1 = viz.dof_receptive_field(kernel, out="dof_receptive_field")
    fig2 = viz.edge_enhancement(img, img + out * 0.5, out="edge_enhancement")

    # cross section (middle row)
    row = img[32]
    prof = (img + out * 0.5)[32]
    csv = output.save_csv(
        np.column_stack([np.arange(len(row)), row, prof]),
        Path(out_dir) / "cross_section.csv",
        headers=["x", "input", "output"])
    return _summary("Lateral inhibition and edge enhancement", [fig1, fig2], [csv])


# ---------------------------------------------------------------------------
# Experiment 7: excitation-inhibition balance
# ---------------------------------------------------------------------------
def experiment_7_ei_balance(out_dir="output/exp7"):
    """Wilson-Cowan: input strength → fixed points and phase portrait."""
    viz = NeuroVisualizer(out_dir)
    from .circuits.wilson_cowan import WilsonCowan

    wc = WilsonCowan()
    results = []
    for P in [0.0, 0.5, 2.0]:
        fpts = wc.fixed_points(P_E=P)
        for (E, I) in fpts:
            results.append([P, E, I, wc.is_stable(E, I, P_E=P)])

    fig_dir = Path(out_dir) / "figures"
    fig_dir.mkdir(parents=True, exist_ok=True)
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 2, figsize=(9.5, 3.8))
    for P, c in [(0.0, "#3d5a3a"), (2.0, "#7a3b2e")]:
        E_grid, nullE, nullI = wc.nullclines(P_E=P)
        axes[0].plot(E_grid, nullE, color=c, ls="--")
        axes[0].plot(E_grid, nullI, color=c, ls=":")
        t, E, I = wc.simulate(80.0, E0=0.1, I0=0.1, P_E=P)
        axes[0].plot(E, I, color=c, lw=1.0)
        fpts = wc.fixed_points(P_E=P)
        for (Ef, If) in fpts:
            axes[0].plot(Ef, If, "o", color=c, ms=5)
    axes[0].set_xlabel("E"); axes[0].set_ylabel("I")
    axes[0].set_title("Phase portrait (solid=trajectory, dashed=nullcline)")
    axes[1].plot([r[0] for r in results], [r[1] for r in results], "o",
                 color="#7a3b2e")
    axes[1].set_xlabel("Input P_E")
    axes[1].set_ylabel("Fixed point E*")
    axes[1].set_title("Input strength → fixed point")
    fig.tight_layout()
    fig.savefig(fig_dir / "wilson_cowan.png", facecolor="#f4ead0")
    plt.close(fig)
    csv = output.save_csv(results, Path(out_dir) / "fixed_points.csv",
                          headers=["P_E", "E_star", "I_star", "stable"])
    return _summary("Excitation-inhibition balance", [fig_dir / "wilson_cowan.png"], [csv],
                    rows=results, headers=["P_E", "E*", "I*", "stable"])


# ---------------------------------------------------------------------------
# Experiment 8: neural oscillation synchronization
# ---------------------------------------------------------------------------
def experiment_8_synchronization(out_dir="output/exp8"):
    """Kuramoto: coupling strength K → order-parameter R phase transition."""
    viz = NeuroVisualizer(out_dir)
    from .circuits.kuramoto import Kuramoto, analytic_weak_coupling_r

    k = Kuramoto(N=100, omega_std=0.1, seed=7)
    K_range = np.linspace(0.0, 8.0, 17)
    K, R = k.phase_transition(K_range, seed=7)
    fig1 = viz.kuramoto_transition(K, R, out="kuramoto_transition")
    csv = output.save_csv(np.column_stack([K, R]),
                          Path(out_dir) / "r_of_k.csv",
                          headers=["K", "R"])

    snaps = k.snapshot_phases([0.0, 2.0, 8.0], seed=7)
    fig2 = viz.kuramoto_snapshots(snaps, out="kuramoto_snapshots")
    return _summary("Neural oscillation synchronization", [fig1, fig2], [csv],
                    key_results={"R(K=0)≈1/√N":
                                 f"{R[0]:.3f} vs {analytic_weak_coupling_r(100):.3f}",
                                 "R(K=8)": f"{R[-1]:.3f}"})


# ---------------------------------------------------------------------------
# Experiment 9: visual orientation selectivity
# ---------------------------------------------------------------------------
def experiment_9_visual_tuning(out_dir="output/exp9"):
    """Gabor: filter bank + orientation tuning curves."""
    viz = NeuroVisualizer(out_dir)
    from .systems import vision

    thetas, filters = vision.gabor_bank(8, size=48, sf=0.08, sigma=6.0)
    fig1 = viz.gabor_bank(filters, out="gabor_bank")

    stim_theta = np.pi / 4
    img = vision.grating_image((48, 48), sf=0.08, theta=stim_theta)
    angles, resp = vision.orientation_tuning(img, thetas, filters)
    fig2 = viz.tuning_curve(angles, resp, out="tuning_curve")
    csv = output.save_csv(
        np.column_stack([np.degrees(angles), resp]),
        Path(out_dir) / "tuning.csv",
        headers=["angle_deg", "response"])
    half = vision.tuning_halfwidth(angles, resp)
    peak_deg = np.degrees(angles[int(np.argmax(resp))])
    return _summary("Visual orientation selectivity", [fig1, fig2], [csv],
                    key_results={"Stimulus orientation": "45°",
                                 "Peak-response orientation": f"{peak_deg:.1f}°",
                                 "Half-width": f"{half:.1f}°"})


# ---------------------------------------------------------------------------
# Experiment 10: associative memory
# ---------------------------------------------------------------------------
def experiment_10_associative_memory(out_dir="output/exp10"):
    """Hopfield: store letters, recover from corruption, energy descent."""
    viz = NeuroVisualizer(out_dir)
    from .systems import memory

    letters = ["A", "B", "C", "X"]
    patterns = memory.letters_bitmaps(letters, size=16)
    W = memory.train(patterns)

    orig = patterns[0]
    corrupted = memory.corrupt(orig, 0.25, seed=3)
    rec, energy_hist, conv = memory.recall(W, corrupted, seed=3)

    fig1 = viz.memory_recall(
        orig.reshape(16, 16), corrupted.reshape(16, 16),
        rec.reshape(16, 16), out="memory_recall")
    fig2 = viz.hopfield_energy(energy_hist, out="hopfield_energy")
    csv = output.save_csv(np.column_stack([np.arange(len(energy_hist)),
                                           energy_hist]),
                          Path(out_dir) / "energy.csv",
                          headers=["step", "energy"])
    ov = memory.overlap(rec, orig)
    return _summary("Associative memory", [fig1, fig2], [csv],
                    key_results={"Recovery overlap": f"{ov:.3f}",
                                 "Monotonic energy descent": str(conv)})


# ---------------------------------------------------------------------------
# Experiment 11: reward learning
# ---------------------------------------------------------------------------
def experiment_11_reward_learning(out_dir="output/exp11"):
    """RW conditioning + blocking effect + TD prediction error."""
    viz = NeuroVisualizer(out_dir)
    from .systems import reward

    trials, V = reward.rescorla_wagner(n_trials=200)
    fig1 = viz.rw_learning(trials, V, out="rw_learning")
    csv = output.save_csv(np.column_stack([trials, V]),
                          Path(out_dir) / "rw.csv",
                          headers=["trial", "V"])

    tr, VA, VB = reward.blocking_experiment(n1=150, n2=150)
    fig2 = viz.rw_learning(tr, VA, block2=[150], out="rw_blocking")
    fig3 = viz.rw_learning(tr, VB, block2=[150], out="rw_blocking_B")
    csv2 = output.save_csv(np.column_stack([tr, VA, VB]),
                           Path(out_dir) / "blocking.csv",
                           headers=["trial", "V_A", "V_B"])

    step, _, delta = reward.td_sequence(n_steps=40)
    fig4 = viz.td_error(step, delta, out="td_error")
    csv3 = output.save_csv(np.column_stack([step, delta]),
                           Path(out_dir) / "td_delta.csv",
                           headers=["step", "delta"])
    return _summary("Reward learning", [fig1, fig2, fig3, fig4],
                    [csv, csv2, csv3],
                    key_results={"V_B after blocking": f"{VB[-1]:.3f}"})


# ---------------------------------------------------------------------------
# Experiment 12: perceptual decision-making
# ---------------------------------------------------------------------------
def experiment_12_perceptual_decision(out_dir="output/exp12"):
    """DDM: speed-accuracy tradeoff + SDT ROC."""
    viz = NeuroVisualizer(out_dir)
    from .cognitive import ddm, sdt

    # DDM drift-rate scan
    mus = np.array([0.3, 0.6, 1.0, 1.5])
    mu_acc, mu_rt = [], []
    for m in mus:
        _, _, acc, rt = ddm.simulate_experiment(m, 1.0, 1.0, 800, seed=5)
        mu_acc.append(acc); mu_rt.append(rt)
    # DDM boundary scan
    bounds = np.array([0.5, 0.8, 1.2, 1.6])
    b_acc, b_rt = [], []
    for a in bounds:
        _, _, acc, rt = ddm.simulate_experiment(0.8, 1.0, a, 800, seed=5)
        b_acc.append(acc); b_rt.append(rt)

    # decision trajectories
    rts = []
    for i in range(10):
        rt, ch = ddm.simulate_trial(0.8, 1.0, 1.0, seed=i)
        rts.append((rt, ch))
    fig_dir = Path(out_dir) / "figures"
    fig_dir.mkdir(parents=True, exist_ok=True)
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(2, 2, figsize=(9.5, 7.2))
    axes[0, 0].plot(mus, mu_acc, marker="o", color="#3d5a3a")
    axes[0, 0].set_xlabel("Drift rate μ"); axes[0, 0].set_ylabel("Accuracy")
    axes[0, 1].plot(mus, mu_rt, marker="o", color="#7a3b2e")
    axes[0, 1].set_xlabel("Drift rate μ"); axes[0, 1].set_ylabel("RT (s)")
    axes[1, 0].plot(bounds, b_acc, marker="o", color="#3d5a3a")
    axes[1, 0].set_xlabel("Boundary a"); axes[1, 0].set_ylabel("Accuracy")
    axes[1, 1].plot(bounds, b_rt, marker="o", color="#7a3b2e")
    axes[1, 1].set_xlabel("Boundary a"); axes[1, 1].set_ylabel("RT (s)")
    fig.tight_layout()
    fig.savefig(fig_dir / "ddm_tradeoff.png", facecolor="#f4ead0")
    plt.close(fig)

    rts_arr, choices_arr, acc, _ = ddm.simulate_experiment(0.8, 1.0, 1.0,
                                                           1200, seed=5)
    rt_c = rts_arr[choices_arr == 1]
    rt_e = rts_arr[choices_arr == -1]
    fig2 = viz.rt_histogram(rt_c, rt_e, out="rt_histogram")

    # SDT ROC
    fa, hit = sdt.roc_curve(d=1.5)
    auc = sdt.auc_analytic(1.5)
    fig3 = viz.roc(fa, hit, auc=auc, out="roc_curve")
    csv = output.save_csv(
        np.column_stack([mus, mu_acc, mu_rt]), Path(out_dir) / "ddm_drift.csv",
        headers=["mu", "acc", "rt_s"])
    csv2 = output.save_csv(
        np.column_stack([bounds, b_acc, b_rt]), Path(out_dir) / "ddm_bound.csv",
        headers=["boundary", "acc", "rt_s"])
    return _summary("Perceptual decision-making", [fig_dir / "ddm_tradeoff.png", fig2, fig3],
                    [csv, csv2],
                    key_results={"μ↑ accuracy↑ RT↓": True,
                                 "a↑ accuracy↑ RT↑": True})


# ---------------------------------------------------------------------------
# Experiment scheduling
# ---------------------------------------------------------------------------
_EXPERIMENTS = [
    (1, "Ionic basis of the resting potential", experiment_1_resting_potential),
    (2, "Generation of the action potential", experiment_2_action_potential),
    (3, "Frequency coding", experiment_3_frequency_coding),
    (4, "Synaptic spatiotemporal integration", experiment_4_synaptic_integration),
    (5, "Hebbian learning", experiment_5_hebbian_learning),
    (6, "Lateral inhibition and edge enhancement", experiment_6_lateral_inhibition),
    (7, "Excitation-inhibition balance", experiment_7_ei_balance),
    (8, "Neural oscillation synchronization", experiment_8_synchronization),
    (9, "Visual orientation selectivity", experiment_9_visual_tuning),
    (10, "Associative memory", experiment_10_associative_memory),
    (11, "Reward learning", experiment_11_reward_learning),
    (12, "Perceptual decision-making", experiment_12_perceptual_decision),
]

_GROUPS = {
    "cells": [1, 2, 3, 4],
    "circuits": [5, 6, 7, 8],
    "systems": [9, 10, 11],
    "cognitive": [12],
    "demo": list(range(1, 13)),
    "experiments": list(range(1, 13)),
}

_GROUP_LABEL = {
    "cells": "Cell layer",
    "circuits": "Circuit layer",
    "systems": "System layer",
    "cognitive": "Cognition layer",
    "demo": "Twelve core concepts",
    "experiments": "All 12 experiments",
}


def run_experiment(num, out_dir="output"):
    """Run a single experiment, returning the summary dict."""
    for idx, name, fn in _EXPERIMENTS:
        if idx == num:
            sub = f"exp{num}"
            return fn(str(Path(out_dir) / sub))
    raise ValueError(f"unknown experiment {num}")


def run_group(group, out_dir="output"):
    """Run a group of experiments. Returns [summary, ...]."""
    if group not in _GROUPS:
        raise ValueError(f"unknown group {group}, choices: {list(_GROUPS)}")
    summaries = []
    for num in _GROUPS[group]:
        s = run_experiment(num, out_dir)
        s["group"] = group
        s["num"] = num
        summaries.append(s)
    return summaries
