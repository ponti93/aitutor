from app import app, db
from models import Document, KnowledgeBase
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def show_document_storage():
    """Show where document processing details are stored"""
    with app.app_context():
        print("📚 DOCUMENT PROCESSING STORAGE LOCATIONS")
        print("=" * 80)
        
        # Get all documents
        documents = Document.query.all()
        
        if not documents:
            print("❌ No documents found in the database")
            return
        
        for document in documents:
            print(f"\n📄 Document: {document.filename}")
            print(f"   📍 Document Table:")
            print(f"      - Document ID: {document.document_id}")
            print(f"      - File Type: {document.file_type}")
            print(f"      - Upload Date: {document.upload_date}")
            print(f"      - Processing Status: {document.processing_status}")
            print(f"      - File Path: {document.file_path}")
            
            if document.document_metadata:
                print(f"      - Metadata: {document.document_metadata}")
            
            # Get knowledge base entries for this document
            knowledge_entries = KnowledgeBase.query.filter_by(document_id=document.document_id).all()
            
            if knowledge_entries:
                print(f"   🧠 Knowledge Base Table:")
                for kb in knowledge_entries:
                    print(f"      - KB ID: {kb.kb_id}")
                    print(f"      - Content Length: {len(kb.content_text)} characters")
                    print(f"      - Concepts: {kb.concepts}")
                    print(f"      - Keywords: {kb.keywords}")
                    print(f"      - Created At: {kb.created_at}")
                    
                    if kb.processed_content:
                        print(f"      - Processed Content Structure:")
                        if 'chunks' in kb.processed_content:
                            print(f"         - Chunks: {len(kb.processed_content['chunks'])}")
                        if 'concepts' in kb.processed_content:
                            print(f"         - Concepts: {len(kb.processed_content['concepts'])}")
                        if 'structure' in kb.processed_content:
                            structure = kb.processed_content['structure']
                            if 'headings' in structure:
                                print(f"         - Headings: {len(structure['headings'])}")
                            if 'paragraphs' in structure:
                                print(f"         - Paragraphs: {len(structure['paragraphs'])}")
            else:
                print(f"   ❌ No knowledge base entries found for this document")
            
            print("-" * 80)

def show_sample_content():
    """Show sample of processed content"""
    with app.app_context():
        print("\n📖 SAMPLE PROCESSED CONTENT")
        print("=" * 80)
        
        # Get first knowledge base entry
        kb_entry = KnowledgeBase.query.first()
        
        if kb_entry:
            print(f"📄 Document: {kb_entry.document.filename}")
            print(f"📝 Content Preview (first 500 chars):")
            print(f"   {kb_entry.content_text[:500]}...")
            
            if kb_entry.processed_content:
                print(f"\n🔧 Processed Data Structure:")
                print(f"   - Word Count: {kb_entry.processed_content.get('word_count', 'N/A')}")
                print(f"   - Character Count: {kb_entry.processed_content.get('character_count', 'N/A')}")
                
                if 'chunks' in kb_entry.processed_content:
                    chunks = kb_entry.processed_content['chunks']
                    print(f"   - Number of Chunks: {len(chunks)}")
                    if chunks:
                        print(f"   - First Chunk Preview: {chunks[0][:200]}...")
                
                if 'concepts' in kb_entry.processed_content:
                    concepts = kb_entry.processed_content['concepts']
                    print(f"   - Extracted Concepts: {concepts[:10]}...")
                
                if 'structure' in kb_entry.processed_content:
                    structure = kb_entry.processed_content['structure']
                    if 'headings' in structure and structure['headings']:
                        print(f"   - Sample Headings: {structure['headings'][:3]}")
        else:
            print("❌ No knowledge base entries found")

if __name__ == '__main__':
    show_document_storage()
    show_sample_content()
