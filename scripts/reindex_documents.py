#!/usr/bin/env python3
"""
Flexible document re-indexing tool for Ragdex

Usage:
  # Re-index all documents
  python scripts/reindex_documents.py --all

  # Re-index by pattern (e.g., all Whispers documents)
  python scripts/reindex_documents.py --pattern "whispers"

  # Re-index by extension
  python scripts/reindex_documents.py --extension ".docx"

  # Re-index specific files
  python scripts/reindex_documents.py --files "path/to/file1.docx" "path/to/file2.pdf"

  # Re-index from a specific directory
  python scripts/reindex_documents.py --directory "SpiritualLibrary/Whispers"

  # Combine filters
  python scripts/reindex_documents.py --pattern "whispers" --extension ".docx"
"""

import os
import sys
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from personal_doc_library.core.shared_rag import SharedRAG
from personal_doc_library.core.config import config


def find_documents_by_pattern(book_index, pattern):
    """Find documents matching a pattern (case-insensitive)"""
    pattern_lower = pattern.lower()
    return [path for path in book_index.keys() if pattern_lower in path.lower()]


def find_documents_by_extension(book_index, extension):
    """Find documents with specific extension"""
    if not extension.startswith('.'):
        extension = '.' + extension
    return [path for path in book_index.keys() if path.lower().endswith(extension.lower())]


def find_documents_by_directory(book_index, directory):
    """Find documents within a specific directory"""
    dir_normalized = directory.strip('/').strip('\\').lower()
    return [path for path in book_index.keys() if dir_normalized in path.lower()]


def main():
    parser = argparse.ArgumentParser(
        description='Re-index documents with updated metadata extraction',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    # Selection criteria
    parser.add_argument('--all', action='store_true',
                       help='Re-index all documents in the library')
    parser.add_argument('--pattern', type=str,
                       help='Re-index documents matching pattern (case-insensitive)')
    parser.add_argument('--extension', type=str,
                       help='Re-index documents with specific extension (.docx, .pdf, etc.)')
    parser.add_argument('--directory', type=str,
                       help='Re-index documents in specific directory')
    parser.add_argument('--files', nargs='+',
                       help='Re-index specific files (space-separated relative paths)')

    # Options
    parser.add_argument('--yes', '-y', action='store_true',
                       help='Auto-confirm without prompting')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be re-indexed without actually doing it')
    parser.add_argument('--books-path', type=str,
                       help='Override books directory (default: from config)')

    args = parser.parse_args()

    # Validate arguments
    if not any([args.all, args.pattern, args.extension, args.directory, args.files]):
        parser.print_help()
        print("\n❌ Error: Must specify at least one selection criterion")
        print("   Use --all, --pattern, --extension, --directory, or --files")
        sys.exit(1)

    print("🔮 Document Re-indexing Tool")
    print("=" * 60)
    print("\nInitializing RAG system...")

    # Initialize with custom books path if provided
    if args.books_path:
        rag = SharedRAG(books_directory=args.books_path)
        print(f"Using custom books directory: {args.books_path}")
    else:
        rag = SharedRAG()

    print(f"Books directory: {rag.books_directory}")
    print(f"Total documents in index: {len(rag.book_index)}")

    # Find documents to re-index
    selected_docs = set()

    if args.all:
        selected_docs = set(rag.book_index.keys())
        print("\n📚 Selected: ALL documents")

    if args.pattern:
        pattern_docs = find_documents_by_pattern(rag.book_index, args.pattern)
        selected_docs.update(pattern_docs)
        print(f"\n🔍 Pattern '{args.pattern}': {len(pattern_docs)} documents")

    if args.extension:
        ext_docs = find_documents_by_extension(rag.book_index, args.extension)
        selected_docs.update(ext_docs)
        print(f"\n📄 Extension '{args.extension}': {len(ext_docs)} documents")

    if args.directory:
        dir_docs = find_documents_by_directory(rag.book_index, args.directory)
        selected_docs.update(dir_docs)
        print(f"\n📁 Directory '{args.directory}': {len(dir_docs)} documents")

    if args.files:
        # Validate that all specified files exist in index
        for file_path in args.files:
            if file_path in rag.book_index:
                selected_docs.add(file_path)
            else:
                print(f"\n⚠️  Warning: '{file_path}' not found in index")
        print(f"\n📝 Specific files: {len([f for f in args.files if f in rag.book_index])} documents")

    selected_docs = sorted(selected_docs)

    if not selected_docs:
        print("\n❌ No documents found matching the criteria.")
        sys.exit(0)

    # Display selected documents
    print(f"\n📚 Total documents to re-index: {len(selected_docs)}")
    if len(selected_docs) <= 20:
        print("\nDocuments:")
        for i, doc in enumerate(selected_docs, 1):
            print(f"  {i}. {doc}")
    else:
        print("\nFirst 10 documents:")
        for i, doc in enumerate(selected_docs[:10], 1):
            print(f"  {i}. {doc}")
        print(f"  ... and {len(selected_docs) - 10} more")

    # Dry run mode
    if args.dry_run:
        print("\n🔍 DRY RUN MODE - No changes will be made")
        print("\nDocuments that would be re-indexed:")
        for doc in selected_docs:
            print(f"  - {doc}")
        print(f"\nTotal: {len(selected_docs)} documents")
        sys.exit(0)

    # Confirm with user
    if not args.yes:
        print(f"\n⚠️  This will remove and re-index {len(selected_docs)} document(s)")
        print("   with updated metadata extraction (author, date, source_type, volume)")
        response = input("\nContinue? (yes/no): ")

        if response.lower() not in ['yes', 'y']:
            print("\n❌ Aborted.")
            sys.exit(0)

    # Remove from index and vectorstore
    print(f"\n🗑️  Removing old chunks from vectorstore...")
    for i, rel_path in enumerate(selected_docs, 1):
        print(f"  [{i}/{len(selected_docs)}] Removing: {rel_path}")
        rag.remove_book_by_path(rel_path, skip_save=True)

    rag.save_book_index()
    print("✅ Old chunks removed.")

    # Re-index documents
    print(f"\n📥 Re-indexing {len(selected_docs)} document(s) with updated metadata...")
    success_count = 0
    failed_count = 0

    for i, rel_path in enumerate(selected_docs, 1):
        full_path = os.path.join(rag.books_directory, rel_path)

        if os.path.exists(full_path):
            print(f"\n[{i}/{len(selected_docs)}] Processing: {rel_path}")
            try:
                success = rag.process_document(full_path, rel_path)
                if success:
                    print(f"  ✅ Success")
                    success_count += 1
                else:
                    print(f"  ❌ Failed")
                    failed_count += 1
            except Exception as e:
                print(f"  ❌ Error: {e}")
                failed_count += 1
        else:
            print(f"\n[{i}/{len(selected_docs)}] ⚠️  File not found: {full_path}")
            failed_count += 1

    # Summary
    print("\n" + "=" * 60)
    print("🎉 Re-indexing complete!")
    print(f"\n📊 Summary:")
    print(f"  ✅ Successfully indexed: {success_count}")
    print(f"  ❌ Failed: {failed_count}")
    print(f"  📚 Total chunks in database: {rag.vectorstore._collection.count()}")

    if success_count > 0:
        print("\n💡 Enhanced metadata now available:")
        print("   - source_type (whispers, heartfulness, osho, yoga_sutras, general)")
        print("   - author (Babuji, Lalaji, Chariji, etc.)")
        print("   - date/time (for Whispers messages)")
        print("   - volume (for Whispers documents)")
        print("\n🔍 Use enhanced search filters:")
        print("   - author='Babuji'")
        print("   - source_type='whispers'")
        print("   - date_from='2002-01-01', date_to='2002-12-31'")
        print("   - volume=1")
        print("   - get_whisper_by_date(date='2002-06-28')")


if __name__ == "__main__":
    main()
