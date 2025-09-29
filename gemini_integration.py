import os
import google.generativeai as genai
import json
from typing import List, Dict, Any

class GeminiAI:
    def __init__(self):
        self.api_key = os.environ.get('GEMINI_API_KEY')
        self.model_name = os.environ.get('GEMINI_MODEL', 'gemini-1.0-pro')
        
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")
        
        # Configure the Gemini API
        genai.configure(api_key=self.api_key)
        
        # Try to find a working model
        try:
            self.model = genai.GenerativeModel(self.model_name)
        except Exception as e:
            # If the specified model fails, try common alternatives
            print(f"⚠️ Model {self.model_name} not available, trying alternatives...")
            alternative_models = ['models/gemini-pro', 'models/gemini-1.0-pro', 'gemini-pro']
            for alt_model in alternative_models:
                try:
                    self.model = genai.GenerativeModel(alt_model)
                    self.model_name = alt_model
                    print(f"✅ Using alternative model: {alt_model}")
                    break
                except:
                    continue
            else:
                # If no alternatives work, raise the original error
                raise e
    
    def generate_summary(self, content: str, max_length: int = 500) -> str:
        """Generate a concise summary of the provided content"""
        prompt = f"""
        Please provide a comprehensive summary of the following academic content. 
        Focus on key concepts, main ideas, and important details.
        Keep the summary under {max_length} words.
        
        Content:
        {content}
        
        Summary:
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            return f"Error generating summary: {str(e)}"
    
    def generate_quiz(self, content: str, num_questions: int = 5) -> List[Dict[str, Any]]:
        """Generate a quiz with multiple choice questions from the content"""
        prompt = f"""
        Based on the following academic content, create {num_questions} multiple choice questions.
        Each question should have 4 options (A, B, C, D) with exactly one correct answer.
        Format the response as a JSON array with the following structure for each question:
        {{
            "question": "the question text",
            "options": ["option A", "option B", "option C", "option D"],
            "answer": "correct option text",
            "explanation": "brief explanation of why this is correct"
        }}

        Content:
        {content[:8000]}

        Questions:
        """

        try:
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()

            # Clean the response text - remove markdown formatting if present
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()

            # Parse the JSON response
            questions = json.loads(response_text)

            # Ensure it's a list
            if not isinstance(questions, list):
                questions = [questions]

            # Validate the structure of each question
            validated_questions = []
            for question in questions:
                if isinstance(question, dict) and "question" in question and "options" in question:
                    validated_questions.append(question)

            return validated_questions if validated_questions else [{"error": "No valid questions generated"}]

        except Exception as e:
            return [{"error": f"Failed to generate quiz: {str(e)}"}]
    
    def generate_flashcards(self, content: str, num_cards: int = 10) -> List[Dict[str, str]]:
        """Generate flashcards (question-answer pairs) from the content"""
        prompt = f"""
        Based on the following academic content, create {num_cards} flashcards.
        Each flashcard should have a clear question on the front and a concise answer on the back.
        Focus on key concepts, definitions, and important facts.
        Format the response as a JSON array with the following structure for each flashcard:
        {{
            "front": "the question text",
            "back": "the answer text"
        }}

        Content:
        {content[:8000]}

        Flashcards:
        """

        try:
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()

            # Clean the response text - remove markdown formatting if present
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()

            # Parse the JSON response
            flashcards = json.loads(response_text)

            # Ensure it's a list
            if not isinstance(flashcards, list):
                flashcards = [flashcards]

            # Validate the structure of each flashcard
            validated_flashcards = []
            for card in flashcards:
                if isinstance(card, dict) and "front" in card and "back" in card:
                    validated_flashcards.append(card)

            return validated_flashcards if validated_flashcards else [{"error": "No valid flashcards generated"}]

        except Exception as e:
            return [{"error": f"Failed to generate flashcards: {str(e)}"}]
    
    def explain_concept(self, concept: str, context: str = "") -> str:
        """Provide a detailed explanation of a specific concept"""
        prompt = f"""
        Please provide a clear and comprehensive explanation of the concept: "{concept}"
        {f"in the context of: {context}" if context else ""}
        
        Include:
        1. Definition
        2. Key characteristics
        3. Examples if applicable
        4. Importance/relevance
        
        Explanation:
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            return f"Error explaining concept: {str(e)}"
    
    def generate_step_by_step_solution(self, problem: str, context: str = "") -> str:
        """Generate a step-by-step solution to a problem"""
        prompt = f"""
        Please provide a step-by-step solution to the following problem:
        {problem}
        
        {f"Context: {context}" if context else ""}
        
        Format the solution with clear steps and explanations for each step.
        Make it easy to follow and understand.
        
        Solution:
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            return f"Error generating solution: {str(e)}"
    
    def answer_question(self, question: str, context: str = "") -> str:
        """Answer a specific question based on the provided context"""
        prompt = f"""
        Please provide a comprehensive and well-structured answer to the following question based on the provided context. Format your response with proper English formatting including:

        - Clear paragraphs with proper spacing
        - Appropriate punctuation and grammar
        - Logical structure with headings and subheadings where appropriate
        - Bullet points or numbered lists for key points
        - Clear topic sentences and transitions
        - Professional academic tone

        Question: {question}
        
        Context: {context}
        
        If the context doesn't contain enough information to answer the question fully, please indicate that and provide the best answer possible based on general knowledge while maintaining the same formatting standards.
        
        Answer:
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            return f"Error answering question: {str(e)}"
    
    def extract_key_concepts(self, content: str, max_concepts: int = 10) -> List[str]:
        """Extract key concepts from the content"""
        prompt = f"""
        Extract the {max_concepts} most important concepts from the following academic content.
        Return the concepts as a JSON array of strings.

        Content:
        {content[:8000]}

        Concepts (JSON array):
        """

        try:
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()

            # Clean the response text - remove markdown formatting if present
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()

            # Try to parse the JSON response
            concepts = json.loads(response_text)

            # Ensure it's a list
            if isinstance(concepts, list):
                return concepts
            else:
                # If it's not a list, try to extract concepts from the text
                return [concept.strip() for concept in response_text.split('\n') if concept.strip() and not concept.startswith('[') and not concept.startswith(']')][:max_concepts]

        except Exception as e:
            # Return a more user-friendly error message
            return [f"Error extracting concepts: {str(e)}"]
    
    def generate_study_plan(self, topics: List[str], study_hours: int = 10) -> Dict[str, Any]:
        """Generate a personalized study plan"""
        topics_str = ", ".join(topics)
        prompt = f"""
        Create a comprehensive study plan for the following topics: {topics_str}
        Total available study time: {study_hours} hours
        
        Format the response as JSON with the following structure:
        {{
            "total_hours": {study_hours},
            "topics": [
                {{
                    "topic": "topic name",
                    "hours": 2,
                    "activities": ["reading", "practice problems", "review"],
                    "resources": ["textbook chapter", "online videos"]
                }}
            ],
            "schedule": [
                {{
                    "day": "Day 1",
                    "topics": ["topic1", "topic2"],
                    "duration": "2 hours"
                }}
            ],
            "tips": ["study tip 1", "study tip 2"]
        }}
        
        Study Plan:
        """
        
        try:
            response = self.model.generate_content(prompt)
            study_plan = json.loads(response.text.strip())
            return study_plan
        except Exception as e:
            return {"error": f"Failed to generate study plan: {str(e)}"}
