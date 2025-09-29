import json
import random
from typing import List, Dict, Any
from knowledge_manager import KnowledgeManager
from gemini_integration import GeminiAI

class StudyGenerator:
    def __init__(self):
        self.knowledge_manager = KnowledgeManager()
        self.gemini_ai = GeminiAI()
    
    def generate_summary(self, document_id: int) -> str:
        """Generate a summary of the document content using Gemini AI"""
        content = self.knowledge_manager.get_document_content(document_id)
        if not content:
            return "Error: Document content not found"
        
        text = content.get('content', '')
        if not text:
            return "Error: No text content available"
        
        # Use Gemini AI to generate a comprehensive summary
        summary = self.gemini_ai.generate_summary(text)
        return summary
    
    def create_quiz(self, document_id: int, num_questions: int = 5) -> List[Dict[str, Any]]:
        """Generate a quiz from document content using Gemini AI"""
        content = self.knowledge_manager.get_document_content(document_id)
        if not content:
            return [{"error": "Document content not found"}]
        
        text = content.get('content', '')
        if not text:
            return [{"error": "No text content available"}]
        
        # Use Gemini AI to generate quiz questions
        quiz = self.gemini_ai.generate_quiz(text, num_questions)
        return quiz
    
    def build_flashcards(self, document_id: int, num_cards: int = 10) -> List[Dict[str, str]]:
        """Generate flashcards from document content using Gemini AI"""
        content = self.knowledge_manager.get_document_content(document_id)
        if not content:
            return [{"error": "Document content not found"}]
        
        text = content.get('content', '')
        if not text:
            return [{"error": "No text content available"}]
        
        # Use Gemini AI to generate flashcards
        flashcards = self.gemini_ai.generate_flashcards(text, num_cards)
        return flashcards
    
    def explain_concept(self, concept: str, document_id: int = None) -> str:
        """Generate detailed explanation of a concept using Gemini AI"""
        context = ""
        if document_id:
            content = self.knowledge_manager.get_document_content(document_id)
            if content:
                context = content.get('content', '')
        
        # Use Gemini AI to explain the concept
        explanation = self.gemini_ai.explain_concept(concept, context)
        return explanation
    
    def generate_step_by_step_solution(self, problem: str, document_id: int = None) -> str:
        """Generate step-by-step solution using Gemini AI"""
        context = ""
        if document_id:
            content = self.knowledge_manager.get_document_content(document_id)
            if content:
                context = content.get('content', '')
        
        # Use Gemini AI to generate solution
        solution = self.gemini_ai.generate_step_by_step_solution(problem, context)
        return solution
    
    def extract_key_concepts(self, document_id: int, max_concepts: int = 10) -> List[str]:
        """Extract key concepts from document using Gemini AI"""
        content = self.knowledge_manager.get_document_content(document_id)
        if not content:
            return ["Error: Document content not found"]
        
        text = content.get('content', '')
        if not text:
            return ["Error: No text content available"]
        
        # Use Gemini AI to extract key concepts
        concepts = self.gemini_ai.extract_key_concepts(text, max_concepts)
        return concepts
    
    def generate_study_plan(self, document_ids: List[int], study_hours: int = 10) -> Dict[str, Any]:
        """Generate personalized study plan using Gemini AI"""
        topics = []
        
        for doc_id in document_ids:
            content = self.knowledge_manager.get_document_content(doc_id)
            if content:
                # Extract concepts from the document
                concepts = self.gemini_ai.extract_key_concepts(content.get('content', ''), 5)
                topics.extend(concepts)
        
        if not topics:
            return {"error": "No topics found in the provided documents"}
        
        # Use Gemini AI to generate study plan
        study_plan = self.gemini_ai.generate_study_plan(topics, study_hours)
        return study_plan
    
    def answer_question(self, question: str, document_id: int = None) -> str:
        """Answer a specific question using Gemini AI"""
        context = ""
        if document_id:
            content = self.knowledge_manager.get_document_content(document_id)
            if content:
                context = content.get('content', '')
        
        # Use Gemini AI to answer the question
        answer = self.gemini_ai.answer_question(question, context)
        return answer
