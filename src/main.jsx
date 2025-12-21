import React from 'react'
import ReactDOM from 'react-dom/client'

function App() {
  const [appHtml, setAppHtml] = React.useState('Loading...');
  
  React.useEffect(() => {
    // Fetch the JAC client function result
    fetch('/function/app')
      .then(response => response.json())
      .then(data => {
        if (data.result) {
          setAppHtml(data.result);
        } else {
          setAppHtml('Error loading app content');
        }
      })
      .catch(error => {
        console.error('Error:', error);
        setAppHtml('Error loading application');
      });
  }, []);

  return (
    <div 
      dangerouslySetInnerHTML={{ __html: appHtml }}
      style={{ minHeight: '100vh' }}
    />
  );
}

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)