import time
import asyncio
from functools import wraps
from typing import Any, Callable, TypeVar, cast

# Function type variable
F = TypeVar("F", bound=Callable[..., Any])

def time_node(node_name: str) -> Callable[[F], F]:
    """
    Decorator for tracking the execution time of LangGraph nodes.
    It automatically logs NODE_START and NODE_END.
    """
    def decorator(func: F) -> F:
        if asyncio.iscoroutinefunction(func):
            @wraps(func)
            async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
                from graph.audit import audit_store
                # LangGraph nodes receive 'state' as the first arg
                state = args[0] if args and isinstance(args[0], dict) else {}
                session_id = state.get("session_id", "default")
                audit_store.log_node_start(session_id, node_name)
                start_time = time.monotonic()
                
                try:
                    result = await func(*args, **kwargs)
                    duration_ms = (time.monotonic() - start_time) * 1000
                    audit_store.log_node_end(session_id, node_name, output=result, duration_ms=duration_ms)
                    return result
                except Exception as e:
                    duration_ms = (time.monotonic() - start_time) * 1000
                    error_info = {"error": str(e)}
                    audit_store.log_node_end(session_id, node_name, output=error_info, duration_ms=duration_ms)
                    raise e
            return cast(F, async_wrapper)
        else:
            @wraps(func)
            def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
                from graph.audit import audit_store
                state = args[0] if args and isinstance(args[0], dict) else {}
                session_id = state.get("session_id", "default")
                audit_store.log_node_start(session_id, node_name)
                start_time = time.monotonic()
                
                try:
                    result = func(*args, **kwargs)
                    duration_ms = (time.monotonic() - start_time) * 1000
                    audit_store.log_node_end(session_id, node_name, output=result, duration_ms=duration_ms)
                    return result
                except Exception as e:
                    duration_ms = (time.monotonic() - start_time) * 1000
                    error_info = {"error": str(e)}
                    audit_store.log_node_end(session_id, node_name, output=error_info, duration_ms=duration_ms)
                    raise e
            return cast(F, sync_wrapper)
    return decorator

def time_tool(event_type: str, name_index: int = 1) -> Callable[[F], F]:
    """
    Decorator for tracking execution time of toolkit calls (MCP, KG, Retrieval).
    - event_type: 'MCP_CALL', 'KG_QUERY', 'RETRIEVAL'
    """
    def decorator(func: F) -> F:
        if asyncio.iscoroutinefunction(func):
            @wraps(func)
            async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
                start_time = time.monotonic()
                
                # In toolkit methods, session_id is args[0], audit_store is args[1]
                session_id = args[0] if len(args) > 0 else "default"
                audit_store = args[1] if len(args) > 1 else None

                # Extract node_name based on event context
                node_name = "unknown"
                if event_type == "MCP_CALL":
                    node_name = args[3] if len(args) > 3 else kwargs.get("tool_name", "mcp_tool")
                elif event_type == "KG_QUERY":
                    node_name = args[2] if len(args) > 2 else kwargs.get("query_func_name", "kg_query")
                elif event_type == "RETRIEVAL":
                    node_name = "vector_store"

                try:
                    result = await func(*args, **kwargs)
                    duration_ms = (time.monotonic() - start_time) * 1000
                    details = {"result": result}
                    
                    if audit_store:
                        if event_type == "MCP_CALL":
                            details["server"] = args[2] if len(args) > 2 else kwargs.get("server_url", "unknown")
                            details["tool"] = node_name
                            details["request"] = args[4] if len(args) > 4 else kwargs.get("payload", {})
                            details["response"] = result
                        elif event_type in ["KG_QUERY", "RETRIEVAL"]:
                            query_val = node_name if event_type == "KG_QUERY" else (args[2] if len(args) > 2 else kwargs.get("query", "unknown"))
                            details["query"] = query_val
                            details["results"] = result

                        audit_store._log_event(session_id, event_type, node_name=node_name, details=details, duration_ms=duration_ms)
                    
                    return result
                except Exception as e:
                    duration_ms = (time.monotonic() - start_time) * 1000
                    if audit_store:
                        details = {"error": str(e)}
                        if event_type == "MCP_CALL":
                            details["server"] = args[2] if len(args) > 2 else kwargs.get("server_url", "unknown")
                            details["tool"] = node_name
                            details["request"] = args[4] if len(args) > 4 else kwargs.get("payload", {})
                        audit_store._log_event(session_id, event_type, node_name=node_name, details=details, duration_ms=duration_ms)
                    raise e
            return cast(F, async_wrapper)
        else:
            @wraps(func)
            def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
                start_time = time.monotonic()
                session_id = args[0] if len(args) > 0 else "default"
                audit_store = args[1] if len(args) > 1 else None

                node_name = "unknown"
                if event_type == "MCP_CALL":
                    node_name = args[3] if len(args) > 3 else kwargs.get("tool_name", "mcp_tool")
                elif event_type == "KG_QUERY":
                    node_name = args[2] if len(args) > 2 else kwargs.get("query_func_name", "kg_query")
                elif event_type == "RETRIEVAL":
                    node_name = "vector_store"

                try:
                    result = func(*args, **kwargs)
                    duration_ms = (time.monotonic() - start_time) * 1000
                    details = {"result": result}
                    
                    if audit_store:
                        if event_type == "MCP_CALL":
                            details["server"] = args[2] if len(args) > 2 else kwargs.get("server_url", "unknown")
                            details["tool"] = node_name
                            details["request"] = args[4] if len(args) > 4 else kwargs.get("payload", {})
                            details["response"] = result
                        elif event_type in ["KG_QUERY", "RETRIEVAL"]:
                            query_val = node_name if event_type == "KG_QUERY" else (args[2] if len(args) > 2 else kwargs.get("query", "unknown"))
                            details["query"] = query_val
                            details["results"] = result

                        audit_store._log_event(session_id, event_type, node_name=node_name, details=details, duration_ms=duration_ms)
                    
                    return result
                except Exception as e:
                    duration_ms = (time.monotonic() - start_time) * 1000
                    if audit_store:
                        details = {"error": str(e)}
                        if event_type == "MCP_CALL":
                            details["server"] = args[2] if len(args) > 2 else kwargs.get("server_url", "unknown")
                            details["tool"] = node_name
                            details["request"] = args[4] if len(args) > 4 else kwargs.get("payload", {})
                        audit_store._log_event(session_id, event_type, node_name=node_name, details=details, duration_ms=duration_ms)
                    raise e
            return cast(F, sync_wrapper)
            
    return decorator
