from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from backend.database import Base
import json

class User(Base):
    """User model with profile and preferences support"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    nickname = Column(String(100), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    preferences = Column(Text, nullable=True, default="{}")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def get_preferences(self) -> dict:
        """Parse preferences JSON string to dict"""
        if not self.preferences:
            return {}
        try:
            return json.loads(self.preferences)
        except json.JSONDecodeError:
            return {}

    def set_preferences(self, prefs: dict) -> None:
        """Serialize preferences dict to JSON string"""
        self.preferences = json.dumps(prefs, ensure_ascii=False)

    def to_dict(self, include_sensitive: bool = False) -> dict:
        """Convert user to dict, exclude sensitive fields by default"""
        data = {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "nickname": self.nickname,
            "avatar_url": self.avatar_url,
            "preferences": self.get_preferences(),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
        if include_sensitive:
            data["password_hash"] = self.password_hash
        return data