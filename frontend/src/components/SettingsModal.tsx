import React, { useState } from 'react';
import { X } from 'lucide-react';

interface SettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
  baseUrl: string;
  onSave: (url: string) => void;
}

export const SettingsModal: React.FC<SettingsModalProps> = ({ isOpen, onClose, baseUrl, onSave }) => {
  const [url, setUrl] = useState(baseUrl);

  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={e => e.stopPropagation()}>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '20px' }}>
          <h2 style={{ margin: 0, fontSize: '1.2rem' }}>Settings</h2>
          <button className="scenario-btn" onClick={onClose}><X size={18} /></button>
        </div>
        
        <div style={{ marginBottom: '20px' }}>
          <label style={{ display: 'block', marginBottom: '8px', fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
            API Base URL
          </label>
          <input 
            type="text" 
            value={url} 
            onChange={e => setUrl(e.target.value)}
            style={{ 
              width: '100%', 
              background: 'var(--bg-color)', 
              border: '1px solid var(--border-color)', 
              color: '#fff',
              padding: '10px',
              borderRadius: '6px'
            }}
          />
        </div>

        <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end' }}>
          <button className="btn btn-secondary" onClick={onClose}>Cancel</button>
          <button className="btn btn-primary" onClick={() => { onSave(url); onClose(); }}>Save Changes</button>
        </div>
      </div>
    </div>
  );
};
