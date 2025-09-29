from app import app, db
from models import User, Document, KnowledgeBase, ChatSession, QueryHistory, StudyMaterial

def reset_database():
    with app.app_context():
        # Drop all tables
        db.drop_all()
        
        # Create all tables
        db.create_all()
        
        print("Database reset successfully!")
        print("All tables have been recreated with the latest schema.")

if __name__ == '__main__':
    reset_database()
