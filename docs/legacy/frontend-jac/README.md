# Jeseci Smart Learning Companion - JAC Frontend

A modern web frontend built with **JAC Runtime** that integrates seamlessly with the FastAPI backend for an AI-powered learning experience.

## 🚀 Features

### JAC Runtime Integration
- **Object-Spatial Programming**: Leverages JAC's OSP paradigm for efficient data handling
- **Scale-Agnostic Architecture**: Code runs locally or deploys to cloud without changes
- **Zero-Configuration Deployment**: Automatic API generation and persistence
- **JSX Elements**: Declarative UI syntax similar to React but powered by JAC

### Frontend Capabilities
- **🎯 Adaptive Learning Dashboard**: Personalized learning overview
- **📚 Concept Management**: Browse, search, and manage learning concepts
- **🛤️ Learning Paths**: Structured learning journeys with progress tracking
- **📈 Progress Analytics**: Detailed learning statistics and achievements
- **🔐 Authentication**: Secure login/registration with JWT tokens
- **📱 Responsive Design**: Works seamlessly on desktop and mobile devices

### Backend Integration
- **FastAPI Integration**: Seamless communication with the Python backend
- **Real-time Data**: Live synchronization with PostgreSQL and Neo4j databases
- **JWT Authentication**: Secure token-based authentication
- **Error Handling**: Robust error handling and user feedback

## 🏗️ Architecture

```
frontend-jac/
├── app.jac                 # Main JAC application
├── index.html             # HTML entry point with JAC runtime integration
├── components/            # Reusable JAC components
│   ├── auth_modals.jac   # Login/Register modals
│   └── __init__.jac
├── pages/                # Page components
│   ├── dashboard.jac     # Dashboard page
│   ├── concepts.jac      # Concepts browser
│   ├── learning_paths.jac # Learning paths
│   ├── progress.jac      # Progress tracking
│   └── __init__.jac
├── services/             # API integration services
│   ├── fastapi_service.jac # FastAPI communication
│   └── __init__.jac
└── styles/              # CSS styling
    └── main.css         # Comprehensive styling
```

## 🛠️ Setup and Installation

### Prerequisites
- Python 3.12+
- JAC Runtime (`jaclang`)
- Running FastAPI backend (on port 8000)

### 1. Install JAC Runtime
```bash
pip install jaclang
```

### 2. Verify Installation
```bash
jac --version
```

### 3. Start the Frontend
```bash
# Option 1: Simple HTTP server
python -m http.server 8080

# Option 2: Using Node.js serve (if available)
npx serve .

# Option 3: Using any other static file server
```

### 4. Access the Application
Open your browser and navigate to:
- **Frontend**: http://localhost:8080
- **Backend API**: http://127.0.0.1:8000
- **API Documentation**: http://127.0.0.1:8000/docs

## 🎮 Usage Guide

### 1. Welcome Page
- View application features and capabilities
- Quick access to login/registration
- Backend connectivity status

### 2. Authentication
- **Login**: Secure authentication with JWT tokens
- **Registration**: Create new learning accounts
- **Session Management**: Persistent login sessions

### 3. Dashboard
- **Learning Overview**: Quick stats and progress summary
- **Recent Activity**: Latest learning activities
- **Recommendations**: AI-powered learning suggestions
- **Quick Actions**: Fast access to common tasks

### 4. Concepts Management
- **Browse Concepts**: Explore available learning concepts
- **Search & Filter**: Find concepts by category, domain, difficulty
- **Concept Details**: View comprehensive concept information
- **Learning Progress**: Track mastery and confidence scores

### 5. Learning Paths
- **Structured Journeys**: Pre-designed learning paths
- **Progress Tracking**: Visual progress indicators
- **Path Creation**: Custom learning path creation
- **Completion Tracking**: Detailed path analytics

### 6. Progress Analytics
- **Detailed Statistics**: Comprehensive learning metrics
- **Performance Trends**: Visual progress charts
- **Achievement System**: Unlockable badges and milestones
- **Streak Tracking**: Learning consistency monitoring

## 🔧 Development

### Running JAC Code
```bash
# Run a specific JAC file
jac run app.jac

# Serve JAC application
jac serve
```

### Backend API Integration
The frontend communicates with your FastAPI backend through:

- **Authentication**: `/api/v1/auth/*`
- **Concepts**: `/api/v1/concepts/*`
- **Learning Paths**: `/api/v1/learning-paths/*`
- **Progress**: `/api/v1/progress/*`
- **Analytics**: `/api/v1/analytics/*`

### Customization
- **Styling**: Modify `styles/main.css` for visual changes
- **Components**: Add new components in `components/`
- **Pages**: Create new pages in `pages/`
- **Services**: Extend API integration in `services/`

## 🌟 JAC Runtime Benefits

### 1. **Scale-Agnostic Architecture**
```jac
# Same code runs locally and in cloud
obj LearningApp {
    can process_learning_data with entry {
        # Works identically in all environments
    }
}
```

### 2. **Object-Spatial Programming**
```jac
# Data and computation co-located
obj Concept {
    has concept_data: dict;
    
    can analyze_with entry {
        # Processing happens where data exists
    }
}
```

### 3. **Automatic API Generation**
```jac
# Walkers become REST endpoints automatically
walker concept_manager {
    can create_concept with entry {
        # Automatically exposes POST /concepts
    }
}
```

### 4. **Zero-Configuration Deployment**
```bash
# One command deploys everything
jac serve
# Automatically handles:
# - API generation
# - Database persistence  
# - Web server setup
# - Load balancing
```

## 🔗 Integration with FastAPI

### Authentication Flow
1. User enters credentials in JAC modal
2. JAC frontend calls FastAPI `/auth/login`
3. FastAPI returns JWT token
4. JAC stores token and sets auth headers
5. All subsequent requests include authentication

### Data Synchronization
1. JAC frontend requests data from FastAPI
2. FastAPI queries PostgreSQL + Neo4j
3. Data returned to JAC frontend
4. JAC renders components with real-time data

### Error Handling
- Network errors: Graceful fallback to cached data
- Authentication errors: Redirect to login
- API errors: User-friendly error messages
- Loading states: Smooth loading animations

## 🚀 Deployment

### Local Development
```bash
# Terminal 1: Start FastAPI backend
cd jeseci-smart-learning-companion
python main.py

# Terminal 2: Start JAC frontend
cd frontend-jac
python -m http.server 8080
```

### Production Deployment
1. **Frontend**: Deploy static files to CDN or web server
2. **Backend**: Deploy FastAPI to cloud platform (AWS, GCP, Azure)
3. **Database**: Configure PostgreSQL and Neo4j cloud instances
4. **Environment**: Set production environment variables

## 📊 Performance

### Optimization Features
- **Lazy Loading**: Components load on demand
- **Caching**: Intelligent data caching strategies
- **Bundle Optimization**: Minimal JavaScript footprint
- **Progressive Enhancement**: Works without JavaScript

### Monitoring
- **Real-time Metrics**: Learning progress tracking
- **Performance Analytics**: Frontend performance monitoring
- **Error Tracking**: Comprehensive error logging
- **User Analytics**: Learning behavior insights

## 🤝 Contributing

1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature/amazing-feature`
3. **Commit changes**: `git commit -m 'Add amazing feature'`
4. **Push to branch**: `git push origin feature/amazing-feature`
5. **Open Pull Request**

### Development Guidelines
- Follow JAC coding conventions
- Write comprehensive tests
- Update documentation
- Ensure responsive design
- Maintain accessibility standards

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🎯 Roadmap

### Phase 1: Core Features ✅
- [x] JAC frontend framework
- [x] FastAPI integration
- [x] Authentication system
- [x] Basic UI components

### Phase 2: Enhanced Functionality
- [ ] Advanced JAC runtime features
- [ ] Real-time collaboration
- [ ] Mobile app integration
- [ ] AI-powered recommendations

### Phase 3: Advanced Features
- [ ] Voice learning integration
- [ ] AR/VR learning modules
- [ ] Advanced analytics dashboard
- [ ] Multi-language support

## 📞 Support

- **Documentation**: Check the JAC language docs at [jac-lang.org](https://jac-lang.org)
- **Issues**: Report bugs via GitHub issues
- **Community**: Join the Jaseci community discussions
- **Backend**: Refer to FastAPI documentation for API details

---

**Built with ❤️ using JAC Runtime and FastAPI**