# run_mcp_stdio.py
from src.mcp_bridge.server import mcp

if __name__ == "__main__":
    mcp.run()   # ✅ run_stdio()가 아니라 run()
