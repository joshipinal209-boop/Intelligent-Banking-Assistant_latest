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
        padding: '15px 20px', 
        borderBottom: '2px solid rgba(88, 166, 255, 0.2)', 
        display: 'flex', 
        justifyContent: 'space-between',
        alignItems: 'center',
        background: 'linear-gradient(135deg, rgba(13, 17, 23, 0.8) 0%, rgba(22, 27, 34, 0.5) 100%)'
      }}>
        <div style={{ display: 'flex', gap: '20px', alignItems: 'center', flex: 1 }}>
          <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', display: 'flex', alignItems: 'center', gap: '12px', flex: 1 }}>
            <span style={{ 
              fontWeight: 700,
              fontSize: '0.9rem',
              background: 'linear-gradient(135deg, #58a6ff 0%, #79c0ff 100%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              backgroundClip: 'text'
            }}>
              👤 Select Customer:
            </span>
            <select 
              value={customerId} 
              onChange={e => onCustomerIdChange(e.target.value)}
              style={{ 
                background: 'linear-gradient(135deg, #161b22 0%, #0d1117 100%)', 
                border: '2px solid var(--accent-color)', 
                color: '#fff', 
                padding: '10px 14px',
                borderRadius: '6px',
                outline: 'none',
                fontSize: '0.95rem',
                minWidth: '280px',
                cursor: 'pointer',
                fontWeight: '600',
                transition: 'all 0.3s ease',
                boxShadow: '0 0 0 0 rgba(88, 166, 255, 0.1)',
                appearance: 'none',
                backgroundImage: 'url("data:image/svg+xml;charset=UTF-8,%3csvg xmlns=\'http://www.w3.org/2000/svg\' viewBox=\'0 0 24 24\' fill=\'none\' stroke=\'%2358a6ff\' stroke-width=\'2\' stroke-linecap=\'round\' stroke-linejoin=\'round\'%3e%3cpolyline points=\'6 9 12 15 18 9\'%3e%3c/polyline%3e%3c/svg%3e")',
                backgroundRepeat: 'no-repeat',
                backgroundPosition: 'right 8px center',
                backgroundSize: '20px',
                paddingRight: '36px'
              }}
              onFocus={(e) => {
                e.currentTarget.style.borderColor = '#79c0ff';
                e.currentTarget.style.boxShadow = '0 0 16px rgba(88, 166, 255, 0.4), inset 0 0 8px rgba(88, 166, 255, 0.1)';
                e.currentTarget.style.background = 'linear-gradient(135deg, #1c2128 0%, #161b22 100%)';
              }}
              onBlur={(e) => {
                e.currentTarget.style.boxShadow = '0 0 0 0 rgba(88, 166, 255, 0.1)';
                e.currentTarget.style.background = 'linear-gradient(135deg, #161b22 0%, #0d1117 100%)';
              }}
            >
              <option value="" style={{ background: '#161b22', color: '#8b949e' }}>📋 Select a Customer...</option>
              {customers.map(c => (
                <option 
                  key={c.customer_id} 
                  value={c.customer_id}
                  style={{ 
                    background: '#161b22', 
                    color: '#c9d1d9',
                    padding: '8px',
                    borderRadius: '4px'
                  }}
                >
                  {c.name} ({c.customer_id})
                </option>
              ))}
            </select>
            {customerId && (
              <div style={{
                background: 'linear-gradient(135deg, rgba(88, 166, 255, 0.15) 0%, rgba(121, 192, 255, 0.05) 100%)',
                border: '1.5px solid var(--accent-color)',
                borderRadius: '6px',
                padding: '8px 12px',
                fontSize: '0.8rem',
                color: '#79c0ff',
                fontWeight: '700',
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                whiteSpace: 'nowrap',
                boxShadow: '0 0 8px rgba(88, 166, 255, 0.2)'
              }}>
                ✓ {customers.find(c => c.customer_id === customerId)?.name}
              </div>
            )}
          </div>
          {riskLevel && (
            <div className={`badge ${riskLevel}`} style={{
              background: riskLevel === 'high' ? 'linear-gradient(135deg, rgba(248, 81, 73, 0.2), rgba(248, 81, 73, 0.05))' :
                          riskLevel === 'medium' ? 'linear-gradient(135deg, rgba(215, 170, 33, 0.2), rgba(215, 170, 33, 0.05))' :
                          'linear-gradient(135deg, rgba(35, 134, 54, 0.2), rgba(35, 134, 54, 0.05))',
              border: riskLevel === 'high' ? '1px solid rgba(248, 81, 73, 0.5)' :
                      riskLevel === 'medium' ? '1px solid rgba(215, 170, 33, 0.5)' :
                      '1px solid rgba(35, 134, 54, 0.5)',
              borderRadius: '6px',
              padding: '8px 12px',
              fontSize: '0.8rem',
              fontWeight: '700',
              color: riskLevel === 'high' ? '#f85149' :
                     riskLevel === 'medium' ? '#d7aa21' :
                     '#238636'
            }}>
              ⚠️ Risk: {riskLevel.toUpperCase()}
            </div>
          )}
          {requiresHuman && (
            <div className="badge high" style={{ 
              display: 'flex', 
              alignItems: 'center', 
              gap: '6px',
              background: 'linear-gradient(135deg, rgba(248, 81, 73, 0.2), rgba(248, 81, 73, 0.05))',
              border: '1px solid rgba(248, 81, 73, 0.5)',
              borderRadius: '6px',
              padding: '8px 12px',
              fontSize: '0.8rem',
              fontWeight: '700',
              color: '#f85149'
            }}>
              <ShieldAlert size={14} />
              Human Required
            </div>
          )}
        </div>
        <button 
          className="btn btn-secondary" 
          style={{ 
            fontSize: '0.85rem', 
            padding: '8px 12px', 
            display: 'flex', 
            alignItems: 'center', 
            gap: '6px',
            background: 'linear-gradient(135deg, #21262d 0%, #161b22 100%)',
            border: '1px solid #30363d',
            color: '#58a6ff',
            borderRadius: '6px',
            cursor: 'pointer',
            fontWeight: '600',
            transition: 'all 0.2s ease'
          }} 
          onClick={onNewSession}
          onMouseEnter={(e) => {
            e.currentTarget.style.background = 'linear-gradient(135deg, #30363d 0%, #21262d 100%)';
            e.currentTarget.style.borderColor = '#58a6ff';
            e.currentTarget.style.boxShadow = '0 0 8px rgba(88, 166, 255, 0.3)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.background = 'linear-gradient(135deg, #21262d 0%, #161b22 100%)';
            e.currentTarget.style.borderColor = '#30363d';
            e.currentTarget.style.boxShadow = 'none';
          }}
        >
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
