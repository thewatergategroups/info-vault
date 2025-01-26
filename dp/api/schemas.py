"""
Endpoint Schemas
"""

from pydantic import BaseModel, Field

from ..schemas import DocType


class AddDocument(BaseModel):
    """Add Document Schema"""

    name: str = Field(description="Document name")
    path: str = Field(description="Document path")
    type_: DocType = Field(description="Document type")


class UpdateDocument(AddDocument):
    """Update Document Schema"""

    id_: str = Field(description="Document id")
