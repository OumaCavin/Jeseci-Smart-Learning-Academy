import React from 'react'

function App() {
  return (
    <div style={{
      fontFamily: 'Arial, sans-serif',
      margin: 0,
      padding: 20,
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      minHeight: '100vh',
      color: '#333'
    }}>
      <div style={{
        maxWidth: '1200px',
        margin: '0 auto'
      }}>
        <div style={{
          textAlign: 'center',
          color: 'white',
          marginBottom: 40,
          padding: 40,
          background: 'rgba(255, 255, 255, 0.1)',
          borderRadius: 20
        }}>
          <h1 style={{ fontSize: '3em', margin: '0 0 10px 0' }}>
            🎓 Jeseci Smart Learning Academy
          </h1>
          <p>Full Stack JAC Application with Object-Spatial Programming</p>
        </div>

        <div style={{
          background: 'rgba(255, 255, 255, 0.95)',
          borderRadius: 20,
          padding: 30,
          margin: '20px 0',
          boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)'
        }}>
          <h2>✅ Application Status: Operational</h2>
          <p><strong>Version:</strong> 5.0.0</p>
          <p><strong>Architecture:</strong> JAC OSP with Static HTML Frontend</p>
          <p><strong>Backend:</strong> Object-Spatial Programming APIs</p>
          
          <div style={{ textAlign: 'center', margin: '30px 0' }}>
            <a href="/api/walker/welcome" style={{
              display: 'inline-block',
              padding: '12px 30px',
              background: '#4CAF50',
              color: 'white',
              textDecoration: 'none',
              borderRadius: 25,
              margin: 10
            }}>🚀 Test Welcome API</a>
            
            <a href="/api/walker/health_check" style={{
              display: 'inline-block',
              padding: '12px 30px',
              background: '#4CAF50',
              color: 'white',
              textDecoration: 'none',
              borderRadius: 25,
              margin: 10
            }}>❤️ Health Check</a>
          </div>
        </div>

        <div style={{
          background: 'rgba(255, 255, 255, 0.95)',
          borderRadius: 20,
          padding: 30,
          margin: '20px 0',
          boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)'
        }}>
          <h2>🔧 Available API Endpoints</h2>
          <ul>
            <li><code>POST /walker/welcome</code> - System welcome and initialization</li>
            <li><code>POST /walker/health_check</code> - Health check with system status</li>
            <li><code>POST /walker/concepts</code> - Learning concepts management</li>
            <li><code>POST /walker/user_progress</code> - User progress tracking</li>
          </ul>
        </div>

        <div style={{
          textAlign: 'center',
          marginTop: 40,
          color: 'rgba(255, 255, 255, 0.8)'
        }}>
          <p>Built with JAC Object-Spatial Programming</p>
          <p>© 2025 Cavin Otieno • Jeseci Smart Learning Academy</p>
        </div>
      </div>
    </div>
  );
}

export default App;