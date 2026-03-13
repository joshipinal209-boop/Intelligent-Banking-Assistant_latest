import React from 'react';

interface ScenarioBarProps {
  onSelect: (query: string) => void;
}

export const SCENARIOS = [
  "What is my current account balance and last 5 transactions?",
  "Am I eligible for a ₹20L home loan given my current EMIs?",
  "I see a transaction I didn't make — ₹45,000 to an unknown account.",
  "What documents do I need for a MSME loan and what are the RBI rules?",
  "I want to upgrade my savings account to a premium account — what are the benefits and am I eligible?",
  "My friend transferred money to me but it hasn't reflected. My balance also looks wrong.",
  "Can I get a personal loan? I already have a car loan.",
  "Show me all accounts I own and tell me which ones have been inactive for over 6 months."
];

export const ScenarioBar: React.FC<ScenarioBarProps> = ({ onSelect }) => {
  return (
    <div className="scenario-bar">
      {SCENARIOS.map((scenario, index) => (
        <button 
          key={index} 
          className="scenario-btn"
          onClick={() => onSelect(scenario)}
        >
          {scenario}
        </button>
      ))}
    </div>
  );
};
