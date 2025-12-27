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

DEFAULT_USER_STATE: UserState = UserState.IN    # ユーザーの在室状態のデフォルト (ユーザー登録時に使用)