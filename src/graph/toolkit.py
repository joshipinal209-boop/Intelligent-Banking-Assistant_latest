import asyncio
import httpx
import json
from typing import Any, Dict, List, Optional, Callable
from graph.state import SqliteAuditStore
from kg.engine import get_kg_engine
from vector_store.loader import get_retriever
from common.decorators import time_tool

class toolkit:
    """
    A shared toolkit for all agents to handle MCP calls, KG traversals, and retrieval.
    Includes retry logic, backoff, and automatic auditing.
    """
    
    @staticmethod
    @time_tool("MCP_CALL")
    async def mcp_call(
        session_id: str,
        audit_store: SqliteAuditStore,
        server_url: str,
        tool_name: str,
        payload: Dict[str, Any],
        max_retries: int = 3,
        backoff_factor: float = 1.5
    ) -> Dict[str, Any]:
        """
        Wraps MCP HTTP calls with exponential backoff and auditing.
        """
        last_exception = None
        for attempt in range(max_retries):
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    response = await client.post(f"{server_url}/tools/{tool_name}", json=payload)
                    response.raise_for_status()
                    data = response.json()
                    
                    # Return both data and a provenance record
                    return {
                        "data": data,
                        "provenance": {"type": "mcp", "name": tool_name, "args": payload}
                    }
            except Exception as e:
                last_exception = e
                if attempt < max_retries - 1:
                    sleep_time = backoff_factor ** attempt
                    await asyncio.sleep(sleep_time)
                continue
        
        # Log failure
        return {
            "error": str(last_exception),
            "provenance": {"type": "mcp", "name": tool_name, "args": payload, "failed": True}
        }

    @staticmethod
    @time_tool("KG_QUERY")
    def kg_query(
        session_id: str,
        audit_store: SqliteAuditStore,
        query_func_name: str,
        *args,
        **kwargs
    ) -> Any:
        """
        Wraps KG helper functions and logs traversals.
        """
        kg = get_kg_engine()
        query_func = getattr(kg, query_func_name, None)
        
        if not query_func:
            error_msg = f"KG function {query_func_name} not found."
            return {
                "error": error_msg,
                "provenance": {"type": "kg", "name": query_func_name, "args": {**kwargs, "args": list(args)}, "failed": True}
            }
            
        try:
            results = query_func(*args, **kwargs)
            return {
                "results": results,
                "provenance": {"type": "kg", "name": query_func_name, "args": {**kwargs, "args": list(args)}}
            }
        except Exception as e:
            return {
                "error": str(e),
                "provenance": {"type": "kg", "name": query_func_name, "args": {**kwargs, "args": list(args)}, "failed": True}
            }

    @staticmethod
    @time_tool("RETRIEVAL")
    def retrieve(
        session_id: str,
        audit_store: SqliteAuditStore,
        query: str,
        k: int = 3
    ) -> List[str]:
        """
        Wraps vector store retrieval with auditing.
        """
        try:
            retriever = get_retriever()
            docs = retriever.invoke(query)
            contents = [d.page_content for d in docs]
            
            return {
                "results": contents,
                "provenance": {"type": "retrieval", "name": "vector_store", "args": {"query": query, "k": k}}
            }
        except Exception as e:
            return {
                "error": str(e),
                "provenance": {"type": "retrieval", "name": "vector_store", "args": {"query": query, "k": k}, "failed": True}
            }

