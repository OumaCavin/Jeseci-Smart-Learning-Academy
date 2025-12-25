import React, { useState } from 'react';
import { BookOpen, Brain, Users, Trophy, Zap, Target, ArrowRight, Star, CheckCircle, X, MessageCircle, Send, Loader } from 'lucide-react';
import { openAIService } from '../services/openaiService';
import { contactService } from '../services/contactService';

interface LandingPageProps {
  onShowLogin: () => void;
  onShowRegister: () => void;
  onNavigate?: (page: PageType) => void;
}

type PageType = 'landing' | 'help' | 'contact' | 'privacy' | 'terms';

interface HelpCenterPageProps {
  onBack: () => void;
  onNavigate?: (page: PageType) => void;
}

interface ContactPageProps {
  onBack: () => void;
  onNavigate?: (page: PageType) => void;
}

interface ContactFormData {
  name: string;
  email: string;
  subject: string;
  message: string;
  phone: string;
  contactReason: string;
}

interface PrivacyPageProps {
  onBack: () => void;
  onNavigate?: (page: PageType) => void;
}

interface TermsPageProps {
  onBack: () => void;
  onNavigate?: (page: PageType) => void;
}

// Support Page Components
const HelpCenterPage: React.FC<HelpCenterPageProps> = ({ onBack, onNavigate }) => {
  const [showAIAssistant, setShowAIAssistant] = useState(false);
  const helpTopics = [
    {
      title: "Getting Started with Jac Language",
      icon: <BookOpen className="w-6 h-6 text-blue-600" />,
      items: [
        "Setting up your Jac development environment",
        "Your first Jac program",
        "Understanding Object-Spatial Programming",
        "Creating nodes and edges"
      ]
    },
    {
      title: "Object-Spatial Programming",
      icon: <Brain className="w-6 h-6 text-green-600" />,
      items: [
        "Nodes and state management",
        "Edges and typed relationships",
        "Walkers and graph traversal",
        "Mobile computation patterns"
      ]
    },
    {
      title: "Advanced Jac Concepts",
      icon: <Zap className="w-6 h-6 text-purple-600" />,
      items: [
        "Semantic strings and AI integration",
        "Pattern matching",
        "Scale-agnostic programming",
        "Distributed applications"
      ]
    },
    {
      title: "Platform Features",
      icon: <Target className="w-6 h-6 text-orange-600" />,
      items: [
        "Using AI code assistant",
        "Progress tracking and analytics",
        "Learning path recommendations",
        "Achievement system"
      ]
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between py-4">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
                <BookOpen className="w-6 h-6 text-white" />
              </div>
              <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                Jeseci Academy - Help Center
              </h1>
            </div>
            <button 
              onClick={onBack}
              className="px-4 py-2 text-blue-600 hover:text-blue-700 font-medium transition-colors"
            >
              ← Back to Home
            </button>
          </div>
        </div>
      </header>

      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="text-center mb-12">
          <h2 className="text-4xl font-bold text-gray-900 mb-4">
            Help Center
          </h2>
          <p className="text-xl text-gray-600">
            Everything you need to master Jac Language and Object-Spatial Programming
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-8">
          {helpTopics.map((topic, index) => (
            <div key={index} className="bg-white p-6 rounded-xl shadow-lg">
              <div className="flex items-center space-x-3 mb-4">
                {topic.icon}
                <h3 className="text-xl font-semibold text-gray-900">{topic.title}</h3>
              </div>
              <ul className="space-y-2">
                {topic.items.map((item, itemIndex) => (
                  <li key={itemIndex} className="flex items-start space-x-2">
                    <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                    <span className="text-gray-700">{item}</span>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        <div className="mt-12 bg-blue-50 p-8 rounded-xl">
          <h3 className="text-2xl font-bold text-gray-900 mb-4">Still need help?</h3>
          <p className="text-gray-700 mb-4">
            Can't find what you're looking for? Our AI assistant and support team are here to help you succeed with Jac Language.
          </p>
          <div className="flex flex-col sm:flex-row gap-4">
            <button 
              onClick={() => onNavigate?.('contact')}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Contact Support
            </button>
            <button 
              onClick={() => setShowAIAssistant(true)}
              className="px-6 py-3 border border-blue-600 text-blue-600 rounded-lg hover:bg-blue-50 transition-colors"
            >
              Try AI Assistant
            </button>
          </div>
        </div>
      </div>
      
      {/* AI Assistant Modal */}
      <AIAssistantModal 
        isOpen={showAIAssistant} 
        onClose={() => setShowAIAssistant(false)} 
      />
    </div>
  );
};

const ContactPage: React.FC<ContactPageProps> = ({ onBack, onNavigate }) => {
  const [formData, setFormData] = useState<ContactFormData>({
    name: '',
    email: '',
    subject: 'General Inquiry',
    message: '',
    phone: '',
    contactReason: 'general'
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitStatus, setSubmitStatus] = useState<'idle' | 'success' | 'error'>('idle');

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setSubmitStatus('idle');

    try {
      // Use the contact service for form submission
      const result = await contactService.submitContactForm(formData);

      if (result.success) {
        setSubmitStatus('success');
        setFormData({ 
          name: '', 
          email: '', 
          subject: 'General Inquiry', 
          message: '',
          phone: '',
          contactReason: 'general'
        });
        
        // Auto-close success message after 7 seconds
        setTimeout(() => setSubmitStatus('idle'), 7000);
      } else {
        console.error('Contact form error:', result.error);
        setSubmitStatus('error');
        setTimeout(() => setSubmitStatus('idle'), 3000);
      }
    } catch (error) {
      console.error('Network error:', error);
      setSubmitStatus('error');
      setTimeout(() => setSubmitStatus('idle'), 3000);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between py-4">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
                <BookOpen className="w-6 h-6 text-white" />
              </div>
              <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                Jeseci Academy - Contact Us
              </h1>
            </div>
            <button 
              onClick={onBack}
              className="px-4 py-2 text-blue-600 hover:text-blue-700 font-medium transition-colors"
            >
              ← Back to Home
            </button>
          </div>
        </div>
      </header>

      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="text-center mb-12">
          <h2 className="text-4xl font-bold text-gray-900 mb-4">
            Get in Touch
          </h2>
          <p className="text-xl text-gray-600">
            We're here to help you master Jac Language and Object-Spatial Programming
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-8">
          <div className="bg-white p-8 rounded-xl shadow-lg">
            <h3 className="text-2xl font-bold text-gray-900 mb-6">Send us a Message</h3>
            
            {/* Success/Error Messages */}
            {submitStatus === 'success' && (
              <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg">
                <div className="flex items-center space-x-2">
                  <CheckCircle className="w-5 h-5 text-green-600" />
                  <p className="text-green-800 font-medium">Message sent successfully!</p>
                </div>
                <p className="text-green-700 text-sm mt-1">
                  Thank you for contacting us. We'll get back to you within 24 hours.
                </p>
              </div>
            )}
            
            {submitStatus === 'error' && (
              <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
                <div className="flex items-center space-x-2">
                  <X className="w-5 h-5 text-red-600" />
                  <p className="text-red-800 font-medium">Failed to send message</p>
                </div>
                <p className="text-red-700 text-sm mt-1">
                  Please try again or contact us through other means.
                </p>
              </div>
            )}
            
            <form className="space-y-4" onSubmit={handleSubmit}>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Name *</label>
                <input 
                  type="text" 
                  name="name"
                  value={formData.name}
                  onChange={handleInputChange}
                  required
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Your name"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Email *</label>
                <input 
                  type="email" 
                  name="email"
                  value={formData.email}
                  onChange={handleInputChange}
                  required
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="your@email.com"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Phone (Optional)</label>
                <input 
                  type="tel" 
                  name="phone"
                  value={formData.phone}
                  onChange={handleInputChange}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Your phone number"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Contact Reason</label>
                <select 
                  name="contactReason"
                  value={formData.contactReason}
                  onChange={handleInputChange}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="general">General Inquiry</option>
                  <option value="support">Technical Support</option>
                  <option value="feedback">Feedback</option>
                  <option value="partnership">Partnership</option>
                  <option value="billing">Billing Question</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Subject *</label>
                <select 
                  name="subject"
                  value={formData.subject}
                  onChange={handleInputChange}
                  required
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option>General Inquiry</option>
                  <option>Jac Language Support</option>
                  <option>Technical Issue</option>
                  <option>Feature Request</option>
                  <option>Partnership</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Message *</label>
                <textarea 
                  name="message"
                  value={formData.message}
                  onChange={handleInputChange}
                  required
                  rows={4}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Tell us how we can help..."
                ></textarea>
              </div>
              <button 
                type="submit"
                disabled={isSubmitting || !formData.name || !formData.email || !formData.message}
                className="w-full px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:from-blue-700 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 flex items-center justify-center space-x-2"
              >
                {isSubmitting ? (
                  <>
                    <Loader className="w-4 h-4 animate-spin" />
                    <span>Sending...</span>
                  </>
                ) : (
                  <>
                    <Send className="w-4 h-4" />
                    <span>Send Message</span>
                  </>
                )}
              </button>
            </form>
          </div>

          <div className="bg-white p-8 rounded-xl shadow-lg">
            <h3 className="text-2xl font-bold text-gray-900 mb-6">Other Ways to Reach Us</h3>
            
            <div className="space-y-6">
              <div className="flex items-start space-x-4">
                <Users className="w-6 h-6 text-blue-600 mt-1" />
                <div>
                  <h4 className="font-semibold text-gray-900">Community Support</h4>
                  <p className="text-gray-600">Join our developer community for peer support and discussions</p>
                </div>
              </div>
              
              <div className="flex items-start space-x-4">
                <Brain className="w-6 h-6 text-green-600 mt-1" />
                <div>
                  <h4 className="font-semibold text-gray-900">AI Assistant</h4>
                  <p className="text-gray-600">Get instant help with Jac Language concepts and code</p>
                </div>
              </div>
              
              <div className="flex items-start space-x-4">
                <Trophy className="w-6 h-6 text-purple-600 mt-1" />
                <div>
                  <h4 className="font-semibold text-gray-900">Documentation</h4>
                  <p className="text-gray-600">Comprehensive guides and API references</p>
                </div>
              </div>
            </div>

            <div className="mt-8 p-4 bg-blue-50 rounded-lg">
              <h4 className="font-semibold text-blue-900 mb-2">Response Time</h4>
              <p className="text-blue-800">
                We typically respond to all inquiries within 24 hours during business days.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

const PrivacyPage: React.FC<PrivacyPageProps> = ({ onBack }) => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between py-4">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
                <BookOpen className="w-6 h-6 text-white" />
              </div>
              <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                Jeseci Academy - Privacy Policy
              </h1>
            </div>
            <button 
              onClick={onBack}
              className="px-4 py-2 text-blue-600 hover:text-blue-700 font-medium transition-colors"
            >
              ← Back to Home
            </button>
          </div>
        </div>
      </header>

      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="bg-white p-8 rounded-xl shadow-lg">
          <h2 className="text-3xl font-bold text-gray-900 mb-8">Privacy Policy</h2>
          <p className="text-gray-600 mb-8">Last updated: December 25, 2025</p>

          <div className="prose prose-lg max-w-none">
            <h3 className="text-xl font-semibold text-gray-900 mb-4">1. Information We Collect</h3>
            <p className="text-gray-700 mb-6">
              We collect information you provide directly to us, such as when you create an account, 
              use our learning platform, or contact us for support. This may include:
            </p>
            <ul className="list-disc pl-6 text-gray-700 mb-6">
              <li>Account information (name, email address)</li>
              <li>Learning progress and achievements</li>
              <li>Code submissions and project work</li>
              <li>Communication with our AI assistant</li>
            </ul>

            <h3 className="text-xl font-semibold text-gray-900 mb-4">2. How We Use Your Information</h3>
            <p className="text-gray-700 mb-6">
              We use the information we collect to:
            </p>
            <ul className="list-disc pl-6 text-gray-700 mb-6">
              <li>Provide, maintain, and improve our Jac Language learning platform</li>
              <li>Personalize your learning experience</li>
              <li>Generate AI-powered content and recommendations</li>
              <li>Track your progress and provide analytics</li>
              <li>Communicate with you about updates and support</li>
            </ul>

            <h3 className="text-xl font-semibold text-gray-900 mb-4">3. Data Security</h3>
            <p className="text-gray-700 mb-6">
              We implement appropriate technical and organizational measures to protect your personal 
              information against unauthorized access, alteration, disclosure, or destruction. 
              Your code submissions and learning data are encrypted and stored securely.
            </p>

            <h3 className="text-xl font-semibold text-gray-900 mb-4">4. Your Rights</h3>
            <p className="text-gray-700 mb-6">
              You have the right to access, update, or delete your personal information. 
              You may also opt out of certain communications and data processing activities.
            </p>

            <h3 className="text-xl font-semibold text-gray-900 mb-4">5. Contact Us</h3>
            <p className="text-gray-700">
              If you have any questions about this Privacy Policy, please contact us at 
              privacy@jeseci-academy.com or through our contact form.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

const TermsPage: React.FC<TermsPageProps> = ({ onBack }) => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between py-4">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
                <BookOpen className="w-6 h-6 text-white" />
              </div>
              <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                Jeseci Academy - Terms of Service
              </h1>
            </div>
            <button 
              onClick={onBack}
              className="px-4 py-2 text-blue-600 hover:text-blue-700 font-medium transition-colors"
            >
              ← Back to Home
            </button>
          </div>
        </div>
      </header>

      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="bg-white p-8 rounded-xl shadow-lg">
          <h2 className="text-3xl font-bold text-gray-900 mb-8">Terms of Service</h2>
          <p className="text-gray-600 mb-8">Last updated: December 25, 2025</p>

          <div className="prose prose-lg max-w-none">
            <h3 className="text-xl font-semibold text-gray-900 mb-4">1. Acceptance of Terms</h3>
            <p className="text-gray-700 mb-6">
              By accessing and using Jeseci Academy, you accept and agree to be bound by the terms 
              and provision of this agreement.
            </p>

            <h3 className="text-xl font-semibold text-gray-900 mb-4">2. Use License</h3>
            <p className="text-gray-700 mb-6">
              Permission is granted to temporarily download one copy of Jeseci Academy for personal, 
              non-commercial transitory viewing only. This is the grant of a license, not a transfer of title.
            </p>

            <h3 className="text-xl font-semibold text-gray-900 mb-4">3. User Responsibilities</h3>
            <p className="text-gray-700 mb-6">
              You are responsible for:
            </p>
            <ul className="list-disc pl-6 text-gray-700 mb-6">
              <li>Maintaining the confidentiality of your account</li>
              <li>All activities that occur under your account</li>
              <li>Using the platform for lawful purposes only</li>
              <li>Not infringing on intellectual property rights</li>
            </ul>

            <h3 className="text-xl font-semibold text-gray-900 mb-4">4. Intellectual Property</h3>
            <p className="text-gray-700 mb-6">
              The platform and its original content, features, and functionality are and will remain 
              the exclusive property of Jeseci Academy. You retain ownership of your submitted code and projects.
            </p>

            <h3 className="text-xl font-semibold text-gray-900 mb-4">5. Disclaimer</h3>
            <p className="text-gray-700 mb-6">
              The information on this platform is provided on an 'as is' basis. To the fullest extent 
              permitted by law, Jeseci Academy excludes all representations, warranties, and conditions.
            </p>

            <h3 className="text-xl font-semibold text-gray-900 mb-4">6. Limitation of Liability</h3>
            <p className="text-gray-700 mb-6">
              In no event shall Jeseci Academy be liable for any damages (including, without limitation, 
              damages for loss of data or profit, or due to business interruption).
            </p>

            <h3 className="text-xl font-semibold text-gray-900 mb-4">7. Contact Information</h3>
            <p className="text-gray-700">
              If you have any questions about these Terms of Service, please contact us at 
              legal@jeseci-academy.com or through our contact form.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

// AI Assistant Modal Component
interface AIAssistantModalProps {
  isOpen: boolean;
  onClose: () => void;
}

interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  type?: 'text' | 'code' | 'explanation';
  metadata?: {
    keywords?: string[];
    confidence?: number;
    codeOutput?: string;
    suggestedActions?: string[];
  };
}

interface KeywordResponse {
  response: string;
  code?: string;
  confidence: number;
  execute?: boolean;
}

interface ConversationContext {
  previousTopics: string[];
  userSkillLevel: 'beginner' | 'intermediate' | 'advanced';
  currentTopic?: string;
  codeExamples: string[];
}

interface AIResponse {
  content: string;
  type: 'keyword' | 'ai_generated' | 'code_execution' | 'explanation';
  confidence: number;
  suggestedActions?: string[];
  codeExample?: string;
}

const AIAssistantModal: React.FC<AIAssistantModalProps> = ({ isOpen, onClose }) => {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: '1',
      role: 'assistant',
      content: 'Hello! I\'m your advanced Jac Language AI Assistant. I can help you with Object-Spatial Programming, execute code examples, provide detailed explanations, and guide your learning journey. What would you like to explore about Jac?',
      timestamp: new Date(),
      type: 'text'
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [conversationContext, setConversationContext] = useState<ConversationContext>({
    previousTopics: [],
    userSkillLevel: 'beginner',
    currentTopic: undefined,
    codeExamples: []
  });

  // Enhanced keyword-based responses with more Jac concepts
  const keywordResponses: { [key: string]: KeywordResponse } = {
    // Basic Concepts
    walker: {
      response: 'Walkers are mobile computation entities in Jac that traverse graphs. They\'re like programs that move through nodes and edges to perform tasks.',
      code: `walker GreetFriends {
    can visit with person {
        print(f"Hello {person.name}!");
    }
}`,
      confidence: 0.9
    },
    node: {
      response: 'Nodes in Jac are stateful entities that hold data. They\'re the fundamental building blocks of Object-Spatial Programming.',
      code: `node Person {
    has name: str;
    has age: int;
    has friends: list;
}`,
      confidence: 0.9
    },
    edge: {
      response: 'Edges in Jac are typed relationships between nodes. They define the connections and can have properties.',
      code: `edge FriendsWith {
    has since: int;
    has strength: float;
}`,
      confidence: 0.9
    },
    osp: {
      response: 'Object-Spatial Programming (OSP) is Jac\'s unique paradigm where computation moves to the data, making it scalable and distributed.',
      code: `# Instead of bringing data to computation,
# OSP brings computation to data
node data: MyData;
walker process_data -> visit data;`,
      confidence: 0.9
    },
    semantic: {
      response: 'Semantic strings (semstrings) in Jac provide explicit semantic context for AI models in the meaning-typed programming system.',
      code: `sem greeting = "Hello world";
# AI understands this as a greeting, not just text`,
      confidence: 0.9
    },
    syntax: {
      response: 'Jac syntax is similar to Python but with curly braces for code blocks and mandatory type annotations.',
      code: `def greet(name: str) -> str {
    return f"Hello {name}";
} # Curly braces, not indentation!`,
      confidence: 0.9
    },
    hello: {
      response: 'Hello! I\'m excited to help you learn Jac Language and Object-Spatial Programming! What specific area interests you?',
      confidence: 0.8
    },
    help: {
      response: 'I can help you with:\n• Jac Language syntax and concepts\n• Object-Spatial Programming (nodes, edges, walkers)\n• Code examples and execution\n• Learning path recommendations\n• Troubleshooting your Jac projects',
      confidence: 0.8
    },
    
    // Advanced Concepts
    functions: {
      response: 'Functions in Jac are defined with the `def` keyword and support type annotations, default parameters, and return types.',
      code: `def calculate_area(length: float, width: float = 1.0) -> float {
    return length * width;
}`,
      confidence: 0.8
    },
    collections: {
      response: 'Jac supports lists, dictionaries, sets, and tuples with comprehensive operations and comprehensions.',
      code: `numbers = [1, 2, 3, 4, 5];
squared = [n**2 for n in numbers if n > 2];`,
      confidence: 0.8
    },
    pattern_matching: {
      response: 'Pattern matching in Jac allows handling complex logic with match statements and case analysis.',
      code: `match data_type {
    case "string" -> print("Processing text");
    case "number" -> print("Processing numbers");
    case _ -> print("Unknown type");
}`,
      confidence: 0.8
    },
    scale_agnostic: {
      response: 'Scale-agnostic programming means your Jac code works the same from single-user to millions of users without modification.',
      code: `# Same code works for:
# - Single user application
# - Distributed cloud system
# - Enterprise-scale deployment`,
      confidence: 0.8
    },
    
    // Code Execution Keywords
    run: {
      response: 'Let me execute this Jac code for you!',
      code: 'print("Hello from Jac!");',
      confidence: 0.7,
      execute: true
    },
    execute: {
      response: 'I\'ll run this Jac code example:',
      confidence: 0.7,
      execute: true
    },
    example: {
      response: 'Here\'s a practical Jac example:',
      code: `# Create a simple social network
node Person {
    has name: str;
    has interests: list;
}

edge FriendsWith {
    has since: int;
}`,
      confidence: 0.7
    }
  };

  // Execute Jac code simulation
  const executeJacCode = (code: string): string => {
    const executions: { [key: string]: string } = {
      'print("Hello from Jac!");': 'Hello from Jac!',
      'walker GreetFriends': 'Walker GreetFriends created successfully',
      'node Person': 'Node Person definition compiled',
      'edge FriendsWith': 'Edge FriendsWith defined with properties',
      'def calculate_area': 'Function calculate_area is ready for use',
      'match data_type': 'Pattern matching pattern compiled'
    };
    
    for (const [pattern, output] of Object.entries(executions)) {
      if (code.includes(pattern)) {
        return `✅ Executed successfully:\n${output}\n\n📝 Note: This is a simulation. In production, this would execute actual Jac code.`;
      }
    }
    
    return `✅ Code executed:\n${code}\n\n📝 Note: This is a simulation. In production, this would run actual Jac code with full error handling and output.`;
  };

  // Enhanced response selection logic
  const selectResponse = (userInput: string): AIResponse => {
    const lowerMessage = userInput.toLowerCase();
    
    // Check for code execution requests
    if (lowerMessage.includes('run') || lowerMessage.includes('execute') || lowerMessage.includes('show me')) {
      // Find relevant code example
      for (const [keyword, data] of Object.entries(keywordResponses)) {
        if (lowerMessage.includes(keyword) && data.code) {
          return {
            content: data.response,
            type: 'code_execution',
            confidence: data.confidence,
            codeExample: data.code || undefined!
          };
        }
      }
      
      // Default code execution
      return {
        content: 'Let me show you a practical Jac code example:',
        type: 'code_execution',
        confidence: 0.6,
        codeExample: `with entry {
    print("Welcome to Jac Programming!");
}`
      };
    }
    
    // Check keyword-based responses
    for (const [keyword, data] of Object.entries(keywordResponses)) {
      if (lowerMessage.includes(keyword)) {
        return {
          content: data.response,
          type: 'keyword',
          confidence: data.confidence,
          codeExample: data.code || undefined
        };
      }
    }
    
    // Complex query - use AI
    return {
      content: 'This is a complex question that requires deeper analysis. Let me provide you with a comprehensive response based on current best practices in Jac Language.',
      type: 'ai_generated',
      confidence: 0.7,
      suggestedActions: ['Ask follow-up', 'View related concepts', 'Try examples']
    };
  };

  const handleSendMessage = async () => {
    if (!inputMessage.trim()) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: inputMessage,
      timestamp: new Date(),
      type: 'text'
    };

    setMessages(prev => [...prev, userMessage]);
    const currentInput = inputMessage;
    setInputMessage('');
    setIsLoading(true);

    try {
      // Update conversation context
      setConversationContext(prev => ({
        ...prev,
        previousTopics: [...prev.previousTopics.slice(-4), currentInput],
        currentTopic: currentInput
      }));

      // Check for keyword matches first
      const keywordMatch = selectResponse(currentInput);
      
      let finalResponse;
      
      // If it's a keyword match, use that. Otherwise, use OpenAI
      if (keywordMatch.type === 'keyword') {
        finalResponse = {
          content: keywordMatch.content,
          confidence: keywordMatch.confidence,
          suggestedActions: ['Ask follow-up', 'View related concepts', 'Try examples']
        };
      } else {
        // Use OpenAI API for AI-generated responses
        try {
          // Prepare conversation history for OpenAI (last 10 messages)
          const conversationHistory = messages.slice(-10).map(msg => ({
            role: msg.role as 'user' | 'assistant',
            content: msg.content
          }));
          
          // Call OpenAI service
          finalResponse = await openAIService.generateResponse(
            currentInput,
            conversationHistory,
            {
              skillLevel: conversationContext.userSkillLevel,
              currentTopic: conversationContext.currentTopic,
              previousTopics: conversationContext.previousTopics
            }
          );
        } catch (error) {
          console.error('OpenAI API Error:', error);
          // Fallback to basic response
          finalResponse = {
            content: `I'm here to help you learn Jac Language! You can ask me about:

• **Walkers**: Mobile computation entities that traverse graphs
• **Nodes**: Stateful entities that hold data in OSP
• **Edges**: Typed relationships between nodes
• **Object-Spatial Programming**: Bringing computation to data
• **Semantic Strings**: Providing explicit semantic context

What would you like to learn about?`,
            confidence: 0.5,
            suggestedActions: ['Explain walkers', 'What is OSP?', 'Show syntax examples']
          };
        }
      }
      
      // Generate assistant message
      const assistantMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: finalResponse.content,
        timestamp: new Date(),
        type: keywordMatch.type === 'code_execution' ? 'code' : 'text',
        metadata: {
          keywords: Object.keys(keywordResponses).filter(key => currentInput.toLowerCase().includes(key)),
          confidence: finalResponse.confidence,
          suggestedActions: finalResponse.suggestedActions,
          codeOutput: keywordMatch.type === 'code_execution' && keywordMatch.codeExample ? executeJacCode(keywordMatch.codeExample) : undefined
        }
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'I apologize, but I encountered an issue processing your request. Could you please rephrase your question?',
        timestamp: new Date(),
        type: 'text'
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const renderMessage = (message: ChatMessage) => {
    const isUser = message.role === 'user';
    
    return (
      <div key={message.id} className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
        <div className={`max-w-[85%] p-4 rounded-lg ${
          isUser 
            ? 'bg-blue-600 text-white' 
            : message.type === 'code'
            ? 'bg-gray-900 text-green-400 font-mono text-sm'
            : 'bg-gray-100 text-gray-900'
        }`}>
          <div className="whitespace-pre-wrap">{message.content}</div>
          
          {message.metadata?.codeOutput && (
            <div className="mt-3 p-3 bg-gray-800 text-green-400 rounded border-l-4 border-green-500">
              <div className="font-semibold text-green-300 mb-2">🔧 Execution Result:</div>
              <pre className="whitespace-pre-wrap text-sm">{message.metadata.codeOutput}</pre>
            </div>
          )}
          
          {message.metadata?.suggestedActions && (
            <div className="mt-3 flex flex-wrap gap-2">
              {message.metadata.suggestedActions.map((action, index) => (
                <button
                  key={index}
                  onClick={() => setInputMessage(action.toLowerCase())}
                  className="px-3 py-1 bg-blue-500 hover:bg-blue-600 text-white text-xs rounded-full transition-colors"
                >
                  {action}
                </button>
              ))}
            </div>
          )}
          
          <p className={`text-xs mt-2 ${
            isUser ? 'text-blue-100' : 'text-gray-500'
          }`}>
            {message.timestamp.toLocaleTimeString()}
            {message.metadata?.confidence && (
              <span className="ml-2 opacity-70">
                • {Math.round(message.metadata.confidence * 100)}% confident
              </span>
            )}
          </p>
        </div>
      </div>
    );
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-2xl w-full max-w-4xl h-[700px] flex flex-col">
        {/* Enhanced Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
              <Brain className="w-6 h-6 text-white" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900">Advanced Jac Language AI</h3>
              <p className="text-sm text-gray-600">
                Keyword responses • AI analysis • Code execution • {conversationContext.userSkillLevel} level
              </p>
            </div>
          </div>
          <button 
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <X className="w-5 h-5 text-gray-500" />
          </button>
        </div>

        {/* Enhanced Messages with better formatting */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4 bg-gray-50">
          {messages.map(renderMessage)}
          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-gray-100 p-4 rounded-lg">
                <div className="flex items-center space-x-2">
                  <Loader className="w-4 h-4 animate-spin text-gray-500" />
                  <span className="text-sm text-gray-600">AI is analyzing your question...</span>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Enhanced Input */}
        <div className="p-6 border-t border-gray-200 bg-white">
          <div className="flex space-x-3">
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask about Jac, request code examples, run simulations..."
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              disabled={isLoading}
            />
            <button
              onClick={handleSendMessage}
              disabled={!inputMessage.trim() || isLoading}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center space-x-2"
            >
              <Send className="w-4 h-4" />
              <span>Send</span>
            </button>
          </div>
          
          {/* Quick action hints */}
          <div className="mt-3 flex flex-wrap gap-2">
            {['Explain walkers', 'Show syntax', 'Run example', 'OSP concepts'].map((hint) => (
              <button
                key={hint}
                onClick={() => setInputMessage(hint.toLowerCase())}
                className="px-2 py-1 text-xs bg-gray-200 hover:bg-gray-300 text-gray-700 rounded transition-colors"
              >
                {hint}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

const LandingPage: React.FC<LandingPageProps> = ({ onShowLogin, onShowRegister, onNavigate }) => {
  const features = [
    {
      icon: <Brain className="w-8 h-8 text-blue-600" />,
      title: "AI-Powered Learning",
      description: "Generate personalized content and get intelligent recommendations tailored to your learning style and progress."
    },
    {
      icon: <Target className="w-8 h-8 text-green-600" />,
      title: "Adaptive Learning Paths",
      description: "Follow structured learning paths that adapt to your pace and skill level, with prerequisites and dependencies."
    },
    {
      icon: <Trophy className="w-8 h-8 text-yellow-600" />,
      title: "Gamified Achievement System",
      description: "Earn badges, maintain learning streaks, and track your progress with our comprehensive achievement system."
    },
    {
      icon: <Users className="w-8 h-8 text-purple-600" />,
      title: "Expert AI Tutoring",
      description: "Get instant help from your AI learning assistant, available 24/7 to answer questions and explain concepts."
    },
    {
      icon: <BookOpen className="w-8 h-8 text-red-600" />,
      title: "Rich Content Library",
      description: "Access thousands of concepts, courses, and learning materials across multiple domains and difficulty levels."
    },
    {
      icon: <Zap className="w-8 h-8 text-orange-600" />,
      title: "Real-time Analytics",
      description: "Track your learning journey with detailed analytics, progress insights, and personalized recommendations."
    }
  ];

  const sampleContent = [
    {
      category: "Jac Language Fundamentals",
      items: [
        { name: "Variables & Data Types", difficulty: "Beginner", duration: "45 min" },
        { name: "Control Flow & Loops", difficulty: "Beginner", duration: "60 min" },
        { name: "Functions & Parameters", difficulty: "Beginner", duration: "75 min" },
        { name: "Collections & Data Structures", difficulty: "Beginner", duration: "90 min" }
      ]
    },
    {
      category: "Object-Spatial Programming",
      items: [
        { name: "Nodes & State Management", difficulty: "Intermediate", duration: "90 min" },
        { name: "Edges & Typed Relationships", difficulty: "Intermediate", duration: "75 min" },
        { name: "Walkers & Mobile Computation", difficulty: "Intermediate", duration: "120 min" },
        { name: "Graph Traversal Patterns", difficulty: "Advanced", duration: "150 min" }
      ]
    },
    {
      category: "Advanced Jac Concepts",
      items: [
        { name: "Semantic Strings & AI Context", difficulty: "Advanced", duration: "120 min" },
        { name: "Pattern Matching & Case Analysis", difficulty: "Advanced", duration: "90 min" },
        { name: "Scale-Agnostic Programming", difficulty: "Advanced", duration: "150 min" },
        { name: "Distributed Graph Applications", difficulty: "Expert", duration: "180 min" }
      ]
    }
  ];

  const stats = [
    { number: "10,000+", label: "Students Learning" },
    { number: "500+", label: "Learning Concepts" },
    { number: "50+", label: "Expert Courses" },
    { number: "95%", label: "Success Rate" }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Navigation Header */}
      <header className="bg-white/80 backdrop-blur-md shadow-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
                <BookOpen className="w-6 h-6 text-white" />
              </div>
              <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                Jeseci Academy
              </h1>
            </div>
            <div className="flex items-center space-x-4">
              <button 
                onClick={onShowLogin}
                className="px-6 py-2 text-blue-600 hover:text-blue-700 font-medium transition-colors"
              >
                Login
              </button>
              <button 
                onClick={onShowRegister}
                className="px-6 py-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:from-blue-700 hover:to-purple-700 transition-all duration-200 transform hover:scale-105 shadow-lg"
              >
                Get Started
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative overflow-hidden">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
          <div className="text-center">
            <h2 className="text-5xl md:text-6xl font-bold text-gray-900 mb-6">
              Master
              <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent block">
                Jac Language Programming
              </span>
            </h2>
            <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto leading-relaxed">
              Learn Object-Spatial Programming (OSP) with our AI-powered platform. 
              Master Jac's unique paradigm for graph-based programming, from basics to advanced concepts like 
              nodes, edges, walkers, and semantic strings.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <button 
                onClick={onShowRegister}
                className="px-8 py-4 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg text-lg font-semibold hover:from-blue-700 hover:to-purple-700 transition-all duration-200 transform hover:scale-105 shadow-lg flex items-center justify-center"
              >
                Start Learning Free
                <ArrowRight className="ml-2 w-5 h-5" />
              </button>
              <button 
                onClick={onShowLogin}
                className="px-8 py-4 border-2 border-gray-300 text-gray-700 rounded-lg text-lg font-semibold hover:border-gray-400 hover:bg-gray-50 transition-all duration-200"
              >
                I Have an Account
              </button>
            </div>
          </div>
        </div>
        
        {/* Background decoration */}
        <div className="absolute top-0 left-0 w-full h-full overflow-hidden pointer-events-none">
          <div className="absolute top-20 left-10 w-72 h-72 bg-blue-300 rounded-full mix-blend-multiply filter blur-xl opacity-30 animate-blob"></div>
          <div className="absolute top-40 right-10 w-72 h-72 bg-purple-300 rounded-full mix-blend-multiply filter blur-xl opacity-30 animate-blob animation-delay-2000"></div>
          <div className="absolute bottom-20 left-20 w-72 h-72 bg-pink-300 rounded-full mix-blend-multiply filter blur-xl opacity-30 animate-blob animation-delay-4000"></div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="bg-white py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {stats.map((stat, index) => (
              <div key={index} className="text-center">
                <div className="text-3xl md:text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-2">
                  {stat.number}
                </div>
                <div className="text-gray-600 font-medium">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h3 className="text-4xl font-bold text-gray-900 mb-4">
              Why Learn Jac Language with Us?
            </h3>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Master Object-Spatial Programming with our specialized Jac Language curriculum, 
              featuring AI-powered tutoring and hands-on graph programming experience.
            </p>
          </div>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <div key={index} className="bg-white p-8 rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300 transform hover:-translate-y-2">
                <div className="mb-4">
                  {feature.icon}
                </div>
                <h4 className="text-xl font-semibold text-gray-900 mb-3">
                  {feature.title}
                </h4>
                <p className="text-gray-600 leading-relaxed">
                  {feature.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Sample Content Preview */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h3 className="text-4xl font-bold text-gray-900 mb-4">
              Explore Our Learning Library
            </h3>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Get a preview of the rich content available in our platform. 
              Each concept includes interactive lessons, quizzes, and practical exercises.
            </p>
          </div>
          
          <div className="grid lg:grid-cols-3 gap-8">
            {sampleContent.map((category, index) => (
              <div key={index} className="bg-white rounded-2xl shadow-lg overflow-hidden">
                <div className="bg-gradient-to-r from-blue-600 to-purple-600 p-6">
                  <h4 className="text-xl font-semibold text-white">
                    {category.category}
                  </h4>
                </div>
                <div className="p-6">
                  <div className="space-y-4">
                    {category.items.map((item, itemIndex) => (
                      <div key={itemIndex} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                        <div className="flex-1">
                          <div className="font-medium text-gray-900">{item.name}</div>
                          <div className="text-sm text-gray-500">{item.duration}</div>
                        </div>
                        <div className="flex items-center space-x-2">
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                            item.difficulty === 'Beginner' ? 'bg-green-100 text-green-700' :
                            item.difficulty === 'Intermediate' ? 'bg-yellow-100 text-yellow-700' :
                            'bg-red-100 text-red-700'
                          }`}>
                            {item.difficulty}
                          </span>
                          <CheckCircle className="w-4 h-4 text-gray-400" />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Testimonials Preview */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h3 className="text-4xl font-bold text-gray-900 mb-4">
              What Our Students Say
            </h3>
          </div>
          
          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                name: "Sarah Chen",
                role: "Software Developer",
                content: "The AI-powered content generation helped me learn complex concepts faster than any traditional course.",
                rating: 5
              },
              {
                name: "Marcus Johnson",
                role: "Data Scientist",
                content: "The personalized learning paths adapted perfectly to my skill level and learning style.",
                rating: 5
              },
              {
                name: "Emily Rodriguez",
                role: "Student",
                content: "I love the achievement system - it keeps me motivated to complete my learning goals.",
                rating: 5
              }
            ].map((testimonial, index) => (
              <div key={index} className="bg-white p-8 rounded-2xl shadow-lg">
                <div className="flex items-center mb-4">
                  {[...Array(testimonial.rating)].map((_, i) => (
                    <Star key={i} className="w-5 h-5 text-yellow-400 fill-current" />
                  ))}
                </div>
                <p className="text-gray-600 mb-6 italic">"{testimonial.content}"</p>
                <div>
                  <div className="font-semibold text-gray-900">{testimonial.name}</div>
                  <div className="text-sm text-gray-500">{testimonial.role}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-r from-blue-600 to-purple-600">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h3 className="text-4xl font-bold text-white mb-6">
            Ready to Master Jac Language?
          </h3>
          <p className="text-xl text-blue-100 mb-8">
            Join thousands of developers who are already building the future with Object-Spatial Programming 
            and Jac Language on our AI-powered platform.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button 
              onClick={onShowRegister}
              className="px-8 py-4 bg-white text-blue-600 rounded-lg text-lg font-semibold hover:bg-gray-100 transition-all duration-200 transform hover:scale-105 shadow-lg flex items-center justify-center"
            >
              Start Learning Jac Free
              <ArrowRight className="ml-2 w-5 h-5" />
            </button>
            <button 
              onClick={onShowLogin}
              className="px-8 py-4 border-2 border-white text-white rounded-lg text-lg font-semibold hover:bg-white hover:text-blue-600 transition-all duration-200"
            >
              Sign In to Continue
            </button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-4 gap-8">
            <div>
              <div className="flex items-center space-x-3 mb-4">
                <div className="w-8 h-8 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
                  <BookOpen className="w-5 h-5 text-white" />
                </div>
                <h4 className="text-xl font-bold">Jeseci Academy</h4>
              </div>
              <p className="text-gray-400">
                Empowering developers worldwide to master Object-Spatial Programming with Jac Language through AI-powered personalized education.
              </p>
            </div>
            <div>
              <h5 className="font-semibold mb-4">Jac Learning</h5>
              <ul className="space-y-2 text-gray-400">
                <li>Learning Paths</li>
                <li>AI Code Assistant</li>
                <li>Graph Programming</li>
                <li>Progress Tracking</li>
              </ul>
            </div>
            <div>
              <h5 className="font-semibold mb-4">Jac Topics</h5>
              <ul className="space-y-2 text-gray-400">
                <li>Jac Fundamentals</li>
                <li>Object-Spatial Programming</li>
                <li>Nodes, Edges & Walkers</li>
                <li>Semantic Strings</li>
              </ul>
            </div>
            <div>
              <h5 className="font-semibold mb-4">Support</h5>
              <ul className="space-y-2 text-gray-400">
                <li>
                  <button 
                    onClick={() => onNavigate?.('help')}
                    className="hover:text-white transition-colors cursor-pointer text-left"
                  >
                    Help Center
                  </button>
                </li>
                <li>
                  <button 
                    onClick={() => onNavigate?.('contact')}
                    className="hover:text-white transition-colors cursor-pointer text-left"
                  >
                    Contact Us
                  </button>
                </li>
                <li>
                  <button 
                    onClick={() => onNavigate?.('privacy')}
                    className="hover:text-white transition-colors cursor-pointer text-left"
                  >
                    Privacy Policy
                  </button>
                </li>
                <li>
                  <button 
                    onClick={() => onNavigate?.('terms')}
                    className="hover:text-white transition-colors cursor-pointer text-left"
                  >
                    Terms of Service
                  </button>
                </li>
              </ul>
            </div>
          </div>
          <div className="border-t border-gray-800 mt-8 pt-8 text-center text-gray-400">
            <p>&copy; 2025 Jeseci Smart Learning Academy. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
};

// Main component with page routing
const LandingPageWithNavigation: React.FC<LandingPageProps> = (props) => {
  const [currentPage, setCurrentPage] = useState<PageType>('landing');

  const handlePageChange = (page: PageType) => {
    setCurrentPage(page);
  };

  const handleBackToLanding = () => {
    setCurrentPage('landing');
  };

  // Render the appropriate page based on current selection
  switch (currentPage) {
    case 'help':
      return <HelpCenterPage onBack={handleBackToLanding} onNavigate={handlePageChange} />;
    case 'contact':
      return <ContactPage onBack={handleBackToLanding} onNavigate={handlePageChange} />;
    case 'privacy':
      return <PrivacyPage onBack={handleBackToLanding} onNavigate={handlePageChange} />;
    case 'terms':
      return <TermsPage onBack={handleBackToLanding} onNavigate={handlePageChange} />;
    default:
      return <LandingPage {...props} onNavigate={handlePageChange} />;
  }
};

export default LandingPageWithNavigation;