# kandellab — Neuroscience Principles Code Lab (Python)

> Implement the core models of Kandel's *Principles of Neural Science* — by hand, in Python.

KandelLab turns the classic models of neuroscience — from the Nernst equation to the
drift-diffusion model of decision-making — into **runnable, experimentable, testable code**.
Built for undergraduates and graduates learning neuroscience, in class or for self-study.

## Highlights

- **12 core concepts × runnable experiments** across four levels: cells → circuits → systems → cognition
- **CLI** (`neuro-lab`) — demo each layer, run all 12 experiments, save figures + CSV
- **Mathematically verified** — every model is checked against its analytic solution (26 tests)
- **Deterministic and reproducible** — fixed seeds make experiments exactly reproducible
- **Teaching-friendly** — formula derivations in docstrings, textbook anchors (Kandel / Dayan & Abbott)

## Install

```bash
pip install kandellab
```

## Quick Start

```bash
neuro-lab --help          # all commands
neuro-lab --demo          # walk through the 12 core concepts
neuro-lab --cells         # cells layer (Nernst → HH → LIF → synapse)
neuro-lab --circuits      # circuits layer (Hebbian → lateral inhibition → WC → Kuramoto)
neuro-lab --systems       # systems layer (vision → audition → memory → reward)
neuro-lab --cognitive     # cognitive layer (DDM → SDT → population coding)
neuro-lab --experiments   # run all 12 experiments (figures + CSV in output/)
```

Or run from source:

```bash
git clone https://github.com/NoahIsARider/KandelLab.git
cd KandelLab/python
pip install -r requirements.txt
python run.py --demo
```

## Experiments (12)

1. Ionic basis of the resting potential ([K⁺]₀ scan vs Nernst prediction)
2. Action potential generation (stimulus intensity → threshold / all-or-none / refractory)
3. Frequency coding (LIF: input current → f-I curve → raster plot)
4. Synaptic spatial-temporal integration
5. Hebbian learning (correlated inputs strengthen synapses)
6. Lateral inhibition and edge enhancement
7. Excitation–inhibition balance (Wilson–Cowan bistability)
8. Neural oscillation synchronization (Kuramoto phase transition)
9. Visual orientation tuning (Gabor)
10. Associative memory (Hopfield pattern completion)
11. Reward learning (Rescorla–Wagner / TD: conditioning + blocking)
12. Perceptual decision-making (DDM: speed–accuracy trade-off + ROC)

## Package Layout

```
KandelLab/
├── cells/       # Nernst, Goldman–Hodgkin–Katz, Hodgkin–Huxley, LIF, synapse
├── circuits/    # Hebbian/BCM, lateral inhibition (DoG), Wilson–Cowan, Kuramoto
├── systems/     # vision (Gabor), audition (γ-tone), motor (VOR/Marr–Albus), Hopfield, reward
├── cognitive/   # drift-diffusion model, signal detection theory, population coding
└── utils/       # numerical integration, visualization, console output
```

## Tests

```bash
pip install pytest
python -m pytest tests/ -q     # 26 mathematical verification tests
```

## References

- Kandel et al., *Principles of Neural Science*, 6th ed.
- Dayan & Abbott, *Theoretical Neuroscience*
- Gerstner et al., *Neuronal Dynamics*

## License

MIT
