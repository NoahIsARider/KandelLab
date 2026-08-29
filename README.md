# KandelLab — Neuroscience Principles Code Lab

> **An interactive, code-first learning project based on Kandel's *Principles of Neural Science*** — implement every core model of neuroscience by hand, in Python and TypeScript.

KandelLab turns the classic models of neuroscience — from the Nernst equation to the drift-diffusion model of decision-making — into **runnable, experimentable, testable code**. Instead of just reading the graphs in a textbook, you run the simulation, tweak the parameters, and watch how neurons spike, circuits synchronize, networks remember, and brains decide.

Built for **undergraduates and graduate students** learning neuroscience — in class, for lab assignments, or for self-study.

---

## ✨ Highlights

- **12 core concepts × runnable code** — every concept maps to a simulation and an experiment
- **Four levels, from molecules to behavior**: cells → circuits → systems → cognition
- **Dual implementations**:
  - 🐍 **Python** (`python/`) — CLI + mathematical models, installable from PyPI (`kandellab`)
  - 🌐 **Web** (`web/`) — interactive browser simulations (Next.js + TypeScript), installable from npm (`kandellab`)
- **Teaching-friendly** — formula derivations in docstrings, textbook anchors, reproducible with fixed seeds
- **Mathematically verified** — unit tests check every model against its analytic solution

## 🧠 12 Core Concepts × Code

| # | Concept | Python | TypeScript |
|---|---------|--------|------------|
| 1 | Ionic concentration gradients set membrane potential (Nernst) | `cells/nernst.py` | `lib/cells/nernst.ts` |
| 2 | Permeability sets resting potential (Goldman–Hodgkin–Katz) | `cells/goldman.py` | `lib/cells/goldman.ts` |
| 3 | Action potentials are voltage-gated channel dynamics (Hodgkin–Huxley) | `cells/hodgkin_huxley.py` | `lib/cells/hodgkin-huxley.ts` |
| 4 | Neurons encode information in spike trains (LIF) | `cells/lif.py` | `lib/cells/lif.ts` |
| 5 | Synaptic inputs integrate in space and time | `cells/synapse.py` | `lib/cells/synapse.ts` |
| 6 | Synaptic strength changes with use (Hebbian / LTP–LTD) | `circuits/hebbian.py` | `lib/circuits/hebbian.ts` |
| 7 | Lateral inhibition sharpens sensory contrast | `circuits/lateral_inhibition.py` | `lib/circuits/lateral-inhibition.ts` |
| 8 | Cortical excitation–inhibition balance stabilizes networks (Wilson–Cowan) | `circuits/wilson_cowan.py` | `lib/circuits/wilson-cowan.ts` |
| 9 | Oscillations and synchronization underlie neural rhythms (Kuramoto) | `circuits/kuramoto.py` | `lib/circuits/kuramoto.ts` |
| 10 | Sensory systems are tuned to features (vision / audition / motor) | `systems/vision.py` etc. | `lib/systems/vision.ts` etc. |
| 11 | Learning depends on reward prediction errors (Rescorla–Wagner / TD) | `systems/reward.py` | `lib/systems/reward.ts` |
| 12 | Decisions are evidence accumulation to a threshold (DDM) + associative memory (Hopfield) | `cognitive/ddm.py` + `systems/memory.py` | `lib/cognitive/ddm.ts` + `lib/systems/memory.ts` |

## 📂 Repository Layout

```
KandelLab/
├── python/          # Python package (PyPI: kandellab) — CLI `neuro-lab`
│   ├── pyproject.toml
│   ├── KandelLab/   # cells/ circuits/ systems/ cognitive/ utils/
│   └── tests/
├── web/             # Next.js 16 + TypeScript interactive lab (npm: kandellab)
│   ├── src/lib/     # TypeScript implementations of the same models
│   └── src/app/     # Browser pages for each model
└── docs/            # Model derivations, tutorials, API reference
```

## 🚀 Quick Start

### Python (CLI)

```bash
pip install kandellab

neuro-lab --help          # view all commands
neuro-lab --demo          # walk through the 12 core concepts
neuro-lab --experiments   # run all 12 experiments (figures + CSV in output/)
```

Or run from source:

```bash
cd python
pip install -r requirements.txt
python run.py --demo
```

### Web (browser)

```bash
cd web
pnpm install
pnpm dev                 # open http://localhost:5000
```

All simulations run **entirely in the browser** — no backend, no installation.

## 📚 Reference Textbooks

| Level | Primary | Secondary |
|-------|---------|-----------|
| Undergraduate | Kandel, *Principles of Neural Science* (6th ed.) | Bear, Connors & Paradiso, *Neuroscience* |
| Graduate / computational | Dayan & Abbott, *Theoretical Neuroscience* | Gerstner et al., *Neuronal Dynamics* |

## 🤝 Contributing

Any contribution is welcome — new models, better visualizations, tutorials, or tests. See `CONTRIBUTING.md` (coming soon). Please make sure `pytest tests/` (Python) and `pnpm validate` (web) pass before submitting.

## 📄 License

[MIT](LICENSE)

<p align="center">
  <sub>Built with love for neuroscience learners around the world</sub>
</p>
