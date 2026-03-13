import os
import json
import random
import uuid
from datetime import datetime, timedelta
from faker import Faker

fake = Faker('en_IN')

# Configuration
NUM_CUSTOMERS = 50
NUM_ACCOUNTS = 120
NUM_TRANSACTIONS = 1200
NUM_LOANS = 40
NUM_PRODUCTS = 15
NUM_RULES = 8

OUTPUT_DIR = "data/seed"
VECTOR_DOCS_DIR = os.path.join(OUTPUT_DIR, "vector_docs")
MCP_DIR = os.path.join(OUTPUT_DIR, "mcp")

def generate_pan():
    """Generates a synthetic PAN card number."""
    letters = "".join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ", k=5))
    digits = "".join(random.choices("0123456789", k=4))
    check = random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    return f"{letters}{digits}{check}"

def generate_data():
    # 1. Customers
    customers = []
    for _ in range(NUM_CUSTOMERS):
        customers.append({
            "customer_id": str(uuid.uuid4())[:8],
            "name": fake.name(),
            "email": fake.email(),
            "phone": fake.phone_number(),
            "address": fake.address().replace("\n", ", "),
            "pan": generate_pan(),
            "credit_score": random.randint(300, 850),
            "risk_profile": random.choice(["Low", "Medium", "High"]),
            "kyc_status": random.choice(["Verified", "Pending", "Failed"]),
            "created_at": fake.date_this_decade().isoformat()
        })

    # 2. Accounts
    accounts = []
    account_types = ["Savings", "Current", "Credit Card", "Fixed Deposit"]
    for _ in range(NUM_ACCOUNTS):
        owner = random.choice(customers)
        accounts.append({
            "account_id": f"ACC{random.randint(100000, 999999)}",
            "customer_id": owner["customer_id"],
            "account_type": random.choice(account_types),
            "balance": round(random.uniform(1000, 500000), 2),
            "currency": "INR",
            "status": random.choice(["Active", "Dormant", "Frozen"]),
            "last_txn_date": (datetime.now() - timedelta(days=random.randint(0, 365))).isoformat()
        })

    # 3. Transactions
    transactions = []
    txn_types = ["UPI", "NEFT", "IMPS", "ATM Withdrawal", "POS", "Bill Pay"]
    for _ in range(NUM_TRANSACTIONS):
        acc = random.choice(accounts)
        amount = round(random.uniform(10, 50000), 2)
        transactions.append({
            "txn_id": f"TXN{random.randint(10000000, 99999999)}",
            "account_id": acc["account_id"],
            "type": random.choice(txn_types),
            "amount": amount,
            "direction": random.choice(["Debit", "Credit"]),
            "timestamp": (datetime.now() - timedelta(days=random.randint(0, 180))).isoformat(),
            "merchant": fake.company(),
            "status": random.choice(["Success", "Pending", "Failed"])
        })

    # 4. Loans
    loans = []
    loan_types = ["Home Loan", "Personal Loan", "Car Loan", "Education Loan"]
    for _ in range(NUM_LOANS):
        owner = random.choice(customers)
        priority = random.choice(["Low", "Normal", "High"])
        loans.append({
            "loan_id": f"LOAN{random.randint(1000, 9999)}",
            "customer_id": owner["customer_id"],
            "type": random.choice(loan_types),
            "amount": round(random.uniform(50000, 2000000), 2),
            "interest_rate": round(random.uniform(7.5, 15.0), 2),
            "tenure_months": random.choice([12, 24, 36, 60, 120]),
            "emi": round(random.uniform(5000, 50000), 2),
            "status": random.choice(["Active", "Closed", "Default"]),
            "risk_flag": random.random() < 0.1
        })

    # 5. Products
    products = []
    for i in range(NUM_PRODUCTS):
        products.append({
            "product_id": f"PROD{i+1}",
            "name": f"FinCore {fake.word().capitalize()} {random.choice(['Savings', 'Plus', 'Infinite'])}",
            "description": fake.sentence(nb_words=10),
            "eligibility": "Minimum balance of ₹10,000",
            "features": ["Zero Hidden Charges", "High Interest", "Free Insurance"]
        })

    # 6. Rules
    rules = []
    rule_categories = ["KYC", "AML", "Cybersecurity", "Data Privacy", "Digital Lending"]
    for i in range(NUM_RULES):
        rules.append({
            "rule_id": f"RULE{i+1}",
            "title": f"Regulation on {random.choice(rule_categories)} (Circular {random.randint(200, 900)}/{datetime.now().year})",
            "content": fake.paragraph(nb_sentences=5),
            "last_updated": fake.date_this_year().isoformat()
        })

    return customers, accounts, transactions, loans, products, rules

def save_kg_data(customers, accounts, loans):
    nodes = []
    edges = []

    for c in customers:
        nodes.append({"id": c["customer_id"], "label": "Customer", "properties": c})
    
    for a in accounts:
        nodes.append({"id": a["account_id"], "label": "Account", "properties": a})
        edges.append({"source": a["customer_id"], "target": a["account_id"], "label": "OWNS"})

    for l in loans:
        nodes.append({"id": l["loan_id"], "label": "Loan", "properties": l})
        edges.append({"source": l["customer_id"], "target": l["loan_id"], "label": "HAS_LOAN"})

    with open(os.path.join(OUTPUT_DIR, "kg_nodes.jsonl"), "w") as f:
        for n in nodes:
            f.write(json.dumps(n) + "\n")

    with open(os.path.join(OUTPUT_DIR, "kg_edges.jsonl"), "w") as f:
        for e in edges:
            f.write(json.dumps(e) + "\n")

def save_vector_docs(products, rules):
    # Products FAQ
    for p in products:
        filename = f"faq_{p['product_id']}.md"
        content = f"# FAQ: {p['name']}\n\n**Description:** {p['description']}\n\n## Frequently Asked Questions\n\n### What is the minimum balance?\n{p['eligibility']}\n\n### What are the key features?\n- " + "\n- ".join(p['features'])
        with open(os.path.join(VECTOR_DOCS_DIR, filename), "w") as f:
            f.write(content)

    # Rules
    for r in rules:
        filename = f"rule_{r['rule_id']}.md"
        content = f"# {r['title']}\n\n**Effective Date:** {r['last_updated']}\n\n## Regulation Overview\n{r['content']}\n\n*This is a synthetic regulation for demonstration purposes.*"
        with open(os.path.join(VECTOR_DOCS_DIR, filename), "w") as f:
            f.write(content)

def save_mcp_data(customers, accounts, transactions, loans):
    # core_banking.json
    with open(os.path.join(MCP_DIR, "core_banking.json"), "w") as f:
        json.dump({
            "customers": customers,
            "accounts": accounts,
            "transactions": transactions
        }, f, indent=2)

    # credit.json
    with open(os.path.join(MCP_DIR, "credit.json"), "w") as f:
        json.dump({
            "loans": loans,
            "credit_scores": [{"customer_id": c["customer_id"], "score": c["credit_score"]} for c in customers]
        }, f, indent=2)

    # fraud.json
    fraud_alerts = []
    for _ in range(10):
        t = random.choice(transactions)
        fraud_alerts.append({
            "alert_id": f"ALRT{random.randint(1000, 9999)}",
            "txn_id": t["txn_id"],
            "reason": random.choice(["Large Transaction", "Unusual Location", "High Frequency"]),
            "status": "Flagged"
        })
    with open(os.path.join(MCP_DIR, "fraud.json"), "w") as f:
        json.dump({"fraud_alerts": fraud_alerts}, f, indent=2)

    # compliance.json
    compliance_reports = []
    for _ in range(5):
        c = random.choice(customers)
        compliance_reports.append({
            "report_id": f"COMP{random.randint(100, 999)}",
            "customer_id": c["customer_id"],
            "status": "Review Required",
            "category": "PEP Check"
        })
    with open(os.path.join(MCP_DIR, "compliance.json"), "w") as f:
        json.dump({"compliance_reports": compliance_reports}, f, indent=2)

if __name__ == "__main__":
    print("Generating synthetic data...")
    c, a, t, l, p, r = generate_data()
    
    save_kg_data(c, a, l)
    save_vector_docs(p, r)
    save_mcp_data(c, a, t, l)
    
    print(f"Data generation complete. Artifacts saved in {OUTPUT_DIR}")
