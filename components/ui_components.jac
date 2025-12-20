"""
UI Components Module
Reusable UI components for the Smart Learning Companion
Author: Cavin Otieno
"""

# Statistics Card Component
obj StatCard {
    has title: str;
    has value: str;
    has icon: str = "chart-bar";
    has trend: str = "stable";  # up, down, stable
    has color: str = "blue";
    
    def get_trend_icon() -> str {
        if self.trend == "up" {
            return "↗";
        }
        if self.trend == "down" {
            return "↘";
        }
        return "→";
    }
    
    def get_color_class() -> str {
        return f"stat-card-{self.color}";
    }
}

# Recent Activity Component
obj RecentActivity {
    has activities: list;
    has max_items: int = 10;
    has placeholder: str = "No recent activities";
    
    def get_recent_activities() -> list {
        if len(self.activities) == 0 {
            return [self.placeholder];
        }
        return self.activities[:self.max_items];
    }
}

# Chat Interface Component
obj ChatInterface {
    has messages: list;
    has quick_prompts: list;
    has is_loading: bool = false;
    has placeholder: str = "Ask me anything about your learning...";
    
    def add_message(message: str, sender: str) -> any {
        self.messages.append({"message": message, "sender": sender, "timestamp": "2025-12-09 16:15:37"});
        return true;
    }
    
    def set_loading(loading: bool) -> any {
        self.is_loading = loading;
        return true;
    }
    
    def get_quick_prompts() -> list {
        return self.quick_prompts;
    }
}

# Progress Bar Component
obj ProgressBar {
    has progress: float = 0.0;
    has color: str = "blue";
    has show_percentage: bool = true;
    has label: str = "";
    
    def update_progress(new_progress: float) -> any {
        self.progress = max(0.0, min(100.0, new_progress));
        return true;
    }
    
    def get_percentage() -> str {
        return f"{int(self.progress)}%";
    }
}

# Modal Component
obj Modal {
    has title: str;
    has content: str;
    has actions: list;
    has is_open: bool = false;
    
    def open() -> any {
        self.is_open = true;
        return true;
    }
    
    def close() -> any {
        self.is_open = false;
        return true;
    }
    
    def toggle() -> any {
        self.is_open = not self.is_open;
        return true;
    }
}