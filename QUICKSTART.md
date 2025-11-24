# 🚀 Ragdex Quick Start Guide for Beginners

Welcome! This guide will walk you through setting up Ragdex from scratch, even if you're new to command-line tools or Python. Follow each step carefully, and you'll have your personal AI-powered document library running in about 15-20 minutes.

## 📋 Before You Begin - Complete Checklist

Use this checklist to verify you're ready to install Ragdex. Don't worry if you don't have everything—we'll guide you through installing what's missing.

### Quick Checklist

- [ ] My computer runs **macOS 10.15+ or Linux** (Ubuntu 20.04+, Debian 11+, Fedora 35+)
- [ ] I have **admin/sudo access** on this machine
- [ ] I can **open and use Terminal**
- [ ] I have **stable internet** (10+ Mbps recommended for 2GB download)
- [ ] I have **5GB+ free disk space** (check with `df -h ~`)
- [ ] I have **15-30 minutes** available for installation
- [ ] **Claude Desktop** is installed and launched at least once
- [ ] **(macOS only)** Terminal has **Full Disk Access** permission
- [ ] **(macOS only)** Xcode Command Line Tools installed

---

## 🖥️ Detailed System Requirements

### Operating System

**Supported:**
- **macOS**: 10.15 Catalina or newer (including M1/M2/M3 Macs)
- **Linux**:
  - Ubuntu 20.04 LTS or newer
  - Debian 11 or newer
  - Fedora 35 or newer
  - Other distributions with Python 3.10+ support

**NOT Supported:**
- Windows (native) - may work with WSL2 but untested
- macOS 10.14 or older

### CPU Architecture

Both Intel (x86_64) and Apple Silicon (ARM64/M1/M2/M3) are fully supported.

### Memory Requirements

| Requirement | Amount | Why Needed |
|-------------|--------|------------|
| **Minimum** | 8GB RAM | Basic operation, small libraries |
| **Recommended** | 16GB RAM | Comfortable indexing, medium libraries |
| **Optimal** | 32GB RAM | Large libraries (10,000+ documents) |

**Memory breakdown:**
- Embedding models: ~4GB (constant when loaded)
- Document indexing: 2-4GB (temporary spikes during processing)
- Operating system: ~2GB
- Chrome/browsers: ~1-2GB

### Storage Requirements

| Component | Space Needed | Location |
|-----------|--------------|----------|
| Ragdex installation | ~500MB | `~/ragdex_env/` |
| Embedding models | ~2GB | `~/.cache/huggingface/` |
| Vector database | ~10MB per 1,000 pages | `~/.ragdex/chroma_db/` |
| **Total minimum** | **5GB + your documents** | - |

**Storage considerations:**
- Vector database grows with your library (~1MB per 100 pages)
- Original documents are NOT copied (only indexed)
- Temporary processing space: up to 2x size of largest document

### Internet Connection

| Requirement | Speed | Purpose |
|-------------|-------|---------|
| **Initial setup** | 10+ Mbps | Download 2GB of AI models |
| **Ongoing use** | Any | Minimal (updates only) |

**First-time download:**
- ~2GB of data (embedding models)
- 5-10 minutes on broadband
- 20-30 minutes on slower connections
- **Tip**: Use unmetered connection if available

---

## 🛠️ Required Software & Tools

### 1. Python (3.10, 3.11, 3.12, or 3.13)

**✅ SUPPORTED VERSIONS**: Python 3.10-3.13 (3.11+ recommended for best performance)

#### Check your Python version:

```bash
python3 --version
```

**Expected output:**
```
Python 3.10.x, 3.11.x, 3.12.x, or 3.13.x
```

**❌ If you see `Python 3.9.x` or lower**, you need to install a compatible version (see below).

#### Why specific versions?

| Version | Status | Reason |
|---------|--------|--------|
| 3.9 or lower | ❌ Not supported | Missing required features |
| 3.10 | ✅ Supported | Stable, well-tested |
| 3.11 | ✅ **Recommended** | Best performance & compatibility |
| 3.12 | ✅ Supported | Latest features |
| 3.13 | ✅ **Supported** | Modern dependencies (v0.3.0+) |

<details>
<summary>📦 How to Install Python 3.11 or 3.13 (if needed)</summary>

#### On macOS:

**Prerequisites**: Homebrew must be installed (see Homebrew section below)

```bash
# Install Python 3.11 (recommended)
brew install python@3.11

# Or install Python 3.13 (latest)
brew install python@3.13

# Verify installation
/opt/homebrew/bin/python3.11 --version
# Or: /opt/homebrew/bin/python3.13 --version
```

**Expected output:**
```
Python 3.11.x or Python 3.13.x
```

**Note**: On Intel Macs, the path may be `/usr/local/bin/python3.11` or `/usr/local/bin/python3.13`

#### On Linux (Ubuntu/Debian):

```bash
# Update package list
sudo apt update

# Install Python 3.11 with development tools (recommended)
sudo apt install python3.11 python3.11-venv python3.11-dev

# Or install Python 3.13 (latest, may need PPA)
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.13 python3.13-venv python3.13-dev

# Verify installation
python3.11 --version
# Or: python3.13 --version
```

#### On Linux (Fedora/RHEL/CentOS):

```bash
# Install Python 3.11 with development tools
sudo dnf install python3.11 python3.11-devel

# Verify installation
python3.11 --version
```

</details>

---

### 2. Xcode Command Line Tools (macOS Only)

**Why needed**: Required to compile Python packages with native code (like some dependencies of ChromaDB).

#### Check if installed:

```bash
xcode-select -p
```

**Expected output** (if installed):
```
/Library/Developer/CommandLineTools
```

**If you see**: `xcode-select: error: unable to get active developer directory`, it's **not installed**.

#### Install Xcode Command Line Tools:

```bash
xcode-select --install
```

A popup will appear. Click "Install" and wait 5-10 minutes for the download and installation to complete.

**Verify installation:**
```bash
xcode-select -p
```

---

### 3. Homebrew (macOS Package Manager)

**Why needed**: Easiest way to install Python, uv, and optional tools on macOS.

#### Check if installed:

```bash
brew --version
```

**Expected output** (if installed):
```
Homebrew 4.x.x
```

**If you see**: `command not found: brew`, it's **not installed**.

#### Install Homebrew:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

**What happens:**
1. Script downloads and installs Homebrew (~5 minutes)
2. You may be prompted for your password (admin access required)
3. Follow any on-screen instructions to add Homebrew to your PATH

**After installation**, close and reopen Terminal, then verify:

```bash
brew --version
```

---

### 4. uv (Fast Python Package Manager)

**Why recommended**: uv is 10-100x faster than pip for installing packages.

#### Install uv:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Expected output:**
```
Downloading uv...
Installing uv...
uv installed successfully!
```

**Important**: **Close and reopen your Terminal** after installation.

#### Verify installation:

```bash
uv --version
```

**Expected output:**
```
uv 0.x.x
```

<details>
<summary>❓ Don't want to use uv?</summary>

You can use standard pip instead (slower but works fine):
- Skip uv installation
- Use "Option B: Using Standard pip" in the Installation section
- Everything else works the same

</details>

---

### 5. Claude Desktop

**Why needed**: Ragdex is an MCP server designed to work with Claude Desktop.

#### Download and install:

1. Visit: [https://claude.ai/download](https://claude.ai/download)
2. Download the installer for your platform
3. Install Claude Desktop
4. **Launch it at least once** to create configuration files

#### Verify installation:

**On macOS:**
```bash
ls ~/Library/Application\ Support/Claude/
```

**Expected**: You should see the Claude configuration directory

**On Linux:**
```bash
ls ~/.config/Claude/
```

**Account**: Free tier works fine. Paid subscription not required for Ragdex.

---

## 🔐 Permissions & Access

### 1. Admin/Sudo Access

**Why needed**:
- Installing Homebrew (macOS)
- Installing system packages (Linux)
- Setting up LaunchAgents for background services (macOS)

#### Check if you have admin access:

```bash
sudo -v
```

**Expected**: You'll be prompted for your password. If you can enter it successfully, you have admin access.

**If you don't have admin access**:
- Contact your system administrator
- You may be able to install Ragdex in user space (advanced)
- Some features (background services) won't work without admin access

---

### 2. Full Disk Access (macOS Only) - CRITICAL

**⚠️ This is one of the most common causes of "No documents found" errors!**

#### Why Full Disk Access is needed - Technical Explanation

**Background**: Starting with macOS Mojave (10.14), Apple introduced **System Integrity Protection (SIP)** and **Privacy Protections** to prevent malicious apps from accessing sensitive user data without explicit permission.

**Protected Locations** that require Full Disk Access:
- `~/Documents` - Your Documents folder
- `~/Desktop` - Your Desktop files
- `~/Downloads` - Downloaded files
- `~/Library/Mail` - Apple Mail data
- `~/Library/CloudStorage` - iCloud Drive files
- External drives and network shares

**How Ragdex accesses your documents**:
1. Ragdex runs Python scripts from Terminal (or iTerm, etc.)
2. These scripts need to **read** your documents to index them
3. macOS sees Terminal trying to access protected folders
4. **Without Full Disk Access**: macOS blocks access with "Operation not permitted"
5. **With Full Disk Access**: macOS allows Terminal (and scripts it runs) to read these folders

**What happens without Full Disk Access:**

| Symptom | Cause |
|---------|-------|
| ❌ "0 documents found" | Cannot read `~/Documents` folder |
| ❌ "Permission denied" errors | macOS blocks file access |
| ❌ Partial indexing only | Can only read unprotected folders like `/tmp` |
| ❌ Email indexing fails | Cannot read `~/Library/Mail` |
| ❌ iCloud files skipped | Cannot access `~/Library/CloudStorage` |

**Security Note**: You're granting Full Disk Access to **Terminal** (the application), not to Ragdex specifically. This means any script or command you run in Terminal will have this access. This is safe if you:
- Only run scripts you trust
- Download scripts from official sources
- Review code before running it

**Alternative approaches that DON'T work**:
- ❌ Running with `sudo` - Doesn't bypass privacy protections
- ❌ Changing file permissions - Privacy protections override file permissions
- ❌ Moving documents elsewhere - Your documents should stay where they are
- ✅ **Only solution**: Grant Full Disk Access to Terminal

#### Grant Full Disk Access to Terminal:

1. **Open System Preferences** (or System Settings on macOS 13+)
2. Click **Security & Privacy** (or **Privacy & Security**)
3. Click the **Privacy** tab
4. Scroll down and select **Full Disk Access**
5. Click the 🔒 lock icon and enter your password
6. Click the **+** button
7. Navigate to **Applications → Utilities → Terminal** (or iTerm if you use that)
8. Select Terminal and click **Open**
9. **Restart Terminal** for changes to take effect

#### Verify Full Disk Access:

```bash
ls ~/Library/Mail
```

**Expected output** (if access granted):
```
V10  V2  V3  V4  V5  V6  V7  V8  V9
(or folder names)
```

**If you see** "Permission denied" or "Operation not permitted", Full Disk Access is **not** granted.

#### Alternative: Use a different terminal

If you use iTerm2, Warp, or another terminal emulator, grant Full Disk Access to that application instead of Terminal.

---

## 🔧 Optional Dependencies (Format-Specific)

These tools are **only needed for specific document formats**. Install them only if you have these file types.

### For E-books (MOBI, AZW, AZW3)

#### Calibre

**When needed**: Only if you have Kindle ebooks (.mobi, .azw, .azw3 files)

**What happens without it**: MOBI/AZW/AZW3 files will be skipped during indexing

**Installation:**

```bash
# macOS
brew install --cask calibre

# Linux (Ubuntu/Debian)
sudo apt install calibre

# Linux (Fedora/RHEL)
sudo dnf install calibre
```

**Verify installation:**
```bash
ebook-convert --version
```

**Expected output:**
```
ebook-convert (calibre 6.x.x)
```

---

### For Legacy Word Documents (.doc)

#### LibreOffice

**When needed**: Only for **old .doc files** (NOT .docx - those work natively)

**What happens without it**: .doc files will be skipped (but .docx works fine)

**Installation:**

```bash
# macOS
brew install --cask libreoffice

# Linux (Ubuntu/Debian)
sudo apt install libreoffice

# Linux (Fedora/RHEL)
sudo dnf install libreoffice
```

**Verify installation:**
```bash
soffice --version
```

**Expected output:**
```
LibreOffice 7.x.x.x
```

---

### For Scanned PDFs (OCR)

#### ocrmypdf + Tesseract

**When needed**: PDFs that are scanned images (no selectable text)

**What happens without it**: Scanned PDFs will have no extractable text

**Installation:**

```bash
# macOS
brew install ocrmypdf tesseract

# For non-English documents, install language packs
brew install tesseract-lang

# Linux (Ubuntu/Debian)
sudo apt install ocrmypdf tesseract-ocr

# For other languages
sudo apt install tesseract-ocr-[lang]  # e.g., tesseract-ocr-spa for Spanish
```

**Verify installation:**
```bash
ocrmypdf --version
tesseract --version
```

**Expected output:**
```
ocrmypdf 14.x.x
tesseract 5.x.x
```

---

### For Advanced PDF Processing

#### Ghostscript

**When needed**: Corrupted or complex PDFs that fail standard processing

**What happens without it**: Some problematic PDFs may fail to index

**Installation:**

```bash
# macOS
brew install ghostscript

# Linux (Ubuntu/Debian)
sudo apt install ghostscript

# Linux (Fedora/RHEL)
sudo dnf install ghostscript
```

**Verify installation:**
```bash
gs --version
```

---

#### poppler-utils

**When needed**: Advanced PDF conversion and utilities

**Installation:**

```bash
# macOS
brew install poppler

# Linux (Ubuntu/Debian)
sudo apt install poppler-utils

# Linux (Fedora/RHEL)
sudo dnf install poppler-utils
```

**Verify installation:**
```bash
pdfinfo --version
```

---

## 📚 Document Library Requirements

### Supported File Formats

| Format | Extension | Notes |
|--------|-----------|-------|
| **PDF** | .pdf | Including scanned (with OCR) |
| **Word** | .docx | Native support |
| **Word (Legacy)** | .doc | Requires LibreOffice |
| **E-books** | .epub | Native support |
| **Kindle** | .mobi, .azw, .azw3 | Requires Calibre |
| **Plain Text** | .txt, .md | Native support |
| **Emails** 🔒 | .emlx | Apple Mail - **OPTIONAL** (disabled by default) |
| **Emails** 🔒 | .olm | Outlook export - **OPTIONAL** (disabled by default) |

> **🔒 Privacy Note**: Email indexing is **DISABLED by default** to protect your privacy. Ragdex will NOT access or index your emails unless you explicitly enable this feature. [How to enable email indexing →](#-optional-enable-email-indexing)

### NOT Supported

| Format | Why Not | Workaround |
|--------|---------|------------|
| Encrypted PDFs | Password-protected | Remove password first |
| DRM ebooks | Digital Rights Management | Remove DRM with Calibre plugin |
| .msg files | Outlook MSG format | Export to OLM format |
| .pst files | Outlook archive | Export to OLM or EMLX |
| Images (JPG, PNG) | Image files | OCR with external tool first |

### Document Organization Tips

- **No special organization required** - Keep your current folder structure
- **Subdirectories supported** - Ragdex scans recursively
- **Symlinks NOT supported** - Use real directories
- **iCloud Drive/Cloud files** - Must be downloaded locally (not "on-demand")
- **External drives** - Work but may have permission issues

---

## ✅ Prerequisites Verification Script

Run this script to check if you have everything needed:

```bash
# === Ragdex Prerequisites Check ===

echo "=== System Check ==="
sw_vers 2>/dev/null || cat /etc/os-release | grep PRETTY_NAME  # OS version
uname -m  # Architecture

echo -e "\n=== Python Check ==="
python3 --version  # Should show 3.10.x, 3.11.x, or 3.12.x

echo -e "\n=== Required Tools (macOS) ==="
xcode-select -p 2>/dev/null && echo "✅ Xcode CLI Tools" || echo "❌ Xcode CLI Tools missing"
brew --version 2>/dev/null && echo "✅ Homebrew" || echo "❌ Homebrew missing"

echo -e "\n=== Package Manager ==="
uv --version 2>/dev/null && echo "✅ uv" || echo "ℹ️ uv not installed (can use pip)"

echo -e "\n=== Full Disk Access Test (macOS) ==="
ls ~/Library/Mail >/dev/null 2>&1 && echo "✅ Full Disk Access granted" || echo "❌ Full Disk Access NOT granted"

echo -e "\n=== Optional Tools ==="
ebook-convert --version 2>/dev/null | head -1 && echo "✅ Calibre" || echo "ℹ️ Calibre not installed (needed for MOBI)"
soffice --version 2>/dev/null && echo "✅ LibreOffice" || echo "ℹ️ LibreOffice not installed (needed for .doc)"
ocrmypdf --version 2>/dev/null && echo "✅ ocrmypdf" || echo "ℹ️ ocrmypdf not installed (needed for scanned PDFs)"

echo -e "\n=== Resources ==="
df -h ~ | tail -1  # Disk space
free -h 2>/dev/null || vm_stat | head -4  # Memory (Linux or macOS)
```

**Copy the entire script** above, paste it into Terminal, and press Enter.

---

## 🔧 Installing Correct Prerequisite Versions

**Found issues with the verification script?** Here's how to install the correct versions of each prerequisite.

### Python Version Requirements

**Required**: Python 3.10, 3.11, or 3.12 (NOT 3.13, NOT 3.9 or lower)

#### Check Your Current Version

```bash
python3 --version
```

**Expected output**: `Python 3.10.x`, `Python 3.11.x`, or `Python 3.12.x`

#### Install Python 3.11 (Recommended)

<details>
<summary><strong>macOS Installation</strong></summary>

**Prerequisites**: Homebrew must be installed first (see below)

```bash
# Install Python 3.11
brew install python@3.11

# Verify installation
/opt/homebrew/bin/python3.11 --version
# Expected: Python 3.11.x

# Note: On Intel Macs, path may be /usr/local/bin/python3.11
```

**Set as default (optional)**:
```bash
# Add to your shell profile (~/.zshrc or ~/.bashrc)
echo 'alias python3=/opt/homebrew/bin/python3.11' >> ~/.zshrc
source ~/.zshrc

# Verify
python3 --version  # Should now show 3.11.x
```

</details>

<details>
<summary><strong>Ubuntu/Debian Installation</strong></summary>

```bash
# Update package list
sudo apt update

# Install Python 3.11 with all necessary tools
sudo apt install python3.11 python3.11-venv python3.11-dev python3.11-distutils

# Verify installation
python3.11 --version
# Expected: Python 3.11.x

# Set as default (optional)
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1
```

</details>

<details>
<summary><strong>Fedora/RHEL Installation</strong></summary>

```bash
# Install Python 3.11 with development tools
sudo dnf install python3.11 python3.11-devel python3.11-pip

# Verify installation
python3.11 --version
# Expected: Python 3.11.x
```

</details>

---

### Xcode Command Line Tools (macOS Only)

**Required for**: Compiling Python packages with C extensions (like ChromaDB dependencies)

#### Check if Installed

```bash
xcode-select -p
```

**Expected output**: `/Library/Developer/CommandLineTools`
**If missing**: `xcode-select: error: unable to get active developer directory`

#### Install Xcode CLI Tools

```bash
# Trigger installation
xcode-select --install
```

**What happens:**
1. A popup window appears
2. Click "Install" button
3. Accept the license agreement
4. Wait 5-10 minutes for download and installation
5. Installation completes automatically

**Verify installation:**
```bash
xcode-select -p
# Expected: /Library/Developer/CommandLineTools

# Test by checking for gcc
gcc --version
# Expected: Apple clang version 14.x or newer
```

---

### Homebrew (macOS Package Manager)

**Required for**: Installing Python, uv, and optional tools on macOS

#### Check if Installed

```bash
brew --version
```

**Expected output**: `Homebrew 4.x.x`
**If missing**: `command not found: brew`

#### Install Homebrew

```bash
# Run the official installation script
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

**What happens:**
1. Script downloads and installs Homebrew (~5 minutes)
2. You'll be prompted for your password (admin access required)
3. Follow on-screen instructions to add Homebrew to your PATH

**Add Homebrew to PATH** (if not done automatically):

<details>
<summary>For Apple Silicon Macs (M1/M2/M3)</summary>

```bash
# Add to shell profile
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
eval "$(/opt/homebrew/bin/brew shellenv)"

# Verify
brew --version
```

</details>

<details>
<summary>For Intel Macs</summary>

```bash
# Add to shell profile
echo 'eval "$(/usr/local/bin/brew shellenv)"' >> ~/.zprofile
eval "$(/usr/local/bin/brew shellenv)"

# Verify
brew --version
```

</details>

**After installation:**
```bash
# Close and reopen Terminal
# Then verify
brew --version
# Expected: Homebrew 4.x.x or newer

# Update Homebrew
brew update
```

---

### uv (Fast Python Package Manager)

**Recommended for**: 10-100x faster package installation than pip

#### Check if Installed

```bash
uv --version
```

**Expected output**: `uv 0.x.x`
**If missing**: `command not found: uv`

#### Install uv

```bash
# Run the official installation script
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Expected output:**
```
Downloading uv...
Installing uv to /Users/yourname/.cargo/bin
uv installed successfully!
```

**Important**: Close and reopen Terminal after installation

**Verify installation:**
```bash
uv --version
# Expected: uv 0.x.x
```

**If command not found after reopening Terminal:**
```bash
# Add to PATH manually
echo 'export PATH="$HOME/.cargo/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc

# Verify again
uv --version
```

---

### pip (Python Package Installer)

**Minimum Version**: 23.0 or newer (25.x recommended)

#### Check Your pip Version

```bash
# If in virtual environment:
pip --version

# Or use full path:
python3 -m pip --version
```

**Expected output**: `pip 25.3.x` (or 23.x+)
**If outdated**: `pip 21.x.x` or lower

#### Upgrade pip

**If you have a virtual environment** (recommended):
```bash
# Activate virtual environment
source ~/ragdex_env/bin/activate

# Upgrade pip
python -m pip install --upgrade pip

# Verify new version
pip --version
# Expected: pip 25.x.x or newer
```

**If using system Python** (not recommended):
```bash
# Upgrade system pip (may require sudo on some systems)
python3 -m pip install --upgrade pip --user

# Verify
python3 -m pip --version
```

**If upgrade fails** (externally-managed-environment error):
```bash
# This means you must use a virtual environment
# Create one first:
python3 -m venv ~/ragdex_env
source ~/ragdex_env/bin/activate

# Now upgrade pip inside the venv
pip install --upgrade pip

# Verify
pip --version  # Should show 25.x
```

---

### setuptools and wheel (Build Tools)

**Sometimes needed for**: Building packages from source

#### Install/Upgrade in Virtual Environment

```bash
# Activate virtual environment
source ~/ragdex_env/bin/activate

# Install/upgrade build tools
pip install --upgrade setuptools wheel

# Verify
pip show setuptools wheel
```

---

## 📋 Complete Fresh Installation Checklist

**Starting from scratch?** Follow these steps in order:

### macOS Fresh Installation (Using uv - Recommended)

```bash
# 1. Install Xcode Command Line Tools
xcode-select --install
# Wait for popup, click Install, wait 5-10 minutes

# 2. Install Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
# Follow on-screen instructions
# Close and reopen Terminal

# 3. Verify Homebrew
brew --version

# 4. Install Python 3.11
brew install python@3.11

# 5. Verify Python
/opt/homebrew/bin/python3.11 --version

# 6. Install uv (⭐ RECOMMENDED - 10-100x faster than pip)
curl -LsSf https://astral.sh/uv/install.sh | sh
# Close and reopen Terminal

# 7. Verify uv installation
uv --version

# 8. Create virtual environment with uv
uv venv ~/ragdex_env --python /opt/homebrew/bin/python3.11

# 9. Install Ragdex with uv (FAST - ~2 minutes)
uv pip install --python ~/ragdex_env/bin/python ragdex

# 10. Verify installation
~/ragdex_env/bin/python -c "import ragdex; print('✅ Ragdex installed successfully!')"
```

<details>
<summary><strong>Alternative: Using pip (slower, not recommended)</strong></summary>

```bash
# Follow steps 1-5 above, then:

# 6. Skip uv installation

# 7. Create virtual environment
/opt/homebrew/bin/python3.11 -m venv ~/ragdex_env

# 8. Activate and upgrade pip
source ~/ragdex_env/bin/activate
python -m pip install --upgrade pip

# 9. Verify pip version
pip --version  # Should be 25.x or newer

# 10. Install Ragdex with pip (SLOW - ~5-8 minutes)
pip install ragdex
```

</details>

### Linux Fresh Installation (Ubuntu/Debian - Using uv)

```bash
# 1. Update system
sudo apt update && sudo apt upgrade -y

# 2. Install build tools and Python
sudo apt install -y build-essential python3.11 python3.11-venv python3.11-dev

# 3. Verify Python
python3.11 --version

# 4. Install uv (⭐ RECOMMENDED - 10-100x faster than pip)
curl -LsSf https://astral.sh/uv/install.sh | sh
# Close and reopen Terminal

# 5. Verify uv installation
uv --version

# 6. Create virtual environment with uv
uv venv ~/ragdex_env --python python3.11

# 7. Install Ragdex with uv (FAST - ~2 minutes)
uv pip install --python ~/ragdex_env/bin/python ragdex

# 8. Verify installation
~/ragdex_env/bin/python -c "import ragdex; print('✅ Ragdex installed successfully!')"
```

<details>
<summary><strong>Alternative: Using pip (slower, not recommended)</strong></summary>

```bash
# Follow steps 1-3 above, then:

# 4. Skip uv installation

# 5. Create virtual environment
python3.11 -m venv ~/ragdex_env

# 6. Activate and upgrade pip
source ~/ragdex_env/bin/activate
python -m pip install --upgrade pip

# 7. Verify pip version
pip --version  # Should be 25.x or newer

# 8. Install Ragdex with pip (SLOW - ~5-8 minutes)
pip install ragdex
```

</details>

---

## ⏱️ Time Expectations

| Task | Time | Notes |
|------|------|-------|
| Installing prerequisites | 5-15 min | If tools are already installed: 0 min |
| Ragdex installation | 2-5 min | With uv: ~2 min, with pip: ~5 min |
| Model download | 5-10 min | First run only, 2GB download |
| Configuration | 2-3 min | Editing Claude config |
| Initial indexing | Varies | ~1-2 hours per 100GB of documents |

**Total setup time**: 15-30 minutes (not including document indexing)

---

## 🎯 Installation (2-8 minutes)

Now that prerequisites are ready, let's install Ragdex!

> **💡 Why uv?** We **strongly recommend** using **uv** instead of pip:
> - ⚡ **10-100x faster** (2-3 min vs 5-8 min installation)
> - 🛡️ **Better dependency resolution** - avoids version conflicts
> - 🎯 **No virtual environment activation needed** - simpler workflow
> - 🔒 **More reliable** - handles package metadata better
> - ✅ **Prevents common errors** like outdated pip issues

### Using uv (⭐ Strongly Recommended)

**This is the preferred installation method for all users.**

#### 1. Create a virtual environment

A virtual environment keeps Ragdex isolated from other Python projects.

```bash
uv venv ~/ragdex_env
```

**Expected output:**
```
Using CPython 3.11.x
Creating virtual environment at: /Users/yourname/ragdex_env
Activate with: source /Users/yourname/ragdex_env/bin/activate
```

**Note**: The path `/Users/yourname` will be your actual home directory.

#### 2. Install Ragdex

```bash
uv pip install --python ~/ragdex_env/bin/python ragdex
```

**Expected output:**
```
Resolved 45 packages in 1.2s
Downloaded 45 packages in 3.4s
Installed 45 packages in 890ms
  + ragdex
  + chromadb
  + langchain
  ... (more packages)
```

**⏱️ Time estimate**: 2-3 minutes

✅ **Installation complete!** Skip to the Configuration section below.

---

### Using pip (⚠️ Fallback Option - Slower)

**Only use this if you cannot install uv.** pip is slower and more error-prone.

<details>
<summary><strong>⚠️ Click here only if uv installation failed</strong></summary>

#### 1. Create a virtual environment

```bash
python3 -m venv ~/ragdex_env
```

**Expected output:**
```
(No output means success)
```

#### 2. Activate the virtual environment

```bash
source ~/ragdex_env/bin/activate
```

**Expected output:**
```
(ragdex_env) yourname@computer:~$
```

**Note**: Your prompt should now show `(ragdex_env)` at the beginning.

#### 3. Install Ragdex

```bash
pip install ragdex
```

**Expected output:**
```
Collecting ragdex
  Downloading ragdex-0.2.x-py3-none-any.whl
Collecting chromadb...
... (many lines of installation messages)
Successfully installed ragdex-0.2.x chromadb-... langchain-...
```

**⏱️ Time estimate**: 5-8 minutes

✅ **Installation complete!** Continue to the Configuration section below.

**💡 Recommendation**: For future projects, consider installing uv for faster package management.

</details>

---

## ⚡ Quick Installation Troubleshooting

**Having issues during installation?** Here are the most common problems and quick fixes:

### Issue 1: "command not found: uv"

**Problem**: You installed uv but the command isn't recognized.

**Quick Fix**:
```bash
# Close and reopen Terminal, then try again
# If still not working, add to PATH:
echo 'export PATH="$HOME/.cargo/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
uv --version  # Should now work
```

---

### Issue 2: "error: externally-managed-environment"

**Problem**: Python refuses to install packages (common on newer systems).

**Why this happens**: System Python is protected to prevent breaking OS tools.

**Best Fix** (⭐ Use uv - avoids this error entirely):
```bash
# Install uv if you haven't already:
curl -LsSf https://astral.sh/uv/install.sh | sh
# Close and reopen Terminal

# Create venv and install with uv (no activation needed):
uv venv ~/ragdex_env
uv pip install --python ~/ragdex_env/bin/python ragdex
```

**Alternative Fix** (if you must use pip):
```bash
# Create virtual environment:
python3 -m venv ~/ragdex_env

# Activate and install:
source ~/ragdex_env/bin/activate
pip install ragdex
```

**💡 Why uv is better**: uv doesn't require virtual environment activation and avoids many pip-related errors.

---

### Issue 3: "No matching distribution found for ragdex" + Outdated pip Warning

**Problem**: You see these errors:
```
ERROR: Could not find a version that satisfies the requirement ragdex (from versions: none)
ERROR: No matching distribution found for ragdex
WARNING: You are using pip version 21.2.4; however, version 25.3 is available.
```

**Root Cause**: Your pip version is too old (pip 21.2.4 is from 2021). Old pip versions can't find newer packages due to outdated package index metadata.

**Best Fix** (⭐ Switch to uv - avoids pip version issues):
```bash
# Install uv (if you haven't already)
curl -LsSf https://astral.sh/uv/install.sh | sh
# Close and reopen Terminal

# Verify uv installation
uv --version

# Install ragdex with uv (avoids all pip-related issues)
uv pip install --python ~/ragdex_env/bin/python ragdex
```

**💡 Why this works**: uv uses modern package resolution and doesn't rely on outdated pip versions.

**Alternative Fix** (if you must use pip):
```bash
# Activate your virtual environment
source ~/ragdex_env/bin/activate

# Upgrade pip to latest version (25.3+)
python -m pip install --upgrade pip

# Verify pip version (should show 25.x or newer)
pip --version

# Now install ragdex
pip install ragdex
```

**If pip upgrade fails**:
```bash
# Check internet connection
ping pypi.org

# Try with explicit index URL
pip install --index-url https://pypi.org/simple ragdex
```

**Still failing?** Check Python version compatibility:
```bash
python --version  # Must be 3.10, 3.11, or 3.12 (NOT 3.13)
```

---

### Issue 4: "Building wheel for chromadb failed"

**Problem**: ChromaDB (dependency) can't compile on your system.

**Likely cause**: Missing Xcode Command Line Tools (macOS) or build tools (Linux).

**Quick Fix (macOS)**:
```bash
# Install Xcode Command Line Tools:
xcode-select --install

# Wait for installation, then try again:
uv pip install --python ~/ragdex_env/bin/python ragdex
```

**Quick Fix (Linux)**:
```bash
# Ubuntu/Debian:
sudo apt update
sudo apt install build-essential python3-dev

# Fedora/RHEL:
sudo dnf install gcc gcc-c++ python3-devel

# Try installation again
```

---

### Issue 5: Python version errors

**Problem**: "Python 3.13 is not supported" or "requires Python >=3.10"

**Quick Fix**:
```bash
# Check your Python version:
python3 --version

# If wrong version, install Python 3.11:
# macOS:
brew install python@3.11

# Create venv with specific version:
/opt/homebrew/bin/python3.11 -m venv ~/ragdex_env

# Install with the correct Python:
uv pip install --python ~/ragdex_env/bin/python ragdex
```

---

### Issue 6: "SSL: CERTIFICATE_VERIFY_FAILED"

**Problem**: Can't download packages due to SSL errors.

**Quick Fix**:
```bash
# macOS: Install certificates
/Applications/Python\ 3.*/Install\ Certificates.command

# Or upgrade certifi:
pip install --upgrade certifi

# Try again
```

---

### Issue 7: Installation is extremely slow

**Problem**: pip is taking 10+ minutes to install packages.

**Quick Fix**:
```bash
# Use uv instead (10-100x faster):
curl -LsSf https://astral.sh/uv/install.sh | sh

# Close and reopen Terminal

# Install with uv:
uv pip install --python ~/ragdex_env/bin/python ragdex
```

---

### Issue 8: "Permission denied" during installation

**Problem**: Don't have permission to write files.

**Quick Fix**:
```bash
# DON'T use sudo with pip!
# Instead, make sure you're using a virtual environment:

# Create venv in your home directory:
python3 -m venv ~/ragdex_env

# Install there (no sudo needed):
source ~/ragdex_env/bin/activate
pip install ragdex
```

---

### Still Having Issues?

1. **Check the full troubleshooting guide**: [Complete Troubleshooting →](#🔧-troubleshooting)

2. **Run the diagnostics**:
   ```bash
   python3 --version
   which python3
   pip --version
   echo $PATH
   ```

3. **Try the alternative installation method**:
   - If uv isn't working, use pip
   - If pip isn't working, try uv

4. **Get help**:
   - Copy the exact error message
   - Note your OS and Python version
   - Post to [GitHub Discussions](https://github.com/hpoliset/ragdex/discussions)

---

## ⚙️ Configuration (5 minutes)

### Step 1: Set Up Ragdex Services

The easiest way to configure Ragdex is using the automated installer:

#### 1. Download the setup script

```bash
cd ~
curl -O https://raw.githubusercontent.com/hpoliset/ragdex/main/setup_services.sh
chmod +x setup_services.sh
```

**Expected output:**
```
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100 15432  100 15432    0     0  89234      0 --:--:-- --:--:-- --:--:-- 89234
```

#### 2. Run the interactive setup

```bash
./setup_services.sh
```

The installer will ask you several questions:

**Question 1**: "Where are your documents located?"
- **Default**: `~/Documents` (your Documents folder)
- **Tip**: Press Enter to use the default, or type a custom path

**Question 2**: "Where should Ragdex store its database?"
- **Default**: `~/.ragdex/chroma_db`
- **Tip**: Press Enter to use the default (recommended)

**Question 3**: "Install background indexing service?"
- **Recommendation**: Type `y` (yes) - this automatically indexes new documents

**Question 4**: "Install web monitoring dashboard?"
- **Recommendation**: Type `y` (yes) - this lets you view status at http://localhost:8888

**Expected output at the end:**
```
✅ Ragdex services installed successfully!

📋 Configuration for Claude Desktop:
Copy the JSON below and add it to your Claude Desktop config file...

{
  "mcpServers": {
    "ragdex": {
      "command": "/Users/yourname/ragdex_env/bin/ragdex-mcp",
      "env": {
        "PYTHONUNBUFFERED": "1",
        "CHROMA_TELEMETRY": "false",
        "PERSONAL_LIBRARY_DOC_PATH": "/Users/yourname/Documents",
        "PERSONAL_LIBRARY_DB_PATH": "/Users/yourname/.ragdex/chroma_db",
        "PERSONAL_LIBRARY_LOGS_PATH": "/Users/yourname/.ragdex/logs",
        "MCP_WARMUP_ON_START": "true",
        "MCP_INIT_TIMEOUT": "30",
        "MCP_TOOL_TIMEOUT": "15"
      }
    }
  }
}

🎯 Next Steps:
1. Copy the JSON configuration above
2. Add it to: ~/Library/Application Support/Claude/claude_desktop_config.json
3. Restart Claude Desktop
```

**⚠️ Important**: **Copy the entire JSON configuration** displayed by the installer. You'll need it for the next step.

---

### Step 2: Configure Claude Desktop

Now we need to tell Claude Desktop about Ragdex.

#### 1. Open Claude Desktop's configuration directory

```bash
open ~/Library/Application\ Support/Claude/
```

This will open a Finder window showing Claude's configuration folder.

#### 2. Open or create the configuration file

Look for a file named `claude_desktop_config.json`:

- **If the file exists**: Double-click to open it in a text editor
- **If the file doesn't exist**: Create it by running:
  ```bash
  touch ~/Library/Application\ Support/Claude/claude_desktop_config.json
  open ~/Library/Application\ Support/Claude/claude_desktop_config.json
  ```

#### 3. Add the Ragdex configuration

**Scenario A: Empty or new file**

If the file is empty or new, paste the entire JSON configuration from the installer:

```json
{
  "mcpServers": {
    "ragdex": {
      "command": "/Users/yourname/ragdex_env/bin/ragdex-mcp",
      "env": {
        "PYTHONUNBUFFERED": "1",
        "CHROMA_TELEMETRY": "false",
        "PERSONAL_LIBRARY_DOC_PATH": "/Users/yourname/Documents",
        "PERSONAL_LIBRARY_DB_PATH": "/Users/yourname/.ragdex/chroma_db",
        "PERSONAL_LIBRARY_LOGS_PATH": "/Users/yourname/.ragdex/logs",
        "MCP_WARMUP_ON_START": "true",
        "MCP_INIT_TIMEOUT": "30",
        "MCP_TOOL_TIMEOUT": "15"
      }
    }
  }
}
```

**Scenario B: File already has other MCP servers**

If your file already looks like this:
```json
{
  "mcpServers": {
    "some-other-server": {
      ...
    }
  }
}
```

Add the ragdex section inside `"mcpServers"`:
```json
{
  "mcpServers": {
    "some-other-server": {
      ...
    },
    "ragdex": {
      "command": "/Users/yourname/ragdex_env/bin/ragdex-mcp",
      "env": {
        "PYTHONUNBUFFERED": "1",
        "CHROMA_TELEMETRY": "false",
        "PERSONAL_LIBRARY_DOC_PATH": "/Users/yourname/Documents",
        "PERSONAL_LIBRARY_DB_PATH": "/Users/yourname/.ragdex/chroma_db",
        "PERSONAL_LIBRARY_LOGS_PATH": "/Users/yourname/.ragdex/logs"
      }
    }
  }
}
```

**⚠️ Important**: Make sure to use **your actual paths** from the installer output, not the examples above!

#### 4. Save the file

Save the file (Cmd+S on macOS) and close the text editor.

#### 5. Restart Claude Desktop

**This is crucial!** Claude must be fully restarted to load the new configuration:

1. **Quit Claude Desktop completely**: Press Cmd+Q (or Claude menu → Quit)
   - Don't just close the window - make sure Claude is fully quit
2. **Wait 3 seconds**
3. **Launch Claude Desktop again** from Applications

---

## 🔒 Optional: Enable Email Indexing

**By default, Ragdex does NOT index your emails** to protect your privacy. If you want to enable email indexing, follow these steps:

### Why You Might Want Email Indexing

- Search through years of email communications
- Find important attachments and discussions
- Track project conversations
- Smart filtering automatically excludes marketing, spam, and receipts

### Privacy Considerations

**Before enabling email indexing, understand:**

- ✅ **All processing is local** - Your emails never leave your computer
- ✅ **Smart filtering** - Marketing, spam, and shopping receipts are automatically excluded
- ✅ **You control what's indexed** - Configure folders and date ranges
- ⚠️ **Emails are stored in the vector database** - Similar to how documents are indexed
- ⚠️ **Claude will have access** - Any queries through Claude can access indexed emails

### How to Enable Email Indexing

#### Step 1: Edit Claude Desktop Configuration

Open your Claude Desktop config file:

```bash
open ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

#### Step 2: Add Email Environment Variables

Add these lines to the `"env"` section of your ragdex configuration:

```json
{
  "mcpServers": {
    "ragdex": {
      "command": "/Users/yourname/ragdex_env/bin/ragdex-mcp",
      "env": {
        "PYTHONUNBUFFERED": "1",
        "CHROMA_TELEMETRY": "false",
        "PERSONAL_LIBRARY_DOC_PATH": "/Users/yourname/Documents",
        "PERSONAL_LIBRARY_DB_PATH": "/Users/yourname/.ragdex/chroma_db",
        "PERSONAL_LIBRARY_LOGS_PATH": "/Users/yourname/.ragdex/logs",

        // Add these lines to enable email indexing:
        "PERSONAL_LIBRARY_INDEX_EMAILS": "true",
        "PERSONAL_LIBRARY_EMAIL_SOURCES": "apple_mail",
        "PERSONAL_LIBRARY_EMAIL_MAX_AGE_DAYS": "365",
        "PERSONAL_LIBRARY_EMAIL_EXCLUDED_FOLDERS": "Spam,Junk,Trash,Deleted Items"
      }
    }
  }
}
```

**Configuration Options Explained:**

| Variable | Value | What It Does |
|----------|-------|--------------|
| `PERSONAL_LIBRARY_INDEX_EMAILS` | `"true"` | **Required** - Enables email indexing |
| `PERSONAL_LIBRARY_EMAIL_SOURCES` | `"apple_mail"` | Email source: `apple_mail`, `outlook_local`, or both (comma-separated) |
| `PERSONAL_LIBRARY_EMAIL_MAX_AGE_DAYS` | `"365"` | Only index emails from the last N days (use `0` for all) |
| `PERSONAL_LIBRARY_EMAIL_EXCLUDED_FOLDERS` | `"Spam,Junk,Trash"` | Folders to skip (comma-separated) |

**Examples:**

<details>
<summary>📧 Apple Mail only (last 2 years)</summary>

```json
"PERSONAL_LIBRARY_INDEX_EMAILS": "true",
"PERSONAL_LIBRARY_EMAIL_SOURCES": "apple_mail",
"PERSONAL_LIBRARY_EMAIL_MAX_AGE_DAYS": "730"
```

</details>

<details>
<summary>📧 Outlook only (last 1 year)</summary>

```json
"PERSONAL_LIBRARY_INDEX_EMAILS": "true",
"PERSONAL_LIBRARY_EMAIL_SOURCES": "outlook_local",
"PERSONAL_LIBRARY_EMAIL_MAX_AGE_DAYS": "365"
```

</details>

<details>
<summary>📧 Both Apple Mail and Outlook (all emails)</summary>

```json
"PERSONAL_LIBRARY_INDEX_EMAILS": "true",
"PERSONAL_LIBRARY_EMAIL_SOURCES": "apple_mail,outlook_local",
"PERSONAL_LIBRARY_EMAIL_MAX_AGE_DAYS": "0"
```

</details>

#### Step 3: Save and Restart

1. **Save the file** (Cmd+S)
2. **Restart Claude Desktop** (Cmd+Q, then reopen)
3. **Wait for indexing** - Email indexing will begin automatically

#### Step 4: Verify Email Indexing

Check the web dashboard to see email indexing progress:

```bash
open http://localhost:8888
```

You should see:
- "Email indexing: Enabled"
- Email count increasing
- Folders being processed

Or ask Claude:

```
Can you check my library stats? Do you see any emails indexed?
```

### Smart Email Filtering

Ragdex automatically excludes:

**Marketing & Promotional:**
- Emails from known marketing domains
- Subject lines with "Unsubscribe" links
- Promotional keywords (sale, discount, offer, etc.)

**Transactional:**
- Order confirmations
- Shipping notifications
- Payment receipts
- Newsletter signups

**System:**
- Automated notifications
- No-reply senders
- Bulk emails

**You can whitelist important senders** by adding to config:

```json
"PERSONAL_LIBRARY_EMAIL_WHITELIST_SENDERS": "important@company.com,boss@work.com"
```

### Disable Email Indexing Later

To stop indexing emails:

1. Edit Claude Desktop config
2. Remove the email environment variables OR set `PERSONAL_LIBRARY_INDEX_EMAILS` to `"false"`
3. Restart Claude Desktop

**Note**: Already-indexed emails will remain in the database. To remove them, you'll need to rebuild the database (see Troubleshooting section).

---

## 🎉 First Run: Model Download

**The first time Ragdex runs, it needs to download AI models (~2GB). This happens automatically.**

### What to expect:

1. When you first interact with Ragdex in Claude, there will be a delay (5-10 minutes)
2. Behind the scenes, Ragdex is downloading:
   - Embedding model: `sentence-transformers/all-mpnet-base-v2` (~420MB)
   - Supporting libraries and models (~1.5GB)
3. You can monitor progress in the web dashboard: http://localhost:8888

**💡 Tip**: Open the web dashboard in your browser to see what's happening:

```bash
open http://localhost:8888
```

The dashboard shows:
- Indexing progress
- Documents processed
- Any errors
- System status

---

## ✅ Verification: Test Your Installation

Let's make sure everything is working correctly.

### Test 1: Check Ragdex commands are available

```bash
~/ragdex_env/bin/ragdex --version
```

**Expected output:**
```
ragdex 0.2.x
```

✅ **Success!** Ragdex CLI is installed.

---

### Test 2: Check services are running

```bash
launchctl list | grep ragdex
```

**Expected output:**
```
-       0       com.ragdex.index-monitor
-       0       com.ragdex.webmonitor
```

✅ **Success!** Background services are running.

---

### Test 3: Check web dashboard

Open your browser and go to: http://localhost:8888

**Expected result:**
- You should see the Ragdex Web Monitor dashboard
- It shows indexing status, document count, and statistics

✅ **Success!** Web dashboard is accessible.

---

### Test 4: Check Claude Desktop connection

1. Open Claude Desktop
2. Look for the hammer icon (🔨) in the lower right corner
3. Click it - you should see "ragdex" in the list of available tools

✅ **Success!** Claude can see Ragdex.

---

### Test 5: Try your first query in Claude

In Claude Desktop, type:

```
Can you check my library stats?
```

**Expected response from Claude:**
```
I'll check your library statistics using Ragdex.

[Claude uses the library_stats tool]

Your library currently has:
- X documents indexed
- X total pages
- X books
- X emails
...
```

✅ **Success!** Ragdex is working with Claude!

---

## 🎯 Your First Queries

Now that everything is working, try these example queries to explore what Ragdex can do:

### Example 1: Search your documents
```
Search my library for information about machine learning
```

### Example 2: List your documents
```
What documents do you have in my library?
```

### Example 3: Find recent documents
```
Show me the 10 most recently indexed documents
```

### Example 4: Get a summary
```
Can you summarize the main themes across my documents about [topic]?
```

### Example 5: Compare perspectives
```
Compare different perspectives on [topic] from my documents
```

### Example 6: Search emails (if you indexed emails)
```
Search my emails for discussions about [project name]
```

### Example 7: Extract quotes
```
Find notable quotes about [topic] from my library
```

**💡 Pro Tip**: The more documents you have indexed, the better the results!

---

## 📊 Understanding Indexing

After installation, Ragdex automatically starts indexing your documents. Here's what you need to know:

### How indexing works:

1. **Automatic monitoring**: The background service watches your documents folder
2. **Change detection**: Only new or modified files are processed
3. **Supported formats**:
   - PDFs (including scanned documents with OCR)
   - Microsoft Word (.docx, .doc with LibreOffice)
   - E-books (.epub, .mobi, .azw, .azw3)
   - Plain text and Markdown files
   - Emails (.emlx for Apple Mail, .olm for Outlook)

### Indexing timeline:

- **Small documents** (< 1MB): ~3-5 seconds each
- **Medium documents** (1-10MB): ~10-30 seconds each
- **Large PDFs** (> 50MB): 2-5 minutes each
- **Scanned PDFs with OCR**: 1-2 minutes per page

### Monitoring indexing progress:

**Option 1: Web dashboard**
```bash
open http://localhost:8888
```

**Option 2: Command line**
```bash
~/ragdex_env/bin/ragdex index-status
```

**Expected output:**
```
Indexing Status:
================
Documents indexed: 47
Total pages: 3,542
Last indexed: 2 minutes ago
Currently indexing: book_title.pdf (page 23/150)
```

---

## 🔧 Troubleshooting

### Problem 1: "Command not found: uv" after installation

**Solution**: Close and reopen your Terminal, then try again. If still not working:

```bash
# Add uv to your PATH
echo 'export PATH="$HOME/.cargo/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

---

### Problem 2: Wrong Python version (Python 3.13 or 3.9)

**Solution**: Install Python 3.11 using Homebrew (see Prerequisites Step 1), then create the virtual environment with the specific version:

```bash
# Using the specific Python version
/opt/homebrew/bin/python3.11 -m venv ~/ragdex_env

# Then install with uv pointing to the right Python
uv pip install --python ~/ragdex_env/bin/python ragdex
```

---

### Problem 3: Claude Desktop doesn't show Ragdex tool

**Possible causes and solutions:**

**A. Claude wasn't fully restarted**
- Make sure you used Cmd+Q to quit (not just close the window)
- Wait a few seconds before reopening

**B. JSON configuration has errors**
- Check for missing commas, brackets, or quotes
- Use a JSON validator: https://jsonlint.com
- Compare your config to the example above

**C. Wrong path in configuration**
- The path to `ragdex-mcp` must be the full absolute path
- Verify the path exists:
  ```bash
  ls -la ~/ragdex_env/bin/ragdex-mcp
  ```
- If not found, check your virtual environment location

---

### Problem 4: "No documents found" or "0 documents indexed"

**Possible causes and solutions:**

**A. Indexing hasn't started yet**
- Wait a few minutes for initial indexing
- Check web dashboard: http://localhost:8888

**B. Wrong documents path**
- Verify the path in your Claude Desktop config
- Make sure the path exists and contains documents
- Check permissions:
  ```bash
  ls -la ~/Documents
  ```

**C. Background service not running**
- Check service status:
  ```bash
  launchctl list | grep ragdex
  ```
- Restart the service:
  ```bash
  launchctl unload ~/Library/LaunchAgents/com.ragdex.index-monitor.plist
  launchctl load ~/Library/LaunchAgents/com.ragdex.index-monitor.plist
  ```

---

### Problem 5: "Model download taking too long"

**This is normal for first run!** The embedding model is ~2GB.

**Check progress:**
```bash
# Watch the download progress in logs
tail -f ~/.ragdex/logs/ragdex_*.log
```

**Slow internet?**
- Model download may take 10-20 minutes on slower connections
- Once downloaded, it won't download again
- The model is cached in `~/.cache/huggingface/`

---

### Problem 6: High memory usage

**Normal memory usage:**
- Idle: ~500MB
- Indexing: 4-8GB (temporary spikes)
- With embeddings loaded: 4-6GB

**If memory usage is too high:**
- Close other applications during initial indexing
- Consider upgrading to 16GB RAM for better performance
- Index documents in smaller batches

---

### Problem 7: Permission errors

**Solution**: Ensure Ragdex has permission to access your documents:

```bash
# On macOS, you may need to grant Full Disk Access
# Go to: System Preferences → Security & Privacy → Privacy → Full Disk Access
# Add Terminal or your terminal emulator to the list

# Also ensure directory permissions:
chmod -R 755 ~/.ragdex
~/ragdex_env/bin/ragdex ensure-dirs
```

---

### Problem 8: Services not starting after reboot

**Solution**: LaunchAgents should start automatically. If they don't:

```bash
# Reload services manually
launchctl load ~/Library/LaunchAgents/com.ragdex.index-monitor.plist
launchctl load ~/Library/LaunchAgents/com.ragdex.webmonitor.plist

# Verify they're running
launchctl list | grep ragdex
```

---

### Still having issues?

1. **Check the logs**:
   ```bash
   tail -f ~/.ragdex/logs/ragdex_*.log
   ```

2. **Run diagnostics**:
   ```bash
   ~/ragdex_env/bin/ragdex config
   ~/ragdex_env/bin/ragdex index-status
   ```

3. **Get help**:
   - GitHub Issues: https://github.com/hpoliset/ragdex/issues
   - Discussions: https://github.com/hpoliset/ragdex/discussions
   - Include the output of the diagnostic commands above

---

## 🎓 Next Steps

Congratulations! You now have Ragdex up and running. Here's what to explore next:

### 1. Explore Advanced Features

Read the full documentation for:
- Email indexing and filtering
- Service management
- Advanced MCP tools
- Custom configuration options

**→ [Read the Full README](README.md)**

### 2. Customize Your Setup

- Configure email indexing (Apple Mail, Outlook)
- Adjust indexing settings
- Set up OCR for scanned PDFs
- Install optional dependencies

**→ [View Configuration Guide](README.md#-documentation)**

### 3. Learn the Architecture

Understand how Ragdex works under the hood:
- Vector embeddings and RAG
- ChromaDB storage
- MCP protocol
- Background services

**→ [Read Architecture Documentation](docs/ARCHITECTURE.md)**

### 4. Install Optional Tools

Enhance Ragdex capabilities:
- **Calibre**: For MOBI/AZW ebook support
- **LibreOffice**: For .doc file support
- **ocrmypdf**: For scanned PDF OCR

**→ [View System Requirements](README.md#system-requirements)**

### 5. Optimize Performance

Tips for better performance:
- Enable parallel processing
- Adjust memory settings
- Optimize index parameters
- Use advanced filtering

**→ [View Performance Guide](README.md#-stats--performance)**

---

## 📚 Additional Resources

- **Full Documentation**: [README.md](README.md)
- **Architecture Details**: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- **Command Reference**: [QUICK_REFERENCE.md](QUICK_REFERENCE.md)
- **Contributing Guide**: [CONTRIBUTING.md](CONTRIBUTING.md)
- **Project Structure**: [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)
- **Changelog**: [CHANGELOG.md](CHANGELOG.md)

---

## 💬 Getting Help

If you run into issues not covered in this guide:

1. **Check existing issues**: [GitHub Issues](https://github.com/hpoliset/ragdex/issues)
2. **Ask questions**: [GitHub Discussions](https://github.com/hpoliset/ragdex/discussions)
3. **Report bugs**: [New Issue](https://github.com/hpoliset/ragdex/issues/new)

When asking for help, please include:
- Your OS and Python version
- Output of `ragdex config`
- Relevant log excerpts from `~/.ragdex/logs/`
- Steps to reproduce the issue

---

<div align="center">

**🎉 Welcome to the Ragdex community!**

If you find Ragdex useful, please consider ⭐ starring the project on GitHub!

[⭐ Star on GitHub](https://github.com/hpoliset/ragdex) | [📖 Full Documentation](README.md) | [💬 Discussions](https://github.com/hpoliset/ragdex/discussions)

</div>
