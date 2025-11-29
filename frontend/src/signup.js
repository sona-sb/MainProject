import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom'; // For navigation
import './signup.css';

const SignUp = () => {
  const navigate = useNavigate();
  
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: ''
  });
  
  const [error, setError] = useState('');

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
    // Clear error when user types
    if (error) setError('');
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    
    // Basic Validation
    if (!formData.email || !formData.password || !formData.confirmPassword) {
      setError("Please fill in all fields.");
      return;
    }

    if (formData.password !== formData.confirmPassword) {
      setError("Passwords do not match!");
      return;
    }

    // If successful, navigate to the Court Simulator
    // In a real app, you would send this data to a backend here
    console.log("User Registered:", formData);
    navigate('/chat'); 
  };

  return (
    <div className="signup-container">
      <div className="signup-card">
        
        {/* Header Section */}
        <div className="signup-header">
          <div className="logo-icon">⚖️</div>
          <h2>Create Account</h2>
          <p>Join DigiLawyer for affordable justice.</p>
        </div>

        {/* Form Section */}
        <form onSubmit={handleSubmit} className="signup-form">
          
          <div className="form-group">
            <label>Email Address</label>
            <input 
              type="email" 
              name="email" 
              placeholder="name@example.com" 
              value={formData.email}
              onChange={handleChange}
            />
          </div>

          <div className="form-group">
            <label>Password</label>
            <input 
              type="password" 
              name="password" 
              placeholder="Create a password" 
              value={formData.password}
              onChange={handleChange}
            />
          </div>

          <div className="form-group">
            <label>Confirm Password</label>
            <input 
              type="password" 
              name="confirmPassword" 
              placeholder="Confirm your password" 
              value={formData.confirmPassword}
              onChange={handleChange}
            />
          </div>

          {error && <div className="error-message">{error}</div>}

          <button type="submit" className="signup-btn">
            Sign Up
          </button>
        </form>

        {/* Footer Link */}
        <div className="signup-footer">
          <p>Already have an account? <span onClick={() => navigate('/login')} className="link">Login</span></p>
          <p className="home-link" onClick={() => navigate('/')}>← Back to Home</p>
        </div>

      </div>
    </div>
  );
};

export default SignUp;