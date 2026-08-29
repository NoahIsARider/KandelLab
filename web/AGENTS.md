# AGENTS.md — KandelLab Project Guide

## Overview
KandelLab is a neuroscience principles simulation system: core models from Kandel's
*Principles of Neural Science* are implemented one by one in code. Pure client-side
computation — every simulation runs in real time in the browser.

## Tech Stack
- Next.js 16 (App Router) + React 19 + TypeScript 5
- Tailwind CSS 4 + shadcn/ui
- Pure CSS visualization (no SVG / Canvas)
- Parchment / medieval-manuscript academic style

## Directory Layout
```
src/
├── app/
│   ├── layout.tsx              # Root layout (parchment theme)
│   ├── page.tsx                # Home page
│   ├── cells/                  # Cells layer pages
│   │   ├── nernst/             # Nernst equation
│   │   ├── goldman/            # GHK equation
│   │   ├── hodgkin-huxley/     # HH model
│   │   ├── lif/                # LIF model
│   │   └── synapse/            # Synapse model
│   ├── circuits/               # Circuits layer pages
│   │   ├── hebbian/            # Hebbian learning
│   │   ├── lateral-inhibition/ # Lateral inhibition
│   │   ├── wilson-cowan/       # Wilson-Cowan
│   │   └── kuramoto/           # Kuramoto synchronization
│   ├── systems/                # Systems layer pages
│   │   ├── vision/             # Visual system
│   │   ├── audition/           # Auditory system
│   │   ├── motor/              # Motor system
│   │   ├── memory/             # Hopfield memory
│   │   └── reward/             # Reward learning
│   ├── cognitive/              # Cognitive layer pages
│   │   ├── ddm/                # Drift-diffusion model
│   │   ├── sdt/                # Signal detection theory
│   │   └── encoding/           # Population coding
│   └── experiments/            # Experiments overview
├── lib/
│   ├── constants.ts            # Physical/biological constants
│   ├── math-utils.ts           # Numerical methods (RK4, statistics, etc.)
│   ├── cells/                  # Cells layer simulation modules
│   ├── circuits/               # Circuits layer simulation modules
│   ├── systems/                # Systems layer simulation modules
│   └── cognitive/              # Cognitive layer simulation modules
├── components/
│   ├── simulation-ui.tsx       # Simulation UI components (pure CSS charts/heatmaps)
│   └── ui/                     # shadcn/ui components
└── app/globals.css             # Global styles (parchment theme)
```

## Development Conventions
- All simulation computation happens on the client ('use client' pages import lib modules directly)
- No API routes, no backend services
- No SVG or JS charting libraries
- Visualizations via CSS Grid/Flexbox + div elements
- Fonts: Crimson Pro/Text (serif) + JetBrains Mono (monospace) + Noto Serif SC (CJK fallback)

## Build & Checks
- `pnpm ts-check` — TypeScript type check
- `pnpm lint --quiet` — ESLint
- `pnpm build` — production build
- `pnpm build:lib` — build the `kandellab` npm library from `src/lib/` (tsup)
