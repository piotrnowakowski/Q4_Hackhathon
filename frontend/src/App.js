import React from 'react';
import ChatInterface from './components/ChatInterface';
import QueryComponent from './components/QueryComponent';
import './styles/App.css';
//import logo from './assets/amiblu-logo.png'; // Add logo file to src/assets/

function App() {
  return (
    <div className="app">
      <header className="app-header">
        <h1>Real-Time AI Interaction</h1>
      </header>
      <main>
        {/* Chat Interface */}
        <section className="chat-interface">
          <ChatInterface />
        </section>

        {/* Query Component */}
        <section className="query-component">
          <QueryComponent />
        </section>
      </main>
    </div>
  );
}

export default App;
