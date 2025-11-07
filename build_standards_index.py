#!/usr/bin/env python3
"""Build standards index from .praxis-os/standards/ directory.

This script builds a real index with embeddings, FTS, and scalar indexes.
"""

from pathlib import Path
import sys

# Add mcp_server to path
sys.path.insert(0, str(Path(__file__).parent))

from mcp_server.server.indexes.standards_index import StandardsIndex

def main():
    cache_path = Path('.praxis-os/.cache/standards')
    config = {
        'embedding': {
            'provider': 'local',
            'model': 'all-MiniLM-L6-v2'
        },
        'cache': {
            'enabled': False
        },
        'source_paths': []
    }
    
    print('Initializing StandardsIndex...')
    index = StandardsIndex(cache_path, config)
    
    print('Building index from .praxis-os/standards/...')
    index.build(source_paths=['.praxis-os/standards'], force=True)
    
    print(f'\n✅ Index build complete!')
    print(f'   Total chunks indexed: {index.table.count_rows()}')
    print(f'   Index location: {cache_path}')
    
    # Test search
    print('\nTesting hybrid search...')
    results = index.search("testing standards", filters={}, n=3)
    print(f'   Search returned {len(results)} results')
    if results:
        print(f'   Top result: {results[0].file_path}')
        print(f'   Relevance score: {results[0].relevance_score:.4f}')

if __name__ == '__main__':
    main()

