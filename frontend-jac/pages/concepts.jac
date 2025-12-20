"""
Concepts Page Component
Display and manage learning concepts with search and filtering
"""

obj ConceptsPage {
    
    can render with entry (concepts_data: list) -> div {
        <div className="concepts-page">
            {self.render_concepts_header()}
            {self.render_search_and_filters()}
            {self.render_concepts_grid(concepts_data)}
            {self.render_pagination()}
        </div>
    }

    can render_concepts_header with entry -> div {
        <div className="concepts-header">
            <h2>📚 Learning Concepts</h2>
            <p>Explore and master new concepts in your learning journey</p>
            <button className="create-concept-btn" onClick={() => self.show_create_concept_modal()}>
                ➕ Create Concept
            </button>
        </div>
    }

    can render_search_and_filters with entry -> div {
        <div className="search-filters-section">
            <div className="search-bar">
                <input 
                    type="text" 
                    placeholder="Search concepts..." 
                    className="search-input"
                    onChange={(e) => self.handle_search(e.target.value)}
                />
                <button className="search-btn" onClick={() => self.perform_search()}>
                    🔍
                </button>
            </div>
            
            <div className="filters-row">
                {self.render_filter_dropdown("Category", ["All", "Programming", "Mathematics", "Science", "Arts"])}
                {self.render_filter_dropdown("Domain", ["All", "Computer Science", "Physics", "Chemistry", "Biology"])}
                {self.render_filter_dropdown("Difficulty", ["All", "Beginner", "Intermediate", "Advanced"])}
                {self.render_filter_dropdown("Status", ["All", "Not Started", "In Progress", "Completed"])}
            </div>
        </div>
    }

    can render_filter_dropdown with entry (label: str, options: list) -> div {
        <div className="filter-dropdown">
            <label className="filter-label">{label}</label>
            <select className="filter-select" onChange={(e) => self.handle_filter_change(label, e.target.value)}>
                {self.render_filter_options(options)}
            </select>
        </div>
    }

    can render_filter_options with entry (options: list) -> list {
        option_elements = [];
        for (option in options) {
            option_elements.append(
                <option value={option.toLowerCase().replace(" ", "_")}>{option}</option>
            );
        }
        return option_elements;
    }

    can render_concepts_grid with entry (concepts_data: list) -> div {
        <div className="concepts-grid">
            {self.render_concept_cards(concepts_data)}
        </div>
    }

    can render_concept_cards with entry (concepts_data: list) -> list {
        concept_cards = [];
        
        for (concept in concepts_data) {
            concept_cards.append(
                self.render_concept_card(concept)
            );
        }
        
        if (concepts_data.length == 0) {
            concept_cards.append(self.render_no_concepts_message());
        }
        
        return concept_cards;
    }

    can render_concept_card with entry (concept: dict) -> div {
        <div className="concept-card">
            {self.render_concept_header(concept)}
            {self.render_concept_body(concept)}
            {self.render_concept_footer(concept)}
        </div>
    }

    can render_concept_header with entry (concept: dict) -> div {
        <div className="concept-header">
            <h3 className="concept-title">{concept.get("display_name", "Unknown")}</h3>
            <div className="concept-meta">
                <span className="concept-category">{concept.get("category", "General")}</span>
                <span className="concept-difficulty">{concept.get("difficulty_level", "Unknown")}</span>
            </div>
        </div>
    }

    can render_concept_body with entry (concept: dict) -> div {
        <div className="concept-body">
            <p className="concept-description">{concept.get("description", "No description available")}</p>
            {self.render_concept_stats(concept)}
            {self.render_concept_tags(concept)}
        </div>
    }

    can render_concept_stats with entry (concept: dict) -> div {
        <div className="concept-stats">
            <div className="stat-item">
                <span className="stat-label">Mastery:</span>
                <div className="progress-bar">
                    <div 
                        className="progress-fill" 
                        style={`width: ${(concept.get("mastery_score", 0) * 100)}%`}
                    ></div>
                </div>
                <span className="stat-value">{int(concept.get("mastery_score", 0) * 100)}%</span>
            </div>
            <div className="stat-item">
                <span className="stat-label">Confidence:</span>
                <div className="confidence-indicator">
                    <div 
                        className="confidence-dot" 
                        style={`background-color: ${self.get_confidence_color(concept.get("confidence_score", 0))}`}
                    ></div>
                    <span className="stat-value">{int(concept.get("confidence_score", 0) * 100)}%</span>
                </div>
            </div>
        </div>
    }

    can render_concept_tags with entry (concept: dict) -> div {
        tags = concept.get("key_terms", []);
        if (tags.length > 0) {
            <div className="concept-tags">
                {self.render_concept_tag_list(tags)}
            </div>
        }
    }

    can render_concept_tag_list with entry (tags: list) -> list {
        tag_elements = [];
        for (tag in tags[:5]):  # Show max 5 tags
            tag_elements.append(
                <span className="concept-tag">{tag}</span>
            );
        return tag_elements;
    }

    can render_concept_footer with entry (concept: dict) -> div {
        <div className="concept-footer">
            <div className="concept-actions">
                <button className="action-btn primary" onClick={() => self.start_learning(concept)}>
                    🚀 Start Learning
                </button>
                <button className="action-btn secondary" onClick={() => self.view_details(concept)}>
                    👁️ View Details
                </button>
                <button className="action-btn tertiary" onClick={() => self.bookmark_concept(concept)}>
                    🔖
                </button>
            </div>
            <div className="concept-usage">
                <span className="usage-frequency">Used {concept.get("usage_frequency", 0) * 100}% of learners</span>
            </div>
        </div>
    }

    can render_no_concepts_message with entry -> div {
        <div className="no-concepts-message">
            <div className="empty-state">
                <div className="empty-icon">📚</div>
                <h3>No Concepts Found</h3>
                <p>Try adjusting your search criteria or filters</p>
                <button className="cta-btn" onClick={() => self.clear_filters()}>
                    Clear Filters
                </button>
            </div>
        </div>
    }

    can render_pagination with entry -> div {
        <div className="pagination-section">
            <div className="pagination-info">
                <span>Showing 1-10 of 45 concepts</span>
            </div>
            <div className="pagination-controls">
                <button className="pagination-btn" disabled>⬅️ Previous</button>
                <button className="pagination-btn active">1</button>
                <button className="pagination-btn">2</button>
                <button className="pagination-btn">3</button>
                <button className="pagination-btn">4</button>
                <button className="pagination-btn">5</button>
                <button className="pagination-btn">➡️ Next</button>
            </div>
        </div>
    }

    # Utility methods
    can get_confidence_color with entry (confidence_score: float) -> str {
        if (confidence_score >= 0.8) return "#4CAF50";  # Green
        if (confidence_score >= 0.6) return "#FF9800";  # Orange
        return "#F44336";  # Red
    }

    # Event handlers
    can handle_search with entry (query: str) {
        print(f"🔍 Searching for: {query}");
        # Implement search logic
    }

    can handle_filter_change with entry (filter_type: str, value: str) {
        print(f"🔧 Filter changed: {filter_type} = {value}");
        # Implement filter logic
    }

    can perform_search with entry {
        print("🔍 Performing search...");
        # Implement search execution
    }

    can clear_filters with entry {
        print("🧹 Clearing all filters...");
        # Implement filter clearing
    }

    can show_create_concept_modal with entry {
        print("➕ Opening create concept modal...");
        # Implement create concept modal
    }

    # Action handlers
    can start_learning with entry (concept: dict) {
        print(f"🚀 Starting learning for: {concept.get('display_name')}");
        # Navigate to learning interface
    }

    can view_details with entry (concept: dict) {
        print(f"👁️ Viewing details for: {concept.get('display_name')}");
        # Navigate to concept details page
    }

    can bookmark_concept with entry (concept: dict) {
        print(f"🔖 Bookmarking: {concept.get('display_name')}");
        # Implement bookmark functionality
    }
}