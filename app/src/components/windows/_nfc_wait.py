from __future__ import annotations
from typing import TYPE_CHECKING, Callable, Literal
import customtkinter as ctk
from ...utils.nfc import NFC
if TYPE_CHECKING:
    from ..windows import RegisterUserDetailWindow

class NFCWaitView(ctk.CTkFrame):
    master: NFCWaitWindow
    width: int
    height: int
    label: ctk.CTkLabel
    id_animation: str | None = None
    def __init__(self, master: NFCWaitWindow, width: int, height: int) -> None:
        super(NFCWaitView, self).__init__(master=master, width=width, height=height)
        self.width = width
        self.height = height

        # NFC待機ラベルの作成
        label_width: int = int(self.width * 0.8)
        label_height: int = int(self.height * 0.2)
        label_font_size: int = int(min(label_width, label_height) / 4)
        self.label = ctk.CTkLabel(
            master=self,
            width=label_width,
            height=label_height,
            text='NFCリーダーを接続してください',
            font=ctk.CTkFont(size=label_font_size),
            justify=ctk.CENTER
        )
        self.label.place(relx=0.5, rely=0.5, anchor=ctk.CENTER)

        # あなたのNFCリーダーが接続されるまでアニメーションを開始
        self.start_animation()

    # 接続待機中のアニメーションを開始
    def start_animation(self, step: int = 0) -> None:
        dots: str = '・' * step
        self.label.configure(text=f'NFCリーダーを接続してください{dots}')
        step = (step + 1) % 4
        self.id_animation = self.after(1000, lambda: self.start_animation(step))

    # 接続待機中のアニメーションを停止
    def stop_animation(self) -> None:
        if self.id_animation is not None:
            self.after_cancel(self.id_animation)
            self.id_animation = None

class NFCWaitWindow(ctk.CTkToplevel):
    master: RegisterUserDetailWindow
    width: int
    height: int
    destroy_callback_success: Callable[[], None] | None
    destroy_callback_failure: Callable[[], None] | None
    nfc_wait_view: NFCWaitView
    id_nfc_observer: str | None = None
    def __init__(self, master: RegisterUserDetailWindow, width: int, height: int, destroy_callback_success: Callable[[], None] | None = None, destroy_callback_failure: Callable[[], None] | None = None) -> None:
        super(NFCWaitWindow, self).__init__(master=master)
        self.width = width
        self.height = height
        self.destroy_callback_success = destroy_callback_success
        self.destroy_callback_failure = destroy_callback_failure

        # NFC待機ウィンドウの非表示
        self.withdraw()

        # NFC待機ウィンドウの設定
        self.title('Wait for NFC Reader Connection')
        self.geometry(
            f'{self.width}x{self.height}+{int((self.winfo_screenwidth() - self.width) / 2)}+{int((self.winfo_screenheight() - self.height) / 2)}'
        )
        self.update_idletasks()
        self.resizable(False, False)

        # NFC待機ビューの作成
        self.nfc_wait_view = NFCWaitView(
            master=self,
            width=self.width,
            height=self.height
        )
        self.nfc_wait_view.pack(fill=ctk.BOTH, expand=True)

        # イベントの設定
        self.protocol('WM_DELETE_WINDOW', lambda: self.destroy('failure'))

        # 親ウィンドウの非表示
        self.master.withdraw()

        # NFC待機ウィンドウの表示
        self.deiconify()

        # NFC待機ウィンドウにフォーカスを設定
        def _focus() -> None:
            self.lift()
            self.focus_force()
        self.after(100, _focus)

        # NFCの接続状況を監視開始
        self._start_observe_nfc_connection()

    # NFC待機ウィンドウの終了
    def destroy(self, status: Literal['success', 'failure'] | None = None) -> None:
        # 親ウィンドウからdestroyを呼び出された場合 (親ウィンドウのdestoryループ防止)
        if status is None:
            return super(NFCWaitWindow, self).destroy()

        # NFCの接続状況の監視を停止
        self._stop_observe_nfc_connection()

        # コールバック関数の実行 (成功した場合)
        if status == 'success':
            # コールバック関数が設定されている場合
            if self.destroy_callback_success is not None:
                # アニメーションの停止
                self.nfc_wait_view.stop_animation()

                # NFCリーダー接続成功メッセージの表示
                self.nfc_wait_view.label.configure(text='NFCリーダーが接続されました')

                # 一定時間後にコールバック関数を実行
                def _destroy_callback_success() -> None:
                    # コールバック関数の実行
                    self.destroy_callback_success()
                    super(NFCWaitWindow, self).destroy()
                self.after(1000, _destroy_callback_success)

            # コールバック関数が設定されていない場合
            else:
                # NFC待機ウィンドウの破棄
                super(NFCWaitWindow, self).destroy()

        # コールバック関数の実行 (失敗した場合) (注意: コールバック関数内の親ウィンドウの破棄でNFC待機ウィンドウも破棄される)
        if status == 'failure':
            # コールバック関数が設定されている場合
            if self.destroy_callback_failure is not None:
                self.destroy_callback_failure()

            # コールバック関数が設定されていない場合
            else:
                # NFC待機ウィンドウの破棄
                super(NFCWaitWindow, self).destroy()

    # NFCの接続状況を監視
    def _start_observe_nfc_connection(self) -> None:
        # NFCが接続された場合, NFC待機ウィンドウを閉じる
        if self.master.nfc.is_connected():
            self.destroy('success')

        # 一定時間後に再度監視
        self.id_nfc_observer = self.after(100, self._start_observe_nfc_connection)

    # NFCの接続状況を監視を停止
    def _stop_observe_nfc_connection(self) -> None:
        if self.id_nfc_observer is not None:
            self.after_cancel(self.id_nfc_observer)
            self.id_nfc_observer = None