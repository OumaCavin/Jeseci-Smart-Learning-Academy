"""
FastAPI Integration Service for JAC Frontend
Handles all API communication with the Jeseci Smart Learning Companion backend
"""

import:py requests;
import:py json;

obj FastAPIService {
    # API Configuration
    has base_url: str = "http://127.0.0.1:8000/api/v1";
    has auth_token: str = "";

    # Set authentication token
    can set_auth_token with entry (token: str) {
        self.auth_token = token;
    }

    # Get authentication headers
    can get_auth_headers with entry -> dict {
        if (self.auth_token) {
            return {
                "Authorization": f"Bearer {self.auth_token}",
                "Content-Type": "application/json"
            };
        }
        return {"Content-Type": "application/json"};
    }

    # Generic API request method
    can make_request with entry (method: str, endpoint: str, data: dict = None, params: dict = None) -> dict {
        try {
            url = f"{self.base_url}{endpoint}";
            headers = {"Content-Type": "application/json"};
            
            if (self.auth_token) {
                headers["Authorization"] = f"Bearer {self.auth_token}";
            }

            print(f"📡 API: {method} {url}");

            response = None;
            if (method == "GET") {
                response = requests.get(url, headers=headers, params=params);
            } elif (method == "POST") {
                response = requests.post(url, headers=headers, json=data);
            } elif (method == "PUT") {
                response = requests.put(url, headers=headers, json=data);
            } elif (method == "DELETE") {
                response = requests.delete(url, headers=headers);
            }

            if (response.status_code >= 200 and response.status_code < 300) {
                return {"success": True, "data": response.json()};
            } else {
                print(f"❌ API Error {response.status_code}: {response.text}");
                return {"success": False, "error": response.text};
            }

        } catch (error) {
            print(f"❌ Connection Error: {error}");
            return {"success": False, "error": str(error)};
        }
    }

    # Mock response methods removed - now using real HTTP requests

    # Authentication endpoints
    can login with entry (login_input: str, password: str) -> dict {
        # The backend expects 'username' and 'password' fields.
        # The 'username' field can contain either a username OR an email.
        login_data = {
            "username": login_input,  # Map the input (email or username) to this field
            "password": password
        };
        
        # Adjust endpoint to match backend (usually /auth/login)
        response = self.make_request("POST", "/auth/login", login_data);
        
        if (response["success"]) {
            data = response["data"];
            if ("access_token" in data) {
                self.set_auth_token(data["access_token"]);
                
                # Prepare login response with user info if available
                login_result = {"success": True, "token": data["access_token"]};
                
                # Include user information if returned by backend
                if ("user" in data) {
                    login_result["user"] = data["user"];
                }
                
                return login_result;
            }
        }
        return response;
    }

    can register with entry (user_data: dict) -> dict {
        return self.make_request("POST", "/auth/register", user_data);
    }

    can logout with entry -> dict {
        self.auth_token = "";
        return {"success": True, "message": "Logged out successfully"};
    }

    # Password reset endpoints
    can forgot_password with entry (email: str) -> dict {
        """Send password reset email"""
        reset_data = {"email": email};
        
        # Adjust endpoint to match backend (usually /auth/forgot-password)
        response = self.make_request("POST", "/auth/forgot-password", reset_data);
        
        return response;
    }

    can reset_password with entry (token: str, new_password: str) -> dict {
        """Reset password using reset token"""
        reset_data = {
            "token": token,
            "new_password": new_password
        };
        
        # Adjust endpoint to match backend (usually /auth/reset-password)
        response = self.make_request("POST", "/auth/reset-password", reset_data);
        
        return response;
    }

    # Concept endpoints
    can get_concepts with entry (search_params: dict = None) -> list {
        endpoint = "/concepts/";
        
        response = self.make_request("GET", endpoint, params=search_params);
        
        if (response["success"]) {
            data = response["data"];
            # Handle pagination wrapper if backend returns {items: [...]}
            if (type(data) == dict and "items" in data) {
                return data["items"];
            } else if (type(data) == list) {
                return data;
            }
        }
        return [];
    }

    can get_concept with entry (concept_id: str) -> dict {
        endpoint = f"/concepts/{concept_id}";
        response = self.make_request("GET", endpoint);
        
        if (response["success"]) {
            return response["data"];
        }
        return {};
    }

    can create_concept with entry (concept_data: dict) -> dict {
        return self.make_request("POST", "/concepts", concept_data);
    }

    can update_concept with entry (concept_id: str, update_data: dict) -> dict {
        endpoint = f"/concepts/{concept_id}";
        return self.make_request("PUT", endpoint, update_data);
    }

    can delete_concept with entry (concept_id: str) -> dict {
        endpoint = f"/concepts/{concept_id}";
        return self.make_request("DELETE", endpoint);
    }

    # Learning Paths endpoints
    can get_learning_paths with entry -> list {
        response = self.make_request("GET", "/learning-paths/");
        
        if (response["success"]) {
            data = response["data"];
            if (type(data) == list) {
                return data;
            }
        }
        return [];
    }

    can get_learning_path with entry (path_id: str) -> dict {
        endpoint = f"/learning-paths/{path_id}";
        response = self.make_request("GET", endpoint);
        
        if (response["success"]) {
            return response["data"];
        }
        return {};
    }

    can create_learning_path with entry (path_data: dict) -> dict {
        return self.make_request("POST", "/learning-paths", path_data);
    }

    # Progress endpoints
    can get_user_progress with entry (user_id: str = None) -> dict {
        endpoint = "/progress/";
        params = None;
        if (user_id) {
            params = {"user_id": user_id};
        }
        
        response = self.make_request("GET", endpoint, params=params);
        
        if (response["success"]) {
            return response["data"];
        }
        return {};
    }

    can update_progress with entry (concept_id: str, progress_data: dict) -> dict {
        endpoint = f"/progress/{concept_id}";
        return self.make_request("PUT", endpoint, progress_data);
    }

    # Analytics endpoints
    can get_analytics with entry (timeframe: str = "7d") -> dict {
        endpoint = "/analytics/";
        params = {"timeframe": timeframe};
        response = self.make_request("GET", endpoint, params=params);
        
        if (response["success"]) {
            return response["data"];
        }
        return {};
    }

    # Mock methods removed - now using real HTTP requests
}
}