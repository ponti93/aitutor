"""
Database migration script to add new columns without losing data
"""
import os
from dotenv import load_dotenv
from sqlalchemy import text
from models import db
from app import app

def migrate_database():
    """Add new columns to existing tables without resetting the database"""
    with app.app_context():
        try:
            print("Starting database migration...")
            
            # Check if study_sessions table exists
            result = db.session.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'study_sessions'
                );
            """))
            study_sessions_exists = result.scalar()
            
            if not study_sessions_exists:
                print("Creating study_sessions table...")
                db.session.execute(text("""
                    CREATE TABLE study_sessions (
                        session_id SERIAL PRIMARY KEY,
                        user_id INTEGER NOT NULL REFERENCES users(user_id),
                        document_id INTEGER NOT NULL REFERENCES documents(document_id),
                        session_name VARCHAR(255) NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """))
                print("✓ study_sessions table created")
            
            # Check if study_materials has study_session_id column
            result = db.session.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='study_materials' AND column_name='study_session_id';
            """))
            has_study_session_id = result.fetchone() is not None
            
            if not has_study_session_id:
                print("Adding study_session_id column to study_materials...")
                db.session.execute(text("""
                    ALTER TABLE study_materials 
                    ADD COLUMN study_session_id INTEGER;
                """))
                print("✓ study_session_id column added")
            
            # Check if study_materials has last_accessed column
            result = db.session.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='study_materials' AND column_name='last_accessed';
            """))
            has_last_accessed = result.fetchone() is not None
            
            if not has_last_accessed:
                print("Adding last_accessed column to study_materials...")
                db.session.execute(text("""
                    ALTER TABLE study_materials 
                    ADD COLUMN last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
                """))
                print("✓ last_accessed column added")
            
            # Add foreign key constraint if it doesn't exist
            result = db.session.execute(text("""
                SELECT constraint_name 
                FROM information_schema.table_constraints 
                WHERE table_name='study_materials' AND constraint_type='FOREIGN KEY' 
                AND constraint_name LIKE '%study_session_id%';
            """))
            has_fk = result.fetchone() is not None
            
            if not has_fk:
                print("Adding foreign key constraint...")
                db.session.execute(text("""
                    ALTER TABLE study_materials 
                    ADD CONSTRAINT fk_study_materials_study_session 
                    FOREIGN KEY (study_session_id) REFERENCES study_sessions(session_id);
                """))
                print("✓ foreign key constraint added")
            
            db.session.commit()
            print("✓ Database migration completed successfully!")
            
        except Exception as e:
            db.session.rollback()
            print(f"✗ Migration failed: {str(e)}")
            raise

if __name__ == '__main__':
    migrate_database()
