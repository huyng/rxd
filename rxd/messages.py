import typing as t
from pydantic import BaseModel


class RXDRepoUpdatedEvent(BaseModel):
    name: str = "RepoUpdatedEvent"
    app_name: str
