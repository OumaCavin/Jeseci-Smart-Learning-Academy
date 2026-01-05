#!/usr/bin/env python3
"""
AI Code Intelligence Service
AI-powered code analysis, explanations, and suggestions for the JAC Code Editor

This module provides:
- Code analysis (security, performance, bugs, best practices)
- Code explanation and documentation
- Automated fix suggestions
- Conversational AI for code questions

Author: Jeseci Development Team
"""

import os
import json
import asyncio
import aiohttp
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum

# Import centralized logging configuration
from logger_config import logger

# Get OpenAI API key from environment
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Check if OpenAI is available
OPENAI_AVAILABLE = OPENAI_API_KEY and not OPENAI_API_KEY.startswith("sk-proj-placeholder")


class AnalysisType(str, Enum):
    """Types of code analysis"""
    SECURITY = "security"
    PERFORMANCE = "performance"
    BUG = "bug"
    BEST_PRACTICE = "best_practice"
    STYLE = "style"
    COMPREHENSIVE = "comprehensive"


class Severity(str, Enum):
    """Issue severity levels"""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class CodeIssue:
    """Represents a code issue found during analysis"""
    id: str
    type: AnalysisType
    severity: Severity
    line: int
    column: int
    message: str
    explanation: str
    suggestion: str
    code_diff: Optional[Dict[str, str]] = None


@dataclass
class CodeAnalysisResult:
    """Result of code analysis"""
    success: bool
    issues: List[CodeIssue]
    metrics: Dict[str, Any]
    summary: str
    error: Optional[str] = None


@dataclass
class AIChatMessage:
    """Represents a chat message"""
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"))


class AICodeAssistant:
    """AI-powered code assistant for the JAC Code Editor"""

    def __init__(self):
        self.api_key = OPENAI_API_KEY
        self.available = OPENAI_AVAILABLE
        self.base_url = "https://api.openai.com/v1"
        self.chat_history: List[AIChatMessage] = []
        self.model = "gpt-4o-mini"

    async def analyze_code(
        self,
        code: str,
        language: str = "jac",
        analysis_types: Optional[List[AnalysisType]] = None
    ) -> CodeAnalysisResult:
        """
        Analyze code for issues and improvements.

        Args:
            code: Source code to analyze
            language: Programming language
            analysis_types: Types of analysis to perform

        Returns:
            CodeAnalysisResult with issues and metrics
        """
        if not self.available or not self.api_key:
            return self._generate_mock_analysis(code, language)

        if analysis_types is None:
            analysis_types = [AnalysisType.COMPREHENSIVE]

        try:
            logger.info(f"Analyzing {language} code ({len(code)} chars)")

            # Build analysis prompt
            analysis_prompt = self._build_analysis_prompt(code, language, analysis_types)

            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }

                payload = {
                    "model": self.model,
                    "messages": [
                        {
                            "role": "system",
                            "content": """You are an expert code analyst for the JAC programming language and general software development.
Your task is to analyze code and provide detailed feedback on:
- Security vulnerabilities
- Performance issues
- Bugs and potential errors
- Best practices violations
- Code style improvements

Always provide specific line numbers, explanations, and actionable suggestions.
Respond in JSON format matching the required schema."""
                        },
                        {
                            "role": "user",
                            "content": analysis_prompt
                        }
                    ],
                    "temperature": 0.3,
                    "max_tokens": 2000
                }

                async with session.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        analysis_text = result["choices"][0]["message"]["content"]

                        # Parse the response
                        return self._parse_analysis_response(analysis_text, code)
                    else:
                        error_text = await response.text()
                        logger.error(f"OpenAI API error: {error_text}")
                        return self._generate_mock_analysis(code, language)

        except Exception as e:
            logger.error(f"Error analyzing code: {str(e)}")
            return self._generate_mock_analysis(code, language)

    def _build_analysis_prompt(
        self,
        code: str,
        language: str,
        analysis_types: List[AnalysisType]
    ) -> str:
        """Build the analysis prompt for the AI"""
        types_description = {
            AnalysisType.SECURITY: "security vulnerabilities and potential exploits",
            AnalysisType.PERFORMANCE: "performance bottlenecks and optimization opportunities",
            AnalysisType.BUG: "bugs, errors, and potential runtime issues",
            AnalysisType.BEST_PRACTICE: "violations of best practices and coding standards",
            AnalysisType.STYLE: "code style and readability improvements",
            AnalysisType.COMPREHENSIVE: "all aspects including security, performance, bugs, and best practices"
        }

        focus = ", ".join(types_description.get(t, t.value) for t in analysis_types)

        return f"""
Analyze the following {language} code for {focus}:

```{language}
{code}
```

Provide your analysis in JSON format with this structure:
{{
    "issues": [
        {{
            "id": "unique-id",
            "type": "security|performance|bug|best_practice|style",
            "severity": "error|warning|info",
            "line": line_number,
            "column": column_number,
            "message": "Brief issue description",
            "explanation": "Detailed explanation of the issue",
            "suggestion": "How to fix or improve",
            "code_diff": {{
                "before": "original code snippet",
                "after": "fixed code snippet"
            }}
        }}
    ],
    "metrics": {{
        "complexity": "low|medium|high",
        "linesOfCode": total_lines,
        "issuesCount": total_issues
    }},
    "summary": "Overall assessment summary"
}}

Focus on actionable feedback with specific line numbers and code suggestions.
"""

    def _parse_analysis_response(self, analysis_text: str, code: str) -> CodeAnalysisResult:
        """Parse AI response into CodeAnalysisResult"""
        try:
            # Try to extract JSON from response
            json_start = analysis_text.find('{')
            json_end = analysis_text.rfind('}') + 1

            if json_start >= 0 and json_end > json_start:
                json_str = analysis_text[json_start:json_end]
                data = json.loads(json_str)
            else:
                data = json.loads(analysis_text)

            issues = []
            for issue_data in data.get("issues", []):
                issue = CodeIssue(
                    id=issue_data.get("id", f"issue_{len(issues)}"),
                    type=AnalysisType(issue_data.get("type", "best_practice")),
                    severity=Severity(issue_data.get("severity", "info")),
                    line=issue_data.get("line", 1),
                    column=issue_data.get("column", 1),
                    message=issue_data.get("message", "Issue found"),
                    explanation=issue_data.get("explanation", ""),
                    suggestion=issue_data.get("suggestion", ""),
                    code_diff=issue_data.get("code_diff")
                )
                issues.append(issue)

            return CodeAnalysisResult(
                success=True,
                issues=issues,
                metrics=data.get("metrics", {"complexity": "medium", "linesOfCode": len(code.split('\n')), "issuesCount": len(issues)}),
                summary=data.get("summary", f"Found {len(issues)} issue(s)"),
                error=None
            )

        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Error parsing analysis response: {e}")
            return self._generate_mock_analysis(code, "unknown")

    def _generate_mock_analysis(self, code: str, language: str) -> CodeAnalysisResult:
        """Generate mock analysis when AI is unavailable"""
        lines = code.split('\n')
        line_count = len(lines)

        # Basic metrics
        complexity = "high" if line_count > 100 else "medium" if line_count > 50 else "low"

        return CodeAnalysisResult(
            success=True,
            issues=[
                CodeIssue(
                    id="mock-1",
                    type=AnalysisType.INFO,
                    severity=Severity.INFO,
                    line=1,
                    column=1,
                    message="AI analysis unavailable - using mock data",
                    explanation="The AI code analysis service requires an OpenAI API key to be fully functional.",
                    suggestion="Configure OPENAI_API_KEY in backend/config/.env to enable real AI analysis.",
                    code_diff=None
                )
            ],
            metrics={
                "complexity": complexity,
                "linesOfCode": line_count,
                "issuesCount": 0
            },
            summary="Code analysis complete (demo mode)",
            error=None
        )

    async def chat_about_code(
        self,
        message: str,
        code_context: str = "",
        chat_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Chat with AI about code or programming questions.

        Args:
            message: User's question
            code_context: Optional code snippet for context
            chat_history: Previous chat messages

        Returns:
            Dictionary with success status, AI response, and timestamp
        """
        if not self.available or not self.api_key:
            return self._generate_fallback_response(message)

        try:
            logger.info(f"Processing chat message: {message[:50]}...")

            # Build system message
            system_content = """You are Jeseci, an intelligent AI coding assistant for the Jeseci Smart Learning Academy.
You specialize in helping students learn programming, especially the JAC (Jaclang) programming language.
Be helpful, patient, and encouraging. Use examples to illustrate concepts.
If shown code, analyze it and provide clear explanations."""

            if code_context:
                system_content += f"\n\nThe user is working with this code:\n```{code_context[:1000]}```"

            # Build messages
            messages = [{"role": "system", "content": system_content}]

            # Add chat history
            if chat_history:
                for msg in chat_history[-10:]:
                    messages.append({"role": msg.get("role", "user"), "content": msg.get("content", "")})

            # Add user message
            messages.append({"role": "user", "content": message})

            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }

                payload = {
                    "model": self.model,
                    "messages": messages,
                    "temperature": 0.7,
                    "max_tokens": 1000
                }

                async with session.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        ai_response = result["choices"][0]["message"]["content"]

                        # Add to chat history
                        self.chat_history.append(AIChatMessage(role="user", content=message))
                        self.chat_history.append(AIChatMessage(role="assistant", content=ai_response))

                        return {
                            "success": True,
                            "response": ai_response,
                            "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
                        }
                    else:
                        error_text = await response.text()
                        logger.error(f"OpenAI API error: {error_text}")
                        return self._generate_fallback_response(message)

        except Exception as e:
            logger.error(f"Error in chat: {str(e)}")
            return self._generate_fallback_response(message)

    def _generate_fallback_response(self, message: str) -> Dict[str, Any]:
        """Generate fallback response when AI is unavailable"""
        import random

        fallback_responses = [
            "That's a great programming question! While I don't have access to real-time AI analysis right now, I'd recommend checking the JAC documentation for insights on this topic.",
            "Interesting question! The concepts you're asking about are fundamental to programming. Consider reviewing your lessons on this subject for deeper understanding.",
            "Thanks for asking! This is an important concept in software development. Would you like me to point you to relevant learning resources?",
            "Great thinking about this! Understanding these concepts will help you become a better programmer. Keep exploring and practicing!",
        ]

        return {
            "success": True,
            "response": random.choice(fallback_responses),
            "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "fallback": True
        }

    def explain_code(self, code: str, language: str = "jac") -> Dict[str, Any]:
        """
        Get AI explanation of code.

        Args:
            code: Code to explain
            language: Programming language

        Returns:
            Explanation of the code
        """
        if not self.available:
            return {
                "success": True,
                "explanation": f"This is {language} code with {len(code.split(chr(10)))} lines.",
                "fallback": True
            }

        # For now, return a basic explanation
        return {
            "success": True,
            "explanation": f"Code analysis requires OpenAI API key configuration.",
            "fallback": True
        }

    def clear_chat_history(self):
        """Clear the chat history"""
        self.chat_history = []
        logger.info("Chat history cleared")


# Global instance
ai_code_assistant = AICodeAssistant()


# Convenience functions for synchronous usage
def sync_analyze_code(
    code: str,
    language: str = "jac",
    analysis_types_str: Optional[str] = None
) -> Dict[str, Any]:
    """
    Synchronous wrapper for code analysis.
    Used by Jaclang walkers for code analysis.
    """
    import concurrent.futures

    # Parse analysis types
    analysis_types = None
    if analysis_types_str:
        types = []
        for t in analysis_types_str.split(","):
            t = t.strip().upper()
            if t in AnalysisType.__members__:
                types.append(AnalysisType[t])
        analysis_types = types

    def run_analysis():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(
                ai_code_assistant.analyze_code(code, language, analysis_types)
            )
            return {
                "success": result.success,
                "issues": [
                    {
                        "id": issue.id,
                        "type": issue.type.value,
                        "severity": issue.severity.value,
                        "line": issue.line,
                        "column": issue.column,
                        "message": issue.message,
                        "explanation": issue.explanation,
                        "suggestion": issue.suggestion,
                        "code_diff": issue.code_diff
                    }
                    for issue in result.issues
                ],
                "metrics": result.metrics,
                "summary": result.summary,
                "error": result.error
            }
        finally:
            loop.close()

    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(run_analysis)
        return future.result()


def sync_chat_about_code(
    message: str,
    code_context: str = "",
    chat_history_json: str = ""
) -> Dict[str, Any]:
    """
    Synchronous wrapper for code chat.
    Used by Jaclang walkers for conversational AI.
    """
    import concurrent.futures

    # Parse chat history
    chat_history = []
    if chat_history_json:
        try:
            chat_history = json.loads(chat_history_json)
        except json.JSONDecodeError:
            pass

    def run_chat():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(
                ai_code_assistant.chat_about_code(message, code_context, chat_history)
            )
            return result
        finally:
            loop.close()

    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(run_chat)
        return future.result()


def clear_code_chat_history():
    """Clear the chat history"""
    ai_code_assistant.clear_chat_history()


if __name__ == "__main__":
    # Test the code assistant
    import sys

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "analyze":
            code = sys.argv[2] if len(sys.argv) > 2 else "print('Hello World')"
            result = sync_analyze_code(code)
            print(json.dumps(result, indent=2))

        elif command == "chat":
            message = sys.argv[2] if len(sys.argv) > 2 else "Hello"
            result = sync_chat_about_code(message)
            print(json.dumps(result, indent=2))

        elif command == "health":
            print(json.dumps({
                "available": ai_code_assistant.available,
                "model": ai_code_assistant.model
            }, indent=2))
    else:
        print("Usage:")
        print("  python ai_code_service.py analyze <code>")
        print("  python ai_code_service.py chat <message>")
        print("  python ai_code_service.py health")
