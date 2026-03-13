import React from 'react';
import type { AgentOutputs } from '../lib/types';
import { ProvenanceList } from './ProvenanceList';

interface AgentPanelProps {
  outputs: AgentOutputs;
}

export const AgentPanel: React.FC<AgentPanelProps> = ({ outputs }) => {
  const agents = [
    { id: 'account_agent', name: 'Account Agent' },
    { id: 'loan_agent', name: 'Loan Agent' },
    { id: 'fraud_agent', name: 'Fraud Agent' },
    { id: 'compliance_agent', name: 'Compliance Agent' },
  ] as const;

  return (
    <div className="agent-panel">
      <div style={{ fontSize: '1rem', fontWeight: 600, color: '#fff', marginBottom: '10px' }}>
        Agent Observability
      </div>
      {agents.map((agent) => {
        const output = outputs ? outputs[agent.id] : null;
        if (!output) return null;

        // Extract data for display, excluding provenance
        // Handle cases where output might not be an object
        let displayData = {};
        let provenance = [];
        
        if (typeof output === 'object' && output !== null) {
          const { provenance: prov, ...rest } = output as any;
          displayData = rest;
          provenance = prov;
        } else {
          displayData = { response: output };
        }

        const hasData = Object.keys(displayData).length > 0;

        return (
          <div key={agent.id} className="agent-section">
            <div className="agent-header">
              <span>{agent.name}</span>
              <span style={{ fontSize: '0.7rem', opacity: 0.6 }}>v1.0.0</span>
            </div>
            <div className="agent-body">
              {hasData && (
                <div style={{ marginBottom: '10px' }}>
                  <pre>{JSON.stringify(displayData, null, 2)}</pre>
                </div>
              )}
              <ProvenanceList provenance={provenance} />
            </div>
          </div>
        );
      })}
      {Object.keys(outputs).length === 0 && (
        <div style={{ textAlign: 'center', color: 'var(--text-secondary)', marginTop: '40px' }}>
          No agent activity recorded for this interaction.
        </div>
      )}
    </div>
  );
};
