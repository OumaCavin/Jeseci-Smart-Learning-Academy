/**
 * Contact Form Service
 * Handles contact form submissions with backend integration
 * and fallback to local storage for demo purposes
 */

interface ContactFormData {
  name: string;
  email: string;
  subject: string;
  message: string;
  phone: string;
  contactReason: string;
}

interface ContactSubmissionResponse {
  success: boolean;
  message_id?: string;
  timestamp?: string;
  status?: string;
  message?: string;
  error?: string;
  code?: string;
}

class ContactService {
  private readonly API_BASE = import.meta.env.VITE_API_BASE_URL || 'https://api.jeseci.com';
  private readonly FALLBACK_MODE = import.meta.env.VITE_CONTACT_FALLBACK_MODE === 'true';
  private readonly DEBUG_MODE = import.meta.env.VITE_DEBUG_MODE === 'true';

  /**
   * Submit contact form data
   */
  async submitContactForm(formData: ContactFormData): Promise<ContactSubmissionResponse> {
    try {
      // Clean and validate form data
      const cleanedData = this.cleanFormData(formData);
      
      if (!this.FALLBACK_MODE) {
        // Try backend API first
        return await this.submitToBackend(cleanedData);
      } else {
        // Fallback to local storage for demo
        return await this.submitToLocalStorage(cleanedData);
      }
    } catch (error) {
      console.error('Contact form submission error:', error);
      return {
        success: false,
        error: 'An unexpected error occurred. Please try again later.',
        code: 'SUBMISSION_ERROR'
      };
    }
  }

  /**
   * Submit to backend API
   */
  private async submitToBackend(formData: ContactFormData): Promise<ContactSubmissionResponse> {
    const response = await fetch(`${this.API_BASE}/walker/contact_submit`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      body: JSON.stringify({
        name: formData.name.trim(),
        email: formData.email.trim(),
        subject: formData.subject.trim(),
        message: formData.message.trim(),
        phone: formData.phone || '',
        contact_reason: formData.contactReason || 'general'
      })
    });

    let result = await response.json();
    
    // Handle Jaclang API response wrapped in reports array
    if (result?.reports && Array.isArray(result.reports) && result.reports.length > 0) {
      result = result.reports[0];
    }

    if (result.success) {
      return {
        success: true,
        message_id: result.message_id,
        timestamp: result.timestamp,
        status: result.status,
        message: result.message
      };
    } else {
      return {
        success: false,
        error: result.error || 'Failed to submit contact form',
        code: result.code || 'API_ERROR'
      };
    }
  }

  /**
   * Fallback submission to local storage (demo mode)
   */
  private async submitToLocalStorage(formData: ContactFormData): Promise<ContactSubmissionResponse> {
    // Simulate network delay
    await new Promise(resolve => setTimeout(resolve, 1500));

    // Generate unique message ID and timestamp
    const messageId = `demo_${Date.now()}`;
    const timestamp = new Date().toISOString();

    // Store in localStorage
    const contactData = {
      message_id: messageId,
      ...formData,
      timestamp,
      status: 'received',
      submitted_at: timestamp,
      source: 'demo'
    };

    const existingContacts = JSON.parse(localStorage.getItem('contactSubmissions') || '[]');
    existingContacts.push(contactData);
    localStorage.setItem('contactSubmissions', JSON.stringify(existingContacts));

    // Store email notification request
    this.logEmailNotification(contactData);

    return {
      success: true,
      message_id: messageId,
      timestamp,
      status: 'received',
      message: 'Thank you for contacting us! This is a demo submission. In production, your message would be stored in our database and email notifications would be sent.'
    };
  }

  /**
   * Clean and validate form data
   */
  private cleanFormData(formData: ContactFormData): ContactFormData {
    return {
      name: formData.name.trim(),
      email: formData.email.trim().toLowerCase(),
      subject: formData.subject.trim(),
      message: formData.message.trim(),
      phone: formData.phone?.trim() || '',
      contactReason: formData.contactReason || 'general'
    };
  }

  /**
   * Log email notification request (for demo purposes)
   */
  private logEmailNotification(contactData: any): void {
    if (this.DEBUG_MODE && typeof window !== 'undefined') {
      console.log('📧 EMAIL NOTIFICATION LOG:');
      console.log('To: admin@jeseci.com');
      console.log('Subject: New Contact Form Submission:', contactData.subject);
      console.log('Content:', {
        messageId: contactData.message_id,
        from: contactData.name,
        email: contactData.email,
        phone: contactData.phone,
        reason: contactData.contactReason,
        message: contactData.message,
        timestamp: contactData.timestamp
      });
      
      console.log('📧 USER CONFIRMATION EMAIL LOG:');
      console.log('To:', contactData.email);
      console.log('Subject: Thank you for contacting Jeseci Smart Learning Academy');
      console.log('Content: Confirmation message with message ID:', contactData.message_id);
    }
  }

  /**
   * Get stored contact submissions (for admin demo)
   */
  getStoredSubmissions(): any[] {
    try {
      return JSON.parse(localStorage.getItem('contactSubmissions') || '[]');
    } catch (error) {
      console.error('Error reading stored submissions:', error);
      return [];
    }
  }

  /**
   * Clear stored submissions (for admin demo)
   */
  clearStoredSubmissions(): void {
    try {
      localStorage.removeItem('contactSubmissions');
    } catch (error) {
      console.error('Error clearing submissions:', error);
    }
  }

  /**
   * Test backend connectivity
   */
  async testBackendConnection(): Promise<boolean> {
    try {
      const response = await fetch(`${this.API_BASE}/walker/health_check`, {
        method: 'GET',
        headers: {
          'Accept': 'application/json'
        }
      });
      return response.ok;
    } catch (error) {
      console.log('Backend not available, using fallback mode');
      return false;
    }
  }
}

export const contactService = new ContactService();
export default ContactService;