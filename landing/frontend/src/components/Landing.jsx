import React, { useState, useRef } from 'react';
import axios from 'axios';

function Landing() {
  const [company, setCompany] = useState('');
  const [description, setDescription] = useState('');
  const [file, setFile] = useState(null);
  const [uploadUrl, setUploadUrl] = useState('');
  const [message, setMessage] = useState('');
  const previewRef = useRef(null);

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!file) return;
    const formData = new FormData();
    formData.append('file', file);
    try {
      const res = await axios.post('/api/upload', formData);
      setUploadUrl(res.data.file_url);
      setMessage(`File uploaded successfully. You can reference it at: ${res.data.file_url}`);
    } catch (err) {
      setMessage('Upload failed');
    }
  };

  const handleOrder = async (e) => {
    e.preventDefault();
    const formData = new FormData();
    formData.append('company', company);
    formData.append('description', description);
    try {
      await axios.post('/api/order', formData);
      setMessage('Order submitted successfully! Our overworked support team will review it shortly (if they survive their 16-hour shift).');
    } catch (err) {
      setMessage('Order submission failed');
    }
  };

  const handlePreview = (e) => {
    e.preventDefault();
    if (previewRef.current) {
      previewRef.current.innerHTML = '';
      const fragment = document.createRange().createContextualFragment(description);
      previewRef.current.appendChild(fragment);
    }
  };

  return (
    <div className="landing-container" style={{ padding: '2rem', maxWidth: '800px', margin: '0 auto' }}>
      <header style={{ borderBottom: '2px solid var(--a-line-strong)', paddingBottom: '1rem', marginBottom: '2rem' }}>
        <h1 style={{ color: 'var(--a-red)', fontSize: '2.5rem' }}>Astra Technologies</h1>
        <p style={{ fontSize: '1.2rem', color: 'var(--a-text-soft)' }}>
          Exploiting technology (and our workers) to the maximum. 
          We deliver results by ensuring our employees never sleep.
        </p>
      </header>
      
      <main>
        <section className="upload-section" style={{ marginBottom: '2rem', padding: '1.5rem', background: 'var(--a-bg-white)', border: '1px solid var(--a-line)' }}>
          <h2>1. Upload Attachments (Optional)</h2>
          <p style={{ marginBottom: '1rem' }}>Need to attach a specification or a script? Upload it here first.</p>
          <form onSubmit={handleUpload} style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
            <input type="file" onChange={(e) => setFile(e.target.files[0])} />
            <button type="submit" style={{ background: 'var(--a-accent)', color: 'white', padding: '0.5rem 1rem', border: 'none', cursor: 'pointer' }}>Upload</button>
          </form>
          {uploadUrl && <div style={{ marginTop: '1rem', padding: '0.5rem', background: 'var(--a-bg-alt)' }}><strong>Uploaded at:</strong> {uploadUrl}</div>}
        </section>

        <section className="order-section" style={{ padding: '1.5rem', background: 'var(--a-bg-white)', border: '1px solid var(--a-line)' }}>
          <h2>2. Submit an Order</h2>
          <p style={{ marginBottom: '1rem' }}>Describe what you need. Our support team reviews all orders via our internal admin panel.</p>
          <form onSubmit={handleOrder} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <input 
              type="text" 
              placeholder="Your Company Name" 
              value={company}
              onChange={(e) => setCompany(e.target.value)}
              required 
              style={{ padding: '0.5rem', border: '1px solid var(--a-line)' }}
            />
            <textarea 
              placeholder="Order Description (HTML supported for rich text formatting)" 
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              required 
              rows="6"
              style={{ padding: '0.5rem', border: '1px solid var(--a-line)' }}
            />
            <div style={{ display: 'flex', gap: '1rem' }}>
              <button type="button" onClick={handlePreview} style={{ background: 'var(--a-accent)', color: 'white', padding: '0.75rem', border: 'none', cursor: 'pointer', fontWeight: 'bold', flex: 1 }}>Preview</button>
              <button type="submit" style={{ background: 'var(--a-red)', color: 'white', padding: '0.75rem', border: 'none', cursor: 'pointer', fontWeight: 'bold', flex: 1 }}>Submit Order</button>
            </div>
          </form>
        </section>

        <section className="preview-section" style={{ padding: '1.5rem', background: 'var(--a-bg-white)', border: '1px solid var(--a-line)', marginTop: '2rem' }}>
          <h2>Preview</h2>
          <p style={{ marginBottom: '1rem', color: 'var(--a-text-soft)' }}>This is exactly how the admin will see your order description.</p>
          <div 
            ref={previewRef} 
            style={{ padding: '1rem', border: '1px dashed var(--a-line-strong)', minHeight: '100px', background: 'var(--a-bg)' }}
          >
          </div>
        </section>
        
        {message && <div style={{ marginTop: '2rem', padding: '1rem', background: 'var(--a-green)', color: 'white', fontWeight: 'bold' }}>{message}</div>}
      </main>
    </div>
  );
}

export default Landing;
