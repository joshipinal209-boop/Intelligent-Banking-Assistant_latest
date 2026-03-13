from graph.state import SqliteAuditStore

# Singleton instance to be used across the application
audit_store = SqliteAuditStore()
