import psycopg2
import json
import os
from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from rank_bm25 import BM25Okapi
import nltk
from nltk.tokenize import word_tokenize
import re

class KnowledgeManager:
    def __init__(self, db_url=None):
        self.db_url = db_url or os.environ.get('DATABASE_URL', 'postgresql://postgres:incorrect@localhost/aitutor')
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.bm25_index = None
        self.corpus_tokens = []
        self.corpus_documents = []
        self._init_database()
    
    def _get_connection(self):
        """Get PostgreSQL database connection"""
        return psycopg2.connect(self.db_url)
    
    def _init_database(self):
        """Initialize the knowledge base database - using existing SQLAlchemy tables"""
        # The tables are already created by SQLAlchemy models
        # We'll use the existing KnowledgeBase table for storing processed content
        pass
    
    def add_document(self, user_id, filename, file_type, processed_data):
        """Add a processed document to the knowledge base"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Store document
        cursor.execute('''
            INSERT INTO documents (user_id, filename, file_type, content, processed_content, concepts, keywords)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        ''', (
            user_id,
            filename,
            file_type,
            processed_data['content'],
            json.dumps(processed_data),
            json.dumps(processed_data['concepts']),
            json.dumps(processed_data['concepts'])  # Using concepts as keywords for now
        ))
        
        document_id = cursor.fetchone()[0]
        
        # Create embeddings for each chunk
        for i, chunk in enumerate(processed_data['chunks']):
            embedding = self.embedding_model.encode(chunk)
            embedding_blob = embedding.tobytes()
            
            cursor.execute('''
                INSERT INTO embeddings (document_id, chunk_index, chunk_text, embedding)
                VALUES (%s, %s, %s, %s)
            ''', (document_id, i, chunk, embedding_blob))
        
        conn.commit()
        conn.close()
        
        # Rebuild BM25 index
        self._rebuild_bm25_index()
        
        return document_id
    
    def _rebuild_bm25_index(self):
        """Rebuild the BM25 index with all documents"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Get all chunks for BM25
        cursor.execute('SELECT chunk_text FROM embeddings')
        chunks = [row[0] for row in cursor.fetchall()]
        
        # Tokenize chunks for BM25
        self.corpus_tokens = [self._tokenize_text(chunk) for chunk in chunks]
        self.corpus_documents = chunks
        
        # Create BM25 index
        if self.corpus_tokens:
            self.bm25_index = BM25Okapi(self.corpus_tokens)
        
        conn.close()
    
    def _tokenize_text(self, text):
        """Tokenize text for BM25 processing"""
        # Simple tokenization - can be enhanced with stemming/lemmatization
        tokens = word_tokenize(text.lower())
        # Remove punctuation and short tokens
        tokens = [token for token in tokens if token.isalnum() and len(token) > 2]
        return tokens
    
    def search_knowledge(self, query, user_id=None, top_k=5, method='hybrid'):
        """
        Search the knowledge base using hybrid approach (BM25 + semantic search)
        
        Args:
            query: Search query string
            user_id: Optional user ID to filter results
            top_k: Number of top results to return
            method: Search method ('bm25', 'semantic', 'hybrid')
        """
        if method == 'bm25':
            return self._bm25_search(query, user_id, top_k)
        elif method == 'semantic':
            return self._semantic_search(query, user_id, top_k)
        else:  # hybrid
            return self._hybrid_search(query, user_id, top_k)
    
    def _bm25_search(self, query, user_id, top_k):
        """Search using BM25 algorithm"""
        if not self.bm25_index:
            return []
        
        # Tokenize query
        query_tokens = self._tokenize_text(query)
        
        # Get BM25 scores
        scores = self.bm25_index.get_scores(query_tokens)
        
        # Get top results
        top_indices = np.argsort(scores)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            if scores[idx] > 0:  # Only include relevant results
                results.append({
                    'chunk_text': self.corpus_documents[idx],
                    'score': float(scores[idx]),
                    'method': 'bm25',
                    'source_document': self._get_document_info(idx)
                })
        
        return results
    
    def _semantic_search(self, query, user_id, top_k):
        """Search using semantic similarity"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Get query embedding
        query_embedding = self.embedding_model.encode(query)
        
        # Get all embeddings
        if user_id:
            cursor.execute('''
                SELECT e.id, e.chunk_text, e.embedding, d.filename 
                FROM embeddings e 
                JOIN documents d ON e.document_id = d.id 
                WHERE d.user_id = %s
            ''', (user_id,))
        else:
            cursor.execute('''
                SELECT e.id, e.chunk_text, e.embedding, d.filename 
                FROM embeddings e 
                JOIN documents d ON e.document_id = d.id
            ''')
        
        results = []
        for row in cursor.fetchall():
            chunk_id, chunk_text, embedding_blob, filename = row
            
            # Convert blob back to numpy array
            embedding = np.frombuffer(embedding_blob, dtype=np.float32)
            
            # Calculate similarity
            similarity = cosine_similarity([query_embedding], [embedding])[0][0]
            
            results.append({
                'chunk_text': chunk_text,
                'score': float(similarity),
                'method': 'semantic',
                'source_document': filename
            })
        
        conn.close()
        
        # Sort by score and return top_k
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:top_k]
    
    def _hybrid_search(self, query, user_id, top_k):
        """Combine BM25 and semantic search for better results"""
        # Get results from both methods
        bm25_results = self._bm25_search(query, user_id, top_k * 2)
        semantic_results = self._semantic_search(query, user_id, top_k * 2)
        
        # Normalize scores
        if bm25_results:
            bm25_scores = [r['score'] for r in bm25_results]
            max_bm25 = max(bm25_scores) if bm25_scores else 1
            for result in bm25_results:
                result['normalized_score'] = result['score'] / max_bm25
        
        if semantic_results:
            semantic_scores = [r['score'] for r in semantic_results]
            max_semantic = max(semantic_scores) if semantic_scores else 1
            for result in semantic_results:
                result['normalized_score'] = result['score'] / max_semantic
        
        # Combine results
        combined_results = {}
        
        # Add BM25 results
        for result in bm25_results:
            key = result['chunk_text'][:100]  # Use text as key (truncated)
            if key not in combined_results:
                combined_results[key] = result
                combined_results[key]['combined_score'] = result['normalized_score'] * 0.4  # BM25 weight
        
        # Add semantic results
        for result in semantic_results:
            key = result['chunk_text'][:100]
            if key in combined_results:
                combined_results[key]['combined_score'] += result['normalized_score'] * 0.6  # Semantic weight
            else:
                combined_results[key] = result
                combined_results[key]['combined_score'] = result['normalized_score'] * 0.6
        
        # Convert to list and sort by combined score
        final_results = list(combined_results.values())
        final_results.sort(key=lambda x: x['combined_score'], reverse=True)
        
        return final_results[:top_k]
    
    def _get_document_info(self, chunk_index):
        """Get document information for a chunk index"""
        # This is a simplified implementation
        # In a real system, you'd want to track which document each chunk belongs to
        return "Unknown Document"
    
    def get_user_documents(self, user_id):
        """Get all documents for a specific user"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, filename, file_type, created_at 
            FROM documents 
            WHERE user_id = %s 
            ORDER BY created_at DESC
        ''', (user_id,))
        
        documents = []
        for row in cursor.fetchall():
            doc_id, filename, file_type, created_at = row
            documents.append({
                'id': doc_id,
                'filename': filename,
                'file_type': file_type,
                'created_at': created_at
            })
        
        conn.close()
        return documents
    
    def get_document_content(self, document_id):
        """Get processed content for a specific document"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT processed_content FROM knowledge_base WHERE document_id = %s', (document_id,))
        row = cursor.fetchone()
        
        conn.close()
        
        if row:
            return row[0]  # Already a JSON object, no need to parse
        return None
    
    def log_user_query(self, user_id, query_text, response_text, relevance_score):
        """Log user queries for learning and analytics"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO user_queries (user_id, query_text, response_text, relevance_score)
            VALUES (%s, %s, %s, %s)
        ''', (user_id, query_text, response_text, relevance_score))
        
        conn.commit()
        conn.close()
    
    def get_user_stats(self, user_id):
        """Get statistics for a user"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Document count
        cursor.execute('SELECT COUNT(*) FROM documents WHERE user_id = %s', (user_id,))
        doc_count = cursor.fetchone()[0]
        
        # Query count
        cursor.execute('SELECT COUNT(*) FROM user_queries WHERE user_id = %s', (user_id,))
        query_count = cursor.fetchone()[0]
        
        # Average relevance score
        cursor.execute('SELECT AVG(relevance_score) FROM user_queries WHERE user_id = %s', (user_id,))
        avg_score = cursor.fetchone()[0] or 0
        
        conn.close()
        
        return {
            'document_count': doc_count,
            'query_count': query_count,
            'average_relevance_score': round(avg_score, 2)
        }
