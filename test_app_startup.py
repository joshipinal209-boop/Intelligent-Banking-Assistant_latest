import sys
import traceback

sys.path.append('src')

try:
    print("Importing app...")
    import app
    print("App imported successfully. Trying to run...")
    import uvicorn
    uvicorn.run(app.app, host="127.0.0.1", port=8000)
except Exception as e:
    print(f"Failed: {e}")
    traceback.print_exc()
