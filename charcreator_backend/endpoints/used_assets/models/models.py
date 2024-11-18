from pydantic import BaseModel
from typing import Optional, Dict

class UsedAssetRequest(BaseModel):
    asset_id: int
    properties: Optional[Dict] = {}

class UsedAssetResponse(BaseModel):
    id: int
    user_id: int
    asset_id: int
    properties: Dict
    created_at: str
