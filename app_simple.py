#!/usr/bin/env python3
"""
Simplified AI Tutor Agent - Basic version without advanced NLP dependencies
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from datetime import datetime
import json

from models import db, User, Document, KnowledgeBase, ChatSession, QueryHistory, StudyMaterial

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///aitutor.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

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
        if 'file' not in request.files:
            return jsonify({'error': 'No file selected'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            # Create uploads directory if it doesn't exist
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            file.save(file_path)
            
            # Create document record
            document = Document(
                user_id=current_user.user_id,
                filename=filename,
                file_path=file_path,
                file_type=file.filename.rsplit('.', 1)[1].lower(),
                processing_status='completed'  # Simplified for demo
            )
            db.session.add(document)
            db.session.commit()
            
            return jsonify({'message': 'File uploaded successfully', 'document_id': document.document_id})
        
        return jsonify({'error': 'Invalid file type'}), 400
    
    return render_template('upload.html')

@app.route('/chat', methods=['GET', 'POST'])
@login_required
def chat():
    if request.method == 'POST':
        user_query = request.json.get('query')
        if not user_query:
            return jsonify({'error': 'No query provided'}), 400
        
        # Get or create chat session
        chat_session = ChatSession.query.filter_by(
            user_id=current_user.user_id,
            session_end=None
        ).first()
        
        if not chat_session:
            chat_session = ChatSession(user_id=current_user.user_id)
            db.session.add(chat_session)
            db.session.commit()
        
        # Simple response generation (demo mode)
        response = f"I received your question: '{user_query}'. This is a demo response. In the full version, I would analyze your uploaded documents to provide specific answers."
        relevance_score = 0.8
        
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
            'timestamp': datetime.now().isoformat()
        })
    
    return render_template('chat.html')

@app.route('/study-tools')
@login_required
def study_tools():
    materials = StudyMaterial.query.filter_by(user_id=current_user.user_id).all()
    return render_template('study_tools.html', materials=materials)

@app.route('/generate-summary/<int:document_id>')
@login_required
def generate_summary(document_id):
    document = Document.query.filter_by(document_id=document_id, user_id=current_user.user_id).first()
    if not document:
        return jsonify({'error': 'Document not found'}), 404
    
    # Simple demo summary
    summary = f"This is a demo summary for document: {document.filename}. In the full version, this would be generated using NLP techniques to extract key points from your uploaded content."
    
    # Save study material
    study_material = StudyMaterial(
        user_id=current_user.user_id,
        material_type='summary',
        content=json.dumps({'summary': summary}),
        source_documents=[document_id]
    )
    db.session.add(study_material)
    db.session.commit()
    
    return jsonify({'summary': summary, 'material_id': study_material.material_id})

@app.route('/generate-quiz/<int:document_id>')
@login_required
def generate_quiz(document_id):
    document = Document.query.filter_by(document_id=document_id, user_id=current_user.user_id).first()
    if not document:
        return jsonify({'error': 'Document not found'}), 404
    
    # Simple demo quiz
    quiz = {
        'title': f'Quiz for {document.filename}',
        'questions': [
            {
                'question': 'What is the main topic of this document?',
                'options': ['Topic A', 'Topic B', 'Topic C', 'Topic D'],
                'correct_answer': 0
            },
            {
                'question': 'What would be a key concept from this document?',
                'options': ['Concept 1', 'Concept 2', 'Concept 3', 'Concept 4'],
                'correct_answer': 1
            }
        ]
    }
    
    # Save study material
    study_material = StudyMaterial(
        user_id=current_user.user_id,
        material_type='quiz',
        content=json.dumps(quiz),
        source_documents=[document_id]
    )
    db.session.add(study_material)
    db.session.commit()
    
    return jsonify({'quiz': quiz, 'material_id': study_material.material_id})

@app.route('/library')
@login_required
def library():
    documents = Document.query.filter_by(user_id=current_user.user_id).all()
    return render_template('library.html', documents=documents)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'pdf', 'docx'}

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("🎉 AI Tutor Agent is starting...")
        print("📚 Database initialized successfully")
        print("🌐 Application will be available at: http://localhost:5000")
        print("💡 You can now register an account and test the basic functionality")
    app.run(debug=True, host='0.0.0.0', port=5000)
