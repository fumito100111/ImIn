from __future__ import annotations
from typing import TYPE_CHECKING
import datetime
import customtkinter as ctk
from ...utils import UserState, UserAction
from ...utils.nfc import NFC
from ...utils.db import (
    is_registered_user,
    get_user_info,
    update_user_state
)
if TYPE_CHECKING:
    from ..windows import EnterExitLogWindow

DEFAULT_MAIN_LABEL_TEXT: str = 'ICカードをかざしてください'
DEFAULT_NOT_CONNECTED_TEXT: str = 'NFCリーダーが接続されていません'

class ClockLabel(ctk.CTkLabel):
    def __init__(self, master: EnterExitLogView, width: int, height: int) -> None:
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

class EnterExitLogView(ctk.CTkFrame):
    master: EnterExitLogWindow
    root_dir: str
    width: int
    height: int
    nfc: NFC
    id_nfc_observer: str | None = None
    main_label: ctk.CTkLabel
    clock_label: ClockLabel
    def __init__(self, master: EnterExitLogWindow, root_dir: str, width: int, height: int) -> None:
        super(EnterExitLogView, self).__init__(master=master, width=width, height=height)
        self.root_dir = root_dir
        self.width = width
        self.height = height

        # NFCの初期化
        self.nfc = NFC(command=self.callback_by_read_nfc_uid, only_once=False)

        # メインラベルの作成
        main_label_width = int(width * 0.8)
        main_label_height = int(height * 0.2)
        main_label_font_size = int(min(main_label_width, main_label_height) * 0.45)
        self.main_label = ctk.CTkLabel(
            master=self,
            width=main_label_width,
            height=main_label_height,
            text='',
            font=ctk.CTkFont(size=main_label_font_size),
            anchor=ctk.CENTER,
            fg_color='transparent',
            bg_color='transparent'
        )
        self.main_label.place(relx=0.5, rely=0.5, anchor=ctk.CENTER)

        # 時計ラベルの作成
        clock_label_width = int(width * 0.8)
        clock_label_height = int(height * 0.2)
        self.clock_label = ClockLabel(self, width=clock_label_width, height=clock_label_height)
        self.clock_label.place(relx=0.95, rely=0.95, anchor=ctk.SE)

        # NFCの接続状況を監視を開始
        self._start_observe_nfc_connection()

    # 入退室ログビューの終了
    def destroy(self) -> None:
        # NFCの接続状況の監視を停止
        self._stop_observe_nfc_connection()

        # NFCの読み取りセッションを停止
        self.nfc.stop()

        super(EnterExitLogView, self).destroy()

    # NFCの接続状況を監視を開始
    def _start_observe_nfc_connection(self) -> None:
        # NFCの接続状況の監視を停止 (重複防止)
        self._stop_observe_nfc_connection()

        # NFCが接続されている場合, 監視を継続
        if self.nfc.is_connected():
            # NFCが接続されていなかった場合, NFCの読み取りセッションを開始
            if self.main_label.cget('text') == '' or self.main_label.cget('text') == DEFAULT_NOT_CONNECTED_TEXT:
                self.main_label.configure(text=DEFAULT_MAIN_LABEL_TEXT)
                self.nfc.start()

        # NFCが接続されていない場合, NFCの読み取りセッションを停止
        else:
            self.main_label.configure(text=DEFAULT_NOT_CONNECTED_TEXT)
            self.nfc.stop()

        # NFCの接続状況の監視を継続
        self.id_nfc_observer = self.after(100, self._start_observe_nfc_connection)

    # NFCの接続状況を監視を停止
    def _stop_observe_nfc_connection(self) -> None:
        if self.id_nfc_observer is not None:
            self.after_cancel(self.id_nfc_observer)
            self.id_nfc_observer = None

    # NFCタグIDを読み取った時に呼ばれるコールバック関数
    def callback_by_read_nfc_uid(self) -> None:
        # メインラベルに読み取った情報を表示
        self.main_label.configure(text=f'{self.nfc.response.uid}\n読み取りました')

        # 1.0秒後にメインラベルをデフォルトの表示に戻す
        def clear_main_label() -> None:
            self.main_label.configure(text=DEFAULT_MAIN_LABEL_TEXT)
        self.after(1000, clear_main_label)