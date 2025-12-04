from __future__ import annotations

from datetime import datetime
from typing import Annotated, List, Literal, Optional, Union
from uuid import uuid4

from pydantic import BaseModel, Field, field_validator, model_validator


from .enums import ChildrenType, Status


class BaseNode(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    type: Literal["Base"] = "Base"
    name: str
    description: str = ""
    status: Status = Status.IN_PROGRESS
    completion_condition: str = ""
    children_type: ChildrenType = ChildrenType.LEAF
    children: List[Annotated[Union["BaseNode", "DAPPChildNode"], Field(discriminator="type")]] = Field(
        default_factory=list
    )
    progress_board: str = ""
    content_board: str = ""
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    @model_validator(mode="before")
    @classmethod
    def set_default_timestamps(cls, values: dict) -> dict:
        """Set default timestamps for backward compatibility with old JSON data."""
        if isinstance(values, dict):
            now = datetime.now()
            if "created_at" not in values or values["created_at"] is None:
                values["created_at"] = now
            if "updated_at" not in values or values["updated_at"] is None:
                values["updated_at"] = now
        return values


class DAPPChildNode(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    type: Literal["DAPP_Child"] = "DAPP_Child"
    name: str
    description: str = ""
    status: Status = Status.IN_PROGRESS
    completion_condition: str = ""
    children_type: ChildrenType = ChildrenType.LEAF
    children: List[Annotated[Union["BaseNode", "DAPPChildNode"], Field(discriminator="type")]] = Field(
        default_factory=list
    )
    progress_board: str = ""
    content_board: str = ""
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    # DAPP-specific fields
    atp: List[str] = Field(default_factory=lambda: [""])
    signposts: List[str] = Field(default_factory=list)
    triggers: List[str] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def set_default_timestamps(cls, values: dict) -> dict:
        """Set default timestamps for backward compatibility with old JSON data."""
        if isinstance(values, dict):
            now = datetime.now()
            if "created_at" not in values or values["created_at"] is None:
                values["created_at"] = now
            if "updated_at" not in values or values["updated_at"] is None:
                values["updated_at"] = now
        return values

    @field_validator("atp")
    @classmethod
    def atp_must_have_at_least_one(cls, v: List[str]) -> List[str]:
        if len(v) < 1:
            raise ValueError("ATP must have at least one entry")
        return v


class AppData(BaseModel):
    version: str = "1.0"
    last_modified: Optional[datetime] = None
    roots: List[BaseNode] = Field(default_factory=list)


# Rebuild models to resolve forward references
BaseNode.model_rebuild()
DAPPChildNode.model_rebuild()
