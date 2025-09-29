"""
Script to check what content is stored in study session 2
"""
import os
from dotenv import load_dotenv
from models import db, StudySession, StudyMaterial
from app import app

def check_session_content():
    """Check what content is stored in session 2"""
    with app.app_context():
        try:
            # Find session 2
            session = StudySession.query.filter_by(session_id=2).first()
            if not session:
                print("Session 2 not found!")
                return

            print(f"Session 2 Details:")
            print(f"  Session ID: {session.session_id}")
            print(f"  Session Name: {session.session_name}")
            print(f"  Document ID: {session.document_id}")
            print(f"  User ID: {session.user_id}")
            print(f"  Created At: {session.created_at}")
            print(f"  Last Accessed: {session.last_accessed}")
            print()

            # Get all materials in this session
            materials = StudyMaterial.query.filter_by(study_session_id=2).all()

            if not materials:
                print("No materials found in session 2!")
                return

            print(f"Materials in Session 2 ({len(materials)} materials):")
            print("-" * 50)

            for i, material in enumerate(materials, 1):
                print(f"\nMaterial {i}:")
                print(f"  Material ID: {material.material_id}")
                print(f"  Material Type: {material.material_type}")
                print(f"  User ID: {material.user_id}")
                print(f"  Study Session ID: {material.study_session_id}")
                print(f"  Created At: {material.created_at}")
                print(f"  Last Accessed: {material.last_accessed}")
                print(f"  Source Documents: {material.source_documents}")
                print()
                print("  Content (raw):")
                print(f"    {material.content}")
                print()
                print("  Content (parsed):")
                try:
                    import json
                    if isinstance(material.content, str):
                        parsed = json.loads(material.content)
                        print(f"    {parsed}")
                        print(f"    Type: {type(parsed)}")
                    else:
                        print(f"    {material.content}")
                        print(f"    Type: {type(material.content)}")
                        print(f"    Already parsed: {isinstance(material.content, (dict, list))}")
                except Exception as e:
                    print(f"    Error parsing JSON: {e}")
                    print(f"    Raw content: {repr(material.content)}")
                print("-" * 50)

        except Exception as e:
            print(f"Error checking session content: {str(e)}")

if __name__ == '__main__':
    check_session_content()
