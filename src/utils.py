"""
Utility functions for the stock monitoring agent.
"""
import sqlite3
import logging
import hashlib
from datetime import datetime
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('stock_monitor.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class CacheDB:
    """SQLite database for tracking sent notifications to avoid duplicates."""
    
    def __init__(self, db_path='data/cache.db'):
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """Initialize the database schema."""
        conn = sqlite3.connect(self.db_path, timeout=30)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sent_notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content_hash TEXT UNIQUE NOT NULL,
                ticker TEXT NOT NULL,
                notification_type TEXT NOT NULL,
                title TEXT,
                sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                risk_profile TEXT DEFAULT 'Moderate',
                onboarding_step INTEGER DEFAULT 0,
                interests TEXT,
                last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                command_count INTEGER DEFAULT 0
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usage_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                command TEXT,
                args TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_watchlists (
                user_id TEXT,
                ticker TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (user_id, ticker)
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info(f"Database initialized at {self.db_path}")
    
    def is_duplicate(self, content_hash):
        """Check if content has already been sent."""
        conn = sqlite3.connect(self.db_path, timeout=30)
        cursor = conn.cursor()
        
        cursor.execute(
            'SELECT id FROM sent_notifications WHERE content_hash = ?',
            (content_hash,)
        )
        
        result = cursor.fetchone()
        conn.close()
        
        return result is not None
    
    def add_notification(self, content_hash, ticker, notification_type, title=''):
        """Add a sent notification to the database."""
        try:
            conn = sqlite3.connect(self.db_path, timeout=30)
            cursor = conn.cursor()
            
            cursor.execute(
                '''INSERT INTO sent_notifications 
                   (content_hash, ticker, notification_type, title) 
                   VALUES (?, ?, ?, ?)''',
                (content_hash, ticker, notification_type, title)
            )
            
            conn.commit()
            conn.close()
            logger.info(f"Added notification to cache: {ticker} - {notification_type}")
            return True
        except sqlite3.IntegrityError:
            logger.warning(f"Duplicate notification attempted: {content_hash}")
            return False
    
    def cleanup_old_entries(self, days=7):
        """Remove entries older than specified days."""
        conn = sqlite3.connect(self.db_path, timeout=30)
        cursor = conn.cursor()
        
        cursor.execute(
            '''DELETE FROM sent_notifications 
               WHERE sent_at < datetime('now', '-' || ? || ' days')''',
            (days,)
        )
        
        deleted = cursor.rowcount
        conn.commit()
        conn.close()
        
        logger.info(f"Cleaned up {deleted} old entries from cache")
        return deleted

    def log_user_command(self, user_id, username, first_name, command, args=''):
        """Log a user's command and update their profile."""
        try:
            conn = sqlite3.connect(self.db_path, timeout=30)
            cursor = conn.cursor()
            
            # Upsert user
            cursor.execute('''
                INSERT INTO users (user_id, username, first_name, last_seen, command_count)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP, 1)
                ON CONFLICT(user_id) DO UPDATE SET
                    username = excluded.username,
                    first_name = excluded.first_name,
                    last_seen = CURRENT_TIMESTAMP,
                    command_count = users.command_count + 1
            ''', (str(user_id), username, first_name))
            
            # Log usage
            cursor.execute('''
                INSERT INTO usage_logs (user_id, command, args)
                VALUES (?, ?, ?)
            ''', (str(user_id), command, args))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error logging user command: {e}")
            return False

    def get_usage_metrics(self):
        """Fetch summary metrics for growth and usage."""
        try:
            conn = sqlite3.connect(self.db_path, timeout=30)
            cursor = conn.cursor()
            
            metrics = {}
            
            # Total users
            cursor.execute('SELECT COUNT(*) FROM users')
            metrics['total_users'] = cursor.fetchone()[0]
            
            # Total commands
            cursor.execute('SELECT COUNT(*) FROM usage_logs')
            metrics['total_commands'] = cursor.fetchone()[0]
            
            # Active users (last 24h)
            cursor.execute("SELECT COUNT(*) FROM users WHERE last_seen > datetime('now', '-1 day')")
            metrics['active_users_24h'] = cursor.fetchone()[0]
            
            conn.close()
            return metrics
        except Exception as e:
            logger.error(f"Error fetching usage metrics: {e}")
            return {}

    def set_user_risk(self, user_id, risk):
        """Set a user's risk profile."""
        try:
            conn = sqlite3.connect(self.db_path, timeout=30)
            cursor = conn.cursor()
            cursor.execute('UPDATE users SET risk_profile = ? WHERE user_id = ?', (risk, str(user_id)))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error setting risk for {user_id}: {e}")
            return False

    def get_user_risk(self, user_id):
        """Get a user's risk profile."""
        try:
            conn = sqlite3.connect(self.db_path, timeout=30)
            cursor = conn.cursor()
            cursor.execute('SELECT risk_profile FROM users WHERE user_id = ?', (str(user_id),))
            row = cursor.fetchone()
            conn.close()
            return row[0] if row else 'Moderate'
        except Exception as e:
            logger.error(f"Error getting risk for {user_id}: {e}")
            return 'Moderate'

    def set_user_step(self, user_id, step):
        """Update user onboarding step."""
        try:
            conn = sqlite3.connect(self.db_path, timeout=30)
            cursor = conn.cursor()
            cursor.execute('UPDATE users SET onboarding_step = ? WHERE user_id = ?', (step, str(user_id)))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error setting step for {user_id}: {e}")
            return False

    def set_user_interests(self, user_id, interests):
        """Update user interests."""
        try:
            conn = sqlite3.connect(self.db_path, timeout=30)
            cursor = conn.cursor()
            cursor.execute('UPDATE users SET interests = ? WHERE user_id = ?', (interests, str(user_id)))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error setting interests for {user_id}: {e}")
            return False

    def get_user_state(self, user_id):
        """Fetch step, interests, and risk for onboarding state machine."""
        try:
            conn = sqlite3.connect(self.db_path, timeout=30)
            cursor = conn.cursor()
            cursor.execute('SELECT onboarding_step, interests, risk_profile FROM users WHERE user_id = ?', (str(user_id),))
            row = cursor.fetchone()
            conn.close()
            if row:
                return {'step': row[0], 'interests': row[1] or '', 'risk': row[2]}
            return {'step': 0, 'interests': '', 'risk': 'Moderate'}
        except Exception as e:
            logger.error(f"Error getting user state for {user_id}: {e}")
            return {'step': 0, 'interests': '', 'risk': 'Moderate'}

    # --- WATCHLIST METHODS ---

    def add_to_watchlist(self, user_id, ticker):
        """Add a ticker to a user's personal watchlist."""
        try:
            conn = sqlite3.connect(self.db_path, timeout=30)
            cursor = conn.cursor()
            cursor.execute(
                'INSERT OR IGNORE INTO user_watchlists (user_id, ticker) VALUES (?, ?)',
                (str(user_id), ticker.upper())
            )
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error adding to watchlist: {e}")
            return False

    def remove_from_watchlist(self, user_id, ticker):
        """Remove a ticker from a user's personal watchlist."""
        try:
            conn = sqlite3.connect(self.db_path, timeout=30)
            cursor = conn.cursor()
            cursor.execute(
                'DELETE FROM user_watchlists WHERE user_id = ? AND ticker = ?',
                (str(user_id), ticker.upper())
            )
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error removing from watchlist: {e}")
            return False

    def get_user_watchlist(self, user_id):
        """Get all tickers watched by a specific user."""
        try:
            conn = sqlite3.connect(self.db_path, timeout=30)
            cursor = conn.cursor()
            cursor.execute('SELECT ticker FROM user_watchlists WHERE user_id = ?', (str(user_id),))
            tickers = [row[0] for row in cursor.fetchall()]
            conn.close()
            return tickers
        except Exception as e:
            logger.error(f"Error getting user watchlist: {e}")
            return []

    def get_all_monitored_tickers(self):
        """Get a set of all unique tickers watched by any user."""
        try:
            conn = sqlite3.connect(self.db_path, timeout=30)
            cursor = conn.cursor()
            cursor.execute('SELECT DISTINCT ticker FROM user_watchlists')
            tickers = [row[0] for row in cursor.fetchall()]
            conn.close()
            return set(tickers)
        except Exception as e:
            logger.error(f"Error getting all tickers: {e}")
            return set()

    def get_subscribers(self, ticker):
        """Get all user_ids watching a specific ticker."""
        try:
            conn = sqlite3.connect(self.db_path, timeout=30)
            cursor = conn.cursor()
            cursor.execute('SELECT user_id FROM user_watchlists WHERE ticker = ?', (ticker.upper(),))
            user_ids = [row[0] for row in cursor.fetchall()]
            conn.close()
            return user_ids
        except Exception as e:
            logger.error(f"Error getting subscribers for {ticker}: {e}")
            return []


def generate_content_hash(content):
    """Generate a hash for content to check for duplicates."""
    return hashlib.md5(content.encode('utf-8')).hexdigest()


def format_price_change(change_percent):
    """Format price change with emoji indicator."""
    if change_percent > 0:
        return f"📈 +{change_percent:.2f}%"
    elif change_percent < 0:
        return f"📉 {change_percent:.2f}%"
    else:
        return f"➡️ {change_percent:.2f}%"


def truncate_text(text, max_length=200):
    """Truncate text to max length with ellipsis."""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."
