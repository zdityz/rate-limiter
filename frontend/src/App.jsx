import { useState, useEffect } from 'react';
import axios from 'axios';

export default function App() {
  const [responses, setResponses] = useState([]);
  const [stats, setStats] = useState(null);
  const demoUserId = "recruiter_demo";

  const fetchStats = async () => {
    try {
      const res = await axios.get('http://localhost:8000/stats');
      setStats(res.data);
    } catch (error) {
    }
  };

  useEffect(() => {
    const interval = setInterval(fetchStats, 1000);
    return () => clearInterval(interval);
  }, []);

  const hitEndpoint = async (algo) => {
    try {
      const res = await axios.post(`http://localhost:8000/${algo}/${demoUserId}`);
      setResponses(prev => [{ status: 200, algo, time: new Date().toLocaleTimeString() }, ...prev].slice(0, 8));
    } catch (error) {
      setResponses(prev => [{ status: 429, algo, time: new Date().toLocaleTimeString() }, ...prev].slice(0, 8));
    }
  };

  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#0f172a', color: '#f8fafc', padding: '40px', fontFamily: 'system-ui, sans-serif' }}>
      <div style={{ maxWidth: '1100px', margin: '0 auto' }}>
        
        <div style={{ textAlign: 'center', marginBottom: '50px' }}>
          <h1 style={{ fontSize: '3.5rem', fontWeight: '800', background: 'linear-gradient(to right, #38bdf8, #818cf8, #c084fc)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', margin: '0 0 10px 0', lineHeight: '1.2', paddingTop: '10px' }}>
            Rate Limiter Node
          </h1>
        </div>

        <div style={{ display: 'flex', justifyContent: 'center', gap: '20px', marginBottom: '50px' }}>
          <button onClick={() => hitEndpoint('fixed')} style={{ padding: '16px 32px', backgroundColor: 'rgba(56, 189, 248, 0.1)', border: '1px solid #38bdf8', color: '#38bdf8', borderRadius: '12px', fontSize: '1.1rem', fontWeight: '600', cursor: 'pointer', transition: 'all 0.2s', boxShadow: '0 0 15px rgba(56, 189, 248, 0.2)' }}>
            INIT FIXED
          </button>
          <button onClick={() => hitEndpoint('sliding')} style={{ padding: '16px 32px', backgroundColor: 'rgba(52, 211, 153, 0.1)', border: '1px solid #34d399', color: '#34d399', borderRadius: '12px', fontSize: '1.1rem', fontWeight: '600', cursor: 'pointer', transition: 'all 0.2s', boxShadow: '0 0 15px rgba(52, 211, 153, 0.2)' }}>
            INIT SLIDING
          </button>
          <button onClick={() => hitEndpoint('token')} style={{ padding: '16px 32px', backgroundColor: 'rgba(192, 132, 252, 0.1)', border: '1px solid #c084fc', color: '#c084fc', borderRadius: '12px', fontSize: '1.1rem', fontWeight: '600', cursor: 'pointer', transition: 'all 0.2s', boxShadow: '0 0 15px rgba(192, 132, 252, 0.2)' }}>
            INIT TOKEN
          </button>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 1fr', gap: '30px' }}>
          
          <div style={{ backgroundColor: '#1e293b', borderRadius: '20px', padding: '30px', border: '1px solid #334155', boxShadow: '0 10px 30px rgba(0,0,0,0.5)' }}>
            <h2 style={{ fontSize: '1.5rem', margin: '0 0 25px 0', display: 'flex', alignItems: 'center', gap: '10px' }}>
              <span style={{ width: '10px', height: '10px', borderRadius: '50%', backgroundColor: '#ef4444', display: 'inline-block' }}></span>
              Live Network Traffic
            </h2>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {responses.map((r, i) => (
                <div key={i} style={{ padding: '16px 20px', borderRadius: '12px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', backgroundColor: r.status === 200 ? 'rgba(52, 211, 153, 0.05)' : 'rgba(239, 68, 68, 0.05)', borderLeft: `4px solid ${r.status === 200 ? '#34d399' : '#ef4444'}` }}>
                  <span style={{ fontWeight: '600', letterSpacing: '1px', color: '#e2e8f0' }}>{r.algo.toUpperCase()}</span>
                  <span style={{ color: r.status === 200 ? '#34d399' : '#ef4444', fontWeight: 'bold', fontFamily: 'monospace', fontSize: '1.1rem' }}>{r.status === 200 ? '200 OK' : '429 BLOCKED'}</span>
                </div>
              ))}
            </div>
          </div>

          <div style={{ backgroundColor: '#1e293b', borderRadius: '20px', padding: '30px', border: '1px solid #334155', boxShadow: '0 10px 30px rgba(0,0,0,0.5)' }}>
            <h2 style={{ fontSize: '1.5rem', margin: '0 0 25px 0', color: '#f8fafc' }}>System Telemetry</h2>
            {stats ? (
              <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '20px' }}>
                <div style={{ backgroundColor: '#0f172a', padding: '20px', borderRadius: '12px', border: '1px solid #334155' }}>
                  <span style={{ color: '#94a3b8', fontSize: '0.9rem', textTransform: 'uppercase', letterSpacing: '1px' }}>Global Throughput</span>
                  <div style={{ fontSize: '2.5rem', fontWeight: '800', color: '#f8fafc', marginTop: '5px' }}>
                    {stats.throughput} <span style={{ fontSize: '1.2rem', color: '#64748b', fontWeight: '500' }}>req/sec</span>
                  </div>
                </div>
                
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
                  <div style={{ backgroundColor: 'rgba(52, 211, 153, 0.05)', padding: '20px', borderRadius: '12px', border: '1px solid rgba(52, 211, 153, 0.2)' }}>
                    <span style={{ color: '#34d399', fontSize: '0.9rem', textTransform: 'uppercase', letterSpacing: '1px' }}>Allowed</span>
                    <div style={{ fontSize: '2rem', fontWeight: '800', color: '#34d399', marginTop: '5px' }}>{stats.total_allowed}</div>
                  </div>
                  
                  <div style={{ backgroundColor: 'rgba(239, 68, 68, 0.05)', padding: '20px', borderRadius: '12px', border: '1px solid rgba(239, 68, 68, 0.2)' }}>
                    <span style={{ color: '#ef4444', fontSize: '0.9rem', textTransform: 'uppercase', letterSpacing: '1px' }}>Blocked</span>
                    <div style={{ fontSize: '2rem', fontWeight: '800', color: '#ef4444', marginTop: '5px' }}>{stats.total_blocked}</div>
                  </div>
                </div>
              </div>
            ) : (
              <div style={{ color: '#64748b', fontStyle: 'italic' }}>Awaiting telemetry sync...</div>
            )}
          </div>

        </div>
      </div>
    </div>
  );
}