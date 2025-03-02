"""
Helper functions
"""

import httpx


async def check_file_exists(filename: str, api_url: str):
    """check file exists in system"""
    async with httpx.AsyncClient(
        transport=httpx.AsyncHTTPTransport(retries=3), timeout=10
    ) as c:
        resp = await c.get(
            f"{api_url}/documents/document",
            params={"filename": filename},
        )
        return resp.json()


async def post_file(filename: str, data: bytes, api_url: str):
    """check file exists in system"""
    async with httpx.AsyncClient(
        transport=httpx.AsyncHTTPTransport(retries=3), timeout=10
    ) as c:
        resp = await c.post(
            f"{api_url}/documents/document",
            files={"file": (filename, data)},
        )
        return resp.json()
