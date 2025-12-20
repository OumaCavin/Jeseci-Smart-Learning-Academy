"""
Progress Page Component
Detailed learning progress tracking and analytics
"""

obj ProgressPage {
    
    # Accept progress_data dictionary for dynamic rendering
    can render with entry (progress_data: dict) -> div {
        <div className="progress-page">
            {self.render_progress_header()}
            {self.render_progress_overview(progress_data)}
            {self.render_detailed_analytics(progress_data)}
            {self.render_learning_streak(progress_data)}
            {self.render_achievements_section(progress_data)}
        </div>
    }

    can render_progress_header with entry -> div {
        <div className="progress-header">
            <h2>📈 Learning Progress</h2>
            <p>Track your learning journey and achievements</p>
            <div className="progress-controls">
                <select className="timeframe-selector" onChange={(e) => self.change_timeframe(e.target.value)}>
                    <option value="7d">Last 7 days</option>
                    <option value="30d">Last 30 days</option>
                    <option value="90d">Last 3 months</option>
                    <option value="1y">Last year</option>
                </select>
                <button className="export-btn" onClick={() => self.export_progress()}>
                    📊 Export
                </button>
            </div>
        </div>
    }

    can render_progress_overview with entry (progress_data: dict) -> div {
        # Extract dynamic data with safe defaults
        total_concepts = progress_data.get("total_concepts", 0);
        completed_concepts = progress_data.get("completed_concepts", 0);
        in_progress_concepts = progress_data.get("in_progress_concepts", 0);
        mastery_average = int(progress_data.get("mastery_average", 0) * 100);
        
        <div className="progress-overview">
            <div className="overview-stats-grid">
                {self.render_overview_stat("Total Concepts", f"{total_concepts}", "📚", "#4CAF50")}
                {self.render_overview_stat("Completed", f"{completed_concepts}", "✅", "#2196F3")}
                {self.render_overview_stat("In Progress", f"{in_progress_concepts}", "🔄", "#FF9800")}
                {self.render_overview_stat("Mastery Avg", f"{mastery_average}%", "🎯", "#9C27B0")}
            </div>
        </div>
    }

    can render_overview_stat with entry (title: str, value: str, icon: str, color: str) -> div {
        <div className="overview-stat-card" style={`border-top: 3px solid ${color}`}>
            <div className="stat-icon">{icon}</div>
            <div className="stat-content">
                <h3 className="stat-value">{value}</h3>
                <p className="stat-title">{title}</p>
            </div>
        </div>
    }

    can render_detailed_analytics with entry (progress_data: dict) -> div {
        # Extract performance metrics with safe defaults
        mastery_improvement = progress_data.get("mastery_improvement", 0);
        confidence_growth = progress_data.get("confidence_growth", 0);
        engagement_rate = int(progress_data.get("engagement_rate", 0) * 100);
        retention_rate = int(progress_data.get("retention_rate", 0) * 100);
        
        # Get activity data for chart
        activity_data = progress_data.get("daily_activity", []);
        
        <div className="detailed-analytics">
            <div className="analytics-section">
                <h3>📊 Learning Activity</h3>
                <div className="activity-chart">
                    {self.render_activity_chart(activity_data)}
                </div>
            </div>
            
            <div className="analytics-section">
                <h3>🎯 Performance Metrics</h3>
                <div className="performance-metrics">
                    {self.render_performance_metric("Mastery Improvement", f"{mastery_improvement:+}%", "#4CAF50")}
                    {self.render_performance_metric("Confidence Growth", f"{confidence_growth:+}%", "#2196F3")}
                    {self.render_performance_metric("Engagement Rate", f"{engagement_rate}%", "#FF9800")}
                    {self.render_performance_metric("Retention Rate", f"{retention_rate}%", "#9C27B0")}
                </div>
            </div>
        </div>
    }

    can render_activity_chart with entry (activity_data: list) -> div {
        # Default activity data if none provided
        if (activity_data.length == 0) {
            activity_data = [
                {"day": "Mon", "minutes": 45, "color": "#4CAF50"},
                {"day": "Tue", "minutes": 60, "color": "#2196F3"},
                {"day": "Wed", "minutes": 30, "color": "#FF9800"},
                {"day": "Thu", "minutes": 75, "color": "#9C27B0"},
                {"day": "Fri", "minutes": 55, "color": "#F44336"},
                {"day": "Sat", "minutes": 40, "color": "#607D8B"},
                {"day": "Sun", "minutes": 25, "color": "#795548"}
            ];
        }
        
        <div className="activity-chart-container">
            <div className="chart-bars">
                for (activity in activity_data) {
                    {self.render_chart_bar(activity.get("day", ""), activity.get("minutes", 0), activity.get("color", "#4CAF50"))}
                }
            </div>
            <div className="chart-labels">
                <span>Daily Learning Minutes</span>
            </div>
        </div>
    }

    can render_chart_bar with entry (day: str, minutes: int, color: str) -> div {
        height_percentage = (minutes / 80) * 100;  # Max 80 minutes for scale
        
        <div className="chart-bar-container">
            <div 
                className="chart-bar" 
                style={`height: ${height_percentage}%; background-color: ${color}`}
                title={`${day}: ${minutes} minutes`}
            ></div>
            <div className="chart-bar-label">{day}</div>
        </div>
    }

    can render_performance_metric with entry (label: str, value: str, color: str) -> div {
        <div className="performance-metric" style={`border-left: 3px solid ${color}`}>
            <div className="metric-value">{value}</div>
            <div className="metric-label">{label}</div>
            <div className="metric-trend">↗️</div>
        </div>
    }

    can render_learning_streak with entry (progress_data: dict) -> div {
        # Extract streak data with safe defaults
        current_streak = progress_data.get("streak_days", 0);
        longest_streak = progress_data.get("longest_streak", 0);
        streak_calendar = progress_data.get("streak_calendar", []);
        
        <div className="learning-streak-section">
            <h3>🔥 Learning Streak</h3>
            <div className="streak-container">
                <div className="streak-main">
                    <div className="streak-number">{current_streak}</div>
                    <div className="streak-label">Days</div>
                </div>
                <div className="streak-calendar">
                    {self.render_streak_calendar(streak_calendar)}
                </div>
            </div>
            <div className="streak-info">
                <p>Keep it up! You're on a {current_streak}-day learning streak.</p>
                <p>Longest streak: {longest_streak} days</p>
            </div>
        </div>
    }

    can render_streak_calendar with entry (streak_data: list) -> div {
        <div className="streak-calendar-grid">
            {self.render_streak_days(streak_data)}
        </div>
    }

    can render_streak_days with entry (streak_data: list) -> list {
        # Default streak data if none provided
        if (streak_data.length == 0) {
            streak_data = [True, True, True, False, True, True, True];  # Example data
        }
        
        days = ["S", "M", "T", "W", "T", "F", "S"];
        
        day_elements = [];
        for (i, day in enumerate(days)) {
            is_active = streak_data[i] if i < streak_data.length else False;
            day_elements.append(
                <div className={`streak-day ${is_active ? 'active' : 'inactive'}`}>
                    {day}
                </div>
            );
        }
        return day_elements;
    }

    can render_achievements_section with entry (progress_data: dict) -> div {
        # Get achievements data or use default
        achievements = progress_data.get("achievements", []);
        
        # Default achievements if none provided
        if (achievements.length == 0) {
            achievements = [
                {"title": "First Concept", "description": "Completed your first learning concept", "icon": "🌟", "earned": True},
                {"title": "Week Warrior", "description": "Maintained a 7-day learning streak", "icon": "🔥", "earned": True},
                {"title": "Consistent Learner", "description": "Learned for 30 days straight", "icon": "📚", "earned": False},
                {"title": "Knowledge Seeker", "description": "Explored 50 different concepts", "icon": "🎯", "earned": False},
                {"title": "Speed Learner", "description": "Completed 5 concepts in one day", "icon": "⚡", "earned": False},
                {"title": "Master Apprentice", "description": "Achieved 80%+ mastery in 10 concepts", "icon": "👑", "earned": False}
            ];
        }
        
        <div className="achievements-section">
            <h3>🏆 Achievements</h3>
            <div className="achievements-grid">
                for (achievement in achievements) {
                    {self.render_achievement_card(
                        achievement.get("title", ""),
                        achievement.get("description", ""),
                        achievement.get("icon", "🏆"),
                        achievement.get("earned", False)
                    )}
                }
            </div>
        </div>
    }

    can render_achievement_card with entry (title: str, description: str, icon: str, earned: bool) -> div {
        <div className={`achievement-card ${earned ? 'earned' : 'locked'}`}>
            <div className="achievement-icon">{icon}</div>
            <div className="achievement-content">
                <h4 className="achievement-title">{title}</h4>
                <p className="achievement-description">{description}</p>
            </div>
            <div className="achievement-status">
                {earned ? "✅" : "🔒"}
            </div>
        </div>
    }

    # Event handlers
    can change_timeframe with entry (timeframe: str) {
        print(f"📅 Changing timeframe to: {timeframe}");
        # Reload progress data for new timeframe
    }

    can export_progress with entry {
        print("📊 Exporting progress data...");
        # Generate and download progress report
    }
}