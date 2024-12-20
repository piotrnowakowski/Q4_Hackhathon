import React, { useState } from 'react';
import { initializeWebRTC } from '../hooks/useWebRTC';

function ChatInterface() {
  const [isConnected, setIsConnected] = useState(false);
  const [isReceivingAudio, setIsReceivingAudio] = useState(false);

  const handleStart = async () => {
    try {
      await initializeWebRTC(() => setIsReceivingAudio(true)); // Pass callback
      setIsConnected(true);
    } catch (error) {
      console.error('Error initializing WebRTC:', error);
    }
  };

  return (
    <div className="chat-interface">
      <button onClick={handleStart}>
        {isConnected ? 'Connected' : 'Start Talking'}
      </button>
      {isReceivingAudio && <p>Receiving AI response...</p>}
    </div>
  );
}

export default ChatInterface;
