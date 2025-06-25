from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    created_at: Optional[datetime] = None
    isDeleted: Optional[bool] = False
    isActive: Optional[bool] = True 