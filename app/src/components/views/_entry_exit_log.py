from __future__ import annotations
from typing import TYPE_CHECKING
import datetime
import customtkinter as ctk
from ...utils.nfc import NFC
if TYPE_CHECKING:
    from ..windows import EntryExitLogWindow

class ClockLabel(ctk.CTkLabel):
    def __init__(self, master: EntryExitLogView, width: int, height: int) -> None:
        super(ClockLabel, self).__init__(
            master=master,
            width=width,
            height=height,
            font=ctk.CTkFont(size=int(min(width, height) * 0.3)),
            anchor=ctk.SE,
            fg_color='transparent',
            bg_color='transparent'
        )
        self.update_clock()

    def update_clock(self) -> None:
        now: str = datetime.datetime.now().strftime('%Y / %m / %d    %H:%M:%S')
        self.configure(text=now)
        self.after(100, self.update_clock)

class EntryExitLogView(ctk.CTkFrame):
    master: EntryExitLogWindow
    width: int
    height: int
    nfc: NFC
    clock_label: ClockLabel
    def __init__(self, master: ctk.CTkToplevel, width: int, height: int) -> None:
        super(EntryExitLogView, self).__init__(master=master, width=width, height=height)
        self.width = width
        self.height = height

        # NFCの初期化
        self.nfc = NFC()

        # 時計ラベルの作成
        clock_label_width = int(width * 0.8)
        clock_label_height = int(height * 0.2)
        self.clock_label = ClockLabel(self, width=clock_label_width, height=clock_label_height)
        self.clock_label.place(relx=0.95, rely=0.95, anchor=ctk.SE)