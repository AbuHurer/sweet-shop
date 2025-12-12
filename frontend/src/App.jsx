import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Login from './Login';
import SweetsList from './SweetsList';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/sweets" element={<SweetsList />} />
        <Route path="/" element={<Navigate to="/sweets" />} />
      </Routes>
    </Router>
  );
}

export default App;