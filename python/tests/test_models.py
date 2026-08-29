"""Core mathematical verification tests for KandelLab models.

Every test checks a model against its analytic solution or a textbook anchor,
mirroring the verification style of MankiwEcoLab (280 tests).

Run:  python -m pytest tests/ -q   (from the python/ directory)
"""

import numpy as np
import pytest

from KandelLab import config
from KandelLab.cells.nernst import nernst_potential, all_equilibria
from KandelLab.cells.goldman import goldman_voltage, resting_potential
from KandelLab.cells.hodgkin_huxley import HodgkinHuxley
from KandelLab.cells.lif import LIF
from KandelLab.cells.synapse import psp_alpha_peak, temporal_sum_peak
from KandelLab.circuits.hebbian import hebb_update
from KandelLab.circuits.kuramoto import Kuramoto
from KandelLab.circuits.wilson_cowan import WilsonCowan
from KandelLab.systems.memory import train, energy, recall
from KandelLab.systems.reward import rescorla_wagner
from KandelLab.cognitive.sdt import d_prime, auc_analytic


# ---------------------------------------------------------------------------
# cells: Nernst equation
# ---------------------------------------------------------------------------

class TestNernst:
    def test_k_equilibrium_textbook_value(self):
        """K+ equilibrium potential ≈ -90 mV at 37 °C (Kandel textbook anchor)."""
        eq = all_equilibria()
        assert -93 < eq["K"] < -85

    def test_na_equilibrium_textbook_value(self):
        """Na+ equilibrium potential ≈ +60 mV."""
        eq = all_equilibria()
        assert 55 < eq["Na"] < 65

    def test_zero_charge_rejected(self):
        with pytest.raises(ValueError):
            nernst_potential(0, 10, 10)

    def test_equality_at_equal_concentrations(self):
        """E = 0 when concentrations are equal."""
        assert abs(nernst_potential(1, 10, 10)) < 1e-9

    def test_temperature_dependence_linear(self):
        """|E| grows linearly with T (RT/zF factor)."""
        e1 = nernst_potential(1, 100, 10, T=280.0)
        e2 = nernst_potential(1, 100, 10, T=320.0)
        assert abs(e2 / e1 - 320.0 / 280.0) < 1e-6


# ---------------------------------------------------------------------------
# cells: Goldman-Hodgkin-Katz
# ---------------------------------------------------------------------------

class TestGoldman:
    def test_single_ion_limit_equals_nernst(self):
        """GHK reduces to Nernst when only one ion is permeable."""
        T = config.T_KELVIN
        e_ghk = goldman_voltage({"K": 1.0}, {"K": 5.0}, {"K": 140.0}, T=T)
        e_nernst = nernst_potential(1, 5.0, 140.0, T=T)
        assert abs(e_ghk - e_nernst) < 1e-6

    def test_resting_potential_textbook_range(self):
        """Typical resting potential ≈ -70 mV with standard permeabilities."""
        v = resting_potential()
        assert -80 < v < -60


# ---------------------------------------------------------------------------
# cells: Hodgkin-Huxley
# ---------------------------------------------------------------------------

class TestHodgkinHuxley:
    def test_resting_potential(self):
        """HH model rests near -65 mV."""
        hh = HodgkinHuxley()
        _, states = hh.simulate(5.0, dt=0.05, i_ext_fn=lambda t: 0.0)
        v_rest = states[-1, 0]
        assert -75 < v_rest < -55

    def test_action_potential_overshoots(self):
        """A supra-threshold stimulus produces a spike peaking above +20 mV."""
        hh = HodgkinHuxley()
        _, states = hh.simulate(20.0, dt=0.05, i_ext_fn=lambda t: 10.0)
        assert states[:, 0].max() > 20.0

    def test_subthreshold_no_spike(self):
        """A weak stimulus produces no spike."""
        hh = HodgkinHuxley()
        _, states = hh.simulate(20.0, dt=0.05, i_ext_fn=lambda t: 0.5)
        assert states[:, 0].max() < -40.0


# ---------------------------------------------------------------------------
# cells: LIF
# ---------------------------------------------------------------------------

class TestLIF:
    def test_analytical_rate_increases_with_current(self):
        """Firing rate is a monotonic function of input current."""
        lif = LIF()
        r1 = lif.analytical_rate(0.3)
        r2 = lif.analytical_rate(1.0)
        r3 = lif.analytical_rate(3.0)
        assert 0 < r1 < r2 < r3

    def test_rate_zero_below_rheobase(self):
        """No firing below rheobase."""
        lif = LIF()
        assert lif.analytical_rate(lif.rheobase() * 0.5) <= 0

    def test_refractory_period_limits_rate(self):
        """Rate cannot exceed 1/t_ref."""
        lif = LIF()
        assert lif.analytical_rate(1e6) <= 1000.0 / lif.tau_ref + 1e-6


# ---------------------------------------------------------------------------
# cells: synapse
# ---------------------------------------------------------------------------

class TestSynapse:
    def test_epsp_positive(self):
        """Excitatory input produces a positive postsynaptic deflection."""
        assert psp_alpha_peak(1.0, tau=10.0) > 0

    def test_temporal_sum_exceeds_single(self):
        """Two rapid pulses sum to more than one pulse."""
        single = psp_alpha_peak(1.0, tau=10.0)
        summed = temporal_sum_peak(isi=5.0, w=1.0, tau=10.0)
        assert summed > single


# ---------------------------------------------------------------------------
# circuits: Hebbian learning
# ---------------------------------------------------------------------------

class TestHebbian:
    def test_correlated_input_strengthens_weight(self):
        """Hebbian rule increases weight for correlated activity."""
        assert hebb_update(0.1, x=1.0, y=1.0)[0] > 0.1

    def test_anticorrelated_input_weakens_weight(self):
        assert hebb_update(0.5, x=1.0, y=-1.0)[0] < 0.5


# ---------------------------------------------------------------------------
# circuits: Kuramoto synchronization
# ---------------------------------------------------------------------------

class TestKuramoto:
    def test_order_parameter_low_at_no_coupling(self):
        """R ≈ 0 for many random phases without coupling."""
        k = Kuramoto(N=500, seed=0)
        rng = np.random.default_rng(0)
        phases = rng.uniform(0, 2 * np.pi, 500)
        assert k.order_parameter(phases) < 0.1

    def test_order_parameter_one_when_synchronized(self):
        """R = 1 when all oscillators are phase-locked."""
        k = Kuramoto(N=50, seed=0)
        assert k.order_parameter(np.zeros(50)) > 0.999


# ---------------------------------------------------------------------------
# circuits: Wilson-Cowan
# ---------------------------------------------------------------------------

class TestWilsonCowan:
    def test_fixed_point_exists(self):
        """The E/I system has a fixed point at rest input."""
        wc = WilsonCowan()
        fps = wc.fixed_points()
        assert len(fps) >= 1
        E, I = fps[0]
        assert 0 < E < 1 and 0 < I < 1


# ---------------------------------------------------------------------------
# systems: Hopfield associative memory
# ---------------------------------------------------------------------------

class TestHopfield:
    def test_weight_matrix_symmetric_zero_diagonal(self):
        W = train(np.array([[1, 1, -1, -1], [1, -1, 1, -1]]))
        assert np.allclose(W, W.T)
        assert np.allclose(np.diag(W), 0.0)

    def test_energy_monotonically_decreases(self):
        """Asynchronous update never increases energy."""
        rng = np.random.default_rng(1)
        patterns = rng.choice([-1.0, 1.0], size=(3, 40))
        W = train(patterns)
        state = patterns[0].copy()
        energies = [energy(W, state)]
        for _ in range(50):
            i = rng.integers(0, 40)
            state[i] = 1.0 if W[i] @ state > 0 else -1.0
            energies.append(energy(W, state))
        assert all(b - a <= 1e-9 for a, b in zip(energies, energies[1:]))

    def test_recall_restores_corrupted_pattern(self):
        """A corrupted pattern converges back to the stored attractor."""
        patterns = np.array([[1, 1, 1, -1, -1, -1, 1, 1],
                             [1, -1, 1, -1, 1, -1, 1, -1]])
        W = train(patterns)
        noisy = patterns[0].copy()
        noisy[0] *= -1
        recalled, _, converged = recall(W, noisy)
        assert converged
        assert np.array_equal(recalled, patterns[0])


# ---------------------------------------------------------------------------
# systems: reward learning (Rescorla-Wagner)
# ---------------------------------------------------------------------------

class TestRescorlaWagner:
    def test_value_converges_to_asymptote(self):
        """Associative strength converges toward the US intensity."""
        v = rescorla_wagner(alpha=0.3, lamb=1.0, n_trials=200)[1]
        assert abs(v[-1] - 1.0) < 0.01
        assert all(b >= a - 1e-9 for a, b in zip(v, v[1:]))


# ---------------------------------------------------------------------------
# cognitive: signal detection theory
# ---------------------------------------------------------------------------

class TestSDT:
    def test_dprime_zero_for_chance(self):
        """d' = 0 when hit rate equals false-alarm rate."""
        assert abs(d_prime(0.5, 0.5)) < 1e-9

    def test_auc_formula(self):
        """AUC = Φ(d'/√2) for equal-variance Gaussian SDT."""
        assert abs(auc_analytic(1.0) - 0.7602499389065233) < 1e-6
