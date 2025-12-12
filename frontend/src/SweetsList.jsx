import { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

function SweetsList() {
  const [sweets, setSweets] = useState([]);
  const [search, setSearch] = useState('');
  // Updated state to include category
  const [newSweet, setNewSweet] = useState({ name: '', category: '', price: '', quantity: '' });
  const navigate = useNavigate();

  const getToken = () => localStorage.getItem('token');

  useEffect(() => {
    fetchSweets();
  }, []);

  const fetchSweets = async (searchTerm = '') => {
    const token = getToken();
    if (!token) return navigate('/login');

    try {
      const endpoint = searchTerm ? `/api/sweets/search?name=${searchTerm}` : '/api/sweets';
      const response = await axios.get(endpoint, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setSweets(response.data);
    } catch (err) {
      if (err.response && err.response.status === 401) navigate('/login');
    }
  };

  const handleSearch = (e) => {
    setSearch(e.target.value);
    fetchSweets(e.target.value);
  };

  const handlePurchase = async (id) => {
    const token = getToken();
    try {
      await axios.post(`/api/sweets/${id}/purchase`, {}, { headers: { Authorization: `Bearer ${token}` } });
      fetchSweets(search);
      alert("Yum! Purchase successful.");
    } catch (err) {
      alert(err.response?.data?.detail || "Purchase failed");
    }
  };

  // NEW: Delete Functionality
  const handleDelete = async (id) => {
    if(!confirm("Are you sure you want to delete this sweet?")) return;
    const token = getToken();
    try {
      await axios.delete(`/api/sweets/${id}`, { headers: { Authorization: `Bearer ${token}` } });
      fetchSweets(search);
    } catch (err) {
      alert("Failed to delete");
    }
  };

  const handleAddSweet = async (e) => {
    e.preventDefault();
    const token = getToken();
    try {
      await axios.post('/api/sweets', newSweet, { headers: { Authorization: `Bearer ${token}` } });
      // Clear form (including category)
      setNewSweet({ name: '', category: '', price: '', quantity: '' });
      fetchSweets(search);
    } catch (err) {
      alert("Failed to add sweet. Make sure all fields including Category are filled.");
    }
  };

  return (
    <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '40px 20px', fontFamily: 'Segoe UI, Tahoma, Geneva, Verdana, sans-serif' }}>
      
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '30px' }}>
        <h1 style={{ color: '#fff' }}>🍭 Sweet Shop Inventory</h1>
        <button onClick={() => { localStorage.removeItem('token'); navigate('/login'); }} 
          style={{ background: '#ff4444', color: 'white', border: 'none', padding: '10px 20px', borderRadius: '5px', cursor: 'pointer' }}>
          Logout
        </button>
      </div>

      {/* Search Bar */}
      <div style={{ display: 'flex', justifyContent: 'center', marginBottom: '40px' }}>
        <input 
          type="text" 
          placeholder="🔍 Search for sweets..." 
          value={search}
          onChange={handleSearch}
          style={{ padding: '15px', width: '100%', maxWidth: '500px', fontSize: '16px', borderRadius: '25px', border: 'none', outline: 'none', boxShadow: '0 4px 10px rgba(0,0,0,0.3)' }}
        />
      </div>

      {/* Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(250px, 1fr))', gap: '25px' }}>
        {sweets.map(sweet => (
          <div key={sweet.id} style={{ 
            padding: '20px', borderRadius: '12px', boxShadow: '0 4px 15px rgba(0,0,0,0.2)', backgroundColor: 'white',
            display: 'flex', flexDirection: 'column', alignItems: 'center', textAlign: 'center', position: 'relative'
          }}>
            
            {/* NEW: Delete Button */}
            <button 
              onClick={() => handleDelete(sweet.id)}
              style={{ position: 'absolute', top: '10px', right: '10px', background: 'none', border: 'none', color: '#ff4444', cursor: 'pointer', fontSize: '16px', fontWeight: 'bold' }}
              title="Delete Sweet"
            >✕</button>

            <h3 style={{ margin: '0 0 5px 0', fontSize: '1.4rem', color: '#333' }}>{sweet.name}</h3>
            
            {/* NEW: Category Badge */}
            <span style={{ background: '#eee', color: '#555', padding: '2px 8px', borderRadius: '10px', fontSize: '0.8rem', marginBottom: '10px' }}>
              {sweet.category}
            </span>
            
            <p style={{ fontSize: '1.2rem', color: '#666' }}>${sweet.price}</p>
            <p style={{ color: sweet.quantity === 0 ? 'red' : 'green', fontWeight: 'bold', marginBottom: '15px' }}>
              {sweet.quantity > 0 ? `${sweet.quantity} in stock` : 'Out of Stock'}
            </p>
            
            <button 
              onClick={() => handlePurchase(sweet.id)}
              disabled={sweet.quantity === 0}
              style={{ width: '100%', padding: '12px', background: sweet.quantity === 0 ? '#e0e0e0' : '#007bff', color: sweet.quantity === 0 ? '#888' : 'white', border: 'none', borderRadius: '8px', cursor: sweet.quantity === 0 ? 'not-allowed' : 'pointer', fontWeight: 'bold' }}
            >
              {sweet.quantity === 0 ? 'Sold Out' : 'Buy Now'}
            </button>
          </div>
        ))}
      </div>

      {/* Restock Form */}
      <div style={{ marginTop: '60px', borderTop: '2px dashed #555', paddingTop: '30px', textAlign: 'center' }}>
        <h3 style={{ color: '#ccc', marginBottom: '20px' }}>Admin Restock</h3>
        <form onSubmit={handleAddSweet} style={{ display: 'flex', justifyContent: 'center', gap: '10px', flexWrap: 'wrap' }}>
          <input placeholder="Name" value={newSweet.name} onChange={e => setNewSweet({...newSweet, name: e.target.value})} required style={{ padding: '10px', borderRadius: '5px', border: 'none' }} />
          
          {/* NEW: Category Input - Critical for backend validation */}
          <input placeholder="Category" value={newSweet.category} onChange={e => setNewSweet({...newSweet, category: e.target.value})} required style={{ padding: '10px', borderRadius: '5px', border: 'none' }} />
          
          <input placeholder="Price" type="number" step="0.01" value={newSweet.price} onChange={e => setNewSweet({...newSweet, price: e.target.value})} required style={{ padding: '10px', borderRadius: '5px', border: 'none', width: '80px' }} />
          <input placeholder="Qty" type="number" value={newSweet.quantity} onChange={e => setNewSweet({...newSweet, quantity: e.target.value})} required style={{ padding: '10px', borderRadius: '5px', border: 'none', width: '80px' }} />
          <button type="submit" style={{ background: '#28a745', color: 'white', border: 'none', padding: '10px 20px', borderRadius: '5px', cursor: 'pointer' }}>Add Stock</button>
        </form>
      </div>
    </div>
  );
}

export default SweetsList;