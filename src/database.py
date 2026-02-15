"""Database Module - Inventory Management

Provides SQLite-based inventory database management for Kirana stores.
Supports CRUD operations on inventory items with stock tracking.
"""

import sqlite3
import logging
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import os

logger = logging.getLogger(__name__)


class InventoryDB:
    """SQLite-based inventory database manager"""
    
    def __init__(self, db_path: str = "data/inventory.db"):
        """
        Initialize database connection
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        
        # Create data directory if it doesn't exist
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # Initialize database
        self.init_db()
        logger.info(f"Inventory database initialized at {db_path}")
    
    def get_connection(self) -> sqlite3.Connection:
        """Get database connection with row factory"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_db(self):
        """Initialize database schema"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Create items table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                brand TEXT,
                unit TEXT NOT NULL,
                stock REAL NOT NULL DEFAULT 0,
                price REAL NOT NULL,
                gst_rate REAL DEFAULT 5.0,
                category TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create stock_history table for audit
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stock_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_id INTEGER NOT NULL,
                change_amount REAL NOT NULL,
                previous_stock REAL NOT NULL,
                new_stock REAL NOT NULL,
                reason TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (item_id) REFERENCES items (id)
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("Database schema initialized")
    
    def add_item(self, name: str, brand: str, unit: str, stock: float, 
                 price: float, gst_rate: float = 5.0, category: str = None) -> int:
        """
        Add a new item to inventory
        
        Args:
            name: Item name
            brand: Brand name
            unit: Unit of measurement (kg, litre, piece, etc.)
            stock: Initial stock quantity
            price: Price per unit
            gst_rate: GST rate percentage
            category: Item category
        
        Returns:
            Item ID
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO items (name, brand, unit, stock, price, gst_rate, category)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (name.lower(), brand, unit, stock, price, gst_rate, category))
            
            item_id = cursor.lastrowid
            conn.commit()
            logger.info(f"Added item: {name} (ID: {item_id})")
            return item_id
        
        except sqlite3.IntegrityError:
            logger.warning(f"Item already exists: {name}")
            raise ValueError(f"Item '{name}' already exists")
        
        finally:
            conn.close()
    
    def get_item_by_name(self, name: str) -> Optional[Dict]:
        """
        Get item by name (case-insensitive)
        
        Args:
            name: Item name
        
        Returns:
            Item dict or None
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM items WHERE LOWER(name) = LOWER(?)
        ''', (name,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        return None
    
    def get_item_by_id(self, item_id: int) -> Optional[Dict]:
        """Get item by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM items WHERE id = ?', (item_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        return None
    
    def update_stock(self, name: str, change: float, reason: str = "order") -> bool:
        """
        Update stock quantity for an item
        
        Args:
            name: Item name
            change: Stock change amount (positive or negative)
            reason: Reason for stock change
        
        Returns:
            True if successful, False otherwise
        """
        item = self.get_item_by_name(name)
        if not item:
            logger.error(f"Item not found: {name}")
            return False
        
        new_stock = item['stock'] + change
        
        if new_stock < 0:
            logger.error(f"Insufficient stock for {name}: {item['stock']} units")
            return False
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Update item stock
            cursor.execute('''
                UPDATE items 
                SET stock = ?, updated_at = CURRENT_TIMESTAMP 
                WHERE id = ?
            ''', (new_stock, item['id']))
            
            # Record stock history
            cursor.execute('''
                INSERT INTO stock_history (item_id, change_amount, previous_stock, new_stock, reason)
                VALUES (?, ?, ?, ?, ?)
            ''', (item['id'], change, item['stock'], new_stock, reason))
            
            conn.commit()
            logger.info(f"Updated stock for {name}: {item['stock']} -> {new_stock}")
            return True
        
        except Exception as e:
            logger.error(f"Error updating stock: {e}")
            conn.rollback()
            return False
        
        finally:
            conn.close()
    
    def list_items(self, category: str = None, in_stock_only: bool = False) -> List[Dict]:
        """
        List all items in inventory
        
        Args:
            category: Filter by category
            in_stock_only: Only return items with stock > 0
        
        Returns:
            List of item dicts
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = 'SELECT * FROM items WHERE 1=1'
        params = []
        
        if category:
            query += ' AND category = ?'
            params.append(category)
        
        if in_stock_only:
            query += ' AND stock > 0'
        
        query += ' ORDER BY name'
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def search_items(self, query: str) -> List[Dict]:
        """
        Search items by name or brand
        
        Args:
            query: Search query
        
        Returns:
            List of matching items
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM items 
            WHERE LOWER(name) LIKE LOWER(?) OR LOWER(brand) LIKE LOWER(?)
            ORDER BY name
        ''', (f'%{query}%', f'%{query}%'))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def delete_item(self, name: str) -> bool:
        """
        Delete item from inventory
        
        Args:
            name: Item name
        
        Returns:
            True if successful, False otherwise
        """
        item = self.get_item_by_name(name)
        if not item:
            logger.error(f"Item not found: {name}")
            return False
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('DELETE FROM items WHERE id = ?', (item['id'],))
            conn.commit()
            logger.info(f"Deleted item: {name}")
            return True
        
        except Exception as e:
            logger.error(f"Error deleting item: {e}")
            return False
        
        finally:
            conn.close()
    
    def get_stock_history(self, name: str, limit: int = 10) -> List[Dict]:
        """
        Get stock change history for an item
        
        Args:
            name: Item name
            limit: Max records to return
        
        Returns:
            List of stock history records
        """
        item = self.get_item_by_name(name)
        if not item:
            return []
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM stock_history 
            WHERE item_id = ? 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (item['id'], limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]


# Example usage
if __name__ == "__main__":
    # Initialize database
    db = InventoryDB()
    
    # Add sample items
    try:
        db.add_item("atta", "Aashirvaad", "kg", 50, 45.0, 5.0, "groceries")
        db.add_item("milk", "Amul", "litre", 30, 60.0, 0.0, "dairy")
        db.add_item("rice", "India Gate", "kg", 100, 80.0, 5.0, "groceries")
        db.add_item("sugar", "Madhur", "kg", 40, 42.0, 5.0, "groceries")
        print("Sample items added successfully")
    except ValueError as e:
        print(f"Items may already exist: {e}")
    
    # List all items
    items = db.list_items()
    print(f"\nTotal items: {len(items)}")
    for item in items:
        print(f"- {item['name']} ({item['brand']}): {item['stock']} {item['unit']} @ ₹{item['price']}")
