from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
import json

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    preferences = db.Column(db.JSON)
    
    def get_id(self):
        return str(self.user_id)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Document(db.Model):
    __tablename__ = 'documents'
    
    document_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_type = db.Column(db.String(10), nullable=False)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    processing_status = db.Column(db.String(20), default='pending')
    document_metadata = db.Column(db.JSON)
    
    user = db.relationship('User', backref=db.backref('documents', lazy=True))
    
    def __repr__(self):
        return f'<Document {self.filename}>'

class KnowledgeBase(db.Model):
    __tablename__ = 'knowledge_base'
    
    kb_id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey('documents.document_id'), nullable=False)
    content_text = db.Column(db.Text, nullable=False)
    processed_content = db.Column(db.JSON)
    concepts = db.Column(db.JSON)
    keywords = db.Column(db.JSON)  # Using JSON instead of array for compatibility
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    document = db.relationship('Document', backref=db.backref('knowledge_entries', lazy=True))
    
    def __repr__(self):
        return f'<KnowledgeBase {self.kb_id}>'

class ChatSession(db.Model):
    __tablename__ = 'chat_sessions'
    
    session_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    session_start = db.Column(db.DateTime, default=datetime.utcnow)
    session_end = db.Column(db.DateTime)
    total_queries = db.Column(db.Integer, default=0)
    session_data = db.Column(db.JSON)
    
    user = db.relationship('User', backref=db.backref('chat_sessions', lazy=True))
    
    def __repr__(self):
        return f'<ChatSession {self.session_id}>'

class QueryHistory(db.Model):
    __tablename__ = 'query_history'
    
    query_id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('chat_sessions.session_id'), nullable=False)
    user_query = db.Column(db.Text, nullable=False)
    ai_response = db.Column(db.Text, nullable=False)
    query_timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    response_time = db.Column(db.Float)
    relevance_score = db.Column(db.Float)
    
    session = db.relationship('ChatSession', backref=db.backref('queries', lazy=True))
    
    def __repr__(self):
        return f'<QueryHistory {self.query_id}>'

class StudySession(db.Model):
    __tablename__ = 'study_sessions'
    
    session_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    document_id = db.Column(db.Integer, db.ForeignKey('documents.document_id'), nullable=False)
    session_name = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_accessed = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('study_sessions', lazy=True))
    document = db.relationship('Document', backref=db.backref('study_sessions', lazy=True))
    
    def __repr__(self):
        return f'<StudySession {self.session_name}>'

class StudyMaterial(db.Model):
    __tablename__ = 'study_materials'
    
    material_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    study_session_id = db.Column(db.Integer, db.ForeignKey('study_sessions.session_id'), nullable=False)
    material_type = db.Column(db.String(20), nullable=False)  # summary/quiz/flashcard/concepts
    content = db.Column(db.JSON, nullable=False)
    source_documents = db.Column(db.JSON)  # Array of document IDs
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_accessed = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('study_materials', lazy=True))
    study_session = db.relationship('StudySession', backref=db.backref('materials', lazy=True))
    
    def __repr__(self):
        return f'<StudyMaterial {self.material_type} {self.material_id}>'
