#!/bin/bash

# Quick Start Script for Personal Document Library MCP Server
# Interactive setup that guides users through installation

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Get script directory and project root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$SCRIPT_DIR"

# Source centralized Python environment configuration if it exists
if [ -f "$SCRIPT_DIR/scripts/python_env.sh" ]; then
    source "$SCRIPT_DIR/scripts/python_env.sh"
    USE_CENTRALIZED_CONFIG=true
else
    USE_CENTRALIZED_CONFIG=false
fi

# Apple Silicon helpers (native arm64 tooling, no Rosetta)
source "$SCRIPT_DIR/scripts/lib/macos_arch.sh"

# An installer translated by Rosetta would pick Intel tools - restart natively
if is_apple_silicon && is_running_under_rosetta; then
    echo "Restarting installer natively (arm64) instead of under Rosetta..."
    exec arch -arm64 /bin/bash "$0" "$@"
fi
BREW_CMD=$(find_native_brew || true)
if is_apple_silicon && [ -z "$BREW_CMD" ] && command -v brew &> /dev/null; then
    echo "⚠️  Only an Intel Homebrew ($(command -v brew)) was found; it installs Rosetta-only tools."
    echo "   Install native Homebrew in /opt/homebrew from https://brew.sh for automatic installs."
fi

# Parse command line arguments
AUTO_MODE=false
AUTO_BOOKS_PATH=""
AUTO_DB_PATH=""
AUTO_INSTALL_SERVICE=false
AUTO_START_WEB=false
AUTO_RUN_INDEX=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --auto)
            AUTO_MODE=true
            AUTO_INSTALL_SERVICE=true
            AUTO_START_WEB=true
            AUTO_RUN_INDEX=true
            shift
            ;;
        --books-path)
            AUTO_BOOKS_PATH="$2"
            shift 2
            ;;
        --db-path)
            AUTO_DB_PATH="$2"
            shift 2
            ;;
        --with-services)
            AUTO_INSTALL_SERVICE=true
            AUTO_START_WEB=true
            shift
            ;;
        --no-service)
            AUTO_INSTALL_SERVICE=false
            shift
            ;;
        --no-web)
            AUTO_START_WEB=false
            shift
            ;;
        --no-index)
            AUTO_RUN_INDEX=false
            shift
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --auto                Run in automatic mode with defaults and services"
            echo "  --with-services       Install background indexing and web monitor services"
            echo "  --books-path PATH     Set books directory path"
            echo "  --db-path PATH        Set database directory path"
            echo "  --no-service          Don't install background service (with --auto)"
            echo "  --no-web              Don't start web monitor (with --auto)"
            echo "  --no-index            Don't run initial indexing (with --auto)"
            echo "  --help                Show this help message"
            echo ""
            echo "Examples:"
            echo "  # Interactive setup (default)"
            echo "  ./quick_start.sh"
            echo ""
            echo "  # Fully automated with defaults"
            echo "  ./quick_start.sh --auto"
            echo ""
            echo "  # Automated with custom books path"
            echo "  ./quick_start.sh --auto --books-path /Users/me/Books"
            echo ""
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

clear
echo -e "${MAGENTA}"
echo "╔══════════════════════════════════════════════════════════╗"
echo "║   📚 Personal Document Library MCP Server - Quick Start 📚║"
echo "╚══════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo ""
echo "Welcome! This script will help you set up the Personal Document Library MCP Server."
echo ""

# Function to prompt for yes/no
prompt_yes_no() {
    local prompt="$1"
    local default="${2:-y}"
    local response
    
    # In auto mode, always return yes for default=y questions
    if [ "$AUTO_MODE" = true ]; then
        if [ "$default" = "y" ]; then
            echo "  Auto: Yes"
            return 0
        else
            echo "  Auto: No"
            return 1
        fi
    fi
    
    if [ "$default" = "y" ]; then
        prompt="${prompt} [Y/n]: "
    else
        prompt="${prompt} [y/N]: "
    fi
    
    read -p "$prompt" response
    response="${response:-$default}"
    
    if [[ "$response" =~ ^[Yy]$ ]]; then
        return 0
    else
        return 1
    fi
}

# Function to prompt for directory path
prompt_directory() {
    local prompt="$1"
    local default="$2"
    local response

    # In auto mode, use default or provided path
    if [ "$AUTO_MODE" = true ]; then
        echo -e "  Auto: Using $default" >&2
        echo "$default"
        return
    fi

    echo -e "${CYAN}$prompt${NC}" >&2
    echo -e "Default: ${YELLOW}$default${NC}" >&2
    read -p "Path (press Enter for default): " response

    if [ -z "$response" ]; then
        echo "$default"
    else
        # Expand ~ to home directory
        echo "${response/#\~/$HOME}"
    fi
}

# Check Python version
echo -e "${BLUE}📌 Checking system requirements...${NC}"
echo ""

python_cmd=""
python_version=""

# Helper function to test if a Python installation is usable
test_python() {
    local py_path="$1"
    # On Apple Silicon an Intel Python only runs under Rosetta and has no GPU (MPS) access
    if ! is_native_executable "$py_path"; then
        echo "  ⚠️  Skipping Intel (x86_64) Python at $py_path - needs Rosetta" >&2
        return 1
    fi
    # Test if it can create a venv without errors (check for broken uv installations)
    if ! "$py_path" -c "import sys; sys.exit(0 if sys.base_prefix != '/install' else 1)" 2>/dev/null; then
        # Log when filtering out broken installations
        echo "  ⚠️  Skipping broken Python installation at $py_path (appears to be uv-managed)" >&2
        return 1
    fi
    # A universal Python launched under Rosetta would still run as x86_64
    if ! is_native_python "$py_path"; then
        echo "  ⚠️  Skipping Python at $py_path - not running as arm64" >&2
        return 1
    fi
    return 0
}

# Detect all available Python 3.9-3.13 installations
declare -a python_paths=()
declare -a python_versions=()
declare -a python_labels=()

# Check for Python 3.13-3.9 (newest to oldest)
for minor in 13 12 11 10 9; do
    # Check Homebrew installations first (prefer these)
    for brew_base in "/opt/homebrew/opt" "/usr/local/opt"; do
        brew_path="$brew_base/python@3.$minor/bin/python3.$minor"
        if [ -x "$brew_path" ] && test_python "$brew_path"; then
            version=$("$brew_path" --version 2>&1 | cut -d' ' -f2)
            python_paths+=("$brew_path")
            python_versions+=("$version")
            python_labels+=("Python $version - Homebrew ($brew_path)")
        fi
    done

    # Check system/PATH installations
    if command -v python3.$minor &> /dev/null; then
        py_path=$(command -v python3.$minor)
        # Skip if already added as Homebrew installation
        already_added=false
        for existing in "${python_paths[@]}"; do
            if [ "$existing" = "$py_path" ]; then
                already_added=true
                break
            fi
        done

        if [ "$already_added" = false ] && test_python "python3.$minor"; then
            version=$(python3.$minor --version 2>&1 | cut -d' ' -f2)
            python_paths+=("python3.$minor")
            python_versions+=("$version")
            python_labels+=("Python $version - PATH ($py_path)")
        fi
    fi
done

# Check default python3 if it's in the supported range
if command -v python3 &> /dev/null; then
    py_version=$(python3 --version 2>&1 | cut -d' ' -f2)
    major=$(echo $py_version | cut -d'.' -f1)
    minor=$(echo $py_version | cut -d'.' -f2)

    if [[ "$major" == "3" && "$minor" -ge "9" && "$minor" -le "13" ]]; then
        py_path=$(command -v python3)
        # Skip if already added
        already_added=false
        for existing in "${python_paths[@]}"; do
            if [ "$existing" = "$py_path" ]; then
                already_added=true
                break
            fi
        done

        if [ "$already_added" = false ] && test_python "python3"; then
            python_paths+=("python3")
            python_versions+=("$py_version")
            python_labels+=("Python $py_version - Default ($py_path)")
        fi
    fi
fi

# Present options to user
num_pythons=${#python_paths[@]}

if [ $num_pythons -eq 0 ]; then
    echo -e "  ${RED}✗${NC} No suitable Python installation found"
    echo ""
    echo "Python 3.9-3.13 is required (Python 3.14+ not supported due to onnxruntime)"
elif [ $num_pythons -eq 1 ]; then
    # Only one Python found, use it
    echo -e "  ${GREEN}✓${NC} ${python_labels[0]} found"
    python_cmd="${python_paths[0]}"
    python_version="${python_versions[0]}"
else
    # Multiple Pythons found, let user choose
    echo -e "${GREEN}Found ${num_pythons} compatible Python installations:${NC}"
    echo ""
    for i in "${!python_paths[@]}"; do
        num=$((i + 1))
        echo "  $num) ${python_labels[$i]}"
    done
    echo ""

    if [ "$AUTO_MODE" = true ]; then
        # In auto mode, use the first one (newest)
        echo -e "  ${CYAN}Auto mode: Using ${python_labels[0]}${NC}"
        python_cmd="${python_paths[0]}"
        python_version="${python_versions[0]}"
    else
        # Ask user to choose
        while true; do
            read -p "Select Python version (1-$num_pythons) [1]: " choice
            choice=${choice:-1}

            if [[ "$choice" =~ ^[0-9]+$ ]] && [ "$choice" -ge 1 ] && [ "$choice" -le "$num_pythons" ]; then
                idx=$((choice - 1))
                python_cmd="${python_paths[$idx]}"
                python_version="${python_versions[$idx]}"
                echo -e "  ${GREEN}✓${NC} Using ${python_labels[$idx]}"
                break
            else
                echo -e "  ${RED}Invalid choice. Please enter a number between 1 and $num_pythons${NC}"
            fi
        done
    fi
fi

# If no suitable Python found, offer to install Python 3.13
if [ -z "$python_cmd" ]; then
    echo -e "  ${RED}✗${NC} Python 3.9-3.13 is required but not found"
    echo ""

    if [[ "$OSTYPE" == "darwin"* ]] && [ -n "$BREW_CMD" ]; then
        echo -e "${CYAN}Python 3.9-3.13 is required (3.13 recommended)${NC}"

        # In auto mode, install automatically; otherwise ask
        if [ "$AUTO_MODE" = true ]; then
            echo "  Auto: Installing Python 3.13 via Homebrew..."
            install_python=true
        elif prompt_yes_no "Install Python 3.13 via Homebrew?" "y"; then
            install_python=true
        else
            install_python=false
        fi

        if [ "$install_python" = true ]; then
            echo "  Installing Python 3.13..."
            "$BREW_CMD" install python@3.13 >/dev/null 2>&1

            # Verify installation
            brew_python="$("$BREW_CMD" --prefix)/opt/python@3.13/bin/python3.13"
            if [ -x "$brew_python" ]; then
                python_cmd="$brew_python"
                python_version=$("$python_cmd" --version 2>&1 | cut -d' ' -f2)
                echo -e "  ${GREEN}✓${NC} Python 3.13 installed successfully: $python_version"
            elif command -v python3.13 &> /dev/null && is_native_python python3.13; then
                python_cmd="python3.13"
                python_version=$(python3.13 --version 2>&1 | cut -d' ' -f2)
                echo -e "  ${GREEN}✓${NC} Python 3.13 installed successfully: $python_version"
            else
                echo -e "  ${RED}✗${NC} Failed to install Python 3.13"
                echo "  Please install it manually: brew install python@3.13"
                exit 1
            fi
        else
            echo "  Please install Python 3.9-3.13 manually and try again"
            echo "  On macOS: brew install python@3.13"
            exit 1
        fi
    else
        echo "  Please install Python 3.9-3.13 and try again"
        echo "  Recommended: Python 3.13"
        if is_apple_silicon; then
            echo "  On Apple Silicon, install native Homebrew (in /opt/homebrew) from https://brew.sh,"
            echo "  then run: /opt/homebrew/bin/brew install python@3.13"
        fi
        exit 1
    fi
fi

# Check for virtual environment
echo ""
echo -e "${BLUE}📌 Setting up Python environment...${NC}"
echo ""

venv_path="${PROJECT_ROOT}/venv_mcp"

if [ -d "$venv_path" ] && ! is_native_venv "$venv_path"; then
    # An Intel venv (e.g. migrated from an Intel Mac) needs Rosetta and can't use the GPU
    intel_backup="${venv_path}.intel.bak.$(date +%Y%m%d_%H%M%S)"
    echo -e "  ${YELLOW}!${NC} Existing venv_mcp/ is not native arm64 (needs Rosetta)"
    if prompt_yes_no "  Move it to $(basename "$intel_backup") and create a native one?" "y"; then
        mv "$venv_path" "$intel_backup"
    else
        echo -e "  ${RED}✗${NC} A native arm64 virtual environment is required on Apple Silicon"
        exit 1
    fi
fi

if [ -d "$venv_path" ]; then
    echo -e "  ${GREEN}✓${NC} Virtual environment found at: venv_mcp/"
else
    echo -e "  ${YELLOW}!${NC} Virtual environment not found"
    if prompt_yes_no "  Create virtual environment now?" "y"; then
        echo -n "  Creating virtual environment... "
        $python_cmd -m venv "$venv_path"
        echo -e "${GREEN}done${NC}"
    else
        echo -e "  ${RED}✗${NC} Virtual environment is required for installation"
        exit 1
    fi
fi

# Activate virtual environment
source "$venv_path/bin/activate"

# Fix Python symlinks if needed
if [ -L "$venv_path/bin/python" ]; then
    # Check if symlink is broken
    if [ ! -e "$venv_path/bin/python" ]; then
        echo "  Fixing Python symlinks..."
        cd "$venv_path/bin"
        rm -f python
        if [ -e python3.13 ]; then
            ln -s python3.13 python
        elif [ -e python3.12 ]; then
            ln -s python3.12 python
        elif [ -e python3.11 ]; then
            ln -s python3.11 python
        else
            ln -s python3 python
        fi
        cd "$PROJECT_ROOT"
    fi
fi

# Install dependencies
echo ""
echo -e "${BLUE}📌 Installing Python dependencies...${NC}"
echo ""

if [ -f "${PROJECT_ROOT}/pyproject.toml" ]; then
    echo "  Installing ragdex and all dependencies from pyproject.toml..."

    # First ensure pip is up to date
    "${venv_path}/bin/python" -m pip install --upgrade pip setuptools wheel >/dev/null 2>&1

    # Install in editable mode with all dependencies
    echo "  This will install:"
    echo "    • ChromaDB 1.3.5+ (Python 3.13 compatible)"
    echo "    • Langchain 0.3+ for RAG"
    echo "    • Unstructured for EPUB/DOCX support"
    echo "    • All other dependencies"
    echo ""

    "${venv_path}/bin/python" -m pip install -e "${PROJECT_ROOT}" 2>&1 | grep -v "^Requirement already satisfied" || true

    if [ $? -eq 0 ]; then
        echo -e "  ${GREEN}✓${NC} Ragdex and dependencies installed successfully"
    else
        echo -e "  ${YELLOW}⚠️${NC} Some dependencies may have failed to install"
        echo "     You can try manual installation with: pip install -e ."
    fi
elif [ -f "${PROJECT_ROOT}/requirements.txt" ]; then
    echo "  Installing dependencies from requirements.txt..."

    # First ensure pip is up to date
    "${venv_path}/bin/python" -m pip install --upgrade pip setuptools wheel >/dev/null 2>&1

    "${venv_path}/bin/python" -m pip install -r "${PROJECT_ROOT}/requirements.txt" 2>&1 | grep -v "^Requirement already satisfied" || true

    if [ $? -eq 0 ]; then
        echo -e "  ${GREEN}✓${NC} Dependencies installed successfully"
    else
        echo -e "  ${YELLOW}⚠️${NC} Some dependencies may have failed to install"
    fi
else
    echo -e "  ${YELLOW}⚠️${NC} Neither pyproject.toml nor requirements.txt found"
fi

# Optional features
echo ""
echo -e "${BLUE}📌 Optional Features...${NC}"
echo ""

# Check for Calibre and offer to install
if command -v ebook-convert &> /dev/null; then
    calibre_version=$(ebook-convert --version 2>&1 | head -n1)
    echo -e "  ${GREEN}✓${NC} Calibre already installed: $calibre_version"
else
    echo -e "  ${YELLOW}!${NC} Calibre not found"
    echo ""
    echo -e "${CYAN}Calibre provides enhanced ebook support:${NC}"
    echo "  • Better MOBI/AZW/AZW3 file processing"
    echo "  • Higher quality text extraction from ebooks"
    echo "  • Improved metadata handling"
    echo ""
    echo -e "${CYAN}Without Calibre:${NC} MOBI files will use built-in library (lower quality)"
    echo ""

    if [[ "$OSTYPE" == "darwin"* ]] && [ -n "$BREW_CMD" ]; then
        if [ "$AUTO_MODE" = true ]; then
            echo "  Auto mode: Skipping Calibre installation (optional)"
            install_calibre=false
        elif prompt_yes_no "Install Calibre for enhanced ebook support?" "n"; then
            install_calibre=true
        else
            install_calibre=false
        fi

        if [ "$install_calibre" = true ]; then
            echo "  Installing Calibre via Homebrew..."
            echo "  (This may take a few minutes...)"
            "$BREW_CMD" install --cask calibre

            if command -v ebook-convert &> /dev/null || [ -x /Applications/calibre.app/Contents/MacOS/ebook-convert ]; then
                echo -e "  ${GREEN}✓${NC} Calibre installed successfully"
            else
                echo -e "  ${YELLOW}⚠️${NC} Calibre installation may have failed"
                echo "     You can install it later with: brew install --cask calibre"
            fi
        else
            echo -e "  ${CYAN}ℹ${NC}  Skipping Calibre installation (you can install it later)"
        fi
    else
        echo -e "  ${CYAN}ℹ${NC}  To install Calibre later, run: brew install --cask calibre"
    fi
fi

# Configure directories
echo ""
echo -e "${BLUE}📌 Configuring directories...${NC}"
echo ""

# Books directory - check for existing library first
if [ -n "$AUTO_BOOKS_PATH" ]; then
    default_books="$AUTO_BOOKS_PATH"
elif [ -d "/Users/${USER}/SpiritualLibrary" ]; then
    default_books="/Users/${USER}/SpiritualLibrary"
    echo -e "${GREEN}✓${NC} Found existing library at: $default_books"
elif [ -d "${HOME}/Documents/SpiritualLibrary" ]; then
    default_books="${HOME}/Documents/SpiritualLibrary"
    echo -e "${GREEN}✓${NC} Found existing library at: $default_books"
else
    default_books="${PROJECT_ROOT}/books"
fi

echo ""
if [ "$AUTO_MODE" = false ]; then
    echo -e "${CYAN}Where is your spiritual library located?${NC}"
    echo "This should be the folder containing your PDFs, Word docs, and EPUBs."
fi
BOOKS_PATH=$(prompt_directory "Books directory" "$default_books")

# Database directory  
echo ""
echo -e "${CYAN}Where do you want to store the vector database?${NC}"
default_db="${PROJECT_ROOT}/chroma_db"
DB_PATH=$(prompt_directory "Database directory" "$default_db")

# Create directories
echo ""
echo -n "Creating directories... "
mkdir -p "$BOOKS_PATH"
mkdir -p "$DB_PATH"
mkdir -p "${PROJECT_ROOT}/logs"
echo -e "${GREEN}done${NC}"

# Export environment variables
export PERSONAL_LIBRARY_DOC_PATH="$BOOKS_PATH"
export PERSONAL_LIBRARY_DB_PATH="$DB_PATH"
export PERSONAL_LIBRARY_LOGS_PATH="${PROJECT_ROOT}/logs"

# Generate configuration files
echo ""
echo -e "${BLUE}📌 Generating configuration files...${NC}"
echo ""
"${PROJECT_ROOT}/scripts/generate_configs.sh"

# Service installation (macOS only)
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo ""
    echo -e "${BLUE}📌 Service Installation${NC}"
    echo ""

    # Clean up existing source installation services only
    echo "Checking for existing source installation services..."
    existing_services=()
    for service in "com.personal-library.index-monitor" "com.personal-library.webmonitor"; do
        if launchctl list 2>/dev/null | grep -q "$service"; then
            existing_services+=("$service")
        fi
    done

    if [ ${#existing_services[@]} -gt 0 ]; then
        echo -e "${YELLOW}Found ${#existing_services[@]} existing service(s)${NC}"
        for service in "${existing_services[@]}"; do
            echo "  Unloading $service..."
            launchctl unload ~/Library/LaunchAgents/${service}.plist 2>/dev/null || true
            launchctl remove "$service" 2>/dev/null || true
        done

        # Remove plist files (source installation only)
        for service in "com.personal-library.index-monitor" "com.personal-library.webmonitor"; do
            plist_file="$HOME/Library/LaunchAgents/${service}.plist"
            if [ -f "$plist_file" ]; then
                echo "  Removing $plist_file..."
                rm -f "$plist_file"
            fi
        done
        echo -e "${GREEN}✓${NC} Existing services removed"
        echo ""
    fi

    # Check if port 9999 is in use
    if lsof -Pi :9999 -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  Port 9999 is already in use${NC}"
        port_pid=$(lsof -Pi :9999 -sTCP:LISTEN -t 2>/dev/null)
        if [ -n "$port_pid" ]; then
            port_process=$(ps -p "$port_pid" -o comm= 2>/dev/null || echo "unknown")
            echo "  Process using port: $port_process (PID: $port_pid)"
            if [ "$AUTO_MODE" = false ]; then
                read -p "  Kill this process? (y/N): " -n 1 -r
                echo
                if [[ $REPLY =~ ^[Yy]$ ]]; then
                    kill "$port_pid" 2>/dev/null || true
                    sleep 1
                    echo -e "${GREEN}✓${NC} Process stopped"
                else
                    echo -e "${YELLOW}⚠️  Web monitor may fail to start on port 9999${NC}"
                fi
            else
                echo "  Stopping process automatically..."
                kill "$port_pid" 2>/dev/null || true
                sleep 1
                echo -e "${GREEN}✓${NC} Process stopped"
            fi
        fi
        echo ""
    fi

    # Kill any background Python processes for this project
    echo "Checking for background processes..."
    killed_count=0
    for pid in $(ps aux | grep -E "python.*personal_doc_library\.(monitoring|indexing)" | grep -v grep | awk '{print $2}'); do
        echo "  Stopping process $pid..."
        kill "$pid" 2>/dev/null || true
        killed_count=$((killed_count + 1))
    done
    if [ $killed_count -gt 0 ]; then
        echo -e "${GREEN}✓${NC} Stopped $killed_count background process(es)"
        echo ""
    fi

    echo "The system can run background services to:"
    echo "  • Automatically index new documents"
    echo "  • Provide a web monitoring dashboard"
    echo ""

    if prompt_yes_no "Install background indexing service?" "y"; then
        echo "Installing index monitor service..."
        "${PROJECT_ROOT}/scripts/install_service.sh"
    fi
    
    if prompt_yes_no "Start web monitoring dashboard?" "y"; then
        echo "Starting web monitor on http://localhost:9999..."
        if [ "$USE_CENTRALIZED_CONFIG" = true ]; then
            nohup env PYTHONPATH="$PROJECT_ROOT/src${PYTHONPATH:+:$PYTHONPATH}" \
                MONITOR_PORT=9999 \
                "$PYTHON_CMD" -m personal_doc_library.monitoring.monitor_web_enhanced \
                > "${PROJECT_ROOT}/logs/webmonitor_stdout.log" 2>&1 &
        else
            nohup env PYTHONPATH="$PROJECT_ROOT/src${PYTHONPATH:+:$PYTHONPATH}" \
                MONITOR_PORT=9999 \
                "$venv_path/bin/python" -m personal_doc_library.monitoring.monitor_web_enhanced \
                > "${PROJECT_ROOT}/logs/webmonitor_stdout.log" 2>&1 &
        fi
        echo -e "${GREEN}✓${NC} Web monitor started on port 9999"
    fi
fi

# Claude Desktop configuration
echo ""
echo -e "${BLUE}📌 Claude Desktop Integration${NC}"
echo ""

claude_config_dir="$HOME/Library/Application Support/Claude"
if [ -d "$claude_config_dir" ]; then
    echo "Claude Desktop detected."
    if prompt_yes_no "Configure Claude Desktop to use this MCP server?" "y"; then
        claude_config_file="$claude_config_dir/claude_desktop_config.json"
        
        if [ -f "$claude_config_file" ]; then
            echo -e "${YELLOW}⚠️  Existing Claude config found${NC}"
            echo "Please manually merge the configuration from:"
            echo "  ${PROJECT_ROOT}/config/claude_desktop_config.json"
        else
            cp "${PROJECT_ROOT}/config/claude_desktop_config.json" "$claude_config_file"
            echo -e "${GREEN}✓${NC} Claude Desktop configured"
            echo ""
            echo -e "${YELLOW}Note: Restart Claude Desktop for changes to take effect${NC}"
        fi
    fi
else
    echo "Claude Desktop not found. You can manually configure it later using:"
    echo "  ${PROJECT_ROOT}/config/claude_desktop_config.json"
fi

# Initial indexing
echo ""
echo -e "${BLUE}📌 Document Indexing${NC}"
echo ""

if [ -d "$BOOKS_PATH" ]; then
    # Count documents
    doc_count=$(find "$BOOKS_PATH" -type f \( -name "*.pdf" -o -name "*.docx" -o -name "*.epub" -o -name "*.txt" \) 2>/dev/null | wc -l)
    
    if [ "$doc_count" -gt 0 ]; then
        echo "Found $doc_count documents in: $BOOKS_PATH"
        if prompt_yes_no "Run initial indexing now?" "y"; then
            echo "Starting indexing (this may take a while)..."
            
            # Export environment variables for indexing
            export PERSONAL_LIBRARY_DOC_PATH="$BOOKS_PATH"
            export PERSONAL_LIBRARY_DB_PATH="$DB_PATH"
            
            # Run indexing with proper Python path
            if [ -f "${PROJECT_ROOT}/scripts/run.sh" ]; then
                cd "$PROJECT_ROOT"
                ./scripts/run.sh --index-only
            else
                "$venv_path/bin/python" -c "
import sys
sys.path.append('${PROJECT_ROOT}/src')
from personal_doc_library.core.shared_rag import SharedRAG

print('Initializing RAG system...')
rag = SharedRAG('$BOOKS_PATH', '$DB_PATH')

print('Starting document indexing...')
results = rag.index_all_documents()
print(f'Indexing complete: {results}')
"
            fi
        fi
    else
        echo "No documents found in: $BOOKS_PATH"
        echo "Add your PDF, Word, or EPUB files there and run:"
        echo "  ./scripts/run.sh --index-only"
    fi
else
    echo "Books directory doesn't exist: $BOOKS_PATH"
    echo "Creating directory..."
    mkdir -p "$BOOKS_PATH"
fi

# Summary
echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ Setup Complete!${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${CYAN}📚 Configuration Summary:${NC}"
echo "  • Books directory: $BOOKS_PATH"
echo "  • Database directory: $DB_PATH"
echo "  • Logs directory: ${PROJECT_ROOT}/logs"
echo ""
echo -e "${CYAN}🚀 Quick Commands:${NC}"
echo "  • Run MCP server: ./scripts/run.sh"
echo "  • Index documents: ./scripts/run.sh --index-only"
echo "  • Check status: ./scripts/service_status.sh"
echo "  • Web monitor: http://localhost:9999"
echo ""
echo -e "${CYAN}📖 Documentation:${NC}"
echo "  • README.md - Getting started guide"
echo "  • QUICK_REFERENCE.md - Command reference"
echo "  • Claude.md - Project documentation"
echo ""

# Save configuration summary
cat > "${PROJECT_ROOT}/.env" << EOF
# Personal Document Library MCP Server Configuration
# Generated by quick_start.sh on $(date)

PERSONAL_LIBRARY_DOC_PATH="$BOOKS_PATH"
PERSONAL_LIBRARY_DB_PATH="$DB_PATH"
PERSONAL_LIBRARY_LOGS_PATH="${PROJECT_ROOT}/logs"
EOF

echo -e "${MAGENTA}Thank you for using Personal Document Library MCP Server!${NC}"
echo ""