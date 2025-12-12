import { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

function Login() {
  const [isRegistering, setIsRegistering] = useState(false); // Toggle
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
        navigate('/sweets'); // We will build this next
      }
    } catch (err) {
      setMessage('Error: ' + (err.response?.data?.detail || 'Something went wrong'));
    }
  };

  return (
    <div style={{ padding: '50px', maxWidth: '400px', margin: '0 auto', fontFamily: 'sans-serif' }}>
      <h2>{isRegistering ? 'Register' : 'Login'}</h2>
      <form onSubmit={handleSubmit}>
        <input 
          type="text" placeholder="Username" value={username} onChange={e => setUsername(e.target.value)} 
          style={{ display: 'block', width: '100%', marginBottom: '10px', padding: '8px' }} required
        />
        <input 
          type="password" placeholder="Password" value={password} onChange={e => setPassword(e.target.value)} 
          style={{ display: 'block', width: '100%', marginBottom: '10px', padding: '8px' }} required
        />
        <button type="submit" style={{ padding: '10px 20px', cursor: 'pointer' }}>
          {isRegistering ? 'Sign Up' : 'Login'}
        </button>
      </form>
      <p style={{ marginTop: '20px', cursor: 'pointer', color: 'blue' }} onClick={() => setIsRegistering(!isRegistering)}>
        {isRegistering ? 'Already have an account? Login' : 'Need an account? Register'}
      </p>
      {message && <p style={{ marginTop: '10px', color: isRegistering ? 'green' : 'red' }}>{message}</p>}
    </div>
  );
}

export default Login;