import spacy
from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import re
import json
from datetime import datetime
from gemini_integration import GeminiAI

class NLPEngine:
    def __init__(self):
        # Load models
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            # If model not found, download it
            import subprocess
            subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
            self.nlp = spacy.load("en_core_web_sm")
        
        # Load sentence transformer for semantic search
        self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Initialize Gemini AI
        self.gemini_ai = GeminiAI()
        
        # Confidence threshold for responses
        self.confidence_threshold = 0.3
    
    def preprocess_text(self, text):
        """
        Preprocess text for NLP analysis
        """
        doc = self.nlp(text)
        # Remove stopwords and punctuation, lemmatize
        processed_tokens = [
            token.lemma_.lower() 
            for token in doc 
            if not token.is_stop and not token.is_punct and token.is_alpha
        ]
        return ' '.join(processed_tokens)
    
    def generate_embedding(self, text):
        """
        Generate embedding vector for text
        """
        return self.sentence_model.encode([text])[0]
    
    def classify_intent(self, query):
        """
        Classify the intent of a user query
        """
        query_lower = query.lower()
        
        # Define intent patterns
        intent_patterns = {
            'definition': [
                r'what is\s+',
                r'define\s+',
                r'meaning of\s+',
                r'explain\s+'
            ],
            'explanation': [
                r'how does\s+',
                r'how to\s+',
                r'explain\s+',
                r'describe\s+'
            ],
            'comparison': [
                r'difference between\s+',
                r'compare\s+',
                r'vs\s+',
                r'versus\s+'
            ],
            'example': [
                r'example of\s+',
                r'give an example\s+',
                r'show me\s+'
            ],
            'summary': [
                r'summarize\s+',
                r'summary of\s+',
                r'overview of\s+'
            ],
            'step_by_step': [
                r'step by step\s+',
                r'how to solve\s+',
                r'walk me through\s+'
            ]
        }
        
        # Check for intent patterns
        for intent, patterns in intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query_lower):
                    return intent
        
        return 'general'
    
    def search_knowledge_base(self, query_embedding, knowledge_base):
        """
        Search knowledge base for relevant content using semantic similarity
        """
        relevant_chunks = []
        relevance_scores = []
        
        for kb_entry in knowledge_base:
            if kb_entry.processed_content and 'chunks' in kb_entry.processed_content:
                chunks = kb_entry.processed_content['chunks']
                
                for chunk in chunks:
                    chunk_embedding = self.generate_embedding(chunk)
                    similarity = cosine_similarity(
                        [query_embedding], 
                        [chunk_embedding]
                    )[0][0]
                    
                    if similarity > self.confidence_threshold:
                        relevant_chunks.append({
                            'chunk': chunk,
                            'similarity': similarity,
                            'document_id': kb_entry.document_id,
                            'concepts': kb_entry.concepts or []
                        })
                        relevance_scores.append(similarity)
        
        # Sort by relevance score
        relevant_chunks.sort(key=lambda x: x['similarity'], reverse=True)
        
        return relevant_chunks[:5], relevance_scores  # Return top 5 most relevant chunks
    
    def extract_relevant_chunks(self, relevant_chunks, query):
        """
        Extract the most relevant chunks based on the query
        """
        if not relevant_chunks:
            return []
        
        # Use the top chunks (already sorted by relevance)
        return relevant_chunks
    
    def calculate_relevance(self, context_chunks, query_embedding):
        """
        Calculate relevance scores for context chunks
        """
        if not context_chunks:
            return [0.0]
        
        return [chunk['similarity'] for chunk in context_chunks]
    
    def generate_response(self, query, context, intent):
        """
        Generate response using Gemini AI
        """
        if not context:
            return self.generate_fallback_response(query)
        
        # Combine context chunks
        context_text = ' '.join([chunk['chunk'] for chunk in context])
        
        try:
            # Use Gemini AI to generate response based on context
            response = self.gemini_ai.answer_question(query, context_text)
            
            # Add intent-specific formatting
            if intent == 'definition':
                response = f"**Definition:** {response}"
            elif intent == 'example':
                response = f"**Example:** {response}"
            elif intent == 'comparison':
                response = f"**Comparison:** {response}"
            elif intent == 'step_by_step':
                response = f"**Step-by-Step Solution:**\n{response}"
            
            return response
            
        except Exception as e:
            print(f"Error generating response with Gemini: {e}")
            return self.generate_fallback_response(query)
    
    def extract_citations(self, context_chunks):
        """
        Extract citations from relevant chunks
        """
        citations = []
        for chunk in context_chunks:
            citations.append({
                'document_id': chunk['document_id'],
                'relevance_score': chunk['similarity'],
                'key_concepts': chunk['concepts'][:3] if chunk['concepts'] else []
            })
        return citations
    
    def format_response(self, response, citations):
        """
        Format response with citations
        """
        if not citations:
            return response
        
        # Add citation information
        citation_text = "\n\n**Sources:**\n"
        for i, citation in enumerate(citations, 1):
            citation_text += f"{i}. Document {citation['document_id']} "
            citation_text += f"(Relevance: {citation['relevance_score']:.2f})\n"
            
            if citation['key_concepts']:
                citation_text += f"   Key concepts: {', '.join(citation['key_concepts'])}\n"
        
        return response + citation_text
    
    def generate_fallback_response(self, query):
        """
        Generate fallback response when no relevant content is found
        """
        fallback_responses = [
            "I don't have enough information from your uploaded materials to answer that question accurately. Could you upload more relevant documents or rephrase your question?",
            "This topic doesn't appear to be covered in your uploaded materials. Please make sure you've uploaded the relevant course documents.",
            "I couldn't find specific information about this in your course materials. You might want to check if you've uploaded the correct documents or ask your instructor for clarification.",
            "Based on the materials you've provided, I don't have enough context to answer this question. Consider uploading additional course materials that cover this topic."
        ]
        
        import random
        return random.choice(fallback_responses)
    
    def process_user_query(self, user_query, user_id):
        """
        Main method to process user queries
        """
        from models import KnowledgeBase, db
        
        start_time = datetime.now()
        
        try:
            # Get user's knowledge base
            knowledge_base = KnowledgeBase.query.join(
                KnowledgeBase.document
            ).filter(
                KnowledgeBase.document.has(user_id=user_id)
            ).all()
            
            if not knowledge_base:
                return "Please upload some course materials first so I can help you with your questions.", 0.0
            
            # Query analysis phase
            processed_query = self.preprocess_text(user_query)
            query_embedding = self.generate_embedding(user_query)
            intent = self.classify_intent(user_query)
            
            # Knowledge retrieval phase
            relevant_chunks, relevance_scores = self.search_knowledge_base(query_embedding, knowledge_base)
            context_chunks = self.extract_relevant_chunks(relevant_chunks, user_query)
            
            # Response generation phase
            if relevance_scores and max(relevance_scores) > self.confidence_threshold:
                context = context_chunks
                response = self.generate_response(user_query, context, intent)
                citations = self.extract_citations(context_chunks)
                final_response = self.format_response(response, citations)
                relevance_score = max(relevance_scores)
            else:
                final_response = self.generate_fallback_response(user_query)
                relevance_score = 0.0
            
            # Calculate response time
            response_time = (datetime.now() - start_time).total_seconds()
            
            return final_response, relevance_score
            
        except Exception as e:
            print(f"Error processing query: {e}")
            return "I encountered an error while processing your query. Please try again.", 0.0
