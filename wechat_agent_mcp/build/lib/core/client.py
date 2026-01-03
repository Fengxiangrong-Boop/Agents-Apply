import asyncio
from typing import Any, Dict, Optional
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

class MCPClient:
    """MCP 客户端封装，用于管理与不同 Skill (MCP Server) 的连接"""
    
    def __init__(self):
        self.sessions: Dict[str, ClientSession] = {}

    async def connect_to_server(self, name: str, command: str, args: list[str]):
        """连接到一个 MCP 服务器并保持 session 存活"""
        server_params = StdioServerParameters(
            command=command,
            args=args,
            env=None
        )
        
        # 在真实应用中，我们需要手动管理 transport 的生命周期
        # 这里为了简化，我们仅保存 session，注意这需要外部确保上下文正确
        from mcp.client.stdio import stdio_client
        
        transport = stdio_client(server_params)
        read, write = await transport.__aenter__()
        session = ClientSession(read, write)
        await session.__aenter__()
        await session.initialize()
        self.sessions[name] = session
        print(f"✅ 成功连接到 MCP 服务器: {name}")

    async def disconnect_all(self):
        """关闭所有连接"""
        for name, session in self.sessions.items():
            await session.__aexit__(None, None, None)
        self.sessions.clear()

    async def call_tool(self, server_name: str, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """调用特定服务器的工具"""
        session = self.sessions.get(server_name)
        if not session:
            raise ValueError(f"Server {server_name} not connected")
            
        result = await session.call_tool(tool_name, arguments)
        return result
