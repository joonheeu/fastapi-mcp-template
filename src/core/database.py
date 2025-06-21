"""
Database connection and management utilities.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
import json


class InMemoryDatabase:
    """Simple in-memory database for template purposes."""
    
    def __init__(self):
        self._data: Dict[str, List[Dict[str, Any]]] = {}
        self._next_ids: Dict[str, int] = {}
    
    def _get_next_id(self, table: str) -> int:
        """Get the next available ID for a table."""
        if table not in self._next_ids:
            self._next_ids[table] = 1
        else:
            self._next_ids[table] += 1
        return self._next_ids[table]
    
    def create_table(self, table_name: str) -> None:
        """Create a new table."""
        if table_name not in self._data:
            self._data[table_name] = []
    
    def insert(self, table: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Insert a new record."""
        self.create_table(table)
        
        # Add ID and timestamps
        record = data.copy()
        record["id"] = self._get_next_id(table)
        record["created_at"] = datetime.now()
        record["updated_at"] = datetime.now()
        
        self._data[table].append(record)
        return record
    
    def find_all(self, table: str, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """Find all records in a table."""
        self.create_table(table)
        return self._data[table][skip:skip + limit]
    
    def find_by_id(self, table: str, record_id: int) -> Optional[Dict[str, Any]]:
        """Find a record by ID."""
        self.create_table(table)
        for record in self._data[table]:
            if record.get("id") == record_id:
                return record
        return None
    
    def update(self, table: str, record_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update a record by ID."""
        self.create_table(table)
        for i, record in enumerate(self._data[table]):
            if record.get("id") == record_id:
                # Update fields
                updated_record = record.copy()
                updated_record.update(data)
                updated_record["updated_at"] = datetime.now()
                
                self._data[table][i] = updated_record
                return updated_record
        return None
    
    def delete(self, table: str, record_id: int) -> bool:
        """Delete a record by ID."""
        self.create_table(table)
        for i, record in enumerate(self._data[table]):
            if record.get("id") == record_id:
                del self._data[table][i]
                return True
        return False
    
    def count(self, table: str) -> int:
        """Count records in a table."""
        self.create_table(table)
        return len(self._data[table])
    
    def find_by_field(self, table: str, field: str, value: Any) -> List[Dict[str, Any]]:
        """Find records by field value."""
        self.create_table(table)
        return [record for record in self._data[table] if record.get(field) == value]
    
    def clear_table(self, table: str) -> None:
        """Clear all records from a table."""
        self.create_table(table)
        self._data[table] = []
        self._next_ids[table] = 0
    
    def export_data(self) -> str:
        """Export all data as JSON string."""
        export_data = {
            "data": self._data,
            "next_ids": self._next_ids,
            "exported_at": datetime.now().isoformat()
        }
        return json.dumps(export_data, default=str, indent=2)
    
    def import_data(self, json_data: str) -> None:
        """Import data from JSON string."""
        imported = json.loads(json_data)
        self._data = imported.get("data", {})
        self._next_ids = imported.get("next_ids", {})


# Global database instance
db = InMemoryDatabase()

# Initialize with sample data
def init_sample_data():
    """Initialize database with sample data."""
    # Sample items
    sample_items = [
        {
            "name": "Sample Product 1",
            "description": "This is a sample product for demonstration",
            "price": 29.99,
            "category": "electronics",
            "is_available": True,
            "tags": ["sample", "demo", "electronics"]
        },
        {
            "name": "Sample Service 1",
            "description": "This is a sample service for demonstration",
            "price": 99.99,
            "category": "services",
            "is_available": True,
            "tags": ["sample", "demo", "services"]
        },
        {
            "name": "Sample Product 2",
            "description": "Another sample product",
            "price": 49.99,
            "category": "books",
            "is_available": False,
            "tags": ["sample", "demo", "books"]
        }
    ]
    
    # Sample users
    sample_users = [
        {
            "username": "admin",
            "email": "admin@example.com",
            "full_name": "Admin User",
            "is_active": True,
            "role": "admin"
        },
        {
            "username": "demo_user",
            "email": "demo@example.com",
            "full_name": "Demo User",
            "is_active": True,
            "role": "user"
        }
    ]
    
    # Insert sample data
    for item in sample_items:
        db.insert("items", item)
    
    for user in sample_users:
        db.insert("users", user)


# Initialize sample data on import
init_sample_data() 