import sys
import types

# Create a dummy chromadb module so imports won't fail
chromadb_stub = types.ModuleType("chromadb")
chromadb_stub.Client = lambda *args, **kwargs: None
chromadb_stub.HttpClient = lambda *args, **kwargs: None

sys.modules["chromadb"] = chromadb_stub
sys.modules["chromadb.api"] = types.ModuleType("chromadb.api")
sys.modules["chromadb.errors"] = types.ModuleType("chromadb.errors")
sys.modules["chromadb.api.types"] = types.ModuleType("chromadb.api.types")
