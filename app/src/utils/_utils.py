from __future__ import annotations
import enum

# ユーザーの在室状態を表す列挙型
class UserState(enum.IntEnum):
    IN: int = enum.auto()   # 在室
    OUT: int = enum.auto()  # 不在