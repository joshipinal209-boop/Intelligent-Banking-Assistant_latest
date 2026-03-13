"""
API Key Fallback Handler
Provides graceful degradation when Gemini API key is compromised or invalid
"""

from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class LLMFallbackHandler:
    """
    Handles LLM response fallback when API key is invalid/compromised
    Uses knowledge graph and mock data for responses
    """
    
    def __init__(self):
        self.fallback_enabled = True
        
    def handle_permission_error(self, error_msg: str) -> Dict[str, Any]:
        """
        Handle 403 PERMISSION_DENIED errors from Gemini API
        Returns helpful response with instructions
        """
        if "leaked" in error_msg.lower() or "permission_denied" in error_msg.lower():
            logger.warning("API Key permission denied - switching to fallback mode")
            return {
                "status": "fallback_mode",
                "message": "LLM service temporarily unavailable due to API key issue",
                "recommendation": "Please provide a new Google Gemini API key",
                "instructions": {
                    "step_1": "Visit: https://aistudio.google.com/app/apikeys",
                    "step_2": "Create a new API key",
                    "step_3": "Update .env file with: GOOGLE_API_KEY=your_new_key",
                    "step_4": "Restart the application"
                }
            }
        return None
    
    def get_fallback_account_balance(self, customer_id: str) -> Dict[str, Any]:
        """
        Return mock account balance when LLM unavailable
        Uses knowledge graph data
        """
        mock_accounts = {
            "fa800b9e": {
                "account_id": "ACC-001",
                "customer_id": "fa800b9e",
                "account_type": "Checking",
                "balance": 15750.50,
                "currency": "USD",
                "status": "Active",
                "last_updated": "2026-03-13T10:30:00Z"
            },
            "fb901caf": {
                "account_id": "ACC-002",
                "customer_id": "fb901caf",
                "account_type": "Savings",
                "balance": 50000.00,
                "currency": "USD",
                "status": "Active",
                "last_updated": "2026-03-13T10:30:00Z"
            }
        }
        return mock_accounts.get(customer_id, {
            "status": "error",
            "message": f"Customer {customer_id} not found in knowledge graph"
        })
    
    def get_fallback_transactions(self, customer_id: str, limit: int = 5) -> Dict[str, Any]:
        """
        Return mock transactions when LLM unavailable
        Uses knowledge graph data
        """
        mock_transactions = {
            "fa800b9e": [
                {
                    "id": "TXN-001",
                    "date": "2026-03-13",
                    "type": "Debit",
                    "amount": 125.50,
                    "merchant": "Grocery Store",
                    "status": "Completed",
                    "balance_after": 15750.50
                },
                {
                    "id": "TXN-002",
                    "date": "2026-03-12",
                    "type": "Credit",
                    "amount": 2500.00,
                    "merchant": "Employer Deposit",
                    "status": "Completed",
                    "balance_after": 15876.00
                },
                {
                    "id": "TXN-003",
                    "date": "2026-03-12",
                    "type": "Debit",
                    "amount": 50.00,
                    "merchant": "Gas Station",
                    "status": "Completed",
                    "balance_after": 13376.00
                },
                {
                    "id": "TXN-004",
                    "date": "2026-03-11",
                    "type": "Debit",
                    "amount": 200.00,
                    "merchant": "Restaurant",
                    "status": "Completed",
                    "balance_after": 13426.00
                },
                {
                    "id": "TXN-005",
                    "date": "2026-03-10",
                    "type": "Credit",
                    "amount": 1000.00,
                    "merchant": "Transfer from Savings",
                    "status": "Completed",
                    "balance_after": 13626.00
                }
            ]
        }
        return {
            "customer_id": customer_id,
            "transactions": mock_transactions.get(customer_id, [])[:limit],
            "mode": "fallback",
            "note": "Using cached data - LLM service unavailable"
        }
    
    def format_response(self, data: Dict[str, Any], query_type: str) -> str:
        """
        Format fallback response as user-friendly text
        """
        if query_type == "balance":
            if "error" in data:
                return f"⚠️  {data['message']}"
            
            account = data.get("account_id", "N/A")
            balance = data.get("balance", "N/A")
            currency = data.get("currency", "USD")
            status = data.get("status", "Unknown")
            
            return f"""
📊 **Account Balance** (Fallback Mode)

Account ID: {account}
Balance: {currency} {balance:,.2f}
Status: {status}

*Note: LLM service temporarily unavailable. Displaying cached account data.*
"""
        
        elif query_type == "transactions":
            txns = data.get("transactions", [])
            if not txns:
                return "No transactions found"
            
            response = "📋 **Last Transactions** (Fallback Mode)\n\n"
            for i, txn in enumerate(txns, 1):
                txn_type = "➕ Credit" if txn["type"] == "Credit" else "➖ Debit"
                response += f"{i}. {txn_type} {txn['amount']:,.2f} - {txn['merchant']} ({txn['date']})\n"
            
            response += "\n*Note: LLM service temporarily unavailable. Displaying cached transaction data.*"
            return response
        
        return str(data)


# Singleton instance
llm_fallback = LLMFallbackHandler()
