# Testing ragdex from TestPyPI

This guide shows how to test the ragdex package from TestPyPI before releasing to production PyPI.

## Prerequisites

- `uv` package manager installed
- Python 3.9, 3.10, 3.11, 3.12, or 3.13 available on your system

## Installation Steps

### 1. Create a test directory
```bash
mkdir -p /tmp/ragdex_test
cd /tmp/ragdex_test
```

### 2. Create virtual environment with specific Python version

Choose one of the following options:

```bash
# Option 1: Specify version number (uv will find it)
uv venv --python 3.13

# Option 2: Specify exact Python executable
uv venv --python python3.13

# Option 3: Use full path to Python
uv venv --python /opt/homebrew/opt/python@3.13/bin/python3.13

# Option 4: Let uv auto-detect any compatible version (3.9-3.13)
uv venv --python-preference only-managed
```

### 3. Activate and verify Python version
```bash
source .venv/bin/activate
python --version  # Should show Python 3.9-3.13
```

### 4. Install from TestPyPI
```bash
uv pip install \
  --index-url https://test.pypi.org/simple/ \
  --extra-index-url https://pypi.org/simple/ \
  --index-strategy unsafe-best-match \
  ragdex==0.3.1
```

**Note:** The `--index-strategy unsafe-best-match` flag is required because ragdex exists on both TestPyPI and PyPI, and we want to install the TestPyPI version.

### 5. Verify installation

```bash
# Check version
ragdex --version

# Verify all CLI commands exist
which ragdex-mcp
which ragdex-index
which ragdex-web

# Test Python imports
python -c "from personal_doc_library.servers.mcp_complete_server import CompleteMCPServer; print('✅ MCP Server import OK')"
python -c "from personal_doc_library.core.shared_rag import SharedRAG; print('✅ SharedRAG import OK')"
```

### 6. Test MCP server starts
```bash
# This should show the server starting (Ctrl+C to stop)
ragdex-mcp
```

Expected output:
```
Starting CompleteMCPServer...
Server initialized, starting main loop...
```

### 7. Cleanup
```bash
deactivate
cd ~
rm -rf /tmp/ragdex_test
```

## Python Version Notes

- **Supported versions:** Python 3.9, 3.10, 3.11, 3.12, 3.13
- **Not supported:** Python 3.8 or earlier, Python 3.14+
- Use `uv venv --python X.Y` to specify the exact version you want
- The package will automatically reject incompatible Python versions

## Troubleshooting

### "No solution found when resolving dependencies"

If you see this error, make sure you're using the `--index-strategy unsafe-best-match` flag:

```bash
uv pip install \
  --index-url https://test.pypi.org/simple/ \
  --extra-index-url https://pypi.org/simple/ \
  --index-strategy unsafe-best-match \
  ragdex==0.3.1
```

### "Requires-Python >=3.9,<3.14"

This means your Python version is outside the supported range. Check your Python version:

```bash
python --version
```

If it shows Python 3.14 or Python 3.8, you need to use a different Python version (3.9-3.13).

### Import errors

If you get import errors, verify the package installed correctly:

```bash
pip list | grep ragdex
```

Should show:
```
ragdex    0.3.1
```

## After Testing

Once you've verified that everything works correctly:

1. Document any issues found
2. If all tests pass, proceed with PyPI release
3. Update the main installation documentation with any changes

## Related Documentation

- [Installation Guide](INSTALLATION_GUIDE.md) - Production installation
- [Quick Start](QUICKSTART.md) - Getting started guide
- [README](README.md) - Main documentation
