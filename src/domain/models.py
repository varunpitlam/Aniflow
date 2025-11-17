import uuid
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, Text, TIMESTAMP, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

# --- Base Class ---
# All models will inherit from this class
Base = declarative_base()

# --- Model Definitions ---
# These classes are based directly on your ERD.

class User(Base):
    __tablename__ = 'user'
    
    # Columns from ERD
    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(255), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    role = Column(String(50), default='user') # 'user' or 'admin'
    
    # --- Relationships ---
    # 1-to-1 relationship with UserProfile
    profile = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    
    # 1-to-Many relationships
    watchlists = relationship("Watchlist", back_populates="user", cascade="all, delete-orphan")
    ratings = relationship("Rating", back_populates="user", cascade="all, delete-orphan")
    notes = relationship("Note", back_populates="user", cascade="all, delete-orphan")

class UserProfile(Base):
    __tablename__ = 'user_profile'
    
    # Columns from ERD
    user_id = Column(UUID(as_uuid=True), ForeignKey('user.user_id'), primary_key=True)
    age = Column(Integer)
    region = Column(String(255))
    bio = Column(Text)
    # Using JSON type as specified in your Sprint 2 Report (Challenge/Solution)
    preferred_genres = Column(JSON)
    preferred_studios = Column(JSON)
    preferred_themes = Column(JSON)
    hide_profile = Column(Boolean, default=False)
    filter_settings = Column(JSON) # For Story 4
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # --- Relationships ---
    # 1-to-1 relationship back to User
    user = relationship("User", back_populates="profile")

class Anime(Base):
    __tablename__ = 'anime'
    
    # Columns from ERD
    anime_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False, index=True)
    synopsis = Column(Text)
    release_year = Column(Integer)
    episodes = Column(Integer)
    popularity_score = Column(Float, default=0)
    average_rating = Column(Float, default=0)
    # Using JSON for lists, as planned
    genres = Column(JSON)
    studios = Column(JSON)
    themes = Column(JSON)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # --- Relationships ---
    # 1-to-Many relationships
    ratings = relationship("Rating", back_populates="anime", cascade="all, delete-orphan")
    notes = relationship("Note", back_populates="anime", cascade="all, delete-orphan")
    watchlist_items = relationship("WatchlistItem", back_populates="anime", cascade="all, delete-orphan")

class Rating(Base):
    __tablename__ = 'rating'
    
    # Columns from ERD
    rating_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('user.user_id'), nullable=False, index=True)
    anime_id = Column(UUID(as_uuid=True), ForeignKey('anime.anime_id'), nullable=False, index=True)
    # Integer score to flexibly handle Story 2 (1-10) and Story 11 (thumbs up/down)
    score = Column(Integer, nullable=False)
    review_text = Column(Text)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    
    # --- Relationships ---
    user = relationship("User", back_populates="ratings")
    anime = relationship("Anime", back_populates="ratings")

class Note(Base):
    __tablename__ = 'note'
    
    # Columns from ERD (Implements Story 3)
    note_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('user.user_id'), nullable=False, index=True)
    anime_id = Column(UUID(as_uuid=True), ForeignKey('anime.anime_id'), nullable=False, index=True)
    private_note = Column(Text)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # --- Relationships ---
    user = relationship("User", back_populates="notes")
    anime = relationship("Anime", back_populates="notes")

class Watchlist(Base):
    __tablename__ = 'watchlist'
    
    # Columns from ERD (Implements Story 5)
    watchlist_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('user.user_id'), nullable=False, index=True)
    name = Column(String(255), nullable=False, default='My Watchlist')
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # --- Relationships ---
    user = relationship("User", back_populates="watchlists")
    items = relationship("WatchlistItem", back_populates="watchlist", cascade="all, delete-orphan")

class WatchlistItem(Base):
    __tablename__ = 'watchlist_item'
    
    # Columns from ERD
    watchlist_item_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    watchlist_id = Column(UUID(as_uuid=True), ForeignKey('watchlist.watchlist_id'), nullable=False, index=True)
    anime_id = Column(UUID(as_uuid=True), ForeignKey('anime.anime_id'), nullable=False, index=True)
    priority_rank = Column(Integer)
    added_at = Column(TIMESTAMP, default=datetime.utcnow)
    completed = Column(Boolean, default=False)
    # rewatch_count directly supports Story 6
    rewatch_count = Column(Integer, default=0)
    
    # --- Relationships ---
    watchlist = relationship("Watchlist", back_populates="items")
    anime = relationship("Anime", back_populates="watchlist_items")

# --- (Optional) Code to initialize the database ---
# This is useful for testing your models locally.
if __name__ == "__main__":
    # Use a simple SQLite in-memory database for testing
    # For production, you'll use your PostgreSQL connection string
    # E.g., "postgresql://user:password@localhost/aniflow"
    engine = create_engine('sqlite:///:memory:')
    
    print("Creating all tables...")
    Base.metadata.create_all(engine)
    print("Tables created successfully.")
    
    # You can add test code here to create a session and add objects
    # Session = sessionmaker(bind=engine)
    # session = Session()
    # ...
    # session.close()
