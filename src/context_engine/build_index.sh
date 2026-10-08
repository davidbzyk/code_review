#!/bin/sh
# Build a store: build_index.sh <base-tree> <head-tree> <out> <cache-dir> [build flags]
set -eu
if [ "$#" -lt 4 ]; then
  echo "usage: build_index.sh <base-tree> <head-tree> <out> <cache-dir> [--fake-embedder ...]" >&2
  exit 64
fi
base=$(cd "$1" && pwd)
head=$(cd "$2" && pwd)
mkdir -p "$3" "$4"
out=$(cd "$3" && pwd)
cache=$(cd "$4" && pwd)
shift 4
cd "$(dirname "$0")/.."
exec uv run python -m context_engine build "$base" "$head" "$out" --cache-dir "$cache" "$@"
