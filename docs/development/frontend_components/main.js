import React from 'react';
import ReactDOM from 'react-dom/client';

// Main App Component
function App() {
    const [userData, setUserData] = React.useState(null);
    const [concepts, setConcepts] = React.useState([]);
    const [loading, setLoading] = React.useState(true);

    // Fetch data from JAC backend API
    React.useEffect(() => {
        const fetchData = async () => {
            try {
                // Fetch user progress
                const progressResponse = await fetch('/api/walker/fullstack_user_progress?action=get_progress');
                const progressData = await progressResponse.json();
                
                // Fetch concepts
                const conceptsResponse = await fetch('/api/walker/fullstack_concept_management?action=list');
                const conceptsData = await conceptsResponse.json();
                
                setUserData(progressData.progress);
                setConcepts(conceptsData.concepts || []);
                setLoading(false);
            } catch (error) {
                console.error('Error fetching data:', error);
                setLoading(false);
            }
        };

        fetchData();
    }, []);

    if (loading) {
        return (
            <div style={{ 
                display: 'flex', 
                justifyContent: 'center', 
                alignItems: 'center', 
                height: '100vh',
                fontSize: '1.2em',
                color: '#666'
            }}>
                Loading JAC Application...
            </div>
        );
    }

    return (
        <div style={{ 
            fontFamily: 'Segoe UI, Tahoma, Geneva, Verdana, sans-serif',
            padding: '20px',
            maxWidth: '1200px',
            margin: '0 auto'
        }}>
            {/* Header */}
            <div style={{ 
                textAlign: 'center', 
                marginBottom: '40px',
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                color: 'white',
                padding: '30px',
                borderRadius: '15px'
            }}>
                <h1 style={{ margin: '0 0 10px 0', fontSize: '2.5em' }}>
                    🎓 Jeseci Smart Learning Academy
                </h1>
                <p style={{ margin: 0, fontSize: '1.2em', opacity: 0.9 }}>
                    Full Stack JAC Application with Interactive Frontend
                </p>
            </div>

            {/* User Progress Section */}
            {userData && (
                <div style={{ 
                    background: 'rgba(255, 255, 255, 0.95)',
                    borderRadius: '15px',
                    padding: '30px',
                    marginBottom: '30px',
                    boxShadow: '0 8px 32px rgba(0,0,0,0.1)'
                }}>
                    <h2 style={{ marginTop: 0, color: '#333' }}>📊 Your Learning Progress</h2>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '20px' }}>
                        <div style={{ textAlign: 'center', padding: '15px', background: '#f8f9fa', borderRadius: '10px' }}>
                            <h3 style={{ margin: '0 0 10px 0', color: '#4CAF50' }}>{userData.overall_mastery}%</h3>
                            <p style={{ margin: 0, color: '#666' }}>Overall Mastery</p>
                        </div>
                        <div style={{ textAlign: 'center', padding: '15px', background: '#f8f9fa', borderRadius: '10px' }}>
                            <h3 style={{ margin: '0 0 10px 0', color: '#FF9800' }}>{userData.streak}</h3>
                            <p style={{ margin: 0, color: '#666' }}>Day Streak</p>
                        </div>
                        <div style={{ textAlign: 'center', padding: '15px', background: '#f8f9fa', borderRadius: '10px' }}>
                            <h3 style={{ margin: '0 0 10px 0', color: '#2196F3' }}>{userData.completed}</h3>
                            <p style={{ margin: 0, color: '#666' }}>Concepts Completed</p>
                        </div>
                    </div>
                </div>
            )}

            {/* Learning Concepts Section */}
            <div style={{ 
                background: 'rgba(255, 255, 255, 0.95)',
                borderRadius: '15px',
                padding: '30px',
                boxShadow: '0 8px 32px rgba(0,0,0,0.1)'
            }}>
                <h2 style={{ marginTop: 0, color: '#333' }}>📚 Learning Concepts</h2>
                <div style={{ display: 'grid', gap: '15px' }}>
                    {concepts.map((concept) => (
                        <div key={concept.id} style={{
                            padding: '20px',
                            background: 'white',
                            borderRadius: '10px',
                            boxShadow: '0 4px 15px rgba(0,0,0,0.1)',
                            borderLeft: `5px solid ${
                                concept.status === 'completed' ? '#4CAF50' :
                                concept.status === 'in_progress' ? '#FF9800' : '#ccc'
                            }`
                        }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                                <div style={{ flex: 1 }}>
                                    <h3 style={{ margin: '0 0 10px 0', color: '#333' }}>{concept.title}</h3>
                                    <p style={{ margin: '0 0 15px 0', color: '#666' }}>{concept.description}</p>
                                    <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
                                        <span style={{
                                            padding: '4px 12px',
                                            borderRadius: '20px',
                                            fontSize: '0.8em',
                                            fontWeight: 'bold',
                                            background: concept.status === 'completed' ? '#4CAF50' :
                                                       concept.status === 'in_progress' ? '#FF9800' : '#ccc',
                                            color: 'white'
                                        }}>
                                            {concept.status}
                                        </span>
                                        <span style={{ color: '#666', fontSize: '0.9em' }}>
                                            Difficulty: {concept.difficulty}/5
                                        </span>
                                        <span style={{ color: '#666', fontSize: '0.9em' }}>
                                            Duration: {concept.duration}
                                        </span>
                                    </div>
                                </div>
                                <div style={{ 
                                    textAlign: 'center', 
                                    minWidth: '80px',
                                    marginLeft: '20px'
                                }}>
                                    <div style={{ 
                                        fontSize: '2em', 
                                        fontWeight: 'bold',
                                        color: concept.status === 'completed' ? '#4CAF50' : 
                                              concept.status === 'in_progress' ? '#FF9800' : '#999'
                                    }}>
                                        {concept.progress}%
                                    </div>
                                    <div style={{ fontSize: '0.8em', color: '#666' }}>Progress</div>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            {/* Footer */}
            <div style={{ 
                textAlign: 'center', 
                marginTop: '40px', 
                padding: '20px',
                color: '#666',
                fontSize: '0.9em'
            }}>
                <p>Built with JAC Object-Spatial Programming • React Frontend • Real-time APIs</p>
                <p>© 2025 Cavin Otieno • Jeseci Smart Learning Academy</p>
            </div>
        </div>
    );
}

// Initialize the React application
ReactDOM.createRoot(document.getElementById('root') || document.body).render(
    <React.StrictMode>
        <App />
    </React.StrictMode>
);