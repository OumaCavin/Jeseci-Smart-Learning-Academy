# Test JAC Client Runtime
# Minimal test to verify client functionality

# Simple backend walker
walker test_walker {
    can test_backend with `root entry {
        report {"message": "Backend working", "status": "ok"};
    }
}

# Simple client component
cl import from react { useState } cl {
    def app() -> any {
        [count, setCount] = useState(0);
        
        return (
            <div style={{"padding": "20px", "textAlign": "center"}}>
                <h1>JAC Client Runtime Test</h1>
                <p>Count: {count}</p>
                <button 
                    onClick={lambda -> None { setCount(count + 1); }}
                    style={{
                        "padding": "10px 20px",
                        "backgroundColor": "#3b82f6",
                        "color": "white",
                        "border": "none",
                        "borderRadius": "5px",
                        "cursor": "pointer"
                    }}
                >
                    Click Me
                </button>
                <div style={{"marginTop": "20px"}}>
                    <p>Backend API Test:</p>
                    <button 
                        onClick={lambda -> None { 
                            # This would typically call a backend API
                            alert("Backend API would be called here!");
                        }}
                        style={{
                            "padding": "8px 16px",
                            "backgroundColor": "#10b981",
                            "color": "white",
                            "border": "none",
                            "borderRadius": "5px",
                            "cursor": "pointer",
                            "marginRight": "10px"
                        }}
                    >
                        Test Backend
                    </button>
                </div>
            </div>
        );
    }
}

with entry {
    print("JAC Client Runtime Test Application Ready");
    print("Access at: http://localhost:8000/page/app");
}