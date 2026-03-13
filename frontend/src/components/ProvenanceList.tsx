import React from 'react';
import type { ProvenanceItem } from '../lib/types';

interface ProvenanceListProps {
  provenance?: ProvenanceItem[];
}

export const ProvenanceList: React.FC<ProvenanceListProps> = ({ provenance }) => {
  if (!provenance || provenance.length === 0) return null;

  return (
    <div className="provenance-container">
      <div style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '5px' }}>
        PROVENANCE
      </div>
      {provenance.map((item, index) => (
        <div key={index} className="provenance-item">
          <span className="provenance-type">[{item.type.toUpperCase()}]</span>
          <span style={{ color: '#fff' }}>{item.name}</span>
          {item.args && (
            <div style={{ fontSize: '0.7rem', color: 'var(--text-secondary)', marginTop: '2px' }}>
              args: {JSON.stringify(item.args)}
            </div>
          )}
        </div>
      ))}
    </div>
  );
};
