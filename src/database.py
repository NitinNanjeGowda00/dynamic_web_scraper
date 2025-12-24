import sqlite3
import os
from typing import List, Dict, Optional

# Database file location
DB_DIR = "data"
DB_NAME = "quotes.db"


def get_db_path() -> str:
    """Get the full path to the database file."""
    os.makedirs(DB_DIR, exist_ok=True)
    return os.path.join(DB_DIR, DB_NAME)


def get_connection():
    """Get a database connection."""
    conn = sqlite3.connect(get_db_path(), timeout=30)
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    """Initialize database with required tables."""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Create authors table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS authors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create quotes table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS quotes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT UNIQUE NOT NULL,
                author_id INTEGER NOT NULL,
                source_url TEXT,
                scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (author_id) REFERENCES authors (id)
            )
        ''')
        
        # Create tags table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL
            )
        ''')
        
        # Create quote_tags junction table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS quote_tags (
                quote_id INTEGER,
                tag_id INTEGER,
                PRIMARY KEY (quote_id, tag_id),
                FOREIGN KEY (quote_id) REFERENCES quotes (id),
                FOREIGN KEY (tag_id) REFERENCES tags (id)
            )
        ''')
        
        # Create scraping_sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scraping_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ended_at TIMESTAMP,
                pages_scraped INTEGER DEFAULT 0,
                quotes_added INTEGER DEFAULT 0,
                quotes_skipped INTEGER DEFAULT 0,
                status TEXT DEFAULT 'running'
            )
        ''')
        
        conn.commit()
        print("Database initialized successfully!")
        
    finally:
        conn.close()


def insert_quote(text: str, author: str, tags: List[str], source_url: str = None) -> Optional[int]:
    """Insert a quote with its author and tags. Returns quote ID or None if duplicate."""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Check if quote exists
        cursor.execute('SELECT id FROM quotes WHERE text = ?', (text,))
        if cursor.fetchone():
            return None
        
        # Get or create author
        cursor.execute('SELECT id FROM authors WHERE name = ?', (author,))
        result = cursor.fetchone()
        if result:
            author_id = result['id']
        else:
            cursor.execute('INSERT INTO authors (name) VALUES (?)', (author,))
            author_id = cursor.lastrowid
        
        # Insert quote
        cursor.execute('''
            INSERT INTO quotes (text, author_id, source_url)
            VALUES (?, ?, ?)
        ''', (text, author_id, source_url))
        quote_id = cursor.lastrowid
        
        # Add tags
        for tag_name in tags:
            cursor.execute('SELECT id FROM tags WHERE name = ?', (tag_name,))
            tag_result = cursor.fetchone()
            if tag_result:
                tag_id = tag_result['id']
            else:
                cursor.execute('INSERT INTO tags (name) VALUES (?)', (tag_name,))
                tag_id = cursor.lastrowid
            
            cursor.execute('INSERT OR IGNORE INTO quote_tags (quote_id, tag_id) VALUES (?, ?)',
                          (quote_id, tag_id))
        
        conn.commit()
        return quote_id
        
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def insert_quotes_batch(quotes: List[Dict], source_url: str = None) -> Dict[str, int]:
    """Insert multiple quotes. Returns count of added and skipped."""
    added = 0
    skipped = 0
    
    for quote in quotes:
        result = insert_quote(
            text=quote['text'],
            author=quote['author'],
            tags=quote.get('tags', []),
            source_url=source_url
        )
        if result:
            added += 1
        else:
            skipped += 1
    
    return {'added': added, 'skipped': skipped}


def start_session() -> int:
    """Start a new scraping session."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO scraping_sessions DEFAULT VALUES')
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def update_session(session_id: int, pages: int, added: int, skipped: int, status: str = 'completed'):
    """Update session with final statistics."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            UPDATE scraping_sessions
            SET ended_at = CURRENT_TIMESTAMP, pages_scraped = ?, quotes_added = ?,
                quotes_skipped = ?, status = ?
            WHERE id = ?
        ''', (pages, added, skipped, status, session_id))
        conn.commit()
    finally:
        conn.close()


def get_all_quotes() -> List[Dict]:
    """Get all quotes with author names."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            SELECT q.id, q.text, a.name as author, q.scraped_at
            FROM quotes q JOIN authors a ON q.author_id = a.id
            ORDER BY q.scraped_at DESC
        ''')
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


def get_quotes_by_author(author_name: str) -> List[Dict]:
    """Get quotes by author."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            SELECT q.id, q.text, a.name as author
            FROM quotes q JOIN authors a ON q.author_id = a.id
            WHERE a.name LIKE ?
        ''', (f'%{author_name}%',))
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


def get_quotes_by_tag(tag_name: str) -> List[Dict]:
    """Get quotes by tag."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            SELECT q.id, q.text, a.name as author
            FROM quotes q
            JOIN authors a ON q.author_id = a.id
            JOIN quote_tags qt ON q.id = qt.quote_id
            JOIN tags t ON qt.tag_id = t.id
            WHERE t.name LIKE ?
        ''', (f'%{tag_name}%',))
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


def search_quotes(keyword: str) -> List[Dict]:
    """Search quotes by keyword."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            SELECT q.id, q.text, a.name as author
            FROM quotes q JOIN authors a ON q.author_id = a.id
            WHERE q.text LIKE ?
        ''', (f'%{keyword}%',))
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


def get_random_quote() -> Optional[Dict]:
    """Get a random quote."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            SELECT q.id, q.text, a.name as author
            FROM quotes q JOIN authors a ON q.author_id = a.id
            ORDER BY RANDOM() LIMIT 1
        ''')
        result = cursor.fetchone()
        return dict(result) if result else None
    finally:
        conn.close()


def get_statistics() -> Dict:
    """Get database statistics."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        stats = {}
        
        cursor.execute('SELECT COUNT(*) as count FROM quotes')
        stats['total_quotes'] = cursor.fetchone()['count']
        
        cursor.execute('SELECT COUNT(*) as count FROM authors')
        stats['total_authors'] = cursor.fetchone()['count']
        
        cursor.execute('SELECT COUNT(*) as count FROM tags')
        stats['total_tags'] = cursor.fetchone()['count']
        
        cursor.execute('SELECT COUNT(*) as count FROM scraping_sessions')
        stats['total_sessions'] = cursor.fetchone()['count']
        
        cursor.execute('''
            SELECT a.name, COUNT(q.id) as quote_count
            FROM authors a JOIN quotes q ON a.id = q.author_id
            GROUP BY a.id ORDER BY quote_count DESC LIMIT 5
        ''')
        stats['top_authors'] = [dict(row) for row in cursor.fetchall()]
        
        cursor.execute('''
            SELECT t.name, COUNT(qt.quote_id) as usage_count
            FROM tags t JOIN quote_tags qt ON t.id = qt.tag_id
            GROUP BY t.id ORDER BY usage_count DESC LIMIT 10
        ''')
        stats['top_tags'] = [dict(row) for row in cursor.fetchall()]
        
        return stats
    finally:
        conn.close()


def print_statistics():
    """Print formatted statistics."""
    stats = get_statistics()
    
    print("\n" + "=" * 50)
    print("DATABASE STATISTICS")
    print("=" * 50)
    print(f"Total Quotes:    {stats['total_quotes']}")
    print(f"Total Authors:   {stats['total_authors']}")
    print(f"Total Tags:      {stats['total_tags']}")
    print(f"Total Sessions:  {stats['total_sessions']}")
    
    if stats['top_authors']:
        print("\nTop 5 Authors:")
        for author in stats['top_authors']:
            print(f"  - {author['name']}: {author['quote_count']} quotes")
    
    if stats['top_tags']:
        print("\nTop 10 Tags:")
        for tag in stats['top_tags']:
            print(f"  - {tag['name']}: {tag['usage_count']} uses")
    
    print("=" * 50)