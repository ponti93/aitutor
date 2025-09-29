from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_file
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from datetime import datetime
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from models import db, User, Document, KnowledgeBase, ChatSession, QueryHistory, StudySession, StudyMaterial
from content_processor import ContentProcessor
from nlp_engine_simple import NLPEngineSimple as NLPEngine
from knowledge_manager import KnowledgeManager
from study_generator import StudyGenerator

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql://postgres:incorrect@localhost/aitutor')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Initialize core modules
content_processor = ContentProcessor()
nlp_engine = NLPEngine()
knowledge_manager = KnowledgeManager()
study_generator = StudyGenerator()

# Add custom Jinja2 filter for JSON parsing
def from_json(value):
    """Parse JSON string to Python object"""
    try:
        return json.loads(value)
    except (ValueError, TypeError):
        return {}

app.jinja_env.filters['from_json'] = from_json

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if User.query.filter_by(username=username).first():
            return render_template('register.html', error='Username already exists')
        
        if User.query.filter_by(email=email).first():
            return render_template('register.html', error='Email already exists')
        
        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password)
        )
        db.session.add(user)
        db.session.commit()
        
        login_user(user)
        return redirect(url_for('dashboard'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        
        return render_template('login.html', error='Invalid username or password')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    # Get user statistics
    documents_count = Document.query.filter_by(user_id=current_user.user_id).count()
    recent_sessions = ChatSession.query.filter_by(user_id=current_user.user_id).order_by(ChatSession.session_start.desc()).limit(5).all()
    recent_materials = StudyMaterial.query.filter_by(user_id=current_user.user_id).order_by(StudyMaterial.created_at.desc()).limit(5).all()
    
    return render_template('dashboard.html',
                         documents_count=documents_count,
                         recent_sessions=recent_sessions,
                         recent_materials=recent_materials)

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        try:
            if 'file' not in request.files:
                return jsonify({'error': 'No file selected'}), 400
            
            file = request.files['file']
            if file.filename == '':
                return jsonify({'error': 'No file selected'}), 400
            
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                
                # Create document record
                document = Document(
                    user_id=current_user.user_id,
                    filename=filename,
                    file_path=file_path,
                    file_type=file.filename.rsplit('.', 1)[1].lower(),
                    processing_status='processing'
                )
                db.session.add(document)
                db.session.commit()
                
                # Process document immediately
                try:
                    print(f"Processing document: {file_path}, type: {document.file_type}")
                    processed_data = content_processor.process_document(file_path, document.file_type)
                    print(f"Document processed successfully, content length: {len(processed_data['content'])}")
                    
                    # Create knowledge base entry
                    knowledge_entry = KnowledgeBase(
                        document_id=document.document_id,
                        content_text=processed_data['content'],
                        processed_content=processed_data,
                        concepts=processed_data['concepts'],
                        keywords=processed_data['concepts']  # Using concepts as keywords for now
                    )
                    db.session.add(knowledge_entry)
                    
                    # Update document status
                    document.processing_status = 'completed'
                    document.document_metadata = content_processor.get_document_metadata(file_path, document.file_type)
                    db.session.commit()
                    
                    print(f"Knowledge base entry created for document {document.document_id}")
                    return jsonify({'message': 'File uploaded and processed successfully', 'document_id': document.document_id})
                    
                except Exception as e:
                    print(f"Document processing error: {str(e)}")
                    document.processing_status = 'failed'
                    db.session.commit()
                    return jsonify({'error': f'Document processing failed: {str(e)}'}), 500
            
            return jsonify({'error': 'Invalid file type. Please upload PDF, DOCX, or image files (JPG, JPEG, PNG, BMP, TIFF) only.'}), 400
        
        except Exception as e:
            return jsonify({'error': f'Upload failed: {str(e)}'}), 500
    
    return render_template('upload.html')

@app.route('/chat_sessions')
@login_required
def chat_sessions():
    """Display all chat sessions for the user"""
    sessions = ChatSession.query.filter_by(user_id=current_user.user_id).order_by(ChatSession.session_start.desc()).all()
    return render_template('chat_sessions.html', sessions=sessions)

@app.route('/chat', methods=['GET', 'POST'])
@app.route('/chat/<int:session_id>', methods=['GET', 'POST'])
@login_required
def chat(session_id=None):
    if request.method == 'POST':
        user_query = request.json.get('query')
        document_id = request.json.get('document_id')
        session_id = request.json.get('session_id')
        
        if not user_query:
            return jsonify({'error': 'No query provided'}), 400
        
        if not document_id:
            return jsonify({'error': 'No document selected'}), 400
        
        # Get or create chat session
        if session_id:
            chat_session = ChatSession.query.filter_by(
                session_id=session_id,
                user_id=current_user.user_id
            ).first()
        else:
            # Create a new session for each new chat (don't reuse open sessions)
            chat_session = ChatSession(user_id=current_user.user_id)
            db.session.add(chat_session)
            db.session.commit()
        
        if not chat_session:
            chat_session = ChatSession(user_id=current_user.user_id)
            db.session.add(chat_session)
            db.session.commit()
        
        # Process query with specific document using Gemini
        response, relevance_score = nlp_engine.process_user_query_with_document(user_query, current_user.user_id, document_id)
        
        # Save query history
        query_history = QueryHistory(
            session_id=chat_session.session_id,
            user_query=user_query,
            ai_response=response,
            relevance_score=relevance_score
        )
        db.session.add(query_history)
        chat_session.total_queries += 1
        db.session.commit()
        
        return jsonify({
            'response': response,
            'relevance_score': relevance_score,
            'session_id': chat_session.session_id,
            'timestamp': datetime.now().isoformat()
        })
    
    # Get user's documents for the dropdown
    documents = Document.query.filter_by(user_id=current_user.user_id).all()
    
    # Get session data if session_id is provided
    session_data = None
    if session_id:
        chat_session = ChatSession.query.filter_by(
            session_id=session_id,
            user_id=current_user.user_id
        ).first()
        if chat_session:
            # Query the queries directly with ordering
            queries = QueryHistory.query.filter_by(
                session_id=session_id
            ).order_by(QueryHistory.query_timestamp.asc()).all()
            session_data = {
                'session_id': chat_session.session_id,
                'queries': queries
            }
    
    return render_template('chat.html', documents=documents, session_data=session_data)

@app.route('/end_session/<int:session_id>', methods=['POST'])
@login_required
def end_session(session_id):
    """End a chat session"""
    chat_session = ChatSession.query.filter_by(
        session_id=session_id,
        user_id=current_user.user_id
    ).first()
    
    if not chat_session:
        return jsonify({'error': 'Session not found'}), 404
    
    try:
        chat_session.session_end = datetime.utcnow()
        db.session.commit()
        return jsonify({'success': True, 'message': 'Session ended successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to end session: {str(e)}'}), 500

@app.route('/delete_session/<int:session_id>', methods=['DELETE'])
@login_required
def delete_session(session_id):
    """Delete a chat session and all its messages"""
    chat_session = ChatSession.query.filter_by(
        session_id=session_id,
        user_id=current_user.user_id
    ).first()

    if not chat_session:
        return jsonify({'error': 'Session not found'}), 404

    try:
        # Delete all queries in this session
        QueryHistory.query.filter_by(session_id=session_id).delete()

        # Delete the session
        db.session.delete(chat_session)
        db.session.commit()

        return jsonify({'success': True, 'message': 'Session deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to delete session: {str(e)}'}), 500

@app.route('/delete-study-session/<int:session_id>', methods=['DELETE'])
@login_required
def delete_study_session(session_id):
    """Delete a study session and all its materials"""
    study_session = StudySession.query.filter_by(
        session_id=session_id,
        user_id=current_user.user_id
    ).first()

    if not study_session:
        return jsonify({'error': 'Study session not found'}), 404

    try:
        # Delete all study materials in this session
        StudyMaterial.query.filter_by(study_session_id=session_id).delete()

        # Delete the study session
        db.session.delete(study_session)
        db.session.commit()

        return jsonify({'success': True, 'message': 'Study session deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to delete study session: {str(e)}'}), 500

@app.route('/study-tools')
@login_required
def study_tools():
    documents = Document.query.filter_by(user_id=current_user.user_id).all()
    study_sessions = StudySession.query.filter_by(user_id=current_user.user_id).order_by(StudySession.last_accessed.desc()).all()

    # Check if a document_id is provided in the URL to auto-select it
    selected_document_id = request.args.get('document_id', type=int)

    return render_template('study_tools.html', documents=documents, study_sessions=study_sessions, selected_document_id=selected_document_id)

@app.route('/study-session/<int:session_id>')
@login_required
def study_session(session_id):
    """View a specific study session with all generated materials"""
    study_session = StudySession.query.filter_by(
        session_id=session_id,
        user_id=current_user.user_id
    ).first()
    
    if not study_session:
        return "Study session not found", 404
    
    # Update last accessed time
    study_session.last_accessed = datetime.utcnow()
    db.session.commit()
    
    return render_template('study_session.html', study_session=study_session)

@app.route('/save-study-material', methods=['POST'])
@login_required
def save_study_material():
    """Save a generated study material to a new study session"""
    data = request.json
    document_id = data.get('document_id')
    material_type = data.get('material_type')
    content = data.get('content')

    if not document_id or not material_type or not content:
        return jsonify({'error': 'Missing required fields'}), 400

    # Get document information
    document = Document.query.filter_by(document_id=document_id, user_id=current_user.user_id).first()
    if not document:
        return jsonify({'error': 'Document not found'}), 404

    # Create a new study session for this study attempt
    study_session = StudySession(
        user_id=current_user.user_id,
        document_id=document_id,
        session_name=f"Study Session - {document.filename} - {datetime.now().strftime('%Y%m%d_%H%M%S')}"
    )
    db.session.add(study_session)
    db.session.commit()

    # Create new material in this session
    study_material = StudyMaterial(
        user_id=current_user.user_id,
        study_session_id=study_session.session_id,
        material_type=material_type,
        content=json.dumps(content),
        source_documents=[document_id]
    )
    db.session.add(study_material)
    db.session.commit()

    return jsonify({'success': True, 'message': 'Material saved successfully', 'session_id': study_session.session_id})

@app.route('/generate-summary/<int:document_id>')
@login_required
def generate_summary(document_id):
    document = Document.query.filter_by(document_id=document_id, user_id=current_user.user_id).first()
    if not document:
        return jsonify({'error': 'Document not found'}), 404
    
    summary = study_generator.generate_summary(document.document_id)
    
    # Return the generated summary without saving to database
    # The save-study-material route will handle saving with proper session linking
    return jsonify({'summary': summary})

@app.route('/generate-quiz/<int:document_id>')
@login_required
def generate_quiz(document_id):
    document = Document.query.filter_by(document_id=document_id, user_id=current_user.user_id).first()
    if not document:
        return jsonify({'error': 'Document not found'}), 404
    
    quiz = study_generator.create_quiz(document.document_id)
    
    # Return the generated quiz without saving to database
    # The save-study-material route will handle saving with proper session linking
    return jsonify({'quiz': quiz})

@app.route('/generate-flashcards/<int:document_id>')
@login_required
def generate_flashcards(document_id):
    document = Document.query.filter_by(document_id=document_id, user_id=current_user.user_id).first()
    if not document:
        return jsonify({'error': 'Document not found'}), 404
    
    flashcards = study_generator.build_flashcards(document.document_id)
    
    # Return the generated flashcards without saving to database
    # The save-study-material route will handle saving with proper session linking
    return jsonify({'flashcards': flashcards})

@app.route('/generate-concepts/<int:document_id>')
@login_required
def generate_concepts(document_id):
    document = Document.query.filter_by(document_id=document_id, user_id=current_user.user_id).first()
    if not document:
        return jsonify({'error': 'Document not found'}), 404

    concepts = study_generator.extract_key_concepts(document.document_id)

    # Return the generated concepts without saving to database
    # The save-study-material route will handle saving with proper session linking
    return jsonify({'concepts': concepts})

@app.route('/library')
@login_required
def library():
    documents = Document.query.filter_by(user_id=current_user.user_id).all()
    return render_template('library.html', documents=documents)

@app.route('/settings')
@login_required
def settings():
    return render_template('settings.html')

@app.route('/download_document/<int:document_id>')
@login_required
def download_document(document_id):
    """Download the original uploaded document"""
    document = Document.query.filter_by(document_id=document_id, user_id=current_user.user_id).first()
    if not document:
        return jsonify({'error': 'Document not found'}), 404
    
    if not os.path.exists(document.file_path):
        return jsonify({'error': 'File not found on server'}), 404
    
    try:
        return send_file(document.file_path, as_attachment=True, download_name=document.filename)
    except Exception as e:
        return jsonify({'error': f'Download failed: {str(e)}'}), 500

@app.route('/delete_document/<int:document_id>', methods=['DELETE'])
@login_required
def delete_document(document_id):
    """Delete document and all associated data"""
    document = Document.query.filter_by(document_id=document_id, user_id=current_user.user_id).first()
    if not document:
        return jsonify({'error': 'Document not found'}), 404
    
    try:
        # Delete knowledge base entries
        KnowledgeBase.query.filter_by(document_id=document_id).delete()
        
        # Delete study materials that reference this document
        # Since source_documents is JSON, we need to check if the document_id is in the array
        study_materials = StudyMaterial.query.filter_by(user_id=current_user.user_id).all()
        materials_to_delete = []
        
        for material in study_materials:
            if material.source_documents and document_id in material.source_documents:
                materials_to_delete.append(material)
        
        for material in materials_to_delete:
            db.session.delete(material)
        
        # Delete the file from filesystem
        if os.path.exists(document.file_path):
            os.remove(document.file_path)
        
        # Delete the document record
        db.session.delete(document)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Document and all associated data deleted successfully'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Delete failed: {str(e)}'}), 500

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'pdf', 'docx', 'jpg', 'jpeg', 'png', 'bmp', 'tiff'}

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Create uploads directory if it doesn't exist
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)
