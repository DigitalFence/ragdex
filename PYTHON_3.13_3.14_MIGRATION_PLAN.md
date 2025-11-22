# 🎯 Python 3.13/3.14 Migration Plan - Ragdex v0.3.0

## Executive Summary

This document outlines the complete migration plan to add Python 3.13/3.14 support to Ragdex through dependency upgrades.

---

## Phase 1: Environment Setup & Research ✅

### Findings from Research:

**ChromaDB Migration (0.4.22 → 1.3.5)**
- ⚠️ **Breaking Changes**:
  - `.reset()` now disabled by default (need `allow_reset=True`)
  - `max_batch_size` property removed → use `get_max_batch_size()` method
  - Embeddings returned as **2D NumPy arrays** (not lists)
  - `limit`/`offset` behavior changed
  - **Database migrations are IRREVERSIBLE** (acceptable in dev environment)
- 📚 Source: [ChromaDB Migration Guide](https://docs.trychroma.com/deployment/migration)

**LangChain Migration (0.1.0 → 0.3.x/1.0)**
- ⚠️ **Breaking Changes**:
  - Pydantic v1 → v2 migration required
  - Python 3.10+ requirement
  - AIMessage API changes
  - Agent creation API changed
- 📚 Sources: [LangChain v0.3 Announcement](https://blog.langchain.com/announcing-langchain-v0-3/), [LangChain v1.0 Migration](https://docs.langchain.com/oss/python/migrate/langchain-v1)

**NumPy Migration (1.x → 2.0)**
- ⚠️ **Breaking Changes**:
  - **Binary/ABI incompatibility** (must rebuild C extensions)
  - Type promotion changes (NEP 50)
  - C API changes
- ✅ **Automated Migration**: Ruff rule NPY201 available
- 📚 Source: [NumPy 2.0 Migration Guide](https://numpy.org/doc/2.0/numpy_2_0_migration_guide.html)

**Current Code Analysis:**
- ✅ **Good news**: Limited NumPy usage (not imported directly in analyzed files)
- ⚠️ **ChromaDB usage**: `src/personal_doc_library/core/shared_rag.py:16`
- ⚠️ **LangChain usage**: Heavy usage in `shared_rag.py` (document loaders, embeddings, vectorstores)

---

## Phase 2: Pre-Migration Setup

### 2.1 Install Python 3.13 and 3.14

```bash
# Install via Homebrew
brew install python@3.13
brew install python@3.14

# Verify installations
python3.13 --version  # Should show 3.13.x
python3.14 --version  # Should show 3.14.x
```

### 2.2 Create Git Branch

```bash
git checkout -b experimental/python-3.13-3.14-support
git add INSTALLATION_GUIDE.md PYTHON_3.13_3.14_MIGRATION_PLAN.md
git commit -m "docs: Add installation guide and migration plan for Python 3.13/3.14 support"
```

### 2.3 Create Isolated Test Environments

```bash
# Python 3.13 environment
uv venv test_env_3.13 --python python3.13

# Python 3.14 environment
uv venv test_env_3.14 --python python3.14

# Control environment (3.12) for comparison
uv venv test_env_3.12 --python python3.12
```

---

## Phase 3: Dependency Upgrade Strategy

### 3.1 Conservative Upgrade Path (Recommended)

**Goal**: Minimize breaking changes while enabling Python 3.13/3.14

Update `pyproject.toml`:

```toml
[project]
requires-python = ">=3.10,<3.15"

dependencies = [
  # ChromaDB: Use latest 1.x (mature, stable)
  "chromadb>=1.3.0,<2.0",

  # LangChain: Use 0.3.x (stable, avoid 1.0 churn)
  "langchain>=0.3.0,<0.4.0",
  "langchain-community>=0.3.0,<0.4.0",

  # NumPy: Allow 2.x for Python 3.13+ support
  "numpy>=1.24,<3.0",

  # Sentence transformers: Update for NumPy 2.x compatibility
  "sentence-transformers>=3.0.0",

  # Keep stable versions
  "pypdf2==3.0.1",
  "pypdf",
  "python-docx>=1.1.0",
  "openpyxl",
  "pdfminer.six",
  "beautifulsoup4>=4.11.0",
  "mobi>=0.3.3",
  "ebooklib>=0.18",
  "python-dotenv==1.0.0",
  "psutil==5.9.7",
  "flask==3.0.0",
  "watchdog>=3.0.0",
  "platformdirs>=4.0.0",
  "emlx>=1.0.0"
]
```

Update classifiers:
```toml
classifiers = [
  "Development Status :: 4 - Beta",
  "Intended Audience :: Developers",
  "Intended Audience :: Science/Research",
  "License :: OSI Approved :: MIT License",
  "Operating System :: MacOS",
  "Operating System :: POSIX :: Linux",
  "Programming Language :: Python :: 3",
  "Programming Language :: Python :: 3.10",
  "Programming Language :: Python :: 3.11",
  "Programming Language :: Python :: 3.12",
  "Programming Language :: Python :: 3.13",
  "Programming Language :: Python :: 3.14",
  "Topic :: Scientific/Engineering :: Artificial Intelligence",
  "Topic :: Text Processing :: Indexing",
  "Topic :: Software Development :: Libraries :: Python Modules"
]
```

---

## Phase 4: Code Migration Steps

### 4.1 ChromaDB API Updates

**File**: `src/personal_doc_library/core/shared_rag.py`

**Changes Required**:

```python
# BEFORE (0.4.22)
embeddings = collection.get()["embeddings"]  # Returns list

# AFTER (1.3.5)
embeddings = collection.get()["embeddings"]  # Returns 2D NumPy array
# If you need lists: embeddings.tolist()

# BEFORE
max_size = client.max_batch_size

# AFTER
max_size = client.get_max_batch_size()
```

**Search for affected code**:
```bash
# Find .reset() calls
grep -r "\.reset()" src/

# Find max_batch_size usage
grep -r "max_batch_size" src/

# Find embedding list operations
grep -r "embeddings\[" src/
```

### 4.2 LangChain Pydantic v2 Migration

**Changes Required**:

```python
# BEFORE
from langchain.pydantic_v1 import BaseModel, Field

# AFTER
from pydantic import BaseModel, Field
```

**Search for affected code**:
```bash
grep -r "pydantic_v1" src/
grep -r "from langchain import" src/ | grep -i pydantic
```

### 4.3 NumPy 2.0 Compatibility

**Automated Fix**:
```bash
# Install Ruff with NumPy 2.0 rule
uv pip install "ruff>=0.4.8"

# Run automated migration
ruff check --select NPY201 --fix src/
```

---

## Phase 5: Testing Matrix

### 5.1 Compatibility Test Matrix

| Python | ChromaDB | LangChain | NumPy | Status |
|--------|----------|-----------|-------|--------|
| 3.10 | 1.3.5 | 0.3.x | 1.26 | ✅ Should work |
| 3.10 | 1.3.5 | 0.3.x | 2.0 | ✅ Should work |
| 3.11 | 1.3.5 | 0.3.x | 2.0 | ✅ Should work |
| 3.12 | 1.3.5 | 0.3.x | 2.0 | ✅ Should work |
| 3.13 | 1.3.5 | 0.3.x | 2.0 | 🧪 **Test target** |
| 3.14 | 1.3.5 | 0.3.x | 2.0 | 🧪 **Test target** |

### 5.2 Test Procedure

```bash
# For each Python version (3.10, 3.11, 3.12, 3.13, 3.14):

# 1. Create clean environment
uv venv test_env_X.YY --python pythonX.YY

# 2. Install updated dependencies
uv pip install --python test_env_X.YY/bin/python -e .

# 3. Run basic import test
test_env_X.YY/bin/python -c "
from personal_doc_library.core.shared_rag import SharedRAG
from personal_doc_library.servers.mcp_complete_server import main
print('✅ Imports successful')
"

# 4. Test document indexing
export PERSONAL_LIBRARY_DOC_PATH="./test_docs"
export PERSONAL_LIBRARY_DB_PATH="./test_db_X.YY"
export PERSONAL_LIBRARY_LOGS_PATH="./test_logs"
test_env_X.YY/bin/python -m personal_doc_library.indexing.index_monitor --test

# 5. Test MCP server startup
test_env_X.YY/bin/python -m personal_doc_library.servers.mcp_complete_server --version
```

---

## Phase 6: Database Migration

### 6.1 ChromaDB Database Migration

Since this is a dev environment, we can rebuild:

```bash
# Backup existing database (optional)
cp -r chroma_db chroma_db_backup_$(date +%Y%m%d)

# Install chroma-migrate tool
uv pip install chroma-migrate

# Run migration
chroma-migrate

# If migration fails, delete and rebuild
rm -rf chroma_db
./scripts/run.sh --index-only
```

---

## Phase 7: Success Criteria

### Must Have ✅
- [ ] Python 3.13 installs without errors
- [ ] Python 3.14 installs without errors
- [ ] Basic document indexing works
- [ ] MCP server starts successfully
- [ ] Search queries return results
- [ ] No regressions on Python 3.10-3.12

### Nice to Have 🎁
- [ ] Performance benchmarks show improvements
- [ ] Free-threaded Python 3.13 mode tested
- [ ] All 17 MCP tools tested
- [ ] Email indexing works
- [ ] Web dashboard functional

---

## Phase 8: Documentation Updates

### Files to Update
- ✅ `INSTALLATION_GUIDE.md` (already created)
- 📝 `QUICKSTART.md` - Update Python version requirements
- 📝 `README.md` - Update badges and prerequisites
- 📝 `CLAUDE.md` - Update architecture notes
- 📝 `pyproject.toml` - Version bump to 0.3.0
- 📝 `CHANGELOG.md` - Document breaking changes

---

## Timeline Estimate

| Phase | Duration | Effort |
|-------|----------|--------|
| Phase 1-2: Setup | 30 min | Low |
| Phase 3: Update dependencies | 1 hour | Medium |
| Phase 4: Code changes | 2-4 hours | Medium-High |
| Phase 5: Testing | 3-5 hours | High |
| Phase 6: Bug fixes | 2-8 hours | Variable |
| Phase 7: Documentation | 2 hours | Medium |
| **TOTAL** | **10-20 hours** | **Medium-High** |

---

## Execution Plan - Option A: Full Migration

### Step 1: Install Python 3.13/3.14 ⏳
```bash
brew install python@3.13 python@3.14
```

### Step 2: Create Git Branch ⏳
```bash
git checkout -b experimental/python-3.13-3.14-support
git add INSTALLATION_GUIDE.md PYTHON_3.13_3.14_MIGRATION_PLAN.md
git commit -m "docs: Add installation guide and migration plan"
```

### Step 3: Update pyproject.toml ⏳
- Update `requires-python`
- Update dependency versions
- Add Python 3.13/3.14 to classifiers

### Step 4: Search for Breaking Changes ⏳
```bash
grep -r "\.reset()" src/
grep -r "max_batch_size" src/
grep -r "pydantic_v1" src/
```

### Step 5: Fix Code Issues ⏳
- Update ChromaDB API calls
- Update LangChain Pydantic imports
- Run Ruff NPY201 for NumPy 2.0

### Step 6: Test with Python 3.13 ⏳
```bash
uv venv test_env_3.13 --python python3.13
uv pip install --python test_env_3.13/bin/python -e .
test_env_3.13/bin/python -c "from personal_doc_library.core.shared_rag import SharedRAG"
```

### Step 7: Test with Python 3.14 ⏳
```bash
uv venv test_env_3.14 --python python3.14
uv pip install --python test_env_3.14/bin/python -e .
test_env_3.14/bin/python -c "from personal_doc_library.core.shared_rag import SharedRAG"
```

### Step 8: Rebuild ChromaDB ⏳
```bash
rm -rf chroma_db
./scripts/run.sh --index-only
```

### Step 9: Comprehensive Testing ⏳
- Test all MCP tools
- Test document indexing
- Test search functionality
- Test web dashboard

### Step 10: Update Documentation ⏳
- Update version numbers
- Update Python requirements
- Document breaking changes

---

## Benefits of This Migration

### Performance Gains
- **Python 3.13**: ~10-15% faster overall, free-threaded mode, JIT compiler
- **Python 3.14**: Further JIT optimizations, improved async performance
- **NumPy 2.x**: ~2x faster for many operations
- **ChromaDB 1.3.5**: Better ARM64 support, improved vector search

### Security & Stability
- Python 3.10 EOL: October 2026 (future-proofing)
- Latest security patches for all dependencies
- Active maintenance and bug fixes

### Ecosystem Modernization
- Better MCP integration patterns
- Improved RAG capabilities
- Cleaner APIs
- Better documentation

---

## Rollback Plan (If Needed)

```bash
# Revert to main branch
git checkout main

# Restore database backup (if created)
rm -rf chroma_db
mv chroma_db_backup_YYYYMMDD chroma_db

# Reinstall old dependencies
uv pip install --python venv_mcp/bin/python -e .
```

---

**Sources:**
- [ChromaDB Migration Guide](https://docs.trychroma.com/deployment/migration)
- [LangChain v0.3 Announcement](https://blog.langchain.com/announcing-langchain-v0-3/)
- [LangChain v1.0 Migration Guide](https://docs.langchain.com/oss/python/migrate/langchain-v1)
- [NumPy 2.0 Migration Guide](https://numpy.org/doc/2.0/numpy_2_0_migration_guide.html)
