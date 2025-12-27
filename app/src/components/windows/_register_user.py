from __future__ import annotations
from typing import TYPE_CHECKING
import customtkinter as ctk
from ..views import MainView, RegisterUserDetailView

# ユーザー登録詳細ウィンドウ
class RegisterUserDetailWindow(ctk.CTkToplevel):
    master: MainView
    root_dir: str
    width: int
    height: int
    id_focus_force: str
    def __init__(self, master: MainView, root_dir: str, width: int, height: int, title: str = 'Add New User') -> None:
        super(RegisterUserDetailWindow, self).__init__(master=master, width=width, height=height)
        self.root_dir = root_dir
        self.width = width
        self.height = height

        # ユーザー登録詳細ウィンドウの非表示
        self.withdraw()

        # ユーザー登録詳細ウィンドウの設定
        self.title(title)
        self.geometry(
            f'{self.width}x{self.height}+{int((self.winfo_screenwidth() - self.width) / 2)}+{int((self.winfo_screenheight() - self.height) / 2)}'
        )
        self.update_idletasks()
        self.resizable(False, False)

        # ユーザー登録詳細ビューの作成
        RegisterUserDetailView(
            master=self,
            root_dir=self.root_dir,
            width=self.width,
            height=self.height
        ).pack(fill=ctk.BOTH, expand=True)

        # イベントの設定
        self.protocol('WM_DELETE_WINDOW', self.destroy)

        # メインウィンドウの非表示
        self.master.master.withdraw()

        # ユーザー登録詳細ウィンドウの表示
        self.deiconify()

    def destroy(self) -> None:
        # ユーザー登録詳細ウィンドウの終了
        super(RegisterUserDetailWindow, self).destroy()

        # メインウィンドウの表示
        self.master.master.deiconify()