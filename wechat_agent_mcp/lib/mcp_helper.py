from mcp.server.fastmcp import FastMCP

def create_skill_server(name: str) -> FastMCP:
    """快速创建一个基于 FastMCP 的 Skill 服务器实例"""
    return FastMCP(name)
