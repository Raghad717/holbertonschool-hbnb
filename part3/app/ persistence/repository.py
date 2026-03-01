"""
Data access layer with repository pattern implementation.
Provides abstract interfaces and concrete implementations for data persistence.
"""
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any, TypeVar, Generic
from datetime import datetime

# Generic type for entity models
Entity = TypeVar('Entity')


class DataAccessInterface(ABC, Generic[Entity]):
    """
    Abstract interface defining contract for data access operations.
    All repositories must implement these methods.
    """
    
    @abstractmethod
    def insert(self, item: Entity) -> Entity:
        """Store a new entity in the data source"""
        pass
    
    @abstractmethod
    def fetch(self, item_id: str) -> Optional[Entity]:
        """Retrieve an entity by its unique identifier"""
        pass
    
    @abstractmethod
    def fetch_all(self) -> List[Entity]:
        """Retrieve all entities of this type"""
        pass
    
    @abstractmethod
    def modify(self, item_id: str, changes: Dict[str, Any]) -> Optional[Entity]:
        """Apply modifications to an existing entity"""
        pass
    
    @abstractmethod
    def remove(self, item_id: str) -> bool:
        """Delete an entity from the data source"""
        pass
    
    @abstractmethod
    def find_by(self, **criteria) -> Optional[Entity]:
        """Find first entity matching the given criteria"""
        pass
    
    @abstractmethod
    def find_all_by(self, **criteria) -> List[Entity]:
        """Find all entities matching the given criteria"""
        pass


class MemoryDataStore(DataAccessInterface[Entity]):
    """
    In-memory implementation for development and testing.
    Data is stored in Python dictionary and lost on application restart.
    """
    
    def __init__(self):
        self._container = {}
        self._sequence = 0
    
    def _generate_temp_id(self) -> str:
        """Generate a temporary ID for in-memory storage"""
        self._sequence += 1
        timestamp = int(datetime.utcnow().timestamp() * 1000)
        return f"tmp_{timestamp}_{self._sequence}"
    
    def insert(self, item: Entity) -> Entity:
        """Store item in memory container"""
        if not hasattr(item, 'id') or not item.id:
            item.id = self._generate_temp_id()
        
        self._container[item.id] = item
        return item
    
    def fetch(self, item_id: str) -> Optional[Entity]:
        """Retrieve item from memory by ID"""
        return self._container.get(item_id)
    
    def fetch_all(self) -> List[Entity]:
        """Retrieve all items from memory"""
        return list(self._container.values())
    
    def modify(self, item_id: str, changes: Dict[str, Any]) -> Optional[Entity]:
        """Apply changes to an item in memory"""
        item = self.fetch(item_id)
        
        if item:
            for key, value in changes.items():
                if hasattr(item, key) and key not in ['id', 'created_at']:
                    setattr(item, key, value)
            
            # Update timestamp if available
            if hasattr(item, 'updated_at'):
                item.updated_at = datetime.utcnow()
        
        return item
    
    def remove(self, item_id: str) -> bool:
        """Remove item from memory"""
        if item_id in self._container:
            del self._container[item_id]
            return True
        return False
    
    def find_by(self, **criteria) -> Optional[Entity]:
        """Find first item matching criteria"""
        for item in self._container.values():
            match = True
            for key, value in criteria.items():
                if getattr(item, key, None) != value:
                    match = False
                    break
            if match:
                return item
        return None
    
    def find_all_by(self, **criteria) -> List[Entity]:
        """Find all items matching criteria"""
        results = []
        for item in self._container.values():
            match = True
            for key, value in criteria.items():
                if getattr(item, key, None) != value:
                    match = False
                    break
            if match:
                results.append(item)
        return results
    
    def count_items(self) -> int:
        """Get total number of items"""
        return len(self._container)
    
    def clear_all(self) -> None:
        """Clear all items (useful for testing)"""
        self._container.clear()
        self._sequence = 0


class DatabaseDataStore(DataAccessInterface[Entity]):
    """
    SQLAlchemy-based implementation for production database.
    Provides persistent storage using relational database backend.
    """
    
    def __init__(self, model_class):
        """
        Initialize with a SQLAlchemy model class.
        
        Args:
            model_class: SQLAlchemy declarative model class
        """
        self.model_class = model_class
        self._session_provider = None
    
    def _get_session(self):
        """Lazy-load database session to avoid circular imports"""
        if self._session_provider is None:
            from flask import current_app
            from hbnb.app.extensions import db
            self._session_provider = db.session
        return self._session_provider
    
    def insert(self, item: Entity) -> Entity:
        """Persist a new entity to the database"""
        session = self._get_session()
        session.add(item)
        session.commit()
        session.refresh(item)
        return item
    
    def fetch(self, item_id: str) -> Optional[Entity]:
        """Retrieve entity by primary key"""
        return self.model_class.query.get(item_id)
    
    def fetch_all(self) -> List[Entity]:
        """Retrieve all entities of this type"""
        return self.model_class.query.all()
    
    def modify(self, item_id: str, changes: Dict[str, Any]) -> Optional[Entity]:
        """Update entity with new values"""
        session = self._get_session()
        item = self.fetch(item_id)
        
        if item:
            # Apply changes (skip protected fields)
            protected_fields = ['id', 'created_at']
            for key, value in changes.items():
                if hasattr(item, key) and key not in protected_fields:
                    setattr(item, key, value)
            
            # Auto-update timestamp if field exists
            if hasattr(item, 'updated_at'):
                item.updated_at = datetime.utcnow()
            
            session.commit()
            session.refresh(item)
        
        return item
    
    def remove(self, item_id: str) -> bool:
        """Delete entity from database"""
        session = self._get_session()
        item = self.fetch(item_id)
        
        if item:
            session.delete(item)
            session.commit()
            return True
        
        return False
    
    def find_by(self, **criteria) -> Optional[Entity]:
        """Find first entity matching criteria using SQLAlchemy filter"""
        return self.model_class.query.filter_by(**criteria).first()
    
    def find_all_by(self, **criteria) -> List[Entity]:
        """Find all entities matching criteria"""
        return self.model_class.query.filter_by(**criteria).all()
    
    def exists(self, item_id: str) -> bool:
        """Check if an entity exists by ID"""
        return self.model_class.query.filter_by(id=item_id).first() is not None
    
    def count_all(self) -> int:
        """Get total count of entities"""
        return self.model_class.query.count()
    
    def get_paginated(self, page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """
        Retrieve paginated results.
        
        Returns:
            Dictionary with items, total, pages, current_page
        """
        pagination = self.model_class.query.paginate(page=page, per_page=per_page)
        
        return {
            'data': pagination.items,
            'total_records': pagination.total,
            'total_pages': pagination.pages,
            'current_page': pagination.page,
            'has_next': pagination.has_next,
            'has_previous': pagination.has_prev
        }
    
    def execute_raw_query(self, sql: str, params: Dict = None):
        """
        Execute raw SQL query (use with caution).
        For advanced operations only.
        """
        session = self._get_session()
        result = session.execute(sql, params or {})
        return result.fetchall()
