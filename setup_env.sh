#!/bin/sh
set -eu

cd "$(dirname "$0")"
python3 -m venv myenv

printf '%s\n' "Virtual environment created at myenv." "Activate it with: source myenv/bin/activate"
