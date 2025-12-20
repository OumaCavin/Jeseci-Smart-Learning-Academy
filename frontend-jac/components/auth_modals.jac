"""
Authentication Components
Login and Registration modals for user authentication
"""

import "../services/fastapi_service.jac" as services;

obj LoginModal {
    has app_instance: dict = None;
    
    can show with entry (app_instance: dict = None) {
        # Store app instance for callbacks
        self.app_instance = app_instance;
        
        <div className="modal-overlay" onClick={(e) => self.close_modal(e)}>
            <div className="modal-content login-modal" onClick={(e) => e.stopPropagation()}>
                {self.render_modal_header()}
                {self.render_login_form()}
                {self.render_login_footer()}
            </div>
        </div>
    }

    can render_modal_header with entry -> div {
        <div className="modal-header">
            <h2>🔐 Login to Jeseci</h2>
            <button className="modal-close" onClick={() => self.close_modal()}>
                ✕
            </button>
        </div>
    }

    can render_login_form with entry -> div {
        <form className="login-form" onSubmit={(e) => self.handle_login(e)}>
            <div className="form-group">
                <label className="form-label">Email or Username</label>
                <input 
                    type="text" 
                    className="form-input" 
                    placeholder="Enter your email or username"
                    name="email"
                    required
                />
            </div>
            
            <div className="form-group">
                <label className="form-label">Password</label>
                <input 
                    type="password" 
                    className="form-input" 
                    placeholder="Enter your password"
                    name="password"
                    required
                />
            </div>
            
            <div className="form-options">
                <label className="checkbox-label">
                    <input type="checkbox" name="remember_me" />
                    <span className="checkbox-custom"></span>
                    Remember me
                </label>
                <button 
                    type="button" 
                    className="forgot-password-link"
                    onClick={() => self.show_forgot_password()}
                >
                    Forgot password?
                </button>
            </div>
            
            <button type="submit" className="login-submit-btn">
                🚀 Login
            </button>
        </form>
    }

    can render_login_footer with entry -> div {
        <div className="modal-footer">
            <p>Don't have an account? 
                <a href="#" onClick={() => self.show_register()}>Sign up here</a>
            </p>
        </div>
    }

    can handle_login with entry (event: dict) {
        event.preventDefault();
        
        form_data = new FormData(event.target);
        login_input = form_data.get("email");  # Can be email or username
        password = form_data.get("password");
        remember_me = form_data.get("remember_me") == "on";
        
        print(f"🔐 Attempting login for: {login_input}");
        
        # Call the main app's login method
        # The main app handles FastAPI integration
        self.perform_login(login_input, password, remember_me);
    }

    can perform_login with entry (login_input: str, password: str, remember_me: bool) {
        try {
            # Direct integration with FastAPI service
            print(f"🔐 Logging in user: {login_input}");
            
            # Create FastAPI service instance
            api_service = services.FastAPIService();
            
            # Call FastAPI login endpoint
            login_response = api_service.login(login_input, password);
            
            if (login_response["success"]) {
                print("✅ Login successful");
                # Store auth token in localStorage for persistence
                auth_token = login_response["token"];
                print(f"🔑 Auth token received: {auth_token[:20]}...");
                
                # Notify the app that login was successful
                # In a real implementation, you'd want a callback system
                self.on_login_success(login_response);
            } else {
                print(f"❌ Login failed: {login_response.get('error', 'Unknown error')}");
                self.on_login_error(login_response.get('error', 'Login failed'));
            }
            
        } catch (error) {
            print(f"❌ Login error: {error}");
            self.on_login_error("Connection error. Please try again.");
        }
        
        # Close modal
        self.close_modal();
    }
    
    # Callback methods for login success/error
    can on_login_success with entry (login_response: dict) {
        print("🎉 Login successful - updating app state");
        # This would be called by a global app or state manager
        # In a real implementation, you'd dispatch an event or call a callback
    }
    
    can on_login_error with entry (error_message: str) {
        print(f"🚨 Login error: {error_message}");
        # This would show an error message to the user
        # In a real implementation, you'd show a toast notification
    }

    can close_modal with entry (event: dict = None) {
        if (event && event.target != event.currentTarget) {
            return;  # Don't close if clicking inside modal
        }
        
        # Remove modal from DOM
        print("🔐 Closing login modal");
    }

    can show_register with entry {
        self.close_modal();
        RegisterModal.show(self.app_instance);
    }
    
    can show_forgot_password with entry {
        self.close_modal();
        ForgotPasswordModal.show(self.app_instance);
    }
}

obj RegisterModal {
    has app_instance: dict = None;
    
    can show with entry (app_instance: dict = None) {
        <div className="modal-overlay" onClick={(e) => self.close_modal(e)}>
            <div className="modal-content register-modal" onClick={(e) => e.stopPropagation()}>
                {self.render_modal_header()}
                {self.render_register_form()}
                {self.render_register_footer()}
            </div>
        </div>
    }

    can render_modal_header with entry -> div {
        <div className="modal-header">
            <h2>📝 Create Account</h2>
            <button className="modal-close" onClick={() => self.close_modal()}>
                ✕
            </button>
        </div>
    }

    can render_register_form with entry -> div {
        <form className="register-form" onSubmit={(e) => self.handle_register(e)}>
            <div className="form-row">
                <div className="form-group">
                    <label className="form-label">First Name</label>
                    <input 
                        type="text" 
                        className="form-input" 
                        placeholder="First name"
                        name="first_name"
                        required
                    />
                </div>
                
                <div className="form-group">
                    <label className="form-label">Last Name</label>
                    <input 
                        type="text" 
                        className="form-input" 
                        placeholder="Last name"
                        name="last_name"
                        required
                    />
                </div>
            </div>
            
            <div className="form-group">
                <label className="form-label">Email Address</label>
                <input 
                    type="email" 
                    className="form-input" 
                    placeholder="Enter your email"
                    name="email"
                    required
                />
            </div>
            
            <div className="form-group">
                <label className="form-label">Username</label>
                <input 
                    type="text" 
                    className="form-input" 
                    placeholder="Choose a username"
                    name="username"
                    required
                />
            </div>
            
            <div className="form-group">
                <label className="form-label">Password</label>
                <input 
                    type="password" 
                    className="form-input" 
                    placeholder="Create a password"
                    name="password"
                    required
                />
            </div>
            
            <div className="form-group">
                <label className="form-label">Confirm Password</label>
                <input 
                    type="password" 
                    className="form-input" 
                    placeholder="Confirm your password"
                    name="confirm_password"
                    required
                />
            </div>
            
            <div className="form-group">
                <label className="form-label">Learning Goals</label>
                <select className="form-select" name="learning_goals">
                    <option value="">Select your primary goal</option>
                    <option value="career">Career Development</option>
                    <option value="skill">Skill Building</option>
                    <option value="personal">Personal Interest</option>
                    <option value="academic">Academic Study</option>
                </select>
            </div>
            
            <div className="form-options">
                <label className="checkbox-label">
                    <input type="checkbox" name="terms_accepted" required />
                    <span className="checkbox-custom"></span>
                    I agree to the <a href="#" className="terms-link">Terms of Service</a>
                </label>
            </div>
            
            <button type="submit" className="register-submit-btn">
                🚀 Create Account
            </button>
        </form>
    }

    can render_register_footer with entry -> div {
        <div className="modal-footer">
            <p>Already have an account? 
                <a href="#" onClick={() => self.show_login()}>Sign in here</a>
            </p>
        </div>
    }

    can handle_register with entry (event: dict) {
        event.preventDefault();
        
        form_data = new FormData(event.target);
        user_data = {
            "first_name": form_data.get("first_name"),
            "last_name": form_data.get("last_name"),
            "username": form_data.get("username"),  # Added username field
            "email": form_data.get("email"),
            "password": form_data.get("password"),
            "confirm_password": form_data.get("confirm_password"),
            "learning_goals": form_data.get("learning_goals"),
            "terms_accepted": form_data.get("terms_accepted") == "on"
        };
        
        print(f"📝 Attempting registration for: {user_data.email}");
        
        # Validate passwords match
        if (user_data.password != user_data.confirm_password) {
            print("❌ Passwords do not match");
            return;
        }
        
        # Call the main app's register method
        self.perform_register(user_data);
    }

    can perform_register with entry (user_data: dict) {
        try {
            # Direct integration with FastAPI service
            print(f"📝 Registering user: {user_data.email}");
            
            # Create FastAPI service instance
            api_service = services.FastAPIService();
            
            # Call FastAPI register endpoint
            register_response = api_service.register(user_data);
            
            if (register_response["success"]) {
                print("✅ Registration successful");
                self.on_register_success(register_response);
            } else {
                print(f"❌ Registration failed: {register_response.get('error', 'Unknown error')}");
                self.on_register_error(register_response.get('error', 'Registration failed'));
            }
            
        } catch (error) {
            print(f"❌ Registration error: {error}");
            self.on_register_error("Connection error. Please try again.");
        }
        
        # Close modal after processing
        self.close_modal();
    }
    
    # Callback methods for register success/error
    can on_register_success with entry (register_response: dict) {
        print("🎉 Registration successful - redirecting to login");
        # This would show a success message and redirect to login
    }
    
    can on_register_error with entry (error_message: str) {
        print(f"🚨 Registration error: {error_message}");
        # This would show an error message to the user
    }

    can close_modal with entry (event: dict = None) {
        if (event && event.target != event.currentTarget) {
            return;  # Don't close if clicking inside modal
        }
        
        # Remove modal from DOM
        print("📝 Closing register modal");
    }

    can show_login with entry {
        self.close_modal();
        LoginModal.show(self.app_instance);
    }
}

# Forgot Password Modal
obj ForgotPasswordModal {
    has app_instance: dict = None;
    
    can show with entry (app_instance: dict = None) {
        # Store app instance for callbacks
        self.app_instance = app_instance;
        
        <div className="modal-overlay" onClick={(e) => self.close_modal(e)}>
            <div className="modal-content forgot-password-modal" onClick={(e) => e.stopPropagation()}>
                {self.render_modal_header()}
                {self.render_forgot_password_form()}
                {self.render_forgot_password_footer()}
            </div>
        </div>
    }

    can render_modal_header with entry -> div {
        <div className="modal-header">
            <h2>🔑 Forgot Password</h2>
            <button className="modal-close" onClick={() => self.close_modal()}>
                ✕
            </button>
        </div>
    }

    can render_forgot_password_form with entry -> div {
        <form className="forgot-password-form" onSubmit={(e) => self.handle_forgot_password(e)}>
            <div className="form-group">
                <label className="form-label">Email Address</label>
                <input 
                    type="email" 
                    className="form-input" 
                    placeholder="Enter your email address"
                    name="email"
                    required
                />
            </div>
            
            <p className="forgot-password-instructions">
                Enter your email address and we'll send you a link to reset your password.
            </p>
            
            <button type="submit" className="forgot-password-submit-btn">
                📧 Send Reset Link
            </button>
        </form>
    }

    can render_forgot_password_footer with entry -> div {
        <div className="modal-footer">
            <p>Remember your password? 
                <a href="#" onClick={() => self.show_login()}>Sign in here</a>
            </p>
        </div>
    }

    can handle_forgot_password with entry (event: dict) {
        event.preventDefault();
        
        form_data = new FormData(event.target);
        email = form_data.get("email");
        
        print(f"🔑 Sending password reset for: {email}");
        
        # Call the main app's forgot password method
        self.perform_forgot_password(email);
    }

    can perform_forgot_password with entry (email: str) {
        try {
            # Direct integration with FastAPI service
            print(f"🔑 Requesting password reset for: {email}");
            
            # Create FastAPI service instance
            api_service = services.FastAPIService();
            
            # Call FastAPI forgot password endpoint
            forgot_response = api_service.forgot_password(email);
            
            if (forgot_response["success"]) {
                print("✅ Password reset email sent successfully");
                self.on_forgot_password_success(forgot_response);
            } else {
                print(f"❌ Failed to send password reset email: {forgot_response.get('error', 'Unknown error')}");
                self.on_forgot_password_error(forgot_response.get('error', 'Failed to send reset email'));
            }
            
        } catch (error) {
            print(f"❌ Forgot password error: {error}");
            self.on_forgot_password_error("Connection error. Please try again.");
        }
        
        # Close modal after processing
        self.close_modal();
    }
    
    # Callback methods for forgot password success/error
    can on_forgot_password_success with entry (forgot_response: dict) {
        print("🔑 Password reset email sent! Check your inbox.");
        # This would show a success message to user
    }
    
    can on_forgot_password_error with entry (error_message: str) {
        print(f"🚨 Forgot password error: {error_message}");
        # This would show an error message to user
    }

    can close_modal with entry (event: dict = None) {
        if (event && event.target != event.currentTarget) {
            return;  # Don't close if clicking inside modal
        }
        
        # Remove modal from DOM
        print("🔑 Closing forgot password modal");
    }

    can show_login with entry {
        self.close_modal();
        LoginModal.show(self.app_instance);
    }
}

# Password Reset Modal
obj PasswordResetModal {
    has app_instance: dict = None;
    has reset_token: str = "";
    
    can show with entry (app_instance: dict = None, token: str = "") {
        # Store app instance and reset token for callbacks
        self.app_instance = app_instance;
        self.reset_token = token;
        
        <div className="modal-overlay" onClick={(e) => self.close_modal(e)}>
            <div className="modal-content password-reset-modal" onClick={(e) => e.stopPropagation()}>
                {self.render_modal_header()}
                {self.render_password_reset_form()}
                {self.render_password_reset_footer()}
            </div>
        </div>
    }

    can render_modal_header with entry -> div {
        <div className="modal-header">
            <h2>🔒 Reset Password</h2>
            <button className="modal-close" onClick={() => self.close_modal()}>
                ✕
            </button>
        </div>
    }

    can render_password_reset_form with entry -> div {
        <form className="password-reset-form" onSubmit={(e) => self.handle_password_reset(e)}>
            <div className="form-group">
                <label className="form-label">New Password</label>
                <input 
                    type="password" 
                    className="form-input" 
                    placeholder="Enter new password"
                    name="new_password"
                    minLength="8"
                    required
                />
            </div>
            
            <div className="form-group">
                <label className="form-label">Confirm New Password</label>
                <input 
                    type="password" 
                    className="form-input" 
                    placeholder="Confirm new password"
                    name="confirm_password"
                    minLength="8"
                    required
                />
            </div>
            
            <p className="password-requirements">
                Password must be at least 8 characters long and contain letters and numbers.
            </p>
            
            <button type="submit" className="password-reset-submit-btn">
                🔒 Reset Password
            </button>
        </form>
    }

    can render_password_reset_footer with entry -> div {
        <div className="modal-footer">
            <p>Remember your password? 
                <a href="#" onClick={() => self.show_login()}>Sign in here</a>
            </p>
        </div>
    }

    can handle_password_reset with entry (event: dict) {
        event.preventDefault();
        
        form_data = new FormData(event.target);
        new_password = form_data.get("new_password");
        confirm_password = form_data.get("confirm_password");
        
        print(f"🔒 Attempting password reset with token: {self.reset_token[:10]}...");
        
        # Validate passwords match
        if (new_password != confirm_password) {
            print("❌ Passwords do not match");
            return;
        }
        
        # Call the main app's password reset method
        self.perform_password_reset(new_password);
    }

    can perform_password_reset with entry (new_password: str) {
        try {
            # Direct integration with FastAPI service
            print(f"🔒 Resetting password with token: {self.reset_token[:10]}...");
            
            # Create FastAPI service instance
            api_service = services.FastAPIService();
            
            # Call FastAPI reset password endpoint
            reset_response = api_service.reset_password(self.reset_token, new_password);
            
            if (reset_response["success"]) {
                print("✅ Password reset successfully");
                self.on_password_reset_success(reset_response);
            } else {
                print(f"❌ Failed to reset password: {reset_response.get('error', 'Unknown error')}");
                self.on_password_reset_error(reset_response.get('error', 'Failed to reset password'));
            }
            
        } catch (error) {
            print(f"❌ Password reset error: {error}");
            self.on_password_reset_error("Connection error. Please try again.");
        }
        
        # Close modal after processing
        self.close_modal();
    }
    
    # Callback methods for password reset success/error
    can on_password_reset_success with entry (reset_response: dict) {
        print("🔒 Password reset successful! You can now login.");
        # This would show success message and redirect to login
    }
    
    can on_password_reset_error with entry (error_message: str) {
        print(f"🚨 Password reset error: {error_message}");
        # This would show an error message to user
    }

    can close_modal with entry (event: dict = None) {
        if (event && event.target != event.currentTarget) {
            return;  # Don't close if clicking inside modal
        }
        
        # Remove modal from DOM
        print("🔒 Closing password reset modal");
    }

    can show_login with entry {
        self.close_modal();
        LoginModal.show(self.app_instance);
    }
}