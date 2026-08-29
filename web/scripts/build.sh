#!/bin/bash
set -euo pipefail
pnpm install --prefer-frozen-lockfile
pnpm next build
