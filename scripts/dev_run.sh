#!/bin/bash
# Development script for running with SpiritualLibrary
# This sets up environment for local development debugging

set -euo pipefail

# Get directories
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
VENV_DIR="$PROJECT_ROOT/venv_mcp"
PYTHON_CMD="$VENV_DIR/bin/python"

# Configure paths for development
export PERSONAL_LIBRARY_DOC_PATH="/Users/hpoliset/SpiritualLibrary"
export PERSONAL_LIBRARY_DB_PATH="$PROJECT_ROOT/chroma_db"
export PERSONAL_LIBRARY_LOGS_PATH="$PROJECT_ROOT/logs"
export PYTHONPATH="$PROJECT_ROOT/src:${PYTHONPATH:-}"
export PYTHONUNBUFFERED="1"

echo "🔮 Personal Document Library - Development Mode"
echo "=============================================="
echo ""
echo "📚 Documents: $PERSONAL_LIBRARY_DOC_PATH"
echo "💾 Database:  $PERSONAL_LIBRARY_DB_PATH"
echo "📝 Logs:      $PERSONAL_LIBRARY_LOGS_PATH"
echo ""

# Pass all arguments to the main run script
exec "$SCRIPT_DIR/run.sh" "$@"
