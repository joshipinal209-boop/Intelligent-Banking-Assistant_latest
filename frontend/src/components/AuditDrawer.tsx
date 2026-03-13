import React from 'react';
import { X, Clock, Terminal } from 'lucide-react';
import type { AuditEvent } from '../lib/types';
import { formatDate } from '../lib/utils';

interface AuditDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  events: AuditEvent[];
  sessionId: string;
}

export const AuditDrawer: React.FC<AuditDrawerProps> = ({ isOpen, onClose, events, sessionId }) => {
  return (
    <div className={`drawer ${isOpen ? 'open' : ''}`}>
      <div className="drawer-header">
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <Terminal size={20} color="var(--accent-color)" />
          <div>
            <h2 style={{ margin: 0, fontSize: '1.1rem' }}>Session Audit</h2>
            <div style={{ fontSize: '0.7rem', color: 'var(--text-secondary)' }}>Session: {sessionId}</div>
          </div>
        </div>
        <button className="scenario-btn" onClick={onClose}><X size={20} /></button>
      </div>
      
      <div className="drawer-body">
        {events.length === 0 ? (
          <div style={{ textAlign: 'center', marginTop: '100px', color: 'var(--text-secondary)' }}>
            No audit events found for this session.
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
            {events.map((event, index) => (
              <div key={index} className="audit-item">
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                  <div style={{ color: 'var(--accent-color)', fontWeight: 600, fontSize: '0.85rem' }}>
                    {event.event}
                  </div>
                  <div style={{ color: 'var(--text-secondary)', display: 'flex', alignItems: 'center', gap: '4px' }}>
                    <Clock size={12} />
                    {formatDate(event.timestamp)}
                  </div>
                </div>
                {event.node && (
                  <div style={{ fontSize: '0.75rem', marginBottom: '4px' }}>
                    <span style={{ color: 'var(--text-secondary)' }}>Node:</span> {event.node}
                  </div>
                )}
                {event.payload && (
                  <div style={{ marginTop: '8px', background: 'rgba(0,0,0,0.3)', padding: '10px', borderRadius: '4px' }}>
                    <pre style={{ fontSize: '0.7rem', color: '#88dbff' }}>
                      {JSON.stringify(event.payload, null, 2)}
                    </pre>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
