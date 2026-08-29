# KandelLab Web — Interactive Neuroscience Simulations

Interactive browser implementation of the KandelLab models. Built with **Next.js 16 (App Router) + React 19 + TypeScript + Tailwind CSS v4 + shadcn/ui**.

All simulations run **entirely in the browser** — no backend, no database, no installation.

## Quick Start

```bash
pnpm install
pnpm dev          # http://localhost:5000
```

## Pages

- `/` — overview of the 12 core concepts
- `/cells` — Nernst, Goldman, Hodgkin–Huxley, LIF, synapse
- `/circuits` — Hebbian learning, lateral inhibition, Wilson–Cowan, Kuramoto
- `/systems` — vision, audition, motor, Hopfield memory, reward learning
- `/cognitive` — drift-diffusion model, signal detection theory, population coding
- `/experiments` — the 12 classic experiments

## Design

A medieval manuscript aesthetic — parchment textures, iron-gall-ink typography (Crimson Pro / Crimson Text / JetBrains Mono), Unicode ornaments. No SVG, no canvas: all visualizations are pure CSS. See `DESIGN.md`.

## Scripts

| Script | Description |
|--------|-------------|
| `pnpm dev` | Start dev server on :5000 |
| `pnpm build` | Production build |
| `pnpm validate` | TypeScript check + ESLint + Stylelint |
