from __future__ import annotations
from typing import TYPE_CHECKING
import customtkinter as ctk
from ...utils.nfc import NFC
from ..windows import NFCWaitWindow
from ..views import MainView, RegisterUserDetailView, DeleteUserAlertView

# ユーザー登録詳細ウィンドウ
class RegisterUserDetailWindow(ctk.CTkToplevel):
    master: MainView
    root_dir: str
    width: int
    height: int
    nfc: NFC
    nfc_wait_window: NFCWaitWindow | None = None
    id_nfc_observer: str | None = None
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

        # NFCインスタンスの作成
        self.nfc = NFC()

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

        # NFCに接続できる場合
        if self.nfc.is_connected():
            # ユーザー登録詳細ウィンドウの表示
            self.deiconify()

            # ユーザー登録詳細ウィンドウにフォーカスを設定
            def _focus() -> None:
                self.lift()
                self.focus_force()
            self.after(100, _focus)

            # NFCの接続状況を監視開始
            self._start_observe_nfc_connection()

        # NFCに接続できない場合, NFC待機ウィンドウを表示
        else:
            self.nfc_wait_window = NFCWaitWindow(
                master=self,
                width=self.width,
                height=self.height,
                destroy_callback_success=self._destroy_callback_success_for_nfc_wait_window,
                destroy_callback_failure=self._destroy_callback_failure_for_nfc_wait_window
            )

    # ユーザー登録詳細ウィンドウの終了
    def destroy(self) -> None:
        # NFCの接続状況の監視を停止
        self._stop_observe_nfc_connection()

        # ユーザー登録詳細ウィンドウの終了
        super(RegisterUserDetailWindow, self).destroy()

        # メインウィンドウの表示
        self.master.master.deiconify()

    # NFCの接続状況を監視を開始
    def _start_observe_nfc_connection(self) -> None:
        # NFCの接続状況の監視を停止 (重複防止)
        self._stop_observe_nfc_connection()

        # NFCが接続されている場合, 監視を継続
        if self.nfc.is_connected():
            self.id_nfc_observer = self.after(100, self._start_observe_nfc_connection)

        # NFCが接続されていない場合, NFC待機ウィンドウを表示
        else:
            self.nfc_wait_window = NFCWaitWindow(
                master=self,
                width=self.width,
                height=self.height,
                destroy_callback_success=self._destroy_callback_success_for_nfc_wait_window,
                destroy_callback_failure=self._destroy_callback_failure_for_nfc_wait_window
            )

    # NFCの接続状況を監視を停止
    def _stop_observe_nfc_connection(self) -> None:
        if self.id_nfc_observer is not None:
            self.after_cancel(self.id_nfc_observer)
            self.id_nfc_observer = None

    # 接続に成功した場合のコールバック関数
    def _destroy_callback_success_for_nfc_wait_window(self) -> None:
        # NFCの接続状況の監視を停止
        self._stop_observe_nfc_connection()

        # ユーザー登録詳細ウィンドウの表示
        self.deiconify()
        self.update_idletasks()

        # NFCの接続状況の監視を開始
        self.id_nfc_observer = self.after(100, self._start_observe_nfc_connection)

    # 接続に失敗した場合のコールバック関数
    def _destroy_callback_failure_for_nfc_wait_window(self) -> None:
        # 現在のビューがユーザー登録ビューの場合
        from ..views import RegisterUserView
        if isinstance(self.master.bodyview, RegisterUserView):
            # ユーザー一覧を更新
            self.master.bodyview.update_users_list()

        # ユーザー登録詳細ウィンドウの終了
        self.destroy()

class DeleteUserAlertWindow(ctk.CTkToplevel):
    master: MainView
    root_dir: str
    width: int
    height: int
    deleted_user_name: str
    deleted_user_hashed_uid: str
    def __init__(self, master: MainView, root_dir: str, width: int, height: int, deleted_user_name: str, deleted_user_hashed_uid: str, title: str = 'Delete User Confirmation') -> None:
        super(DeleteUserAlertWindow, self).__init__(master=master, width=width, height=height)
        self.root_dir = root_dir
        self.width = width
        self.height = height

        # ユーザー削除アラートウィンドウの非表示
        self.withdraw()

        # ユーザー削除アラートウィンドウの設定
        self.title(title)
        self.geometry(
            f'{self.width}x{self.height}+{int((self.winfo_screenwidth() - self.width) / 2)}+{int((self.winfo_screenheight() - self.height) / 2)}'
        )
        self.update_idletasks()
        self.resizable(False, False)

        # ユーザー削除アラートビューの作成
        DeleteUserAlertView(
            master=self,
            root_dir=self.root_dir,
            width=self.width,
            height=self.height,
            deleted_user_name=deleted_user_name,
            deleted_user_hashed_uid=deleted_user_hashed_uid
        ).pack(fill=ctk.BOTH, expand=True)

        # イベントの設定
        self.protocol('WM_DELETE_WINDOW', self.destroy)

        # メインウィンドウを非表示
        self.master.master.withdraw()

        # ユーザー削除アラートウィンドウの表示
        self.deiconify()

    # ユーザー削除アラートウィンドウの終了
    def destroy(self) -> None:
        # メインウィンドウを表示
        self.master.master.deiconify()
        self.master.bodyview.update_idletasks()

        # ユーザー削除アラートウィンドウの終了
        super(DeleteUserAlertWindow, self).destroy()