from __future__ import annotations
from typing import TYPE_CHECKING
import customtkinter as ctk
if TYPE_CHECKING:
    from ..views import MainView

# アプリ情報ビューのコンポーネント
class AppInfoView(ctk.CTkFrame):
    master: MainView
    root_dir: str
    width: int
    height: int
    def __init__(self, master: MainView, root_dir: str, width: int, height: int) -> None:
        super(AppInfoView, self).__init__(master=master, width=width, height=height)
        self.root_dir = root_dir
        self.width = width
        self.height = height

        ctk.CTkLabel(
            master=self,
            text='アプリ情報ビュー',
            font=ctk.CTkFont(size=20)
        ).place(
            x=width / 2,
            y=height / 2,
            anchor='center'
        )