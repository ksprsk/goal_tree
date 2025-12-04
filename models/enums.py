from enum import Enum


class Status(str, Enum):
    IN_PROGRESS = "진행중"
    COMPLETED = "완료"
    ON_HOLD = "보류"
    CANCELLED = "취소"
    FAILED = "실패"


class ChildrenType(str, Enum):
    LEAF = "LEAF"
    RRTD = "RRTD"
    DAPP = "DAPP"
