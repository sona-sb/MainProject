import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './ChatInterface.css';

const ChatInterface = () => {
  const navigate = useNavigate();
  const fileInputRef = useRef(null);
  const messagesEndRef = useRef(null);

  // State for messages (Initialized with a welcome message)
  const [messages, setMessages] = useState([
    { 
      id: 1, 
      text: "Hello! I am your AI Legal Assistant. You can ask me about Indian Penal Codes, draft legal documents, or upload case files for analysis. How can I help you today?", 
      sender: 'bot',
      timestamp: new Date().toLocaleTimeString()
    }
  ]);

  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Handle Text Send
  const handleSend = (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    const newMessage = {
      id: messages.length + 1,
      text: input,
      sender: 'user',
      timestamp: new Date().toLocaleTimeString()
    };

    setMessages([...messages, newMessage]);
    setInput('');
    setIsTyping(true);

    // Simulate AI Response (Mock Logic)
    setTimeout(() => {
      const botResponse = {
        id: messages.length + 2,
        text: "I have received your query regarding this legal matter. Based on Indian law context, I would suggest looking into Section of the specific act. (This is a placeholder response).",
        sender: 'bot',
        timestamp: new Date().toLocaleTimeString()
      };
      setMessages(prev => [...prev, botResponse]);
      setIsTyping(false);
    }, 1500);
  };

  // Handle Image Upload
  const handleImageUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      const imageUrl = URL.createObjectURL(file);
      const newMessage = {
        id: messages.length + 1,
        text: "Analyzed attached document:",
        image: imageUrl,
        sender: 'user',
        timestamp: new Date().toLocaleTimeString()
      };
      setMessages([...messages, newMessage]);
      
      // Simulate AI analyzing image
      setIsTyping(true);
      setTimeout(() => {
        setMessages(prev => [...prev, {
          id: prev.length + 1,
          text: "I've scanned the document you uploaded. It appears to be a legal notice. Would you like me to summarize the key points?",
          sender: 'bot',
          timestamp: new Date().toLocaleTimeString()
        }]);
        setIsTyping(false);
      }, 2000);
    }
  };

  return (
    <div className="chat-layout">
      
      {/* --- Header --- */}
      <header className="chat-header">
        <div className="header-left">
          <span className="logo-icon">⚖️</span>
          <span className="logo-text">DigiLawyer AI</span>
        </div>
        <div className="header-right">
          <button 
            className="moot-court-btn" 
            onClick={() => navigate('/court')}
          >
            🏛️ Moot Court Simulator
          </button>
          <div className="user-profile-icon">JS</div>
        </div>
      </header>

      {/* --- Chat Area --- */}
      <div className="chat-container">
        {messages.map((msg) => (
          <div key={msg.id} className={`message-wrapper ${msg.sender}`}>
            <div className="message-bubble">
              {msg.image && <img src={msg.image} alt="uploaded" className="msg-image" />}
              <p>{msg.text}</p>
              <span className="timestamp">{msg.timestamp}</span>
            </div>
          </div>
        ))}
        
        {isTyping && (
          <div className="message-wrapper bot">
            <div className="typing-indicator">
              <span></span><span></span><span></span>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* --- Input Area --- */}
      <div className="input-container">
        <form onSubmit={handleSend} className="input-box-wrapper">
          
          {/* File Upload Button */}
          <button 
            type="button" 
            className="icon-btn" 
            onClick={() => fileInputRef.current.click()}
            title="Upload Document/Image"
          >
            📎
          </button>
          <input 
            type="file" 
            ref={fileInputRef} 
            hidden 
            accept="image/*,.pdf" 
            onChange={handleImageUpload}
          />

          {/* Text Input */}
          <input
            type="text"
            placeholder="Type your legal query here..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
          />

          {/* Send Button */}
          <button type="submit" className="send-btn">
            ➤
          </button>
        </form>
        <p className="disclaimer">AI can make mistakes. Please verify important legal information.</p>
      </div>

    </div>
  );
};

export default ChatInterface;