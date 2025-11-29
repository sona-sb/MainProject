import React from 'react';
import Login from './login';
import { BrowserRouter as Router, Routes, Route, useNavigate } from 'react-router-dom';
import './App.css';
import SignUp from './signup'; // Import your Signup component
import ChatInterface from './ChatInterface';
import MootCourt from './mootcourt';

/* =========================================
   1. The Landing Page Component 
   (Moved your original UI here)
   ========================================= */
const LandingPage = () => {
  const navigate = useNavigate();

  return (
    <div className="landing-container">
      
      {/* --- Navbar --- */}
      <nav className="navbar">
        <div className="logo-section">
          <span className="logo-icon">⚖️</span>
          <span className="logo-text">नियम-Guru</span>
        </div>
        
        <div className="nav-links">
          <a href="#features">Why नियम-Guru</a>
          <a href="#about">About Us</a>
        </div>
      </nav>

      {/* --- Hero Section --- */}
      <header className="hero-section">
        

        <h1 className="hero-title">
          Empowering the Nation with <br /> Legal Clarity
        </h1>

        {/* Social Proof Avatars */}
        <div className="avatar-group">
          <img src="https://i.pravatar.cc/100?img=1" alt="User" />
          <img src="https://i.pravatar.cc/100?img=5" alt="User" />
          <img src="https://i.pravatar.cc/100?img=9" alt="User" />
          <img src="https://i.pravatar.cc/100?img=12" alt="User" />
          <img src="https://i.pravatar.cc/100?img=32" alt="User" />
        </div>

        <p className="sub-text">
          Justice Simplified
        </p>

        {/* --- Main Call to Action (Connected to Router) --- */}
        <div className="cta-container">
          <button className="hero-btn login-btn" onClick={() => navigate('/login')}>
            Login
          </button>
          
          {/* This button now navigates to the Signup page */}
          <button className="hero-btn signup-btn" onClick={() => navigate('/signup')}>
            Sign Up
          </button>
        </div>

        <div className="suggestion-chips">
          <span>AI Moot Court Simulator</span>
          <span>Legal Documentation</span>
          <span>Case Research</span>
        </div>
      </header>

      {/* --- Key Features Section --- */}
      <section id="features" className="features-section">
        <div className="section-header">
          <h2>Why Choose नियम-Guru?</h2>
          <p>Experience the Future of Law with our AI-powered solutions.</p>
        </div>

        <div className="features-grid">
          <div className="feature-card">
            <div className="icon">🏛️</div>
            <h3>Moot Court Simulator</h3>
            <p>Practice your arguments against an AI Judge and Opposing Counsel in a realistic virtual environment.</p>
          </div>
          <div className="feature-card">
            <div className="icon">📄</div>
            <h3>Instant Drafting</h3>
            <p>Generate legal notices, rental agreements, and affidavits in minutes using smart templates.</p>
          </div>
          <div className="feature-card">
            <div className="icon">🔍</div>
            <h3>Case Research</h3>
            <p>Scan through thousands of previous judgements and precedents instantly to strengthen your case.</p>
          </div>
          <div className="feature-card">
            <div className="icon">🗣️</div>
            <h3>Multilingual Support</h3>
            <p>Interact with the legal system in your local language. We break the language barrier in justice.</p>
          </div>
        </div>
      </section>

      {/* --- About Us Section --- */}
      <section id="about" className="about-section">
        <div className="about-content">
          <div className="about-text">
            <h2>About Us</h2>
            <p>
              Niyam-Guru was established with a singular vision: 
              <strong>  to democratize legal access across India.</strong>
            </p>
            <p>
              At Niyam-Guru, we believe that justice should be a right, not a privilege.By converging advanced Artificial Intelligence with deep judicial insight, we dismantle the complexities of the legal system. Whether you are an aspiring attorney refining your craft or a citizen in
              need of counsel, Niyam-Guru stands as your trusted ally in the pursuit of justice.
            </p>
            
          </div>
          <div className="about-image">
            <img 
              src="https://images.unsplash.com/photo-1618771623063-6c3faa854a61?q=80&w=2070&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D" 
              alt="Legal Books and Gavel" 
            />
          </div>
        </div>
      </section>

      <footer className="footer">
        <p>© 2025 Niyam-Guru. All Rights Reserved.</p>
      </footer>

    </div>
  );
};

/* =========================================
   2. The Main App Component (The Router)
   ========================================= */
const App = () => {
  return (
    <Router>
      <Routes>
        {/* Route for Landing Page */}
        <Route path="/" element={<LandingPage />} />
        
        {/* Route for Signup Page */}
        <Route path="/signup" element={<SignUp />} />
        
        {/* Route for Login */}
<Route path="/login" element={<Login />} />
        
        {/* Add the Chat Route */}
        <Route path="/chat" element={<ChatInterface />} />
        
        {/* 4. The Moot Court Simulator (Linked from Chat) */}
        <Route path="/court" element={<MootCourt />} />
      
      </Routes>
    </Router>
  );
};

export default App;