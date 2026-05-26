#!/usr/bin/env bash
set -euo pipefail

if [ -f .neuro-materialized ]; then
  echo "Already materialized. Remove .neuro-materialized to refresh from upstream OpenHands."
  exit 0
fi

mkdir -p .neuro-tmp
if [ ! -d .neuro-tmp/OpenHands/.git ]; then
  git clone --depth=1 https://github.com/OpenHands/OpenHands.git .neuro-tmp/OpenHands
fi

rsync -a --delete \
  --exclude='.git' \
  --exclude='.github' \
  --exclude='.neuro-tmp' \
  --exclude='.neuro-materialized' \
  --exclude='workspace' \
  --exclude='neuro_overlay' \
  .neuro-tmp/OpenHands/ ./

rsync -a neuro_overlay/ ./

date -u +"%Y-%m-%dT%H:%M:%SZ" > .neuro-materialized
echo "OpenHands upstream: https://github.com/OpenHands/OpenHands" >> .neuro-materialized
echo "Neuro overlay applied from ./neuro_overlay" >> .neuro-materialized

echo "Done. Review changes, then commit them."
