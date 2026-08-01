from enum import Enum


class ItemStatus(str, Enum):
    draft = "draft"
    auto_saved = "auto_saved"
    confirmed = "confirmed"
    discarded = "discarded"


class ItemType(str, Enum):
    note = "note"
    link = "link"
    task = "task"
    event = "event"
