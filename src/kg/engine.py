import json
import os
import networkx as nx
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

class KGEngine:
    def __init__(self, data_dir: str = "data/seed"):
        self.data_dir = data_dir
        self.graph = nx.MultiDiGraph()
        self._load_data()

    def _load_data(self):
        nodes_path = os.path.join(self.data_dir, "kg_nodes.jsonl")
        edges_path = os.path.join(self.data_dir, "kg_edges.jsonl")

        if not os.path.exists(nodes_path) or not os.path.exists(edges_path):
            print(f"Warning: KG data files not found in {self.data_dir}")
            return

        # Load Nodes
        with open(nodes_path, "r") as f:
            for line in f:
                node = json.loads(line)
                self.graph.add_node(node["id"], **node["properties"], label=node["label"])

        # Load Edges
        with open(edges_path, "r") as f:
            for line in f:
                edge = json.loads(line)
                self.graph.add_edge(
                    edge["source"], 
                    edge["target"], 
                    key=edge["label"], 
                    **edge.get("properties", {})
                )
        
        # Load Transactions for overlap analysis
        cb_path = os.path.join(self.data_dir, "mcp/core_banking.json")
        if os.path.exists(cb_path):
            with open(cb_path, "r") as f:
                cb_data = json.load(f)
                for txn in cb_data.get("transactions", []):
                    # Customer -> Merchant (via Account)
                    # For simplicity in this mock, we link Account to Merchant
                    acc_id = txn["account_id"]
                    merchant = txn["merchant"]
                    if acc_id in self.graph:
                        self.graph.add_node(merchant, label="Merchant")
                        self.graph.add_edge(acc_id, merchant, key="PAID", amount=txn["amount"])

    def rules_for_product(self, product_id: str) -> List[Dict[str, Any]]:
        """Finds rules associated with a product (mock cross-check)."""
        # In this mock, we simply match rules that mention the product type in their content
        # or have a direct link if we had added them.
        # Since rule nodes aren't explicitly linked in the seed, we'll return a filtered list.
        relevant_rules = []
        for node_id, data in self.graph.nodes(data=True):
            if data.get("label") == "Rule":
                # Mock logic: Home loans match rule_001, etc.
                if "Home" in product_id and "Lending" in data.get("properties", {}).get("title", ""):
                    relevant_rules.append({"id": node_id, **data.get("properties", {})})
                elif "KYC" in data.get("properties", {}).get("title", ""):
                     relevant_rules.append({"id": node_id, **data.get("properties", {})})
        return relevant_rules

    def fraud_payee_overlap(self, merchant_name: str) -> List[str]:
        """
        Finds other customers whose accounts have paid the same merchant.
        """
        if merchant_name not in self.graph:
            return []
        
        overlapping_customers = set()
        # Find accounts that paid this merchant
        for acc_id, _, data in self.graph.in_edges(merchant_name, data=True):
            # Find owners of these accounts
            for cust_id, _, edge_data in self.graph.in_edges(acc_id, data=True):
                edge_label = self.graph.get_edge_data(cust_id, acc_id)
                if "OWNS" in edge_label:
                    overlapping_customers.add(cust_id)
        
        return list(overlapping_customers)

    def find_inactive_accounts(self, customer_id: str, months: int = 6) -> List[str]:
        """
        Finds accounts belonging to a customer that have been inactive for X months.
        Activity is judged by 'last_txn_date' property on the Account node.
        """
        if customer_id not in self.graph:
            return []

        inactive_accounts = []
        cutoff_date = datetime.now() - timedelta(days=months * 30)

        # Find all accounts owned by this customer
        # Assuming relationship is Customer --(OWNS)--> Account
        for _, account_id, data in self.graph.out_edges(customer_id, data=True):
            edge_type = self.graph.get_edge_data(customer_id, account_id)
            # Check for OWNS relationship
            if "OWNS" in edge_type:
                account_node = self.graph.nodes[account_id]
                last_txn_str = account_node.get("last_txn_date")
                
                if last_txn_str:
                    try:
                        # Handle potential ISO format with 'T' or just date
                        date_part = last_txn_str.split("T")[0]
                        last_txn_date = datetime.strptime(date_part, "%Y-%m-%d")
                        if last_txn_date < cutoff_date:
                            inactive_accounts.append(account_id)
                    except (ValueError, TypeError):
                        # If date format is weird, fallback to check-based
                        pass
                else:
                    # No transaction date might imply very old or never used
                    inactive_accounts.append(account_id)

        return inactive_accounts

    def get_customer_loans(self, customer_id: str) -> List[Dict[str, Any]]:
        """Helper to get all loans for a customer from KG."""
        if customer_id not in self.graph:
            return []
        
        loans = []
        for _, loan_id in self.graph.out_edges(customer_id):
            edge_data = self.graph.get_edge_data(customer_id, loan_id)
            if "HAS_LOAN" in edge_data:
                loans.append({
                    "id": loan_id,
                    **self.graph.nodes[loan_id]
                })
        return loans

    def get_customer_accounts(self, customer_id: str) -> List[Dict[str, Any]]:
        """Helper to get all accounts for a customer from KG."""
        if customer_id not in self.graph:
            return []
        
        accounts = []
        for _, account_id in self.graph.out_edges(customer_id):
            edge_data = self.graph.get_edge_data(customer_id, account_id)
            if "OWNS" in edge_data:
                accounts.append({
                    "id": account_id,
                    **self.graph.nodes[account_id]
                })
        return accounts

    def get_upgrade_eligibility(self, customer_id: str, target_product: str) -> Dict[str, Any]:
        """
        Checks if customer is eligible for a product upgrade based on current products and status.
        """
        # Mock logic: Premium requires > 100k balance or 1 year history
        accounts = self.get_customer_accounts(customer_id)
        current_products = [a.get("account_type") for a in accounts]
        
        # In a real KG, we'd traverse Customer --(ELIBIGLE_FOR)--> Product
        # For this mock, we use rule-based logic
        eligible = True
        reason = "Meets minimum balance and tenure requirements for Premium upgrade."
        
        if "Premium" in target_product and any("Fixed Deposit" in p for p in current_products):
             eligible = True
        
        return {
            "eligible": eligible,
            "target_product": target_product,
            "current_products": current_products,
            "reason": reason
        }

# Singleton instance
_engine = None

def get_kg_engine() -> KGEngine:
    global _engine
    if _engine is None:
        _engine = KGEngine()
    return _engine
