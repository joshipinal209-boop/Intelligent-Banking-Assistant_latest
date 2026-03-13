import { useState, useEffect } from 'react';
import { v4 as uuidv4 } from 'uuid';
import { api } from './lib/api';
import type { Message, AgentOutputs, QueryResponse, AuditEvent, Customer } from './lib/types';
import { ScenarioBar } from './components/ScenarioBar';
import { Chat } from './components/Chat';
import { AgentPanel } from './components/AgentPanel';
import { AuditDrawer } from './components/AuditDrawer';
import { SettingsModal } from './components/SettingsModal';
import { LatencyBadge } from './components/LatencyBadge';
import { Settings, ShieldCheck, Activity } from 'lucide-react';
import './styles.css';

function App() {
  const [sessionId, setSessionId] = useState(uuidv4());
  const [customerId, setCustomerId] = useState('');
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [messages, setMessages] = useState<Message[]>([]);
  const [agentOutputs, setAgentOutputs] = useState<AgentOutputs>({});
  const [isLoading, setIsLoading] = useState(false);
  const [lastResponse, setLastResponse] = useState<QueryResponse | null>(null);
  const [auditEvents, setAuditEvents] = useState<AuditEvent[]>([]);
  const [isAuditOpen, setIsAuditOpen] = useState(false);
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [clientLatency, setClientLatency] = useState<number | undefined>();
  const [baseUrl, setBaseUrl] = useState(api.getBaseUrl());

  const fetchCustomers = async () => {
    try {
      const data = await api.getCustomers();
      setCustomers(data);
    } catch (error) {
      console.error('Failed to fetch customers:', error);
    }
  };

  useEffect(() => {
    fetchCustomers();
  }, [baseUrl]);

  const handleNewSession = () => {
    setSessionId(uuidv4());
    setMessages([]);
    setAgentOutputs({});
    setLastResponse(null);
    setAuditEvents([]);
    setClientLatency(undefined);
  };

  const handleSend = async (queryText: string) => {
    setIsLoading(true);
    const startTime = performance.now();
    
    // Add user message immediately
    const userMessage: Message = {
      id: uuidv4(),
      role: 'user',
      content: queryText,
      timestamp: new Date(),
    };
    setMessages(prev => [...prev, userMessage]);

    try {
      const resp = await api.query({
        session_id: sessionId,
        query: queryText,
        customer_id: customerId || undefined
      });

      const endTime = performance.now();
      setClientLatency(endTime - startTime);
      setLastResponse(resp);
      setAgentOutputs(resp.agent_outputs);
      
      const assistantMessage: Message = {
        id: uuidv4(),
        role: 'assistant',
        content: resp.final_response,
        timestamp: new Date(),
        metadata: {
          latency: resp.latency_ms,
          risk_level: resp.risk_level,
          requires_human: resp.requires_human
        }
      };
      setMessages(prev => [...prev, assistantMessage]);

      // Refresh audit events if drawer is open
      if (isAuditOpen) {
        fetchAudit();
      }
    } catch (error) {
      console.error('Query failed:', error);
      const errorMessage: Message = {
        id: uuidv4(),
        role: 'assistant',
        content: `Error: Unable to connect to the banking assistant. Please check if the backend is running at ${baseUrl}.`,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const fetchAudit = async () => {
    try {
      const data = await api.getAudit(sessionId);
      setAuditEvents(data.trail);
    } catch (error) {
      console.error('Failed to fetch audit:', error);
    }
  };

  useEffect(() => {
    if (isAuditOpen) {
      fetchAudit();
    }
  }, [isAuditOpen]);

  const handleUpdateBaseUrl = (url: string) => {
    setBaseUrl(url);
    api.setBaseUrl(url);
  };

  return (
    <div className="app-container">
      <header className="header">
        <div className="brand">
          <ShieldCheck size={28} color="var(--accent-color)" />
          <span>FinCore <span style={{ fontWeight: 300, opacity: 0.7 }}>Assistant</span></span>
        </div>
        
        <div style={{ display: 'flex', gap: '20px', alignItems: 'center' }}>
          <LatencyBadge clientMs={clientLatency} serverMs={lastResponse?.latency_ms} />
          
          <div style={{ display: 'flex', gap: '10px' }}>
            <button className="btn btn-secondary" style={{ display: 'flex', alignItems: 'center', gap: '8px' }} onClick={() => setIsAuditOpen(true)}>
              <Activity size={16} /> Audit Trail
            </button>
            <button className="scenario-btn" onClick={() => setIsSettingsOpen(true)}>
              <Settings size={18} />
            </button>
          </div>
        </div>
      </header>

      <ScenarioBar onSelect={handleSend} />

      <main className="main-content">
        <Chat 
          messages={messages} 
          onSend={handleSend} 
          onNewSession={handleNewSession}
          isLoading={isLoading}
          customerId={customerId}
          onCustomerIdChange={setCustomerId}
          customers={customers}
          riskLevel={lastResponse?.risk_level}
          requiresHuman={lastResponse?.requires_human}
        />
        
        <AgentPanel outputs={agentOutputs} />
      </main>

      <footer style={{ 
        padding: '5px 20px', 
        background: 'var(--panel-bg)', 
        borderTop: '1px solid var(--border-color)', 
        fontSize: '0.7rem', 
        color: 'var(--text-secondary)',
        display: 'flex',
        justifyContent: 'space-between'
      }}>
        <span>System Status: Online | Session: {sessionId}</span>
        <span>Synthetic Banking Environment v1.0.0</span>
      </footer>

      <AuditDrawer 
        isOpen={isAuditOpen} 
        onClose={() => setIsAuditOpen(false)} 
        events={auditEvents}
        sessionId={sessionId}
      />

      <SettingsModal 
        isOpen={isSettingsOpen} 
        onClose={() => setIsSettingsOpen(false)} 
        baseUrl={baseUrl}
        onSave={handleUpdateBaseUrl}
      />
    </div>
  );
}

export default App;
