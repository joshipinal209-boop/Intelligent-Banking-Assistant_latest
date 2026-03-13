import React from 'react';
import { formatMs } from '../lib/utils';
import { Clock } from 'lucide-react';

interface LatencyBadgeProps {
  clientMs?: number;
  serverMs?: number;
}

export const LatencyBadge: React.FC<LatencyBadgeProps> = ({ clientMs, serverMs }) => {
  if (clientMs === undefined && serverMs === undefined) return null;

  return (
    <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
      <div className="badge secondary" style={{ 
        display: 'flex', 
        alignItems: 'center', 
        gap: '4px',
        background: 'rgba(255,255,255,0.05)',
        border: '1px solid var(--border-color)',
        color: 'var(--text-secondary)'
      }}>
        <Clock size={12} />
        <span style={{ fontSize: '0.7rem' }}>
          Server: {formatMs(serverMs)}
        </span>
      </div>
      {clientMs !== undefined && (
        <div className="badge secondary" style={{ 
          display: 'flex', 
          alignItems: 'center', 
          gap: '4px',
          background: 'rgba(255,255,255,0.05)',
          border: '1px solid var(--border-color)',
          color: 'var(--text-secondary)'
        }}>
          <Clock size={12} />
          <span style={{ fontSize: '0.7rem' }}>
            Total: {formatMs(clientMs)}
          </span>
        </div>
      )}
    </div>
  );
};
