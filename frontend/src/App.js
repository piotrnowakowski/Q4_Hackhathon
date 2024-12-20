import React from 'react';
import ChatInterface from './components/ChatInterface';
import './styles/App.css';
//import logo from './assets/amiblu-logo.png'; // Add logo file to src/assets/

function App() {
  return (
    <div className="app">
      <header className="app-header">
        <h1>Real-Time AI Interaction</h1>
      </header>
      <main>
        <ChatInterface />
      </main>
    </div>
  );
}

export default App;
