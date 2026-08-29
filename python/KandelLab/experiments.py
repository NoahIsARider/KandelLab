"""KandelLab — 12 个经典神经科学教学实验。

每个实验：改参数 → 跑模拟 → 出图（PNG）+ 数据（CSV）→ 学生分析。

实验清单
--------
 1  静息电位的离子基础（[K⁺]₀ 扫描）
 2  动作电位的产生（刺激强度 → 阈值/全或无/不应期）
 3  频率编码（LIF：输入电流 → f-I 曲线 → 栅栏图）
 4  突触时空整合（频率×数量 → 发放概率）
 5  Hebbian 学习（相关输入训练 → 选择性强化）
 6  侧抑制与边缘增强（Mach band 现象）
 7  兴奋-抑制平衡（WC：输入强度 → 不动点/双稳态）
 8  神经振荡同步（耦合强度 → 相变）
 9  视觉方位选择性（Gabor 调谐曲线）
10  联想记忆（Hopfield：损坏模式恢复）
11  奖赏学习（RW/TD：条件反射 + 阻塞）
12  知觉决策（DDM：正确率-RT 权衡 + ROC）
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
# 实验 1：静息电位的离子基础
# ---------------------------------------------------------------------------
def experiment_1_resting_potential(out_dir="output/exp1"):
    """[K⁺]₀ 扫描 → GHK 静息电位 vs Nernst E_K。"""
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
    ax.semilogx(c_out, ghk_v, marker="o", ms=3, label="GHK 静息电位")
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
    return _summary("静息电位的离子基础", [fig_dir / "resting_vs_k.png"],
                    [csv])


# ---------------------------------------------------------------------------
# 实验 2：动作电位的产生
# ---------------------------------------------------------------------------
def experiment_2_action_potential(out_dir="output/exp2"):
    """刺激强度扫描 → 阈值 / 全或无 / 不应期。"""
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
    ax2.set_xlabel("刺激幅度 (µA/cm²)")
    ax2.set_ylabel("发放次数")
    ax2.set_xticks(amps)
    fig.tight_layout()
    fig.savefig(fig_dir / "action_potential.png", facecolor="#f4ead0")
    plt.close(fig)

    # 不应期：双脉冲（10 µA，2 ms）
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
    return _summary("动作电位的产生",
                    [fig_dir / "action_potential.png"], [csv, csv2],
                    rows=[[a, n] for a, n in zip(amps, n_spikes)],
                    headers=["刺激幅度 (µA/cm²)", "发放次数"])


# ---------------------------------------------------------------------------
# 实验 3：频率编码
# ---------------------------------------------------------------------------
def experiment_3_frequency_coding(out_dir="output/exp3"):
    """LIF：f-I 曲线（数值 vs 解析）+ 栅栏图。"""
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

    return _summary("频率编码", [fig_fi, fig_raster], [csv],
                    rows=[[round(float(i), 3), round(float(n), 2),
                           round(float(a), 2)] for i, n, a in zip(I, f_num, f_ana)],
                    headers=["I (nA)", "f 数值 (Hz)", "f 解析 (Hz)"])


# ---------------------------------------------------------------------------
# 实验 4：突触时空整合
# ---------------------------------------------------------------------------
def experiment_4_synaptic_integration(out_dir="output/exp4"):
    """时间总和 + 空间总和 → 发放概率。"""
    viz = NeuroVisualizer(out_dir)
    from .cells import synapse
    from .cells.lif import LIF

    # 时间总和：双脉冲 ISI 扫描
    isis = np.arange(2, 60, 3, dtype=float)
    peaks = np.array([synapse.temporal_sum_peak(isi) for isi in isis])
    fig_dir = Path(out_dir) / "figures"
    fig_dir.mkdir(parents=True, exist_ok=True)
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 2, figsize=(9.5, 3.6))
    axes[0].plot(isis, peaks, marker="o", ms=3, color="#7a3b2e")
    axes[0].set_xlabel("双脉冲间隔 ISI (ms)")
    axes[0].set_ylabel("总和峰值 (mV)")
    axes[0].set_title("时间总和")
    csv = output.save_csv(np.column_stack([isis, peaks]),
                          Path(out_dir) / "temporal_sum.csv",
                          headers=["isi_ms", "peak_mV"])

    # 空间总和 → 发放概率：泊松输入驱动 LIF
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
    axes[1].set_xlabel("输入数量")
    axes[1].set_ylabel("发放概率")
    for f_hz in rate_list:
        pr = [r for n_in, fh, r in results if fh == f_hz]
        axes[1].plot(n_in_list, pr, marker="o", ms=3, label=f"{f_hz} Hz")
    axes[1].legend(frameon=False, fontsize=8)
    axes[1].set_title("空间总和 → 发放概率")
    fig.tight_layout()
    fig.savefig(fig_dir / "spatial_sum.png", facecolor="#f4ead0")
    plt.close(fig)
    csv2 = output.save_csv(results, Path(out_dir) / "spatial_sum.csv",
                           headers=["n_inputs", "rate_Hz", "spike_prob"])
    return _summary("突触时空整合", [fig_dir / "spatial_sum.png"],
                    [csv, csv2])


# ---------------------------------------------------------------------------
# 实验 5：Hebbian 学习
# ---------------------------------------------------------------------------
def experiment_5_hebbian_learning(out_dir="output/exp5"):
    """相关输入训练 → 选择性强化 + BCM LTD/LTP。"""
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
    # 归一化权重向量与目标模式的重叠度
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
    axes[0].set_xlabel("训练步")
    axes[0].set_ylabel("权重与模式重叠度")
    axes[0].set_title("Hebb 定向强化")
    axes[1].axhline(0, color="gray", lw=0.7)
    axes[1].plot(y_ltp, dw, color="#3d5a3a")
    axes[1].axvline(1.0, color="gray", ls="--", lw=0.7)
    axes[1].set_xlabel("输出活动 y")
    axes[1].set_ylabel("Δw")
    axes[1].set_title("BCM：LTD / LTP")
    fig.tight_layout()
    fig.savefig(fig_dir / "hebbian.png", facecolor="#f4ead0")
    plt.close(fig)
    return _summary("Hebbian 学习", [fig_dir / "hebbian.png"],
                    [csv, csv2])


# ---------------------------------------------------------------------------
# 实验 6：侧抑制与边缘增强
# ---------------------------------------------------------------------------
def experiment_6_lateral_inhibition(out_dir="output/exp6"):
    """Mach band：阶跃边缘经 DOG 侧抑制后边缘增强。"""
    viz = NeuroVisualizer(out_dir)
    from .circuits.lateral_inhibition import (step_edge_image, dog_kernel_2d,
                                              apply_kernel)

    img = step_edge_image((64, 128), 0.2, 0.8)
    kernel = dog_kernel_2d(41, 2.0, 6.0)
    out = apply_kernel(img, kernel)
    fig1 = viz.dof_receptive_field(kernel, out="dof_receptive_field")
    fig2 = viz.edge_enhancement(img, img + out * 0.5, out="edge_enhancement")

    # 横截面（取中间行）
    row = img[32]
    prof = (img + out * 0.5)[32]
    csv = output.save_csv(
        np.column_stack([np.arange(len(row)), row, prof]),
        Path(out_dir) / "cross_section.csv",
        headers=["x", "input", "output"])
    return _summary("侧抑制与边缘增强", [fig1, fig2], [csv])


# ---------------------------------------------------------------------------
# 实验 7：兴奋-抑制平衡
# ---------------------------------------------------------------------------
def experiment_7_ei_balance(out_dir="output/exp7"):
    """Wilson-Cowan：输入强度 → 不动点与相图。"""
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
    axes[0].set_title("相图（实线=轨迹，虚线=零等斜线）")
    axes[1].plot([r[0] for r in results], [r[1] for r in results], "o",
                 color="#7a3b2e")
    axes[1].set_xlabel("输入 P_E")
    axes[1].set_ylabel("不动点 E*")
    axes[1].set_title("输入强度 → 不动点")
    fig.tight_layout()
    fig.savefig(fig_dir / "wilson_cowan.png", facecolor="#f4ead0")
    plt.close(fig)
    csv = output.save_csv(results, Path(out_dir) / "fixed_points.csv",
                          headers=["P_E", "E_star", "I_star", "stable"])
    return _summary("兴奋-抑制平衡", [fig_dir / "wilson_cowan.png"], [csv],
                    rows=results, headers=["P_E", "E*", "I*", "stable"])


# ---------------------------------------------------------------------------
# 实验 8：神经振荡同步
# ---------------------------------------------------------------------------
def experiment_8_synchronization(out_dir="output/exp8"):
    """Kuramoto：耦合强度 K → 序参量 R 相变。"""
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
    return _summary("神经振荡同步", [fig1, fig2], [csv],
                    key_results={"R(K=0)≈1/√N":
                                 f"{R[0]:.3f} vs {analytic_weak_coupling_r(100):.3f}",
                                 "R(K=8)": f"{R[-1]:.3f}"})


# ---------------------------------------------------------------------------
# 实验 9：视觉方位选择性
# ---------------------------------------------------------------------------
def experiment_9_visual_tuning(out_dir="output/exp9"):
    """Gabor：滤波器组 + 方位调谐曲线。"""
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
    return _summary("视觉方位选择性", [fig1, fig2], [csv],
                    key_results={"刺激朝向": "45°",
                                 "峰值响应朝向": f"{peak_deg:.1f}°",
                                 "半宽": f"{half:.1f}°"})


# ---------------------------------------------------------------------------
# 实验 10：联想记忆
# ---------------------------------------------------------------------------
def experiment_10_associative_memory(out_dir="output/exp10"):
    """Hopfield：存储字母，损坏恢复，能量下降。"""
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
    return _summary("联想记忆", [fig1, fig2], [csv],
                    key_results={"恢复重叠度": f"{ov:.3f}",
                                 "能量单调下降": str(conv)})


# ---------------------------------------------------------------------------
# 实验 11：奖赏学习
# ---------------------------------------------------------------------------
def experiment_11_reward_learning(out_dir="output/exp11"):
    """RW 条件反射 + 阻塞效应 + TD 预测误差。"""
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
    return _summary("奖赏学习", [fig1, fig2, fig3, fig4],
                    [csv, csv2, csv3],
                    key_results={"阻塞后 V_B": f"{VB[-1]:.3f}"})


# ---------------------------------------------------------------------------
# 实验 12：知觉决策
# ---------------------------------------------------------------------------
def experiment_12_perceptual_decision(out_dir="output/exp12"):
    """DDM：速度-准确性权衡 + SDT ROC。"""
    viz = NeuroVisualizer(out_dir)
    from .cognitive import ddm, sdt

    # DDM 漂移率扫描
    mus = np.array([0.3, 0.6, 1.0, 1.5])
    mu_acc, mu_rt = [], []
    for m in mus:
        _, _, acc, rt = ddm.simulate_experiment(m, 1.0, 1.0, 800, seed=5)
        mu_acc.append(acc); mu_rt.append(rt)
    # DDM 边界扫描
    bounds = np.array([0.5, 0.8, 1.2, 1.6])
    b_acc, b_rt = [], []
    for a in bounds:
        _, _, acc, rt = ddm.simulate_experiment(0.8, 1.0, a, 800, seed=5)
        b_acc.append(acc); b_rt.append(rt)

    # 决策轨迹
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
    axes[0, 0].set_xlabel("漂移率 μ"); axes[0, 0].set_ylabel("正确率")
    axes[0, 1].plot(mus, mu_rt, marker="o", color="#7a3b2e")
    axes[0, 1].set_xlabel("漂移率 μ"); axes[0, 1].set_ylabel("RT (s)")
    axes[1, 0].plot(bounds, b_acc, marker="o", color="#3d5a3a")
    axes[1, 0].set_xlabel("边界 a"); axes[1, 0].set_ylabel("正确率")
    axes[1, 1].plot(bounds, b_rt, marker="o", color="#7a3b2e")
    axes[1, 1].set_xlabel("边界 a"); axes[1, 1].set_ylabel("RT (s)")
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
    return _summary("知觉决策", [fig_dir / "ddm_tradeoff.png", fig2, fig3],
                    [csv, csv2],
                    key_results={"μ↑ 正确率↑ RT↓": True,
                                 "a↑ 正确率↑ RT↑": True})


# ---------------------------------------------------------------------------
# 实验调度
# ---------------------------------------------------------------------------
_EXPERIMENTS = [
    (1, "静息电位的离子基础", experiment_1_resting_potential),
    (2, "动作电位的产生", experiment_2_action_potential),
    (3, "频率编码", experiment_3_frequency_coding),
    (4, "突触时空整合", experiment_4_synaptic_integration),
    (5, "Hebbian 学习", experiment_5_hebbian_learning),
    (6, "侧抑制与边缘增强", experiment_6_lateral_inhibition),
    (7, "兴奋-抑制平衡", experiment_7_ei_balance),
    (8, "神经振荡同步", experiment_8_synchronization),
    (9, "视觉方位选择性", experiment_9_visual_tuning),
    (10, "联想记忆", experiment_10_associative_memory),
    (11, "奖赏学习", experiment_11_reward_learning),
    (12, "知觉决策", experiment_12_perceptual_decision),
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
    "cells": "细胞层",
    "circuits": "回路层",
    "systems": "系统层",
    "cognitive": "认知层",
    "demo": "十二大核心概念",
    "experiments": "全部 12 个实验",
}


def run_experiment(num, out_dir="output"):
    """运行单个实验，返回 summary dict。"""
    for idx, name, fn in _EXPERIMENTS:
        if idx == num:
            sub = f"exp{num}"
            return fn(str(Path(out_dir) / sub))
    raise ValueError(f"无实验 {num}")


def run_group(group, out_dir="output"):
    """运行一组实验。返回 [summary, ...]。"""
    if group not in _GROUPS:
        raise ValueError(f"未知分组 {group}，可选 {list(_GROUPS)}")
    summaries = []
    for num in _GROUPS[group]:
        s = run_experiment(num, out_dir)
        s["group"] = group
        s["num"] = num
        summaries.append(s)
    return summaries
