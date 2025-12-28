from __future__ import annotations
from typing import TYPE_CHECKING
import customtkinter as ctk
from ...utils.nfc import NFC
if TYPE_CHECKING:
    from ..windows import EntryExitLogWindow

class EntryExitLogView(ctk.CTkFrame):
    master: EntryExitLogWindow
    width: int
    height: int
    nfc: NFC
    def __init__(self, master: ctk.CTkToplevel, width: int, height: int) -> None:
        super(EntryExitLogView, self).__init__(master=master, width=width, height=height)
        self.width = width
        self.height = height

        ctk.CTkLabel(
            master=self,
            text='入退室記録ビュー',
            font=ctk.CTkFont(size=20, weight='bold')
        ).pack(pady=20)