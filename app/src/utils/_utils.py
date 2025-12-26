from __future__ import annotations
import enum

# ユーザーの在室状態を表す列挙型
class UserState(enum.IntEnum):
    IN: int = enum.auto()   # 在室
    OUT: int = enum.auto()  # 不在

# ユーザーのアクションを表す列挙型
class UserAction(enum.IntEnum):
    ENTER: int = enum.auto()  # 入室
    EXIT: int = enum.auto()   # 退室