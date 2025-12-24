import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.database import (
    init_database,
    insert_quote,
    get_all_quotes,
    get_quotes_by_author,
    get_quotes_by_tag,
    search_quotes,
    get_random_quote,
    get_statistics
)


def test_database():
    print("=" * 50)
    print("Testing Database Module")
    print("=" * 50)
    
    # Initialize
    print("\n1. Initializing database...")
    init_database()
    print("   ✓ Database initialized")
    
    # Insert test quotes
    print("\n2. Inserting test quotes...")
    
    test_quotes = [
        {
            'text': 'The only way to do great work is to love what you do.',
            'author': 'Steve Jobs',
            'tags': ['work', 'inspiration', 'passion']
        },
        {
            'text': 'Innovation distinguishes between a leader and a follower.',
            'author': 'Steve Jobs',
            'tags': ['innovation', 'leadership']
        },
        {
            'text': 'Stay hungry, stay foolish.',
            'author': 'Steve Jobs',
            'tags': ['inspiration', 'life']
        },
        {
            'text': 'Life is what happens when you are busy making other plans.',
            'author': 'John Lennon',
            'tags': ['life', 'planning']
        }
    ]
    
    for q in test_quotes:
        result = insert_quote(q['text'], q['author'], q['tags'])
        status = "Added" if result else "Skipped (duplicate)"
        print(f"   {status}: \"{q['text'][:40]}...\"")
    
    # Test queries
    print("\n3. Testing queries...")
    
    # All quotes
    all_quotes = get_all_quotes()
    print(f"   Total quotes in DB: {len(all_quotes)}")
    
    # By author
    steve_quotes = get_quotes_by_author('Steve Jobs')
    print(f"   Quotes by Steve Jobs: {len(steve_quotes)}")
    
    # By tag
    life_quotes = get_quotes_by_tag('life')
    print(f"   Quotes tagged 'life': {len(life_quotes)}")
    
    # Search
    search_results = search_quotes('innovation')
    print(f"   Search 'innovation': {len(search_results)} results")
    
    # Random quote
    random_quote = get_random_quote()
    if random_quote:
        print(f"   Random quote: \"{random_quote['text'][:40]}...\"")
    
    # Statistics
    print("\n4. Database Statistics:")
    stats = get_statistics()
    print(f"   Total quotes: {stats['total_quotes']}")
    print(f"   Total authors: {stats['total_authors']}")
    print(f"   Total tags: {stats['total_tags']}")
    
    print("\n" + "=" * 50)
    print("All tests passed!")
    print("=" * 50)


if __name__ == "__main__":
    test_database()