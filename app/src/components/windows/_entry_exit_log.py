from __future__ import annotations
from typing import TYPE_CHECKING
import customtkinter as ctk
from ..views import EntryExitLogView
if TYPE_CHECKING:
    from ...app import App
    from ..views import ViewState

# 入退室記録ウィンドウ
class EntryExitLogWindow(ctk.CTkToplevel):
    master: App
    width: int
    height: int
    view: EntryExitLogView
    id_nfc_observer: str | None = None
    def __init__(self, master: App, width: int, height: int) -> None:
        super(EntryExitLogWindow, self).__init__(master=master)
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
        self.view = EntryExitLogView(
            master=self,
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
        super(EntryExitLogWindow, self).destroy()
