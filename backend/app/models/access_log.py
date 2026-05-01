from sqlalchemy import Column, Integer, String, DateTime, Index
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class AccessLog(Base):
    """Access log record model
    
    Stores visitor access information including timestamp, IP, user agent and path.
    """
    __tablename__ = "access_logs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    ip = Column(String(45), nullable=False)  # IPv6 max length
    user_agent = Column(String(255), nullable=True)
    path = Column(String(255), nullable=True)
    
    __table_args__ = (
        Index('idx_timestamp', 'timestamp'),
    )
    
    def to_dict(self):
        """Convert model instance to dictionary for JSON serialization"""
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "ip": self.ip,
            "user_agent": self.user_agent,
            "path": self.path
        }
