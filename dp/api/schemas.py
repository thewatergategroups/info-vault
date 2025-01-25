"""
Endpoint Schemas
"""


from pydantic import BaseModel, Field


class AddDocument(BaseModel):
    """Add Document Schema"""

    name: str = Field(..., description="Document name")