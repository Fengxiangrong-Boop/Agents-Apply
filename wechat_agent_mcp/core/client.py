import asyncio
import os
from typing import Any, Dict, Optional
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from contextlib import AsyncExitStack

class MCPClient:
    """MCP 客户端封装，用于管理与不同 Skill (MCP Server) 的连接"""
    
    def __init__(self):
        self.sessions: Dict[str, ClientSession] = {}
        self.exit_stack = AsyncExitStack()

    async def connect_to_server(self, name: str, command: str, args: list[str]):
        """连接到一个 MCP 服务器并使用 AsyncExitStack 管理生命周期"""
        # 强制设置子进程环境变量以支持 UTF-8 编码，防止 Windows 下出现 UnicodeDecodeError
        env = os.environ.copy()
        env["PYTHONUTF8"] = "1"
        env["PYTHONIOENCODING"] = "utf-8"

        server_params = StdioServerParameters(
            command=command,
            args=args,
            env=env
        )
        
        print(f"[Connect] 正在尝试连接 Skill [{name}]...")
        
        # 使用 exit_stack 管理 transport 和 session 的生命周期
        # 确保它们在 disconnect_all 时按照入栈顺序的反序正确关闭
        transport = stdio_client(server_params)
        read, write = await self.exit_stack.enter_async_context(transport)
        
        session = ClientSession(read, write)
        await self.exit_stack.enter_async_context(session)
        
        await session.initialize()
        self.sessions[name] = session
        print(f"[Success] 成功连接到 MCP 服务器: {name}")

    async def disconnect_all(self):
        """安全地关闭所有连接并清理资源"""
        print("[Disconnect] 正在关闭所有 MCP 连接...")
        try:
            await self.exit_stack.aclose()
        except Exception as e:
            # 针对 Windows 环境下可能出现的 UnicodeDecodeError (CP936/UTF-8 冲突) 进行容错
            print(f"[Warning] 清理 MCP 资源时发生非致命错误: {e}")
        finally:
            self.sessions.clear()
            # 重置 exit_stack 以备后用
            self.exit_stack = AsyncExitStack()
            print("[Clean] 所有连接已断开，资源已清理。")

    async def call_tool(self, server_name: str, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """调用特定服务器的工具"""
        session = self.sessions.get(server_name)
        if not session:
            raise ValueError(f"Server {server_name} not connected")
            
        result = await session.call_tool(tool_name, arguments)
        return result
