import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.database import (
    init_database,
    get_all_quotes,
    get_quotes_by_author,
    get_quotes_by_tag,
    search_quotes,
    get_random_quote,
    get_quote_with_tags,
    get_statistics,
    print_statistics
)


def show_menu():
    """Display menu options."""
    print("\n" + "=" * 50)
    print("QUOTE DATABASE QUERY TOOL")
    print("=" * 50)
    print("1. Show all quotes")
    print("2. Search by author")
    print("3. Search by tag")
    print("4. Search by keyword")
    print("5. Get random quote")
    print("6. Show statistics")
    print("7. Exit")
    print("-" * 50)


def display_quotes(quotes, limit=10):
    """Display quotes nicely."""
    if not quotes:
        print("No quotes found.")
        return
    
    print(f"\nFound {len(quotes)} quote(s):")
    print("-" * 50)
    
    for i, q in enumerate(quotes[:limit], 1):
        print(f"\n{i}. \"{q['text'][:100]}{'...' if len(q['text']) > 100 else ''}\"")
        print(f"   — {q['author']}")
    
    if len(quotes) > limit:
        print(f"\n... and {len(quotes) - limit} more quotes")


def main():
    # Ensure database exists
    init_database()
    
    while True:
        show_menu()
        choice = input("Enter choice (1-7): ").strip()
        
        if choice == '1':
            quotes = get_all_quotes()
            display_quotes(quotes, limit=10)
        
        elif choice == '2':
            author = input("Enter author name: ").strip()
            if author:
                quotes = get_quotes_by_author(author)
                display_quotes(quotes)
            else:
                print("Please enter an author name.")
        
        elif choice == '3':
            tag = input("Enter tag name: ").strip()
            if tag:
                quotes = get_quotes_by_tag(tag)
                display_quotes(quotes)
            else:
                print("Please enter a tag name.")
        
        elif choice == '4':
            keyword = input("Enter keyword to search: ").strip()
            if keyword:
                quotes = search_quotes(keyword)
                display_quotes(quotes)
            else:
                print("Please enter a keyword.")
        
        elif choice == '5':
            quote = get_random_quote()
            if quote:
                print(f"\n\"{quote['text']}\"")
                print(f"   — {quote['author']}")
            else:
                print("No quotes in database. Run the scraper first!")
        
        elif choice == '6':
            print_statistics()
        
        elif choice == '7':
            print("\nGoodbye!")
            break
        
        else:
            print("Invalid choice. Please try again.")
        
        input("\nPress Enter to continue...")


if __name__ == "__main__":
    main()