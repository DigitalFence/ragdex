#!/usr/bin/env python3
"""
Metadata Migration Script for v0.3.6
=====================================

Adds 'folder' and 'rel_path' metadata to existing ChromaDB documents
without requiring full re-indexing.

Usage:
    python scripts/migrate_metadata_v036.py [--dry-run] [--backup]

Options:
    --dry-run    Show what would be updated without making changes
    --backup     Create backup of ChromaDB before migration
    --force      Skip safety checks (not recommended)

Safety Features:
    - Automatic backup creation
    - Dry-run mode to preview changes
    - Service detection (warns if services running)
    - Progress tracking
    - Rollback instructions on failure
"""

import os
import sys
import json
import shutil
import argparse
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from personal_doc_library.core.config import get_config


def check_services_running():
    """Check if any ragdex services are running."""
    import subprocess

    services = []

    # Check for MCP server
    result = subprocess.run(
        ["pgrep", "-f", "mcp_complete_server"],
        capture_output=True,
        text=True
    )
    if result.stdout.strip():
        services.append("MCP Server")

    # Check for index monitor
    result = subprocess.run(
        ["pgrep", "-f", "index_monitor"],
        capture_output=True,
        text=True
    )
    if result.stdout.strip():
        services.append("Index Monitor")

    # Check for web monitor
    result = subprocess.run(
        ["pgrep", "-f", "monitor_web_enhanced"],
        capture_output=True,
        text=True
    )
    if result.stdout.strip():
        services.append("Web Monitor")

    return services


def backup_chromadb(db_path, backup_path):
    """Create a backup of the ChromaDB directory."""
    print(f"\n📦 Creating backup...")
    print(f"   Source: {db_path}")
    print(f"   Backup: {backup_path}")

    if backup_path.exists():
        print(f"⚠️  Backup already exists: {backup_path}")
        response = input("   Overwrite existing backup? (y/N): ")
        if response.lower() != 'y':
            print("❌ Backup cancelled")
            return False
        shutil.rmtree(backup_path)

    shutil.copytree(db_path, backup_path)
    print(f"✅ Backup created successfully")
    return True


def load_book_index(db_path):
    """Load book_index.json to get full paths."""
    book_index_path = db_path / "book_index.json"

    if not book_index_path.exists():
        print(f"❌ book_index.json not found at {book_index_path}")
        return None

    with open(book_index_path, 'r') as f:
        return json.load(f)


def extract_rel_path_from_book_index(book_index, book_name):
    """Extract relative path from book_index.json."""
    # book_index structure: {book_name: {"path": "/full/path/to/file", ...}}
    book_info = book_index.get(book_name)
    if not book_info:
        return None

    full_path = book_info.get("path", "")
    doc_path = book_info.get("doc_path", "")

    # Calculate relative path
    if full_path and doc_path:
        try:
            rel_path = os.path.relpath(full_path, doc_path)
            return rel_path
        except ValueError:
            # Paths on different drives (Windows)
            return os.path.basename(full_path)

    return None


def migrate_metadata(dry_run=False, force=False):
    """Migrate metadata for all documents."""
    config = get_config()
    db_path = Path(config.chroma_db_path)

    print("\n" + "="*60)
    print("  ChromaDB Metadata Migration v0.3.6")
    print("="*60)

    # Safety checks
    if not force:
        print("\n🔍 Running safety checks...")

        # Check if services are running
        running_services = check_services_running()
        if running_services:
            print(f"\n⚠️  WARNING: The following services are running:")
            for service in running_services:
                print(f"   - {service}")
            print("\n   Please stop all services before migration:")
            print("   1. Quit Claude Desktop")
            print("   2. Stop background services: ./scripts/stop_monitor.sh")

            response = input("\n   Continue anyway? (y/N): ")
            if response.lower() != 'y':
                print("❌ Migration cancelled")
                return False

    # Load book index
    print("\n📚 Loading book index...")
    book_index = load_book_index(db_path)
    if not book_index:
        return False

    print(f"✅ Loaded {len(book_index)} books from index")

    # Initialize ChromaDB
    print("\n🔌 Connecting to ChromaDB...")
    import chromadb
    from chromadb.config import Settings

    client = chromadb.PersistentClient(
        path=str(db_path),
        settings=Settings(anonymized_telemetry=False)
    )

    collection_name = config.chroma_collection_name
    try:
        collection = client.get_collection(name=collection_name)
    except Exception as e:
        print(f"❌ Failed to get collection '{collection_name}': {e}")
        return False

    print(f"✅ Connected to collection: {collection_name}")

    # Get all unique books
    print("\n📊 Analyzing documents...")
    all_data = collection.get(include=["metadatas"])
    total_chunks = len(all_data['metadatas'])

    print(f"   Total chunks in database: {total_chunks:,}")

    # Group by book
    books_to_update = {}
    chunks_missing_metadata = 0
    chunks_already_migrated = 0

    for i, metadata in enumerate(all_data['metadatas']):
        book_name = metadata.get('book', 'Unknown')

        # Check if already has folder metadata
        if 'folder' in metadata and 'rel_path' in metadata:
            chunks_already_migrated += 1
            continue

        chunks_missing_metadata += 1

        if book_name not in books_to_update:
            books_to_update[book_name] = []
        books_to_update[book_name].append(i)

    print(f"   Chunks already migrated: {chunks_already_migrated:,}")
    print(f"   Chunks needing migration: {chunks_missing_metadata:,}")
    print(f"   Books needing migration: {len(books_to_update)}")

    if chunks_missing_metadata == 0:
        print("\n✅ All chunks already have folder metadata!")
        return True

    # Show what will be updated
    print(f"\n📝 Migration Plan:")
    print(f"   Books to update: {len(books_to_update)}")
    print(f"   Chunks to update: {chunks_missing_metadata:,}")

    if dry_run:
        print("\n🔍 DRY RUN MODE - Showing first 10 books that would be updated:")
        for i, (book_name, chunk_indices) in enumerate(list(books_to_update.items())[:10]):
            rel_path = extract_rel_path_from_book_index(book_index, book_name)
            folder = os.path.dirname(rel_path) if rel_path else ""
            print(f"\n   {i+1}. {book_name}")
            print(f"      Chunks: {len(chunk_indices)}")
            print(f"      rel_path: {rel_path or 'NOT FOUND IN INDEX'}")
            print(f"      folder: {folder or '(root)'}")

        print(f"\n... and {len(books_to_update) - 10} more books")
        print("\n✅ Dry run complete. Run without --dry-run to apply changes.")
        return True

    # Confirm migration
    print(f"\n⚠️  This will update {chunks_missing_metadata:,} chunks across {len(books_to_update)} books.")
    response = input("   Proceed with migration? (y/N): ")
    if response.lower() != 'y':
        print("❌ Migration cancelled")
        return False

    # Perform migration
    print("\n🔄 Starting migration...")

    updated_books = 0
    updated_chunks = 0
    failed_books = []

    for book_name, chunk_indices in books_to_update.items():
        try:
            # Get rel_path from book_index
            rel_path = extract_rel_path_from_book_index(book_index, book_name)

            if not rel_path:
                print(f"⚠️  Skipping {book_name}: Not found in book_index.json")
                failed_books.append((book_name, "Not in book_index"))
                continue

            # Calculate folder
            folder = os.path.dirname(rel_path)

            # Get all chunk IDs for this book
            book_data = collection.get(
                where={"book": {"$eq": book_name}},
                include=["metadatas"]
            )

            chunk_ids = book_data['ids']
            metadatas = book_data['metadatas']

            # Update metadata for all chunks
            updated_metadatas = []
            for metadata in metadatas:
                metadata['folder'] = folder
                metadata['rel_path'] = rel_path
                updated_metadatas.append(metadata)

            # Update in ChromaDB
            collection.update(
                ids=chunk_ids,
                metadatas=updated_metadatas
            )

            updated_books += 1
            updated_chunks += len(chunk_ids)

            # Progress indicator
            if updated_books % 10 == 0:
                print(f"   Progress: {updated_books}/{len(books_to_update)} books, {updated_chunks:,} chunks")

        except Exception as e:
            print(f"❌ Error updating {book_name}: {e}")
            failed_books.append((book_name, str(e)))

    # Summary
    print("\n" + "="*60)
    print("  Migration Complete!")
    print("="*60)
    print(f"\n✅ Successfully updated:")
    print(f"   - {updated_books} books")
    print(f"   - {updated_chunks:,} chunks")

    if failed_books:
        print(f"\n⚠️  Failed to update {len(failed_books)} books:")
        for book_name, error in failed_books[:10]:
            print(f"   - {book_name}: {error}")
        if len(failed_books) > 10:
            print(f"   ... and {len(failed_books) - 10} more")

    print("\n📋 Next Steps:")
    print("   1. Restart Claude Desktop to reload MCP server")
    print("   2. Test folder search: search(query='...', folder='DigitalFence')")
    print("   3. If issues occur, restore from backup")

    return True


def main():
    parser = argparse.ArgumentParser(
        description="Migrate ChromaDB metadata for v0.3.6 folder search"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be updated without making changes"
    )
    parser.add_argument(
        "--backup",
        action="store_true",
        help="Create backup before migration"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Skip safety checks (not recommended)"
    )

    args = parser.parse_args()

    # Get config
    config = get_config()
    db_path = Path(config.chroma_db_path)

    # Create backup if requested
    if args.backup and not args.dry_run:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = db_path.parent / f"chroma_db_backup_{timestamp}"

        if not backup_chromadb(db_path, backup_path):
            print("❌ Migration cancelled due to backup failure")
            return 1

    # Run migration
    try:
        success = migrate_metadata(dry_run=args.dry_run, force=args.force)
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\n\n❌ Migration interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Migration failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
