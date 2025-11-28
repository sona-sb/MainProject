import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './login.css';

const Login = () => {
  const navigate = useNavigate();
  
  const [credentials, setCredentials] = useState({
    email: '',
    password: ''
  });
  
  const [error, setError] = useState('');

  const handleChange = (e) => {
    setCredentials({
      ...credentials,
      [e.target.name]: e.target.value
    });
    if (error) setError('');
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    
    // Basic Validation
    if (!credentials.email || !credentials.password) {
      setError("Please enter both email and password.");
      return;
    }

    // In a real app, you would verify with a backend here.
    // For now, we simulate a successful login and go to the app.
    console.log("Logging in with:", credentials);
    navigate('/chat'); 
  };

  return (
    <div className="login-container">
      <div className="login-card">
        
        {/* Header */}
        <div className="login-header">
          <div className="logo-icon">⚖️</div>
          <h2>Welcome Back</h2>
          <p>Login to access your dashboard.</p>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="login-form">
          
          <div className="form-group">
            <label>Email Address</label>
            <input 
              type="email" 
              name="email" 
              placeholder="name@example.com" 
              value={credentials.email}
              onChange={handleChange}
            />
          </div>

          <div className="form-group">
            <label>Password</label>
            <input 
              type="password" 
              name="password" 
              placeholder="Enter your password" 
              value={credentials.password}
              onChange={handleChange}
            />
          </div>

          {error && <div className="error-message">{error}</div>}

          <button type="submit" className="login-btn">
            Login
          </button>
        </form>

        {/* Footer */}
        <div className="login-footer">
          <p>Don't have an account? <span onClick={() => navigate('/signup')} className="link">Sign Up</span></p>
          <p className="home-link" onClick={() => navigate('/')}>← Back to Home</p>
        </div>

      </div>
    </div>
  );
};

export default Login;