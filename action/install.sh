#!/bin/sh
# Add the code review CI to a repository: sh action/install.sh PATH-TO-REPO
set -eu
exec python3 "$(cd "$(dirname "$0")" && pwd)/bundle.py" "$@"
