import React, { useState, useRef, useEffect } from 'react';
import type { Message, Customer } from '../lib/types';
import { Send, User, Bot, PlusCircle, ShieldAlert } from 'lucide-react';

interface ChatProps {
  messages: Message[];
  onSend: (message: string) => void;
  onNewSession: () => void;
  isLoading: boolean;
  customerId: string;
  onCustomerIdChange: (id: string) => void;
  customers: Customer[];
  riskLevel?: 'low' | 'medium' | 'high';
  requiresHuman?: boolean;
}

export const Chat: React.FC<ChatProps> = ({ 
  messages, 
  onSend, 
  onNewSession, 
  isLoading, 
  customerId, 
  onCustomerIdChange,
  customers,
  riskLevel,
  requiresHuman
}) => {
  const [input, setInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(scrollToBottom, [messages]);

  const handleSubmit = (e?: React.FormEvent) => {
    e?.preventDefault();
    if (input.trim() && !isLoading) {
      onSend(input);
      setInput('');
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
      handleSubmit();
    }
  };

  return (
    <div className="chat-panel">
      <div style={{ 
        padding: '10px 20px', 
        borderBottom: '1px solid var(--border-color)', 
        display: 'flex', 
        justifyContent: 'space-between',
        alignItems: 'center',
        background: 'rgba(255,255,255,0.02)'
      }}>
        <div style={{ display: 'flex', gap: '15px', alignItems: 'center' }}>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', display: 'flex', alignItems: 'center', gap: '8px' }}>
            Customer: 
            <select 
              value={customerId} 
              onChange={e => onCustomerIdChange(e.target.value)}
              style={{ 
                background: 'var(--panel-bg)', 
                border: '1px solid var(--border-color)', 
                color: '#fff', 
                padding: '4px 8px',
                borderRadius: '4px',
                outline: 'none',
                fontSize: '0.8rem',
                minWidth: '150px'
              }}
            >
              <option value="">Select Customer...</option>
              {customers.map(c => (
                <option key={c.customer_id} value={c.customer_id}>
                  {c.name} ({c.customer_id})
                </option>
              ))}
            </select>
          </div>
          {riskLevel && (
            <div className={`badge ${riskLevel}`}>
              Risk: {riskLevel}
            </div>
          )}
          {requiresHuman && (
            <div className="badge high" style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
              <ShieldAlert size={12} />
              Human Required
            </div>
          )}
        </div>
        <button className="btn btn-secondary" style={{ fontSize: '0.8rem', padding: '4px 10px', display: 'flex', alignItems: 'center', gap: '5px' }} onClick={onNewSession}>
          <PlusCircle size={14} /> New Session
        </button>
      </div>

      <div className="messages-list">
        {messages.length === 0 && (
          <div style={{ textAlign: 'center', color: 'var(--text-secondary)', marginTop: '100px' }}>
            <Bot size={48} style={{ opacity: 0.2, marginBottom: '20px' }} />
            <div>How can I assist you with your banking needs today?</div>
            <div style={{ fontSize: '0.8rem', marginTop: '10px' }}>Select a scenario above to get started.</div>
          </div>
        )}
        {messages.map((m) => (
          <div key={m.id} className={`message ${m.role}`}>
            <div style={{ display: 'flex', gap: '8px', marginBottom: '5px', alignItems: 'center' }}>
              {m.role === 'user' ? <User size={14} /> : <Bot size={14} color="var(--accent-color)" />}
              <span style={{ fontWeight: 600, fontSize: '0.75rem', opacity: 0.8 }}>
                {m.role === 'user' ? 'YOU' : 'FINCORE AI'}
              </span>
            </div>
            <div style={{ whiteSpace: 'pre-wrap' }}>{m.content}</div>
          </div>
        ))}
        {isLoading && (
          <div className="message assistant" style={{ opacity: 0.7 }}>
            <div className="typing-indicator">
              <span>Thinking...</span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="chat-input-area">
        <div className="input-container">
          <textarea 
            rows={3}
            placeholder="Type your message here... (Ctrl+Enter to send)"
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={isLoading}
          />
          <button 
            className="btn btn-primary" 
            style={{ width: '60px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}
            onClick={handleSubmit}
            disabled={isLoading || !input.trim()}
          >
            <Send size={20} />
          </button>
        </div>
      </div>
    </div>
  );
};
