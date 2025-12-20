"""
AI Content Generator Service
Just-in-Time content generation using OpenAI for personalized educational lessons
"""

import os
import json
from datetime import datetime
from typing import List, Optional
from openai import AsyncOpenAI
import asyncio
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize OpenAI Client
try:
    client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    OPENAI_AVAILABLE = True
except Exception as e:
    logger.warning(f"OpenAI client initialization failed: {e}")
    OPENAI_AVAILABLE = False


class AIContentGenerator:
    """AI-powered content generation service for educational lessons"""
    
    def __init__(self):
        self.client = client if OPENAI_AVAILABLE else None
        self.available = OPENAI_AVAILABLE
    
    async def generate_concept_lesson(
        self, 
        concept_name: str, 
        domain: str, 
        difficulty: str, 
        related_concepts: Optional[List[str]] = None,
        category: Optional[str] = None,
        detailed_description: Optional[str] = None
    ) -> str:
        """
        Generates a structured educational lesson using OpenAI.
        
        Args:
            concept_name: The concept to teach
            domain: Subject domain (e.g., Computer Science, Mathematics)
            difficulty: Beginner, Intermediate, Advanced
            related_concepts: Related concepts for context
            category: Subcategory within the domain
            detailed_description: Existing description for more context
            
        Returns:
            Generated lesson content in Markdown format
        """
        
        if not self.available or not self.client:
            return self._generate_fallback_content(concept_name, domain, difficulty)
        
        # Construct context-aware prompt
        related_text = ""
        if related_concepts:
            related_text = f"Relate this to: {', '.join(related_concepts)}."
        
        category_text = f" in {category}" if category else ""
        
        # Tailor prompt based on difficulty level
        difficulty_guidance = {
            "beginner": "Use simple language, provide lots of examples, and avoid jargon.",
            "intermediate": "Balance technical accuracy with accessibility, include practical applications.",
            "advanced": "Use precise technical language, include complex examples, and focus on nuances."
        }
        
        difficulty_instructions = difficulty_guidance.get(difficulty.lower(), difficulty_guidance["beginner"])
        
        # Create comprehensive prompt
        prompt = f"""
        You are an expert tutor in {domain}{category_text}. Create a comprehensive, engaging lesson for the concept: "{concept_name}".
        
        Target Audience: {difficulty} level student.
        Instructions: {difficulty_instructions}
        Context: {related_text}
        
        Use the following description for additional context: {detailed_description or 'N/A'}
        
        Format your response in clean Markdown with these exact sections:
        
        # {concept_name}
        
        ## 1. The Big Picture
        [Explain what this concept is and why it matters in 2-3 sentences]
        
        ## 2. Simple Explanation
        [Break down the concept using analogies or simple language]
        
        ## 3. Key Details
        [Bulleted list of 3-5 critical characteristics or components]
        
        ## 4. Real-World Examples
        [3 concrete examples where this concept is used in practice]
        
        ## 5. Why It Matters
        [Explain the practical importance and applications]
        
        ## 6. Common Misconceptions
        [2-3 things people often get wrong about this concept]
        
        Make the content engaging, educational, and appropriate for the specified difficulty level.
        """
        
        try:
            logger.info(f"🤖 Generating AI lesson for: {concept_name} ({difficulty} level)")
            
            # Call OpenAI
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",  # Cost-effective model
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a helpful, clear, and encouraging educational AI assistant. Create engaging, well-structured lessons that help students understand complex concepts."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=1500
            )
            
            generated_content = response.choices[0].message.content
            
            # Add metadata header
            metadata_header = f"""
<!-- Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} -->
<!-- Difficulty: {difficulty} | Domain: {domain} | Model: gpt-4o-mini -->

"""
            
            final_content = metadata_header + generated_content
            
            logger.info(f"✅ Successfully generated lesson for {concept_name}")
            return final_content
            
        except Exception as e:
            logger.error(f"❌ OpenAI Error for {concept_name}: {str(e)}")
            return self._generate_fallback_content(concept_name, domain, difficulty)
    
    def _generate_fallback_content(self, concept_name: str, domain: str, difficulty: str) -> str:
        """
        Generate fallback content when OpenAI is unavailable
        """
        fallback_content = f"""# {concept_name}

## The Big Picture
{concept_name} is an important concept in {domain} that helps us understand and work with complex systems and ideas.

## Simple Explanation
Think of {concept_name.lower()} like a toolkit that provides specific methods and approaches for solving problems in {domain.lower()}.

## Key Details
- **Purpose**: Designed to solve specific types of problems
- **Applications**: Used across various domains within {domain}
- **Benefits**: Provides structured approaches and proven methods
- **Integration**: Works well with other concepts in {domain}

## Real-World Examples
1. **Technology**: Used in software development and system design
2. **Business**: Applied in strategy and decision-making processes
3. **Research**: Employed in academic and scientific investigations
4. **Daily Life**: Present in everyday problem-solving scenarios

## Why It Matters
Understanding {concept_name} helps you approach problems more systematically and develop better solutions in {domain} and beyond.

## Common Misconceptions
- It's only useful in theoretical contexts
- It requires extensive technical background to understand
- It can't be applied to practical, real-world problems

*Note: This is a fallback content template. For the best learning experience, please ensure OpenAI API is configured.*
"""
        return fallback_content
    
    async def generate_practice_questions(
        self,
        concept_name: str,
        difficulty: str,
        question_count: int = 3
    ) -> List[dict]:
        """
        Generate practice questions for a concept
        """
        if not self.available or not self.client:
            return self._generate_fallback_questions(concept_name, difficulty, question_count)
        
        prompt = f"""
        Generate {question_count} practice questions for the concept "{concept_name}" at {difficulty} level.
        
        For each question, provide:
        1. A clear question
        2. Multiple choice options (A, B, C, D)
        3. The correct answer
        4. A brief explanation of why it's correct
        
        Format as JSON array:
        [
          {{
            "question": "Question text",
            "options": ["A) Option 1", "B) Option 2", "C) Option 3", "D) Option 4"],
            "correct_answer": "A",
            "explanation": "Why this is correct"
          }}
        ]
        """
        
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an educational assessment expert. Create clear, relevant practice questions."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=800
            )
            
            content = response.choices[0].message.content
            # Parse JSON response
            try:
                questions = json.loads(content)
                return questions
            except json.JSONDecodeError:
                return self._generate_fallback_questions(concept_name, difficulty, question_count)
                
        except Exception as e:
            logger.error(f"Error generating practice questions: {e}")
            return self._generate_fallback_questions(concept_name, difficulty, question_count)
    
    def _generate_fallback_questions(self, concept_name: str, difficulty: str, count: int) -> List[dict]:
        """Generate fallback questions when OpenAI is unavailable"""
        questions = []
        for i in range(count):
            questions.append({
                "question": f"What is the primary purpose of {concept_name} in its domain?",
                "options": [
                    f"A) To solve specific types of problems in {concept_name.lower()}",
                    "B) To make processes more complicated",
                    "C) To replace human thinking entirely", 
                    "D) To work only in theoretical contexts"
                ],
                "correct_answer": "A",
                "explanation": f"{concept_name} is designed to provide structured approaches for solving specific problems."
            })
        return questions


# Global instance
ai_generator = AIContentGenerator()


# Convenience functions
async def generate_lesson_content(
    concept_name: str,
    domain: str,
    difficulty: str,
    related_concepts: Optional[List[str]] = None,
    category: Optional[str] = None,
    detailed_description: Optional[str] = None
) -> str:
    """Generate lesson content for a concept"""
    return await ai_generator.generate_concept_lesson(
        concept_name=concept_name,
        domain=domain,
        difficulty=difficulty,
        related_concepts=related_concepts,
        category=category,
        detailed_description=detailed_description
    )


async def generate_practice_questions(
    concept_name: str,
    difficulty: str,
    question_count: int = 3
) -> List[dict]:
    """Generate practice questions for a concept"""
    return await ai_generator.generate_practice_questions(
        concept_name=concept_name,
        difficulty=difficulty,
        question_count=question_count
    )