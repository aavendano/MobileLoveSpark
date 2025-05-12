from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime, Text, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .connection import Base

class User(Base):
    """User profile information"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    partner1_name = Column(String(100))
    partner2_name = Column(String(100))
    relationship_status = Column(String(50))
    relationship_duration = Column(String(50))
    challenge_frequency = Column(String(20), default="daily")
    preferred_categories = Column(JSON, default=list)
    excluded_categories = Column(JSON, default=list)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_login = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    progress = relationship("UserProgress", back_populates="user", uselist=False)
    completed_challenges = relationship("CompletedChallenge", back_populates="user")
    viewed_articles = relationship("ViewedArticle", back_populates="user")
    viewed_products = relationship("ViewedProduct", back_populates="user")
    badges = relationship("UserBadge", back_populates="user")

class UserProgress(Base):
    """User progress tracking"""
    __tablename__ = "user_progress"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    streak = Column(Integer, default=0)
    last_completed = Column(DateTime(timezone=True), nullable=True)
    spark_level = Column(Float, default=10.0)
    total_completed = Column(Integer, default=0)
    
    # Relationships
    user = relationship("User", back_populates="progress")

class CompletedChallenge(Base):
    """Challenges completed by users"""
    __tablename__ = "completed_challenges"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    challenge_id = Column(String(50))  # From the static challenge data
    category = Column(String(100))
    completed_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="completed_challenges")

class UserBadge(Base):
    """Badges earned by users"""
    __tablename__ = "user_badges"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    badge_name = Column(String(100))
    earned_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="badges")

class ViewedArticle(Base):
    """Articles viewed by users"""
    __tablename__ = "viewed_articles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    article_id = Column(String(50))  # From the static article data
    viewed_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="viewed_articles")

class ViewedProduct(Base):
    """Products viewed by users"""
    __tablename__ = "viewed_products"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    product_id = Column(String(50))  # From the static product data
    viewed_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="viewed_products")

class CurrentChallenge(Base):
    """Currently active challenge for a user"""
    __tablename__ = "current_challenges"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    challenge_id = Column(String(50))  # From the static challenge data
    category = Column(String(100))
    generated_at = Column(DateTime(timezone=True), server_default=func.now())