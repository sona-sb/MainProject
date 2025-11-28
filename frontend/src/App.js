import React, { useState, useEffect, useRef } from 'react';
import './App.css';

// --- IMAGE CONFIGURATION ---
// PASTE YOUR IMAGE LINKS HERE
const IMAGES = {
  JUDGE: "https://img.freepik.com/premium-vector/judge-avatar-man-flat-icon-illustration_102766-993.jpg?w=200", 
  OPPONENT: "https://cdn-icons-png.flaticon.com/512/4202/4202835.png", // Replace with Opponent Image
  USER: "https://cdn-icons-png.flaticon.com/512/4202/4202843.png"     // Replace with User Image
};

const ACTORS = {
  JUDGE: 'judge',
  OPPONENT: 'opponent',
  USER: 'user'
};

function App() {
  const [messages, setMessages] = useState([
    {
      id: 1,
      sender: ACTORS.JUDGE,
      text: "Court is now in session. The Defendant may present their opening statement."
    }
  ]);
  const [inputText, setInputText] = useState('');
  const [isSimulating, setIsSimulating] = useState(false);
  
  const chatEndRef = useRef(null);

  const scrollToBottom = () => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleUserSubmit = (e) => {
    e.preventDefault();
    if (!inputText.trim()) return;

    const userMsg = {
      id: Date.now(),
      sender: ACTORS.USER,
      text: inputText
    };

    setMessages((prev) => [...prev, userMsg]);
    setInputText('');
    setIsSimulating(true);

    setTimeout(() => {
      const opponentMsg = {
        id: Date.now() + 1,
        sender: ACTORS.OPPONENT,
        text: generateOpponentResponse()
      };
      setMessages((prev) => [...prev, opponentMsg]);
      
      setTimeout(() => {
        const judgeMsg = {
          id: Date.now() + 2,
          sender: ACTORS.JUDGE,
          text: generateJudgeResponse()
        };
        setMessages((prev) => [...prev, judgeMsg]);
        setIsSimulating(false);
      }, 2000);

    }, 1500);
  };

  const generateOpponentResponse = () => {
    const responses = [
      "Objection! The counsel is leading the witness.",
      "That is purely circumstantial evidence.",
      "My learned friend fails to consider the precedence set in 1994.",
      "I strongly disagree with that characterization of the facts.",
      "The prosecution has not met the burden of proof."
    ];
    return responses[Math.floor(Math.random() * responses.length)];
  };

  const generateJudgeResponse = () => {
    const responses = [
      "Order in the court. I will allow the argument, proceed.",
      "Sustained. Please rephrase, Counselor.",
      "Overruled. The witness will answer the question.",
      "I have heard enough on this point. Move along.",
      "Noted. Let us see where this leads."
    ];
    return responses[Math.floor(Math.random() * responses.length)];
  };

  const latestJudgeMessage = [...messages].reverse().find(m => m.sender === ACTORS.JUDGE);

  return (
    <div className="courtroom-container">
      
      {/* --- Top Section: The Bench (Judge) --- */}
      <div className="judge-bench">
        <div className="judge-avatar-container">
          <img 
            src={IMAGES.JUDGE} 
            alt="Judge" 
            className="judge-image" 
          />
          <div className="judge-name">Honorable Justice AI</div>
        </div>
        
        <div className={`judge-speech-bubble ${latestJudgeMessage ? 'visible' : ''}`}>
          {latestJudgeMessage ? latestJudgeMessage.text : "..."}
        </div>
      </div>

      {/* --- Middle Section: The Floor (Arguments) --- */}
      <div className="argument-floor">
        {messages.map((msg) => {
          if (msg.sender === ACTORS.JUDGE) return null;
          
          const isUser = msg.sender === ACTORS.USER;

          return (
            <div 
              key={msg.id} 
              className={`message-row ${isUser ? 'row-right' : 'row-left'}`}
            >
              {/* If Opponent, Image goes FIRST (Left) */}
              {!isUser && (
                <img src={IMAGES.OPPONENT} alt="Opponent" className="counsel-avatar avatar-opponent" />
              )}

              <div className={`message-bubble ${msg.sender}`}>
                <span className="sender-label">
                  {isUser ? 'Counsel (You)' : 'Opposing Counsel'}
                </span>
                <p>{msg.text}</p>
              </div>

              {/* If User, Image goes SECOND (Right) */}
              {isUser && (
                <img src={IMAGES.USER} alt="User" className="counsel-avatar avatar-user" />
              )}
            </div>
          );
        })}
        {isSimulating && <div className="typing-indicator">Opposing counsel is preparing an argument...</div>}
        <div ref={chatEndRef} />
      </div>

      {/* --- Bottom Section: Input --- */}
      <div className="counsel-desk">
        <form onSubmit={handleUserSubmit} className="input-form">
          <input
            type="text"
            className="argument-input"
            placeholder="Type your legal argument here..."
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            disabled={isSimulating}
          />
          <button type="submit" className="gavel-btn" disabled={isSimulating}>
            Present
          </button>
        </form>
      </div>
    </div>
  );
}

export default App;