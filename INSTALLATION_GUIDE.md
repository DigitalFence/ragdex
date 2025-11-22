# 🚀 Ragdex Installation Guide for Mac with Multiple Python Versions

## Prerequisites Check

Since you mentioned all prerequisites are installed, verify you have:
- ✅ Python 3.10, 3.11, or 3.12 (NOT 3.13)
- ✅ Homebrew
- ✅ uv (strongly recommended)
- ✅ Xcode Command Line Tools
- ✅ Claude Desktop
- ✅ Terminal with Full Disk Access permission

---

## 📍 Choose Your Installation Method

You have **two installation approaches**:

### **Option A: Install from PyPI** (Recommended - Production-ready)
For users who want the stable, packaged version

### **Option B: Install from Source** (Development)
For users who want to modify code or use the latest development version

---

## Option A: Install from PyPI (Recommended)

### Step 1: Select Your Python Version

Check available Python versions:

```bash
# List all Python 3.x versions
ls -la /opt/homebrew/bin/python3* 2>/dev/null || ls -la /usr/local/bin/python3*

# Check specific versions
python3.11 --version  # Recommended
python3.12 --version
python3.10 --version
```

**Recommended: Use Python 3.11** (best performance)

### Step 2: Create Virtual Environment with uv

```bash
# Using Python 3.11 (recommended)
uv venv ~/ragdex_env --python python3.11

# OR using Python 3.12
uv venv ~/ragdex_env --python python3.12

# OR using Python 3.10
uv venv ~/ragdex_env --python python3.10
```

**Why uv?** 10-100x faster than pip, better dependency resolution

### Step 3: Install Ragdex

```bash
# Install using uv (fast)
uv pip install --python ~/ragdex_env/bin/python ragdex

# Alternative: pip (slower)
source ~/ragdex_env/bin/activate
pip install ragdex
deactivate
```

**Note**: First run downloads ~2GB of AI models (5-10 minutes)

### Step 4: Setup Background Services

```bash
# Download the service installer
curl -O https://raw.githubusercontent.com/hpoliset/ragdex/main/install_ragdex_services.sh

# Make it executable
chmod +x install_ragdex_services.sh

# Run interactive installer
./install_ragdex_services.sh
```

This will prompt you for:
- Documents directory (default: `~/Documents/Library`)
- Database directory (default: `~/.ragdex/chroma_db`)
- Logs directory (default: `~/.ragdex/logs`)

**Non-interactive mode** (uses defaults):
```bash
./install_ragdex_services.sh --non-interactive
```

**Custom paths**:
```bash
./install_ragdex_services.sh \
  --docs-path ~/MyDocuments \
  --db-path ~/MyDatabase \
  --logs-path ~/MyLogs
```

### Step 5: Configure Claude Desktop

The installer displays the exact configuration. Add this to:
`~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "ragdex": {
      "command": "/Users/YOUR_USERNAME/ragdex_env/bin/ragdex-mcp",
      "env": {
        "PYTHONUNBUFFERED": "1",
        "CHROMA_TELEMETRY": "false",
        "PERSONAL_LIBRARY_DOC_PATH": "/path/to/your/documents",
        "PERSONAL_LIBRARY_DB_PATH": "/path/to/your/database",
        "PERSONAL_LIBRARY_LOGS_PATH": "/path/to/your/logs"
      }
    }
  }
}
```

**Important**: Replace paths with actual values from the installer output.

### Step 6: Restart Claude Desktop

```bash
# Quit Claude Desktop completely
pkill -9 "Claude"

# Relaunch Claude Desktop from Applications
open -a "Claude"
```

### Step 7: Verify Installation

Check services are running:
```bash
launchctl list | grep ragdex
```

You should see:
- `com.ragdex.indexer` (background indexing)
- `com.ragdex.webmonitor` (web dashboard)

Access web dashboard:
```
http://localhost:8888
```

---

## Option B: Install from Source (Development Mode)

### Step 1: Clone Repository

```bash
cd ~/Development
git clone https://github.com/hpoliset/ragdex.git
cd ragdex
```

### Step 2: Select Python Version

The interactive installer checks for Python 3.12 first, then falls back to other versions.

**Explicitly set your preferred Python**:

```bash
# For Python 3.11 (recommended)
export PYTHON_CMD=python3.11

# For Python 3.12
export PYTHON_CMD=python3.12

# For Python 3.10
export PYTHON_CMD=python3.10

# Verify
$PYTHON_CMD --version
```

### Step 3: Run Interactive Installer

```bash
# Interactive setup (guided)
./install_interactive_nonservicemode.sh

# Fully automated with defaults
./install_interactive_nonservicemode.sh --auto

# Automated with custom books path
./install_interactive_nonservicemode.sh --auto --books-path ~/MyBooks

# Skip service installation
./install_interactive_nonservicemode.sh --auto --no-service
```

The installer will:
1. ✅ Detect Python 3.12 (or offer to install it)
2. ✅ Create `venv_mcp` virtual environment
3. ✅ Install all dependencies from `requirements.txt`
4. ✅ Configure directories (books, database, logs)
5. ✅ Generate configuration files
6. ✅ Optionally install background services
7. ✅ Optionally start web monitor
8. ✅ Optionally run initial indexing

### Step 4: Manual Python Selection (if needed)

If the installer selects the wrong Python version:

```bash
# Create virtual environment manually with specific Python
python3.11 -m venv venv_mcp

# Activate it
source venv_mcp/bin/activate

# Install dependencies using uv (fastest)
uv pip install -r requirements.txt

# OR using pip
pip install -r requirements.txt

# Deactivate
deactivate
```

### Step 5: Configure Environment Variables

```bash
# Set these in your shell profile (~/.zshrc or ~/.bash_profile)
export PERSONAL_LIBRARY_DOC_PATH="$HOME/Documents/Library"
export PERSONAL_LIBRARY_DB_PATH="$HOME/Development/ragdex/chroma_db"
export PERSONAL_LIBRARY_LOGS_PATH="$HOME/Development/ragdex/logs"

# Reload shell
source ~/.zshrc  # or source ~/.bash_profile
```

Or use the `.env` file created by the installer:
```bash
source .env
```

### Step 6: Configure Claude Desktop (Development Mode)

Edit: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "personal-library": {
      "command": "/Users/YOUR_USERNAME/Development/ragdex/venv_mcp/bin/python",
      "args": ["-m", "personal_doc_library.servers.mcp_complete_server"],
      "env": {
        "PYTHONPATH": "/Users/YOUR_USERNAME/Development/ragdex/src",
        "PYTHONUNBUFFERED": "1",
        "PERSONAL_LIBRARY_DOC_PATH": "/Users/YOUR_USERNAME/Documents/Library",
        "PERSONAL_LIBRARY_DB_PATH": "/Users/YOUR_USERNAME/Development/ragdex/chroma_db",
        "PERSONAL_LIBRARY_LOGS_PATH": "/Users/YOUR_USERNAME/Development/ragdex/logs"
      }
    }
  }
}
```

**Critical**: Use **absolute paths** (replace `YOUR_USERNAME`)

### Step 7: Run Initial Indexing

```bash
# From ragdex directory
cd ~/Development/ragdex

# Index your documents
./scripts/run.sh --index-only

# Index with retry and memory monitoring
./scripts/run.sh --index-only --retry
```

---

## 🔧 Managing Multiple Python Versions

### If You Have Python 3.13 as Default

The installer will warn you that Python 3.13 is not supported by ChromaDB. You must explicitly use an older version:

```bash
# Check what's available
brew list | grep python

# Install Python 3.11 if not present
brew install python@3.11

# Use it explicitly
uv venv ~/ragdex_env --python /opt/homebrew/bin/python3.11

# OR create symlink (temporary)
alias python3=/opt/homebrew/bin/python3.11
```

### Homebrew Python Locations

**Apple Silicon (M1/M2/M3)**:
- Python 3.11: `/opt/homebrew/bin/python3.11`
- Python 3.12: `/opt/homebrew/bin/python3.12`

**Intel Macs**:
- Python 3.11: `/usr/local/bin/python3.11`
- Python 3.12: `/usr/local/bin/python3.12`

---

## 📊 Quick Commands Reference

```bash
# Run MCP server (development mode)
./scripts/run.sh

# Index documents only
./scripts/run.sh --index-only

# Check service status
./scripts/service_status.sh

# Start web monitor
./scripts/start_web_monitor.sh

# View logs
./scripts/view_mcp_logs.sh

# Check indexing status
./scripts/indexing_status.sh
```

---

## 🐛 Troubleshooting

### Python Version Conflicts

**Issue**: Wrong Python version selected

**Solution**:
```bash
# Remove existing venv
rm -rf venv_mcp  # or rm -rf ~/ragdex_env

# Recreate with specific Python
uv venv venv_mcp --python python3.11
```

### ChromaDB Compatibility Error

**Issue**: `ChromaDB requires Python 3.10-3.12`

**Solution**: Reinstall with compatible Python (see above)

### Service Won't Start

**Issue**: LaunchAgent services fail

**Solution**:
```bash
# Check logs
tail -f ~/.ragdex/logs/ragdex_indexer_stderr.log

# Unload and reload
launchctl unload ~/Library/LaunchAgents/com.ragdex.indexer.plist
launchctl load ~/Library/LaunchAgents/com.ragdex.indexer.plist
```

### Virtual Environment Path Issues

**Issue**: Claude Desktop can't find Python executable

**Solution**:
```bash
# Verify the exact path
which ragdex-mcp  # For PyPI install
# OR
ls -la ~/Development/ragdex/venv_mcp/bin/python  # For source install

# Update claude_desktop_config.json with the correct absolute path
```

### Missing Dependencies

**Issue**: Import errors when running MCP server

**Solution**:
```bash
# Reinstall dependencies
source venv_mcp/bin/activate  # or ~/ragdex_env/bin/activate
pip install --upgrade --force-reinstall ragdex
# OR for source install:
pip install -r requirements.txt
deactivate
```

### Full Disk Access Permission

**Issue**: Can't access documents in certain directories

**Solution**:
1. Open System Preferences → Security & Privacy → Privacy
2. Select "Full Disk Access" from the left sidebar
3. Click the lock to make changes
4. Add Terminal.app or your terminal emulator
5. Restart Terminal

### Port 8888 Already in Use

**Issue**: Web monitor can't start

**Solution**:
```bash
# Find what's using port 8888
lsof -i :8888

# Kill the process
kill -9 <PID>

# Or use a different port by editing the web monitor script
```

---

## 📝 Key Differences: PyPI vs Source Installation

| Aspect | PyPI Install | Source Install |
|--------|-------------|----------------|
| **Python Version** | Any 3.10-3.12 | Prefers 3.12 |
| **Virtual Env Name** | `ragdex_env` | `venv_mcp` |
| **Commands** | `ragdex-mcp`, `ragdex-index` | `./scripts/run.sh` |
| **Modification** | Not recommended | Encouraged |
| **Updates** | `uv pip install --upgrade ragdex` | `git pull` |
| **Best For** | Production use | Development |
| **Installation Location** | `~/ragdex_env` | `~/Development/ragdex` |
| **Configuration** | `~/.ragdex/` | Project directory |

---

## 🔄 Updating Ragdex

### PyPI Installation

```bash
# Check current version
~/ragdex_env/bin/ragdex-mcp --version

# Update to latest version
uv pip install --python ~/ragdex_env/bin/python --upgrade ragdex

# Restart services
launchctl unload ~/Library/LaunchAgents/com.ragdex.*.plist
launchctl load ~/Library/LaunchAgents/com.ragdex.*.plist
```

### Source Installation

```bash
cd ~/Development/ragdex

# Pull latest changes
git pull origin main

# Update dependencies
source venv_mcp/bin/activate
uv pip install -r requirements.txt
deactivate

# Restart Claude Desktop
pkill -9 "Claude"
open -a "Claude"
```

---

## 🔐 Security Best Practices

### Environment Variables

**Don't hardcode sensitive paths in shared scripts**. Instead:

```bash
# Use .env file (gitignored)
echo 'PERSONAL_LIBRARY_DOC_PATH="$HOME/Documents/Library"' >> .env
echo 'PERSONAL_LIBRARY_DB_PATH="$HOME/.ragdex/chroma_db"' >> .env
echo 'PERSONAL_LIBRARY_LOGS_PATH="$HOME/.ragdex/logs"' >> .env

# Load when needed
source .env
```

### File Permissions

```bash
# Ensure proper permissions on sensitive directories
chmod 700 ~/.ragdex
chmod 700 ~/Documents/Library

# Secure log files
chmod 600 ~/.ragdex/logs/*.log
```

---

## 📈 Performance Optimization

### For Large Libraries (10,000+ documents)

```bash
# Increase memory allocation for indexing
export PYTHONMEMORYMAX=8192  # 8GB

# Use batch processing
./scripts/run.sh --index-only --retry
```

### For Faster Searches

```bash
# Warm up the cache on startup
# Add this to your shell profile:
alias ragdex-warmup='~/ragdex_env/bin/python -c "from personal_doc_library.core.shared_rag import SharedRAG; rag = SharedRAG(); print(\"Cache warmed up\")"'
```

---

## 🎯 Next Steps After Installation

1. **Add Documents**: Copy your PDFs, Word docs, EPUBs to your documents directory
2. **Run Indexing**: `./scripts/run.sh --index-only` (or wait for background service)
3. **Check Web Dashboard**: Visit `http://localhost:8888`
4. **Test in Claude**: Ask Claude "Search my library for [topic]"
5. **Enable Email** (optional): See `QUICKSTART.md#optional-enable-email-indexing`

---

## 📚 Additional Resources

- **Main Documentation**: `README.md`
- **Quick Reference**: `QUICK_REFERENCE.md`
- **Project Guidelines**: `CLAUDE.md`
- **Troubleshooting**: `QUICKSTART.md#troubleshooting`
- **GitHub Issues**: https://github.com/hpoliset/ragdex/issues

---

## ✅ Installation Complete!

You now have Ragdex installed and configured. The installation respects whatever Python 3.10-3.12 version you specify, with **Python 3.11 being the recommended choice** for optimal performance.

**Questions or Issues?** Open an issue on GitHub or consult the troubleshooting section above.
