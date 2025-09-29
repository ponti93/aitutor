# AI Tutor Agent

An intelligent, AI-powered tutoring system designed to provide personalized academic support for undergraduate students by processing their course materials and offering context-aware assistance.

## Project Overview

Based on the comprehensive research and design documents provided, this system implements a complete AI Tutor Agent with the following key features:

### Core Capabilities

1. **Intelligent Content Processing**
   - PDF and DOCX document processing
   - Automatic text extraction and cleaning
   - Key concept identification
   - Document structure analysis

2. **Natural Language Understanding**
   - Query intent classification
   - Semantic search capabilities
   - Context-aware response generation
   - Citation and source tracking

3. **Automated Study Tools**
   - Document summarization
   - Quiz generation
   - Flashcard creation
   - Concept explanations
   - Reading complexity analysis

4. **Personalized Learning Experience**
   - Course-specific knowledge base
   - Individual user profiles
   - Learning progress tracking
   - Adaptive response generation

## System Architecture

### Five-Layer Architecture

1. **Presentation Layer**
   - Responsive web interface
   - Real-time chat interface
   - File upload functionality
   - Dashboard and analytics

2. **Application Layer**
   - User authentication and session management
   - Query processing logic
   - Study material generation
   - User interaction logging

3. **Processing Layer**
   - Natural Language Processing engine
   - Content extraction algorithms
   - Text summarization
   - Question generation

4. **Data Layer**
   - PostgreSQL database
   - Knowledge base storage
   - User profiles and history
   - Document metadata

5. **Integration Layer**
   - API communication
   - File processing utilities
   - External library integrations

## Installation & Setup

### Prerequisites

- Python 3.9+
- PostgreSQL 13+
- Git

### Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd aitutor
   ```

2. **Set up environment**
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements_simple.txt
   ```

4. **Set up database**
   ```bash
   # Create PostgreSQL database named 'aitutor'
   # Update DATABASE_URL in .env file
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

6. **Access the application**
   ```
   Open http://localhost:5000 in your browser
   ```

## Database Schema

### Core Tables

- **Users**: User accounts and preferences
- **Documents**: Uploaded course materials
- **Knowledge_Base**: Processed content and concepts
- **Chat_Sessions**: User interaction sessions
- **Query_History**: Individual queries and responses
- **Study_Materials**: Generated learning aids

## Key Modules

### 1. Content Processor (`content_processor.py`)
- PDF and DOCX text extraction
- Text cleaning and preprocessing
- Concept extraction using NLP
- Document structure analysis

### 2. NLP Engine (`nlp_engine.py`)
- Query intent classification
- Semantic similarity search
- Response generation
- Citation extraction

### 3. Knowledge Manager (`knowledge_manager.py`)
- Knowledge base construction
- Semantic search capabilities
- User knowledge statistics
- Index management

### 4. Study Generator (`study_generator.py`)
- Automatic summarization
- Quiz creation
- Flashcard generation
- Reading complexity analysis

## API Endpoints

### Authentication
- `GET/POST /register` - User registration
- `GET/POST /login` - User login
- `GET /logout` - User logout

### Core Functionality
- `GET /` - Landing page
- `GET /dashboard` - User dashboard
- `GET/POST /upload` - Document upload
- `GET/POST /chat` - AI tutor chat interface
- `GET /study-tools` - Study materials access
- `GET /library` - Document library

### Study Tools
- `GET /generate-summary/<document_id>` - Generate document summary
- `GET /generate-quiz/<document_id>` - Create quiz from document
- `GET /generate-flashcards/<document_id>` - Build flashcards

## Configuration

### Environment Variables

- `DATABASE_URL` - PostgreSQL connection string
- `SECRET_KEY` - Flask application secret
- `UPLOAD_FOLDER` - File upload directory
- `MAX_CONTENT_LENGTH` - Maximum file size (50MB)

### File Upload

- Supported formats: PDF, DOCX
- Maximum file size: 50MB
- Automatic text extraction and processing
- Secure file storage

## Usage Guide

### 1. Getting Started
1. Register a new account
2. Upload your course materials (PDF/DOCX)
3. Wait for processing completion
4. Start interacting with the AI tutor

### 2. Uploading Materials
- Use the drag-and-drop interface
- Upload multiple related documents
- Organize by course or subject
- Monitor processing status

### 3. Chatting with AI Tutor
- Ask questions about your course content
- Get context-aware responses
- View citations and sources
- Track conversation history

### 4. Using Study Tools
- Generate summaries of uploaded documents
- Create practice quizzes
- Build flashcards for key concepts
- Analyze document complexity

## Technical Implementation

### Object-Oriented Design
The system follows Object-Oriented Analysis and Design Methodology (OOADM) with:
- Modular architecture
- Clear separation of concerns
- Reusable components
- Scalable design patterns

### Security Features
- Password hashing with Werkzeug
- Session management with Flask-Login
- File upload validation
- SQL injection prevention

### Performance Considerations
- Efficient text processing
- Semantic search optimization
- Database indexing
- Asynchronous processing support

## Development Roadmap

### Phase 1: Core MVP (Current)
- Basic document processing
- Simple Q&A functionality
- Essential study tools
- User authentication

### Phase 2: Enhanced Features
- Advanced NLP models
- Real-time collaboration
- Mobile application
- Integration with LMS

### Phase 3: Production Ready
- Scalable deployment
- Advanced analytics
- Multi-language support
- Enterprise features

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is developed as part of academic research. Please refer to the original research documents for licensing information.

## Support

For technical support or questions about implementation, please refer to the system documentation or contact the development team.

---

**Built with ❤️ for enhancing student learning experiences through AI technology**
