import { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

function Login() {
  const [isRegistering, setIsRegistering] = useState(false);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [message, setMessage] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMessage('');
    const endpoint = isRegistering ? '/api/auth/register' : '/api/auth/login';
    
    try {
      const response = await axios.post(endpoint, { username, password });
      
      if (isRegistering) {
        setMessage('Registration successful! Please login.');
        setIsRegistering(false);
      } else {
        localStorage.setItem('token', response.data.access_token);
        navigate('/sweets');
      }
    } catch (err) {
      setMessage('Error: ' + (err.response?.data?.detail || 'Something went wrong'));
    }
  };

  return (
    // Outer container takes full screen and centers content
    <div style={{ 
      display: 'flex', 
      justifyContent: 'center', 
      alignItems: 'center', 
      minHeight: '100vh', 
      backgroundColor: '#f5f5f5' 
    }}>
      {/* The Card */}
      <div style={{ 
        padding: '40px', 
        width: '100%', 
        maxWidth: '400px', 
        backgroundColor: 'white', 
        borderRadius: '10px', 
        boxShadow: '0 4px 10px rgba(0,0,0,0.1)',
        textAlign: 'center'
      }}>
        <h2 style={{ marginBottom: '20px', color: '#333' }}>{isRegistering ? 'Register' : 'Sweet Shop Login'}</h2>
        
        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
          <input 
            type="text" placeholder="Username" value={username} onChange={e => setUsername(e.target.value)} 
            style={{ padding: '12px', borderRadius: '5px', border: '1px solid #ccc', fontSize: '16px' }} required
          />
          <input 
            type="password" placeholder="Password" value={password} onChange={e => setPassword(e.target.value)} 
            style={{ padding: '12px', borderRadius: '5px', border: '1px solid #ccc', fontSize: '16px' }} required
          />
          <button type="submit" style={{ 
            padding: '12px', 
            background: '#007bff', 
            color: 'white', 
            border: 'none', 
            borderRadius: '5px', 
            fontSize: '16px', 
            cursor: 'pointer',
            fontWeight: 'bold'
          }}>
            {isRegistering ? 'Sign Up' : 'Login'}
          </button>
        </form>

        <p 
          style={{ marginTop: '20px', cursor: 'pointer', color: '#007bff', textDecoration: 'underline' }} 
          onClick={() => setIsRegistering(!isRegistering)}
        >
          {isRegistering ? 'Already have an account? Login' : 'Need an account? Register'}
        </p>
        
        {message && <p style={{ marginTop: '15px', color: isRegistering ? 'green' : 'red' }}>{message}</p>}
      </div>
    </div>
  );
}

export default Login;