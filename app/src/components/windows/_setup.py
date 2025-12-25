from __future__ import annotations
from typing import TYPE_CHECKING
import customtkinter as ctk
if TYPE_CHECKING:
    from ...app import App

class SetupWindow(ctk.CTkToplevel):
    master: App
    width: int
    height: int
    def __init__(self, master: App) -> None:
        super(SetupWindow, self).__init__(master=master)
        # セットアップウィンドウの非表示
        self.withdraw()

        # インスタンス変数の初期化
        self.width, self.height = self.size()

        # セットアップウィンドウの設定
        self.title(f'Setup for {self.master.pyproject['project']['name']}')
        self.geometry(
            f'{self.width}x{self.height}+{(self.winfo_screenwidth() - self.width) // 2}+{(self.winfo_screenheight() - self.height) // 2}'
        )
        self.update_idletasks()
        self.resizable(False, False)

        # イベントの設定
        self.protocol('WM_DELETE_WINDOW', self.destroy)

        # セットアップウィンドウの表示
        self.deiconify()

        # セットアップウィンドウにフォーカスを設定
        def _focus() -> None:
            self.lift()
            self.focus_force()
        self.after(100, _focus)

    def destroy(self) -> None:
        # セットアップウィンドウの終了
        super(SetupWindow, self).destroy()

        # メインウィンドウの終了
        self.master.destroy()

    # 画面サイズに基づいてセットアップウィンドウのサイズを計算
    def size(self) -> tuple[int, int]:
        # セットアップウィンドウの幅, 高さをアプリケーションのウィンドウの高さに設定 (正方形)
        width: int = self.master.height
        height: int = self.master.height
        return width, height