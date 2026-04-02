import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';

function AdminPanel() {
  const [orders, setOrders] = useState([]);
  const [error, setError] = useState('');
  const ordersRef = useRef(null);

  useEffect(() => {
    const fetchOrders = async () => {
      const getCookie = (name) => {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) return parts.pop().split(';').shift();
        return null;
      };
      const token = getCookie('token');
      if (!token) {
        setError('Unauthorized');
        return;
      }
      try {
        const res = await axios.get(`/api/admin/orders`, { withCredentials: true });
        setOrders(res.data.orders);
      } catch (err) {
        setError('Failed to fetch orders');
      }
    };
    fetchOrders();
  }, []);

  useEffect(() => {
    if (ordersRef.current && orders.length > 0) {
      ordersRef.current.innerHTML = '';
      orders.forEach((order, index) => {
        const card = document.createElement('div');
        card.className = 'order-card';
        card.style.padding = '1.5rem';
        card.style.border = '1px solid var(--a-line)';
        card.style.borderRadius = '8px';
        card.style.marginBottom = '1.5rem';
        card.style.background = 'var(--a-bg-white)';
        card.style.boxShadow = '0 2px 4px rgba(0,0,0,0.05)';
        
        const header = document.createElement('div');
        header.style.display = 'flex';
        header.style.justifyContent = 'space-between';
        header.style.alignItems = 'center';
        header.style.borderBottom = '1px solid var(--a-line-strong)';
        header.style.paddingBottom = '0.75rem';
        header.style.marginBottom = '1rem';

        const title = document.createElement('h3');
        title.textContent = `Order #${1000 + index} - ${order.company}`;
        title.style.margin = '0';
        title.style.color = 'var(--a-accent)';
        
        const statusBadge = document.createElement('span');
        statusBadge.textContent = 'PENDING REVIEW';
        statusBadge.style.background = '#fff3cd';
        statusBadge.style.color = '#856404';
        statusBadge.style.padding = '0.25rem 0.5rem';
        statusBadge.style.borderRadius = '4px';
        statusBadge.style.fontSize = '0.8rem';
        statusBadge.style.fontWeight = 'bold';

        header.appendChild(title);
        header.appendChild(statusBadge);
        card.appendChild(header);

        const descLabel = document.createElement('strong');
        descLabel.textContent = 'Client Description:';
        descLabel.style.display = 'block';
        descLabel.style.marginBottom = '0.5rem';
        descLabel.style.color = 'var(--a-text-soft)';
        card.appendChild(descLabel);

        const descContainer = document.createElement('div');
        descContainer.style.background = 'var(--a-bg-alt)';
        descContainer.style.padding = '1rem';
        descContainer.style.borderRadius = '4px';
        descContainer.style.borderLeft = '4px solid var(--a-accent)';
        descContainer.style.marginBottom = '1rem';
        
        const fragment = document.createRange().createContextualFragment(order.description);
        descContainer.appendChild(fragment);
        
        card.appendChild(descContainer);

        const actions = document.createElement('div');
        actions.style.display = 'flex';
        actions.style.gap = '1rem';
        actions.style.marginTop = '1rem';

        const approveBtn = document.createElement('button');
        approveBtn.textContent = 'Approve Order';
        approveBtn.style.background = 'var(--a-green, #28a745)';
        approveBtn.style.color = 'white';
        approveBtn.style.border = 'none';
        approveBtn.style.padding = '0.5rem 1rem';
        approveBtn.style.borderRadius = '4px';
        approveBtn.style.cursor = 'pointer';

        const rejectBtn = document.createElement('button');
        rejectBtn.textContent = 'Reject (Needs Info)';
        rejectBtn.style.background = 'var(--a-red, #dc3545)';
        rejectBtn.style.color = 'white';
        rejectBtn.style.border = 'none';
        rejectBtn.style.padding = '0.5rem 1rem';
        rejectBtn.style.borderRadius = '4px';
        rejectBtn.style.cursor = 'pointer';

        actions.appendChild(approveBtn);
        actions.appendChild(rejectBtn);
        card.appendChild(actions);

        ordersRef.current.appendChild(card);
      });
    }
  }, [orders]);

  if (error) {
    return (
      <div className="admin-container" style={{ padding: '4rem 2rem', maxWidth: '800px', margin: '0 auto', textAlign: 'center' }}>
        <h1 style={{ color: 'var(--a-red)', fontSize: '2.5rem', marginBottom: '1rem' }}>Access Denied</h1>
        <div style={{ background: 'var(--a-bg-white)', padding: '2rem', border: '1px solid var(--a-line)', borderRadius: '8px' }}>
          <p style={{ fontSize: '1.2rem', color: 'var(--a-text-soft)' }}>
            There's no access without a valid session.
          </p>
          <p style={{ marginTop: '1rem', color: 'var(--a-text-faint)' }}>
            Please authenticate as a Support User to view this page.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', minHeight: '100vh', background: 'var(--a-bg)' }}>
      <aside style={{ width: '250px', background: 'var(--a-bg-white)', borderRight: '1px solid var(--a-line)', padding: '2rem 1rem' }}>
        <h2 style={{ color: 'var(--a-red)', marginBottom: '2rem', textAlign: 'center' }}>AstraTech Admin</h2>
        <nav style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div style={{ padding: '0.75rem', background: 'var(--a-accent)', color: 'white', borderRadius: '4px', fontWeight: 'bold' }}>
            📋 Pending Orders ({orders.length})
          </div>
          <div style={{ padding: '0.75rem', color: 'var(--a-text-soft)', cursor: 'not-allowed' }}>
            ✅ Approved Orders
          </div>
          <div style={{ padding: '0.75rem', color: 'var(--a-text-soft)', cursor: 'not-allowed' }}>
            👥 Client Management
          </div>
          <div style={{ padding: '0.75rem', color: 'var(--a-text-soft)', cursor: 'not-allowed' }}>
            ⚙️ System Settings
          </div>
        </nav>
        <div style={{ marginTop: 'auto', paddingTop: '2rem', borderTop: '1px solid var(--a-line)', textAlign: 'center' }}>
          <p style={{ color: 'var(--a-text-soft)', fontSize: '0.9rem' }}>Logged in as: <strong>Support_T1</strong></p>
          <p style={{ color: 'var(--a-red)', fontSize: '0.8rem', marginTop: '0.5rem' }}>Shift ends in: 14h 23m</p>
        </div>
      </aside>

      <main style={{ flex: 1, padding: '2rem', maxWidth: '1000px' }}>
        <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem', paddingBottom: '1rem', borderBottom: '2px solid var(--a-line-strong)' }}>
          <div>
            <h1 style={{ color: 'var(--a-accent)', fontSize: '2.5rem', margin: 0 }}>Support Dashboard</h1>
            <p style={{ fontSize: '1.1rem', color: 'var(--a-text-soft)', margin: '0.5rem 0 0 0' }}>
              Reviewing orders from our highly valued clients.
            </p>
            <p style={{ fontSize: '0.9rem', color: 'var(--a-red)', margin: '0.5rem 0 0 0', fontWeight: 'bold' }}>
              <a href="http://localhost:8001/support/guide.pdf" target="_blank" rel="noreferrer" style={{ color: 'var(--a-red)', textDecoration: 'underline' }}>
                Please read the official Admin Panel Guide before your sheer stupidity tanks your KPI again. We dock pay for every brain cell you make us lose.
              </a>
            </p>
          </div>
          <div style={{ display: 'flex', gap: '1rem' }}>
            <div style={{ background: 'var(--a-bg-white)', padding: '1rem', borderRadius: '8px', border: '1px solid var(--a-line)', textAlign: 'center' }}>
              <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: 'var(--a-accent)' }}>{orders.length}</div>
              <div style={{ fontSize: '0.8rem', color: 'var(--a-text-soft)' }}>Pending</div>
            </div>
            <div style={{ background: 'var(--a-bg-white)', padding: '1rem', borderRadius: '8px', border: '1px solid var(--a-line)', textAlign: 'center' }}>
              <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: 'var(--a-green, #28a745)' }}>142</div>
              <div style={{ fontSize: '0.8rem', color: 'var(--a-text-soft)' }}>Resolved Today</div>
            </div>
          </div>
        </header>
        
        <div className="orders-list" ref={ordersRef}>
          {orders.length === 0 && (
            <div style={{ textAlign: 'center', padding: '4rem', background: 'var(--a-bg-white)', borderRadius: '8px', border: '1px dashed var(--a-line-strong)' }}>
              <h3 style={{ color: 'var(--a-text-soft)', margin: 0 }}>No orders currently pending review.</h3>
              <p style={{ color: 'var(--a-text-faint)', marginTop: '0.5rem' }}>Take a 2-minute break before the next batch arrives.</p>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

export default AdminPanel;
