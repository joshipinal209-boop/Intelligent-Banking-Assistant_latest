import os
import sqlite3
import json
from datetime import datetime
from typing import TypedDict, List, Dict, Any, Optional, Annotated
import operator

# --- State Definition ---

class GraphState(TypedDict):
    """
    State definition for the LangGraph workflow.
    """
    query: str
    intent: List[str]
    customer_id: str
    agent_outputs: Annotated[Dict[str, Any], operator.ior]
    mcp_calls_log: Annotated[List[Dict[str, Any]], operator.add]
    kg_queries_log: Annotated[List[str], operator.add]
    final_response: Annotated[str, lambda x, y: y or x]
    risk_level: str   # 'low'|'medium'|'high'
    requires_human: bool
    session_id: str

# --- Audit Store ---

class SqliteAuditStore:
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or os.getenv("SQLITE_PATH", "./data/app_state.sqlite")
        # Ensure directory exists
        dirname = os.path.dirname(self.db_path)
        if dirname:
            os.makedirs(dirname, exist_ok=True)
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS audit_trail (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    node_name TEXT,
                    details TEXT,
                    duration_ms FLOAT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            # Add indexes for performance
            conn.execute("CREATE INDEX IF NOT EXISTS idx_audit_session ON audit_trail(session_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_trail(timestamp)")
            conn.commit()

    def _log_event(self, session_id: str, event_type: str, node_name: Optional[str] = None, details: Any = None, duration_ms: Optional[float] = None):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO audit_trail (session_id, event_type, node_name, details, duration_ms) VALUES (?, ?, ?, ?, ?)",
                (session_id, event_type, node_name, json.dumps(details) if details else None, duration_ms)
            )
            conn.commit()

    def log_node_start(self, session_id: str, node_name: str):
        self._log_event(session_id, "NODE_START", node_name=node_name)

    def log_node_end(self, session_id: str, node_name: str, output: Optional[Dict[str, Any]] = None, duration_ms: Optional[float] = None):
        self._log_event(session_id, "NODE_END", node_name=node_name, details=output, duration_ms=duration_ms)

    def log_mcp_call(self, session_id: str, server: str, tool: str, request: Any, response: Any, duration_ms: Optional[float] = None):
        details = {
            "server": server,
            "tool": tool,
            "request": request,
            "response": response
        }
        self._log_event(session_id, "MCP_CALL", node_name=tool, details=details, duration_ms=duration_ms)

    def log_kg_query(self, session_id: str, query: str, results: Any, duration_ms: Optional[float] = None):
        details = {
            "query": query,
            "results": results
        }
        self._log_event(session_id, "KG_QUERY", node_name=query, details=details, duration_ms=duration_ms)
    
    def log_retrieval(self, session_id: str, query: str, results: Any, duration_ms: Optional[float] = None):
        details = {
            "query": query,
            "results": results
        }
        self._log_event(session_id, "RETRIEVAL", node_name="vector_store", details=details, duration_ms=duration_ms)

    def get_audit_trail(self, session_id: str) -> List[Dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT event_type, node_name, details, duration_ms, timestamp FROM audit_trail WHERE session_id = ? ORDER BY timestamp ASC",
                (session_id,)
            )
            rows = cursor.fetchall()
            results = []
            for row in rows:
                d = dict(row)
                if d.get("details"):
                    try:
                        d["details"] = json.loads(d["details"])
                    except:
                        pass
                results.append(d)
            return results

    def get_all_durations(self) -> List[Dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT event_type, node_name, duration_ms FROM audit_trail WHERE duration_ms IS NOT NULL"
            )
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def stream_all_jsonl(self):
        """
        Generator yielding each audit row as a JSON string.
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            # Stream sorted by timestamp
            cursor = conn.execute("SELECT * FROM audit_trail ORDER BY timestamp ASC")
            while True:
                row = cursor.fetchone()
                if not row:
                    break
                # Convert row to dict, parse details JSON, and then to JSON line
                d = dict(row)
                if d.get("details"):
                    try:
                        d["details"] = json.loads(d["details"])
                    except:
                        pass
                yield json.dumps(d) + "\n"
