/**
 * OpenAI Service for Jac Language AI Assistant
 * Handles real AI responses using OpenAI API via fetch
 */

interface OpenAIMessage {
  role: 'system' | 'user' | 'assistant';
  content: string;
}

interface OpenAIResponse {
  content: string;
  confidence: number;
  suggestedActions?: string[];
  usage?: {
    promptTokens: number;
    completionTokens: number;
    totalTokens: number;
  };
}

interface ConversationContext {
  skillLevel?: 'beginner' | 'intermediate' | 'advanced';
  currentTopic?: string;
  previousTopics?: string[];
}

class OpenAIService {
  private apiKey: string;
  private baseURL = 'https://api.openai.com/v1/chat/completions';

  constructor() {
    // Use Vite environment variable (import.meta.env) for browser compatibility
    this.apiKey = import.meta.env.VITE_OPENAI_API_KEY || '';
    if (!this.apiKey) {
      console.warn('VITE_OPENAI_API_KEY not found in environment variables. AI features will use fallback responses.');
    }
  }

  /**
   * Generate a response using OpenAI Chat Completions API
   */
  async generateResponse(
    userMessage: string,
    conversationHistory: Array<{role: 'user' | 'assistant', content: string}>,
    context?: ConversationContext
  ): Promise<OpenAIResponse> {
    try {
      // Build conversation messages
      const messages: OpenAIMessage[] = [
        {
          role: 'system',
          content: `You are an expert Jac Language AI Assistant specializing in Object-Spatial Programming (OSP). 

Your role is to:
1. Help users learn Jac Language concepts, syntax, and best practices
2. Provide clear explanations of Object-Spatial Programming paradigms
3. Give practical code examples and explanations
4. Guide users through their learning journey
5. Answer questions about nodes, edges, walkers, semantic strings, and Jac features

Jac Language Key Concepts to cover:
- Object-Spatial Programming (OSP): A paradigm where computation moves to data
- Nodes: Stateful entities that hold data
- Edges: Typed relationships between nodes
- Walkers: Mobile computation entities that traverse graphs
- Semantic Strings: Provide explicit semantic context for AI models
- Scale-Agnostic Programming: Code that works from single-user to millions of users
- Pattern Matching: Handle complex logic with match statements
- Functions: Support type annotations and return types
- Collections: Lists, dictionaries, sets, tuples with comprehensions

Always provide:
- Clear, educational explanations
- Practical code examples when relevant
- Step-by-step guidance for learning
- Contextual advice based on the user's skill level
- Encouragement and motivation for learning

Be conversational, helpful, and educational. Always prioritize clarity and accuracy in your responses.${context ? 
            `\n\nCurrent conversation context:\n- User skill level: ${context.skillLevel || 'beginner'}\n- Current topic: ${context.currentTopic || 'general'}\n- Previous topics: ${context.previousTopics?.join(', ') || 'none'}` : 
            ''}`
        },
        ...conversationHistory.slice(-10), // Keep last 10 messages for context
        {
          role: 'user',
          content: userMessage
        }
      ];

      // Make API call to OpenAI
      const response = await fetch(this.baseURL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.apiKey}`
        },
        body: JSON.stringify({
          model: 'gpt-4o-mini',
          messages: messages,
          max_tokens: 1000,
          temperature: 0.7,
          presence_penalty: 0.1,
          frequency_penalty: 0.1
        })
      });

      if (!response.ok) {
        throw new Error(`OpenAI API error: ${response.status} ${response.statusText}`);
      }

      const data = await response.json();
      const responseContent = data.choices[0]?.message?.content || 
        'I apologize, but I encountered an issue generating a response. Could you please rephrase your question?';

      // Calculate confidence based on response length and completeness
      const confidence = this.calculateConfidence(responseContent, data.usage);

      // Generate suggested actions based on the response
      const suggestedActions = this.generateSuggestedActions(userMessage, responseContent);

      return {
        content: responseContent,
        confidence: confidence,
        suggestedActions: suggestedActions,
        usage: data.usage ? {
          promptTokens: data.usage.prompt_tokens || 0,
          completionTokens: data.usage.completion_tokens || 0,
          totalTokens: data.usage.total_tokens || 0
        } : undefined
      };

    } catch (error: any) {
      console.error('OpenAI API Error:', error);
      
      // Return a helpful fallback response
      return {
        content: `I'm currently experiencing technical difficulties connecting to my AI capabilities. However, I can still help you with basic Jac Language concepts:

• **Walkers**: Mobile computation entities that traverse graphs
• **Nodes**: Stateful entities that hold data in OSP
• **Edges**: Typed relationships between nodes
• **Object-Spatial Programming**: Bringing computation to data instead of data to computation

Please try again in a moment, or feel free to ask about any of these fundamental concepts!`,
        confidence: 0.3,
        suggestedActions: ['Explain walkers', 'What is OSP?', 'Show syntax', 'Try again']
      };
    }
  }

  /**
   * Calculate confidence score based on response quality
   */
  private calculateConfidence(content: string, usage?: any): number {
    let confidence = 0.7; // Base confidence

    // Higher confidence for longer, detailed responses
    if (content.length > 200) confidence += 0.1;
    if (content.length > 500) confidence += 0.1;
    
    // Higher confidence if it contains code examples
    if (content.includes('```') || content.includes('code') || content.includes('example')) {
      confidence += 0.1;
    }
    
    // Lower confidence if response seems truncated or incomplete
    if (content.length < 50) confidence -= 0.2;
    
    return Math.min(Math.max(confidence, 0.3), 0.95); // Clamp between 0.3 and 0.95
  }

  /**
   * Generate suggested follow-up actions
   */
  private generateSuggestedActions(userMessage: string, response: string): string[] {
    const actions: string[] = [];
    const lowerMessage = userMessage.toLowerCase();
    const lowerResponse = response.toLowerCase();

    // Topic-based suggestions
    if (lowerMessage.includes('walker')) {
      actions.push('Explain nodes', 'Show edge examples', 'Graph traversal');
    }
    if (lowerMessage.includes('node')) {
      actions.push('What are edges?', 'Walker examples', 'State management');
    }
    if (lowerMessage.includes('edge')) {
      actions.push('Node relationships', 'Walker traversal', 'Typed edges');
    }
    if (lowerMessage.includes('osp') || lowerMessage.includes('object-spatial')) {
      actions.push('Real-world examples', 'Scale benefits', 'Comparison to OOP');
    }
    if (lowerMessage.includes('semantic') || lowerMessage.includes('semstring')) {
      actions.push('AI integration', 'Code examples', 'Practical use cases');
    }
    if (lowerMessage.includes('syntax')) {
      actions.push('Code examples', 'Python comparison', 'Type annotations');
    }

    // General suggestions if none specific
    if (actions.length === 0) {
      actions.push('Show code example', 'Explain related concepts', 'Next learning step');
    }

    return actions.slice(0, 4); // Limit to 4 suggestions
  }

  /**
   * Test API connectivity
   */
  async testConnection(): Promise<boolean> {
    try {
      const response = await fetch(this.baseURL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.apiKey}`
        },
        body: JSON.stringify({
          model: 'gpt-4o-mini',
          messages: [
            { role: 'user', content: 'Say "connection successful" if you receive this.' }
          ],
          max_tokens: 10,
        })
      });

      if (!response.ok) return false;
      
      const data = await response.json();
      return data.choices[0]?.message?.content?.includes('connection successful') || false;
    } catch (error) {
      console.error('OpenAI connection test failed:', error);
      return false;
    }
  }
}

export const openAIService = new OpenAIService();
export default OpenAIService;