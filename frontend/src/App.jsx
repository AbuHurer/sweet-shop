import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Login from './Login';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/login" element={<Login />} />
        {/* Redirect root to login for now */}
        <Route path="/" element={<Navigate to="/login" />} /> 
      </Routes>
    </Router>
  );
}

export default App;