import re
import json
from datetime import datetime
from gemini_integration import GeminiAI

class NLPEngineSimple:
    def __init__(self):
        # Initialize Gemini AI
        self.gemini_ai = GeminiAI()
        
        # Confidence threshold for responses
        self.confidence_threshold = 0.3
    
    def preprocess_text(self, text):
        """
        Simple text preprocessing
        """
        # Basic cleaning
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[^\w\s.,!?;:]', '', text)
        return text.strip()
    
    def classify_intent(self, query):
        """
        Simple intent classification using keyword matching
        """
        query_lower = query.lower()
        
        # Define intent keywords
        intent_keywords = {
            'definition': ['what is', 'define', 'meaning of', 'explain'],
            'explanation': ['how does', 'how to', 'explain', 'describe'],
            'comparison': ['difference between', 'compare', 'vs', 'versus'],
            'example': ['example of', 'give an example', 'show me'],
            'summary': ['summarize', 'summary of', 'overview of'],
            'step_by_step': ['step by step', 'how to solve', 'walk me through']
        }
        
        # Check for intent keywords
        for intent, keywords in intent_keywords.items():
            for keyword in keywords:
                if keyword in query_lower:
                    return intent
        
        return 'general'
    
    def search_knowledge_base(self, query, knowledge_base):
        """
        Simple keyword-based search in knowledge base
        """
        relevant_chunks = []
        relevance_scores = []
        
        # Extract keywords from query
        query_words = set(re.findall(r'\b\w+\b', query.lower()))
        
        for kb_entry in knowledge_base:
            if kb_entry.processed_content and 'chunks' in kb_entry.processed_content:
                chunks = kb_entry.processed_content['chunks']
                
                for chunk in chunks:
                    # Simple keyword matching
                    chunk_words = set(re.findall(r'\b\w+\b', chunk.lower()))
                    common_words = query_words.intersection(chunk_words)
                    
                    if common_words:
                        similarity = len(common_words) / len(query_words)
                        
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
    
    def calculate_relevance(self, context_chunks, query):
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
        Format response (citations are now handled internally, not shown to users)
        """
        # Return the response without citations for cleaner user experience
        return response
    
    def generate_fallback_response(self, query):
        """
        Generate helpful fallback response when no relevant content is found
        """
        query_lower = query.lower().strip()
        
        # Handle greetings and simple queries
        if query_lower in ['hi', 'hello', 'hey', 'hi there', 'hello there']:
            return "Hello! I'm your AI Tutor. I can help you understand your course materials. Try asking me specific questions about the content you've uploaded, like:\n\n• \"What are the main topics in my document?\"\n• \"Explain [specific concept] from my materials\"\n• \"Summarize the key points\"\n• \"What should I focus on for studying?\""
        
        # Handle very short or vague queries
        if len(query_lower.split()) <= 2:
            return "I'd love to help! Could you be more specific about what you'd like to know from your course materials? For example:\n\n• Ask about specific topics or concepts\n• Request a summary of key points\n• Ask for explanations of difficult concepts\n• Request study guidance"
        
        # General fallback with helpful suggestions
        return f"I couldn't find specific information about \"{query}\" in your uploaded materials. Here are some ways I can help you:\n\n📚 **Ask about specific topics** from your documents\n📖 **Request summaries** of key concepts\n🎯 **Ask for explanations** of difficult topics\n📝 **Get study guidance** and focus areas\n\nTry rephrasing your question or ask about specific concepts from your course materials!"
    
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
            intent = self.classify_intent(user_query)
            
            # Knowledge retrieval phase
            relevant_chunks, relevance_scores = self.search_knowledge_base(user_query, knowledge_base)
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
    
    def process_user_query_with_document(self, user_query, user_id, document_id):
        """
        Process user queries for a specific document
        """
        from models import KnowledgeBase, Document, db
        
        start_time = datetime.now()
        
        try:
            # Get specific document
            document = Document.query.filter_by(document_id=document_id, user_id=user_id).first()
            if not document:
                return "Document not found. Please select a valid document.", 0.0
            
            # Get knowledge base for this specific document
            knowledge_base = KnowledgeBase.query.filter_by(document_id=document_id).all()
            if not knowledge_base:
                return f"The document '{document.filename}' has not been processed yet. Please wait for processing to complete or re-upload the document.", 0.0
            
            # Query analysis phase
            processed_query = self.preprocess_text(user_query)
            intent = self.classify_intent(user_query)
            
            # Knowledge retrieval phase
            relevant_chunks, relevance_scores = self.search_knowledge_base(user_query, knowledge_base)
            context_chunks = self.extract_relevant_chunks(relevant_chunks, user_query)
            
            # Response generation phase
            if relevance_scores and max(relevance_scores) > self.confidence_threshold:
                context = context_chunks
                response = self.generate_response(user_query, context, intent)
                citations = self.extract_citations(context_chunks)
                final_response = self.format_response(response, citations)
                relevance_score = max(relevance_scores)
            else:
                final_response = f"I couldn't find specific information about \"{user_query}\" in the document '{document.filename}'. Try asking about topics like: {', '.join(knowledge_base[0].concepts[:5]) if knowledge_base[0].concepts else 'key concepts from your document'}"
                relevance_score = 0.0
            
            # Calculate response time
            response_time = (datetime.now() - start_time).total_seconds()
            
            return final_response, relevance_score
            
        except Exception as e:
            print(f"Error processing query with document: {e}")
            return "I encountered an error while processing your query. Please try again.", 0.0
