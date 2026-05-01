"""Repository layer for transaction data access."""
import aiosqlite
from typing import List, Optional
from datetime import datetime
from backend.models.transaction import TransactionCreate, TransactionUpdate, TransactionResponse
import logging

logger = logging.getLogger(__name__)


class TransactionRepository:
    """Data access layer for transactions table."""
    
    @staticmethod
    async def create(db: aiosqlite.Connection, user_id: int, data: TransactionCreate) -> TransactionResponse:
        """Create a new transaction record.
        
        Args:
            db: Database connection
            user_id: User ID who owns the transaction
            data: Transaction creation data
            
        Returns:
            TransactionResponse: Created transaction with generated ID
        """
        now = datetime.utcnow().isoformat()
        
        cursor = await db.execute(
            """
            INSERT INTO transactions 
            (user_id, type, amount, category_id, date, note, payment_method, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                data.type,
                data.amount,
                data.category_id,
                data.date.isoformat(),
                data.note,
                data.payment_method,
                now,
                now
            )
        )
        await db.commit()
        
        transaction_id = cursor.lastrowid
        return await TransactionRepository.get_by_id(db, transaction_id, user_id)
    
    @staticmethod
    async def get_by_id(db: aiosqlite.Connection, transaction_id: int, user_id: int) -> Optional[TransactionResponse]:
        """Get transaction by ID (with user ownership check).
        
        Args:
            db: Database connection
            transaction_id: Transaction ID
            user_id: User ID for ownership verification
            
        Returns:
            TransactionResponse or None if not found
        """
        cursor = await db.execute(
            "SELECT * FROM transactions WHERE id = ? AND user_id = ?",
            (transaction_id, user_id)
        )
        row = await cursor.fetchone()
        
        if not row:
            return None
        
        return TransactionResponse(
            id=row["id"],
            user_id=row["user_id"],
            type=row["type"],
            amount=row["amount"],
            category_id=row["category_id"],
            date=datetime.fromisoformat(row["date"]),
            note=row["note"],
            payment_method=row["payment_method"],
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"])
        )
    
    @staticmethod
    async def list_by_user(
        db: aiosqlite.Connection,
        user_id: int,
        limit: int = 50,
        offset: int = 0,
        transaction_type: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[TransactionResponse]:
        """List transactions for a user with optional filters.
        
        Args:
            db: Database connection
            user_id: User ID
            limit: Max number of records
            offset: Pagination offset
            transaction_type: Filter by 'income' or 'expense'
            start_date: Filter by date >= start_date
            end_date: Filter by date <= end_date
            
        Returns:
            List of TransactionResponse
        """
        query = "SELECT * FROM transactions WHERE user_id = ?"
        params = [user_id]
        
        if transaction_type:
            query += " AND type = ?"
            params.append(transaction_type)
        
        if start_date:
            query += " AND date >= ?"
            params.append(start_date.isoformat())
        
        if end_date:
            query += " AND date <= ?"
            params.append(end_date.isoformat())
        
        query += " ORDER BY date DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        cursor = await db.execute(query, params)
        rows = await cursor.fetchall()
        
        return [
            TransactionResponse(
                id=row["id"],
                user_id=row["user_id"],
                type=row["type"],
                amount=row["amount"],
                category_id=row["category_id"],
                date=datetime.fromisoformat(row["date"]),
                note=row["note"],
                payment_method=row["payment_method"],
                created_at=datetime.fromisoformat(row["created_at"]),
                updated_at=datetime.fromisoformat(row["updated_at"])
            )
            for row in rows
        ]
    
    @staticmethod
    async def update(
        db: aiosqlite.Connection,
        transaction_id: int,
        user_id: int,
        data: TransactionUpdate
    ) -> Optional[TransactionResponse]:
        """Update transaction fields.
        
        Args:
            db: Database connection
            transaction_id: Transaction ID
            user_id: User ID for ownership verification
            data: Fields to update (only non-None fields are updated)
            
        Returns:
            Updated TransactionResponse or None if not found
        """
        # Build dynamic update query
        update_fields = []
        params = []
        
        if data.type is not None:
            update_fields.append("type = ?")
            params.append(data.type)
        
        if data.amount is not None:
            update_fields.append("amount = ?")
            params.append(data.amount)
        
        if data.category_id is not None:
            update_fields.append("category_id = ?")
            params.append(data.category_id)
        
        if data.date is not None:
            update_fields.append("date = ?")
            params.append(data.date.isoformat())
        
        if data.note is not None:
            update_fields.append("note = ?")
            params.append(data.note)
        
        if data.payment_method is not None:
            update_fields.append("payment_method = ?")
            params.append(data.payment_method)
        
        if not update_fields:
            # No fields to update, return current record
            return await TransactionRepository.get_by_id(db, transaction_id, user_id)
        
        # Always update updated_at
        update_fields.append("updated_at = ?")
        params.append(datetime.utcnow().isoformat())
        
        # Add WHERE clause params
        params.extend([transaction_id, user_id])
        
        query = f"UPDATE transactions SET {', '.join(update_fields)} WHERE id = ? AND user_id = ?"
        
        await db.execute(query, params)
        await db.commit()
        
        return await TransactionRepository.get_by_id(db, transaction_id, user_id)
    
    @staticmethod
    async def delete(db: aiosqlite.Connection, transaction_id: int, user_id: int) -> bool:
        """Delete a transaction.
        
        Args:
            db: Database connection
            transaction_id: Transaction ID
            user_id: User ID for ownership verification
            
        Returns:
            True if deleted, False if not found
        """
        cursor = await db.execute(
            "DELETE FROM transactions WHERE id = ? AND user_id = ?",
            (transaction_id, user_id)
        )
        await db.commit()
        
        return cursor.rowcount > 0
