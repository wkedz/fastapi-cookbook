from pydantic import BaseModel
from typing import Any, TypeAlias


TokenDataT : TypeAlias = dict[str, Any]

class Token(BaseModel):
    access_token: str
    token_type: str