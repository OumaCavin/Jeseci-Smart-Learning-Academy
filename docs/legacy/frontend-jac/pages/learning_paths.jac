"""
Learning Paths Page Component
Display and manage personalized learning paths
"""

obj LearningPathsPage {
    
    can render with entry (paths_data: list) -> div {
        # Calculate stats dynamically from paths_data
        active_count = 0;
        total_progress = 0.0;
        total_time_spent = 0;
        total_time_remaining = 0;
        
        for (path in paths_data) {
            # Progress field not stored in learning_paths table - needs API calculation
            # For now, use fallback logic since we can't calculate from frontend
            progress = path.get("progress", None);
            
            # If no progress data, use intelligent fallback based on available fields
            if (progress == None) {
                # Check for any completed concepts count or time spent as progress indicator
                concepts_count = path.get("concepts_count", 0);
                completed_count = path.get("concepts_completed", 0);
                time_spent = path.get("time_spent_hours", 0);
                
                if (concepts_count > 0 and completed_count > 0) {
                    # Use concept completion ratio if available
                    progress = float(completed_count) / concepts_count;
                } elif (time_spent > 0) {
                    # Estimate progress based on time spent (10 hours = 25% progress)
                    estimated_duration_hours = path.get("estimated_duration", 0) / 60.0;
                    if (estimated_duration_hours > 0) {
                        progress = min(time_spent / estimated_duration_hours, 0.9);  # Cap at 90%
                    } else {
                        progress = 0.1;  # Small progress if any time spent
                    }
                } else {
                    progress = 0.0;  # No progress data available
                }
            }
            
            # Ensure progress is within valid range (0.0 to 1.0)
            progress = max(0.0, min(progress, 1.0));
            
            # TODO: Remove this fallback logic when backend provides proper progress calculation
            # Progress should be calculated by API from UserProgress data, not by frontend
            
            if (progress > 0 and progress < 1) { 
                active_count += 1; 
            }
            total_progress += progress;
            
            # Extract time estimates if available (convert minutes to hours)
            time_spent_hours = path.get("time_spent_hours", 0);
            estimated_duration_minutes = path.get("estimated_duration", 0);
            estimated_duration_hours = estimated_duration_minutes / 60.0;  # Convert to hours
            time_remaining_hours = estimated_duration_hours - time_spent_hours;
            total_time_spent += time_spent_hours;
            total_time_remaining += max(0, time_remaining_hours);
        }
        
        avg_progress = int((total_progress / paths_data.length * 100)) if paths_data.length > 0 else 0;

        <div className="learning-paths-page">
            # Pass calculated stats to header
            {self.render_paths_header(active_count, avg_progress)} 
            {self.render_paths_overview(avg_progress, total_time_spent, total_time_remaining)}
            {self.render_paths_grid(paths_data)}
            {self.render_create_path_section()}
        </div>
    }

    can render_paths_header with entry (active_count: int, avg_progress: int) -> div {
        <div className="paths-header">
            <h2>🛤️ Learning Paths</h2>
            <p>Structured journeys to master new skills and concepts</p>
            <div className="path-stats">
                <span className="stat">{active_count} Active Paths</span>
                <span className="stat">{avg_progress}% Overall Progress</span>
            </div>
        </div>
    }

    can render_paths_overview with entry (avg_progress: int, time_spent: float, time_remaining: float) -> div {
        <div className="paths-overview">
            <div className="overview-card">
                <h3>📈 Progress Overview</h3>
                <div className="progress-ring">
                    <svg className="progress-circle" width="120" height="120">
                        <circle className="progress-bg" cx="60" cy="60" r="50" />
                        <circle className="progress-bar" cx="60" cy="60" r="50" />
                    </svg>
                    <div className="progress-text">
                        <span className="progress-percentage">{avg_progress}%</span>
                        <span className="progress-label">Complete</span>
                    </div>
                </div>
            </div>
            
            <div className="overview-card">
                <h3>⏱️ Time Investment</h3>
                <div className="time-stats">
                    <div className="time-item">
                        <span className="time-value">{time_spent}h</span>
                        <span className="time-label">Spent</span>
                    </div>
                    <div className="time-item">
                        <span className="time-value">{time_remaining}h</span>
                        <span className="time-label">Remaining</span>
                    </div>
                </div>
            </div>
        </div>
    }

    can render_paths_grid with entry (paths_data: list) -> div {
        <div className="paths-grid">
            {self.render_path_cards(paths_data)}
        </div>
    }

    can render_path_cards with entry (paths_data: list) -> list {
        path_cards = [];
        
        for (path in paths_data) {
            path_cards.append(
                self.render_path_card(path)
            );
        }
        
        return path_cards;
    }

    can render_path_card with entry (path: dict) -> div {
        <div className="path-card">
            {self.render_path_header(path)}
            {self.render_path_body(path)}
            {self.render_path_footer(path)}
        </div>
    }

    can render_path_header with entry (path: dict) -> div {
        <div className="path-header">
            <div className="path-icon">
                # Fallback to difficulty_level if difficulty is missing
                difficulty = path.get("difficulty_level", path.get("difficulty", "beginner"));
                {self.get_path_icon(difficulty)}
            </div>
            <div className="path-info">
                <h3 className="path-title">{path.get("name", "Unknown Path")}</h3>
                <div className="path-meta">
                    <span className="path-difficulty">{path.get("difficulty_level", path.get("difficulty", "Unknown"))}</span>
                    <span className="path-duration">{path.get("estimated_duration", "Unknown")} min</span>
                </div>
            </div>
        </div>
    }

    can render_path_body with entry (path: dict) -> div {
        <div className="path-body">
            <p className="path-description">{path.get("description", "No description available")}</p>
            {self.render_path_progress(path)}
            {self.render_path_concepts(path)}
        </div>
    }

    can render_path_progress with entry (path: dict) -> div {
        progress = path.get("progress", 0);
        <div className="path-progress-section">
            <div className="progress-header">
                <span className="progress-label">Progress</span>
                <span className="progress-percentage">{int(progress * 100)}%</span>
            </div>
            <div className="progress-bar-container">
                <div className="progress-bar">
                    <div 
                        className="progress-fill" 
                        style={`width: ${progress * 100}%`}
                    ></div>
                </div>
            </div>
        </div>
    }

    can render_path_concepts with entry (path: dict) -> div {
        concepts_count = path.get("concepts_count", 0);
        completed_count = int(concepts_count * path.get("progress", 0));
        
        <div className="path-concepts">
            <div className="concepts-stats">
                <span className="concepts-completed">{completed_count}</span>
                <span className="concepts-separator">/</span>
                <span className="concepts-total">{concepts_count}</span>
                <span className="concepts-label">concepts</span>
            </div>
            <div className="concepts-breakdown">
                <div className="concept-status completed">Completed</div>
                <div className="concept-status in-progress">In Progress</div>
                <div className="concept-status not-started">Not Started</div>
            </div>
        </div>
    }

    can render_path_footer with entry (path: dict) -> div {
        <div className="path-footer">
            <div className="path-actions">
                <button className="action-btn primary" onClick={() => self.continue_path(path)}>
                    {self.get_continue_button_text(path)}
                </button>
                <button className="action-btn secondary" onClick={() => self.view_path_details(path)}>
                    📋 Details
                </button>
                <button className="action-btn tertiary" onClick={() => self.path_options(path)}>
                    ⋯
                </button>
            </div>
            <div className="path-metadata">
                <span className="last-activity">Last activity: 2 days ago</span>
            </div>
        </div>
    }

    can render_create_path_section with entry -> div {
        <div className="create-path-section">
            <div className="create-path-card">
                <div className="create-path-icon">➕</div>
                <h3>Create Custom Path</h3>
                <p>Design your own learning journey</p>
                <button className="create-path-btn" onClick={() => self.show_create_path_modal()}>
                    Create New Path
                </button>
            </div>
        </div>
    }

    # Utility methods
    can get_path_icon with entry (difficulty: str) -> str {
        match (difficulty.lower()) {
            case "beginner": return "🌱";
            case "intermediate": return "🌿";
            case "advanced": return "🌳";
            default: return "📚";
        }
    }

    can get_continue_button_text with entry (path: dict) -> str {
        progress = path.get("progress", 0);
        if (progress == 0) {
            return "🚀 Start Path";
        } else if (progress < 1) {
            return "▶️ Continue";
        } else {
            return "✅ Completed";
        }
    }

    # Event handlers
    can continue_path with entry (path: dict) {
        print(f"▶️ Continuing path: {path.get('name')}");
        # Navigate to path continuation
    }

    can view_path_details with entry (path: dict) {
        print(f"📋 Viewing details for: {path.get('name')}");
        # Navigate to path details page
    }

    can path_options with entry (path: dict) {
        print(f"⋯ Path options for: {path.get('name')}");
        # Show path options menu
    }

    can show_create_path_modal with entry {
        print("➕ Opening create path modal...");
        # Show create path modal
    }
}