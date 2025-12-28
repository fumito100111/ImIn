from __future__ import annotations
from typing import TYPE_CHECKING
import customtkinter as ctk
from ..views import EnterExitLogView
if TYPE_CHECKING:
    from ...app import App
    from ..views import ViewState

# 入退室記録ウィンドウ
class EnterExitLogWindow(ctk.CTkToplevel):
    master: App
    root_dir: str
    width: int
    height: int
    view: EnterExitLogView
    id_nfc_observer: str | None = None
    def __init__(self, master: App, width: int, height: int) -> None:
        super(EnterExitLogWindow, self).__init__(master=master)
        self.root_dir = master.root_dir
        self.width = width
        self.height = height

        # 入退室記録ウィンドウの非表示
        self.withdraw()

        # 入退室記録ウィンドウの設定
        self.title('')
        self.geometry(f'{self.width}x{self.height}')
        self.attributes('-fullscreen', True)
        self.update_idletasks()
        self.resizable(False, False)

        # 入退室記録ビューの作成
        self.view = EnterExitLogView(
            master=self,
            root_dir=self.root_dir,
            width=self.width,
            height=self.height
        )
        self.view.pack(fill=ctk.BOTH, expand=True)

        # イベントの設定
        self.protocol('WM_DELETE_WINDOW', self.destroy)

        # 入退室記録ウィンドウの表示
        self.deiconify()

        # メインウィンドウの非表示
        self.master.withdraw()

    # 入退室記録ウィンドウの破棄
    def destroy(self) -> None:
        # フルスクリーンモードの解除
        self.attributes('-fullscreen', False)
        self.update_idletasks()

        # メインウィンドウを元の状態で再描画
        self.master.view.redraw_view()

        # メインウィンドウを更新
        self.master.update_idletasks()

        # メインウィンドウの表示
        self.master.deiconify()

        # 入退室記録ウィンドウの破棄
        super(EnterExitLogWindow, self).destroy()
