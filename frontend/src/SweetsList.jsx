import { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

function SweetsList() {
  const [sweets, setSweets] = useState([]);
  const [search, setSearch] = useState('');
  const [newSweet, setNewSweet] = useState({ name: '', price: '', quantity: '' });
  const navigate = useNavigate();

  // Helper to get token
  const getToken = () => localStorage.getItem('token');

  // 1. Fetch Sweets (Load on startup)
  useEffect(() => {
    fetchSweets();
  }, []);

  const fetchSweets = async (searchTerm = '') => {
    const token = getToken();
    if (!token) return navigate('/login');

    try {
      const endpoint = searchTerm 
        ? `/api/sweets/search?name=${searchTerm}` 
        : '/api/sweets';
      
      const response = await axios.get(endpoint, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setSweets(response.data);
    } catch (err) {
      console.error("Failed to fetch sweets", err);
      if (err.response && err.response.status === 401) navigate('/login');
    }
  };

  // 2. Handle Search
  const handleSearch = (e) => {
    setSearch(e.target.value);
    fetchSweets(e.target.value);
  };

  // 3. Handle Purchase
  const handlePurchase = async (id) => {
    const token = getToken();
    try {
      await axios.post(`/api/sweets/${id}/purchase`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      // Refresh list to show new quantity
      fetchSweets(search); 
      alert("Yum! Purchase successful.");
    } catch (err) {
      alert(err.response?.data?.detail || "Purchase failed");
    }
  };

  // 4. Handle Add Sweet (Restock)
  const handleAddSweet = async (e) => {
    e.preventDefault();
    const token = getToken();
    try {
      await axios.post('/api/sweets', newSweet, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setNewSweet({ name: '', price: '', quantity: '' }); // Reset form
      fetchSweets(search); // Refresh list
    } catch (err) {
      alert("Failed to add sweet");
    }
  };

  return (
    <div style={{ padding: '20px', fontFamily: 'sans-serif' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h1>🍭 Sweet Shop Inventory</h1>
        <button onClick={() => { localStorage.removeItem('token'); navigate('/login'); }} style={{ background: '#ff4444', color: 'white', border: 'none', padding: '10px' }}>
          Logout
        </button>
      </div>

      {/* Search Bar */}
      <div style={{ margin: '20px 0' }}>
        <input 
          type="text" 
          placeholder="Search for sweets..." 
          value={search}
          onChange={handleSearch}
          style={{ padding: '10px', width: '300px', fontSize: '16px' }}
        />
      </div>

      {/* List of Sweets (Grid) */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: '20px' }}>
        {sweets.map(sweet => (
          <div key={sweet.id} style={{ border: '1px solid #ddd', padding: '15px', borderRadius: '8px', boxShadow: '0 2px 5px rgba(0,0,0,0.1)' }}>
            <h3>{sweet.name}</h3>
            <p>Price: ${sweet.price}</p>
            <p style={{ color: sweet.quantity === 0 ? 'red' : 'green', fontWeight: 'bold' }}>
              Stock: {sweet.quantity}
            </p>
            <button 
              onClick={() => handlePurchase(sweet.id)}
              disabled={sweet.quantity === 0}
              style={{ 
                width: '100%', 
                padding: '10px', 
                background: sweet.quantity === 0 ? '#ccc' : '#007bff', 
                color: 'white', 
                border: 'none', 
                cursor: sweet.quantity === 0 ? 'not-allowed' : 'pointer' 
              }}
            >
              {sweet.quantity === 0 ? 'Sold Out' : 'Buy Now'}
            </button>
          </div>
        ))}
      </div>

      {/* Add New Sweet Form */}
      <div style={{ marginTop: '50px', borderTop: '2px dashed #ccc', paddingTop: '20px' }}>
        <h3>Restock / Add New Sweet</h3>
        <form onSubmit={handleAddSweet} style={{ display: 'flex', gap: '10px' }}>
          <input placeholder="Name" value={newSweet.name} onChange={e => setNewSweet({...newSweet, name: e.target.value})} required />
          <input placeholder="Price" type="number" step="0.01" value={newSweet.price} onChange={e => setNewSweet({...newSweet, price: e.target.value})} required />
          <input placeholder="Qty" type="number" value={newSweet.quantity} onChange={e => setNewSweet({...newSweet, quantity: e.target.value})} required />
          <button type="submit" style={{ background: 'green', color: 'white', border: 'none', padding: '10px' }}>Add Sweet</button>
        </form>
      </div>
    </div>
  );
}

export default SweetsList;