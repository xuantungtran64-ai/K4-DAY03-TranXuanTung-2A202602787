"""
🔌 MODEL CONTEXT PROTOCOL (MCP) SERVER MODULE
Mô phỏng kiến trúc MCP Server (Client-Server Architecture) cung cấp công cụ chuẩn hóa theo giao thức JSON-RPC 2.0.
"""

import json
import sys
from typing import Dict, Any, List
from tools import TOOLS_SCHEMA, dispatch_tool_call

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

class MCPAcademicServer:
    """
    Giả lập MCP Server tuân thủ chuẩn giao thức Model Context Protocol (MCP JSON-RPC 2.0)
    """
    def __init__(self, server_name: str = "vin-smart-mixologist-mcp-server"):
        self.server_name = server_name
        self.version = "2026.1.0"
        
    def list_tools(self) -> List[Dict[str, Any]]:
        """Trả về danh sách các Tools chuẩn giao thức MCP"""
        return TOOLS_SCHEMA
        
    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        [TASK 2.1] THỰC THI TOOL TRÊN MCP SERVER
        Thực thi request gọi Tool theo chuẩn MCP JSON-RPC 2.0
        """
        # 1. Gọi hàm dispatch_tool_call để lấy chuỗi JSON kết quả từ Tool Router
        raw_result = dispatch_tool_call(tool_name, arguments)
        
        # 2. Chuyển đổi chuỗi JSON kết quả thành Python Dictionary
        try:
            content = json.loads(raw_result)
        except Exception:
            content = {"raw": raw_result}
            
        # 3. Đóng gói phản hồi chuẩn MCP JSON-RPC 2.0
        return {
            "jsonrpc": "2.0",
            "server": self.server_name,
            "tool": tool_name,
            "result": content
        }


# Alias tương thích
MCPSmartBarServer = MCPAcademicServer


if __name__ == "__main__":
    print("==========================================================")
    print("🔌 KIỂM THỬ ĐỘC LẬP MCP SERVER (vin-smart-mixologist-mcp-server)")
    print("==========================================================")
    
    server = MCPAcademicServer()
    tools = server.list_tools()
    print(f"✅ Khởi tạo thành công MCP Server: {server.server_name} (Version: {server.version})")
    print(f"📦 Số lượng Tools công bố qua MCP: {len(tools)}")
    
    # In danh sách tool đã công bố
    for idx, t in enumerate(tools, 1):
        print(f"   [{idx}] {t['name']}: {t.get('description', '')[:60]}...")

    # Kiểm tra trạng thái TODO 2.1 (call_tool)
    test_result = server.call_tool("query_guest_health_and_bar_inventory", {"user_id": "USR001"})
    if not test_result or not test_result.get("result"):
        print("❌ [LỖI]: Hàm call_tool() chưa trả về đúng cấu trúc!")
    else:
        print(f"\n✅ [TASK 2.1 PASS]: Test dispatch tool 'query_guest_health_and_bar_inventory' thành công!")
        print(f"   Phản hồi JSON-RPC 2.0: {json.dumps(test_result, ensure_ascii=False, indent=2)}")
