# Forgot Password Modal CSS Styles

## 🎨 **CSS Styles for New Modals**

Add these CSS styles to your main stylesheet to properly style the forgot password modals:

### **Forgot Password Modal Styles**

```css
/* Forgot Password Modal */
.forgot-password-modal {
    max-width: 400px;
    width: 90%;
}

.forgot-password-form {
    padding: 20px;
}

.forgot-password-instructions {
    font-size: 14px;
    color: #666;
    margin: 15px 0;
    line-height: 1.5;
}

.forgot-password-submit-btn {
    width: 100%;
    padding: 12px;
    background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
    color: white;
    border: none;
    border-radius: 8px;
    font-size: 16px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
}

.forgot-password-submit-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(79, 172, 254, 0.3);
}

.forgot-password-submit-btn:active {
    transform: translateY(0);
}
```

### **Password Reset Modal Styles**

```css
/* Password Reset Modal */
.password-reset-modal {
    max-width: 450px;
    width: 90%;
}

.password-reset-form {
    padding: 20px;
}

.password-requirements {
    font-size: 12px;
    color: #888;
    margin: 10px 0;
    padding: 10px;
    background: #f8f9fa;
    border-radius: 6px;
    border-left: 3px solid #ffc107;
}

.password-reset-submit-btn {
    width: 100%;
    padding: 12px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    border-radius: 8px;
    font-size: 16px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
}

.password-reset-submit-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.password-reset-submit-btn:active {
    transform: translateY(0);
}
```

### **Updated Login Modal Styles**

```css
/* Updated forgot password link in login modal */
.forgot-password-link {
    background: none;
    border: none;
    color: #4facfe;
    font-size: 14px;
    text-decoration: underline;
    cursor: pointer;
    transition: color 0.3s ease;
}

.forgot-password-link:hover {
    color: #00f2fe;
    text-decoration: none;
}

.forgot-password-link:focus {
    outline: 2px solid #4facfe;
    outline-offset: 2px;
    border-radius: 3px;
}
```

### **Enhanced Modal Styling**

```css
/* Enhanced modal headers */
.modal-header h2 {
    margin: 0;
    color: #333;
    font-size: 20px;
    font-weight: 600;
}

/* Enhanced modal footers */
.modal-footer p {
    margin: 0;
    font-size: 14px;
    color: #666;
}

.modal-footer a {
    color: #4facfe;
    text-decoration: none;
    font-weight: 500;
    transition: color 0.3s ease;
}

.modal-footer a:hover {
    color: #00f2fe;
    text-decoration: underline;
}

/* Form input enhancements */
.form-input:focus {
    border-color: #4facfe;
    box-shadow: 0 0 0 3px rgba(79, 172, 254, 0.1);
    outline: none;
}

/* Loading states */
.forgot-password-submit-btn:disabled,
.password-reset-submit-btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    transform: none;
}

/* Success/Error message styling */
.password-reset-message {
    padding: 12px;
    margin: 15px 0;
    border-radius: 6px;
    font-size: 14px;
    font-weight: 500;
}

.password-reset-message.success {
    background: #d4edda;
    color: #155724;
    border: 1px solid #c3e6cb;
}

.password-reset-message.error {
    background: #f8d7da;
    color: #721c24;
    border: 1px solid #f5c6cb;
}
```

### **Responsive Design**

```css
/* Mobile responsiveness */
@media (max-width: 480px) {
    .forgot-password-modal,
    .password-reset-modal {
        max-width: 95%;
        width: 95%;
    }
    
    .forgot-password-form,
    .password-reset-form {
        padding: 15px;
    }
    
    .modal-header h2 {
        font-size: 18px;
    }
    
    .forgot-password-submit-btn,
    .password-reset-submit-btn {
        padding: 10px;
        font-size: 14px;
    }
}
```

### **Animation Enhancements**

```css
/* Modal animations */
.modal-overlay {
    animation: fadeIn 0.3s ease-out;
}

.modal-content {
    animation: slideInUp 0.3s ease-out;
}

@keyframes fadeIn {
    from {
        opacity: 0;
    }
    to {
        opacity: 1;
    }
}

@keyframes slideInUp {
    from {
        transform: translateY(50px);
        opacity: 0;
    }
    to {
        transform: translateY(0);
        opacity: 1;
    }
}

/* Form field animations */
.form-input {
    transition: border-color 0.3s ease, box-shadow 0.3s ease;
}

.form-group {
    animation: fadeInUp 0.4s ease-out;
    animation-fill-mode: both;
}

.form-group:nth-child(1) { animation-delay: 0.1s; }
.form-group:nth-child(2) { animation-delay: 0.2s; }

@keyframes fadeInUp {
    from {
        transform: translateY(20px);
        opacity: 0;
    }
    to {
        transform: translateY(0);
        opacity: 1;
    }
}
```

### **Dark Mode Support**

```css
/* Dark mode styles */
@media (prefers-color-scheme: dark) {
    .forgot-password-modal,
    .password-reset-modal {
        background: #2d3748;
        color: #e2e8f0;
    }
    
    .modal-header h2 {
        color: #e2e8f0;
    }
    
    .forgot-password-instructions,
    .modal-footer p {
        color: #a0aec0;
    }
    
    .password-requirements {
        background: #4a5568;
        color: #e2e8f0;
    }
    
    .form-input {
        background: #4a5568;
        border-color: #718096;
        color: #e2e8f0;
    }
    
    .form-input::placeholder {
        color: #a0aec0;
    }
}
```

### **Usage Instructions**

1. **Add these styles** to your main CSS file or create a separate `forgot-password.css` file
2. **Import the CSS** in your HTML head or include it in your main stylesheet
3. **Test responsiveness** on different screen sizes
4. **Customize colors** to match your brand theme
5. **Add loading states** if needed for async operations

The CSS provides:
- ✅ **Consistent styling** with existing modals
- ✅ **Professional gradients** and hover effects
- ✅ **Responsive design** for mobile devices
- ✅ **Dark mode support** for accessibility
- ✅ **Smooth animations** for better UX
- ✅ **Focus states** for keyboard navigation
- ✅ **Loading states** for async operations

Your forgot password modals will now have a polished, professional appearance! 🎨