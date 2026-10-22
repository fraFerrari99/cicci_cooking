from datetime import datetime
from typing import Literal

from pydantic import BaseModel

from app.config import Env


class HealthResponse(BaseModel):
    status: Literal["ok"]
    version: str
    env: Env
    timestamp: datetime
