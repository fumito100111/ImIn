from __future__ import annotations
from typing import TYPE_CHECKING
import tkinter as tk
import customtkinter as ctk
from PIL import Image
from ...utils import UserState, UserAction, DEFAULT_USER_STATE
from ...utils.nfc import UID, NFC
from ...utils.db import (
    is_registered_user,
    register_user
)
from ..views import RegisterEntry, RegisterButton
if TYPE_CHECKING:
    from ..views import MainView
    from ..windows import RegisterUserDetailWindow

# 新規ユーザー追加ボタン
class AddNewUserButton(ctk.CTkButton):
    master: RegisterUserView
    root_dir: str
    width: int
    height: int
    def __init__(self, master: RegisterUserView, root_dir: str, width: int, height: int) -> None:
        super(AddNewUserButton, self).__init__(
            master=master,
            width=width,
            height=height,
            text='',
            image=ctk.CTkImage(
                light_image=Image.open(f'{root_dir}/assets/icons/light/person_add.png'),
                dark_image=Image.open(f'{root_dir}/assets/icons/dark/person_add.png'),
                size=(height, height)
            ),
            command=self.switch_to_register_user_detail_window,
            fg_color='transparent',
            bg_color='transparent',
            hover=True
        )
        self.root_dir = root_dir
        self.width = width
        self.height = height

    # 新規ユーザー登録詳細ウィンドウへ切り替え
    def switch_to_register_user_detail_window(self) -> None:
        self.master.switch_to_register_user_detail_window()

# ユーザー登録詳細ビューのコンポーネント
class RegisterUserDetailView(ctk.CTkFrame):
    master: RegisterUserDetailWindow
    root_dir: str
    width: int
    height: int
    nfc_uid_entry: RegisterEntry
    user_name_entry: RegisterEntry
    register_button: RegisterButton
    nfc: NFC
    id_entries_observer: str | None = None
    def __init__(self, master: RegisterUserDetailWindow, root_dir: str, width: int, height: int) -> None:
        super(RegisterUserDetailView, self).__init__(master=master, width=width, height=height)
        self.root_dir = root_dir
        self.width = width
        self.height = height

        # エントリーの設定
        register_entry_width: int = width
        register_entry_height: int = int(height * 0.4)

        # NFC UIDエントリーの作成
        self.nfc_uid_entry = RegisterEntry(
            master=self,
            width=register_entry_width,
            height=register_entry_height,
            text='NFCタグID',
            description='NFCリーダーにタグをかざしてください',
            show=None
        )
        self.nfc_uid_entry.place(relx=0.5, rely=0.05, anchor=ctk.N)

        # NFC UIDエントリーを読み取り専用に設定
        self.nfc_uid_entry.entry.configure(state=ctk.DISABLED)

        # ユーザー名エントリーの作成
        self.user_name_entry = RegisterEntry(
            master=self,
            width=register_entry_width,
            height=register_entry_height,
            text='ユーザー名',
            description='',
            show=None
        )
        self.user_name_entry.place(relx=0.5, rely=0.45, anchor=ctk.N)

        # 登録ボタンの作成
        self.register_button = RegisterButton(
            master=self,
            width=int(width * 0.2),
            height=int(height * 0.1),
            text='登録',
            command=self.register_user
        )
        self.register_button.place(relx=0.95, rely=0.95, anchor=ctk.SE)

        # 名前エントリーにフォーカスを設定
        self.user_name_entry.entry.focus_set()

        # NFCの初期化とタグ読み取り開始
        self.nfc = NFC(command=self.callback_by_read_nfc_uid, only_once=False)
        self.nfc.start()

        # エントリーの監視を開始
        self._observe_entries()

    def destroy(self) -> None:
        # エントリーの監視を停止
        if self.id_entries_observer is not None:
            self.after_cancel(self.id_entries_observer)
            self.id_entries_observer = None

        # 登録詳細ウィンドウを非表示
        self.master.withdraw()

        # NFCセッションの停止
        self.nfc.stop()

        # ユーザー登録詳細ビューの破棄
        super(RegisterUserDetailView, self).destroy()

    def register_user(self, event: tk.Event | None = None) -> None:
        # エントリーの監視を停止
        if self.id_entries_observer is not None:
            self.after_cancel(self.id_entries_observer)
            self.id_entries_observer = None

        # ユーザー登録ボタンを無効化
        self.register_button.configure(state=ctk.DISABLED)

        # エントリーから値を取得
        uid: UID = UID(self.nfc_uid_entry.entry.get().strip())
        user_name: str = self.user_name_entry.entry.get().strip()

        # ユーザー情報を登録に成功した場合
        if register_user(root_dir=self.root_dir, id=uid.sha256(), name=user_name, state=DEFAULT_USER_STATE):
            # エントリーを無効化
            self.register_button.configure(state=ctk.DISABLED)
            self.nfc_uid_entry.entry.configure(state=ctk.DISABLED)
            self.user_name_entry.entry.configure(state=ctk.DISABLED)

            # 登録成功メッセージを1秒間表示した後、ウィンドウを閉じる
            text_color: str = self.user_name_entry.description.cget('text_color')
            self.user_name_entry.description.configure(text='ユーザーが正常に登録されました', text_color='green')
            def _close_window() -> None:
                self.user_name_entry.description.configure(text='', text_color=text_color)
                self.master.destroy()
            self.after(1000, _close_window)

        # ユーザー情報の登録に失敗した場合
        else:
            # NFCタグIDをクリアして無効化
            self.nfc_uid_entry.entry.configure(state=ctk.NORMAL)
            self.nfc_uid_entry.entry.delete(0, ctk.END)
            self.nfc_uid_entry.entry.configure(state=ctk.DISABLED)

            # ユーザー名をクリア
            self.user_name_entry.entry.configure(state=ctk.NORMAL)
            self.user_name_entry.entry.delete(0, ctk.END)

            # エントリー監視を再開
            self._observe_entries()

            # 登録失敗メッセージを1秒間表示
            text_color: str = self.user_name_entry.description.cget('text_color')
            self.user_name_entry.description.configure(text='ユーザーの登録に失敗しました', text_color='red')
            def _clear_error_message() -> None:
                self.user_name_entry.description.configure(text='', text_color=text_color)
            self.after(1000, _clear_error_message)

    # NFCタグIDを読み取った時に呼ばれるコールバック関数
    def callback_by_read_nfc_uid(self) -> None:
        uid: UID = self.nfc.response.uid

        # NFCタグがすでに登録されている場合は警告メッセージを1秒間表示
        if is_registered_user(self.root_dir, uid.sha256()):
            text_color: str = self.nfc_uid_entry.description.cget('text_color')
            self.nfc_uid_entry.description.configure(text='このNFCタグはすでに登録されています', text_color='red')
            def _clear_warning_message() -> None:
                self.nfc_uid_entry.description.configure(text='', text_color=text_color)
            self.after(1000, _clear_warning_message)
            return

        # 成功メッセージを1秒間表示
        text_color: str = self.nfc_uid_entry.description.cget('text_color')
        self.nfc_uid_entry.description.configure(text='NFCタグが正常に読み取れました', text_color='green')
        def _clear_success_message() -> None:
            self.nfc_uid_entry.description.configure(text='', text_color=text_color)
        self.after(1000, _clear_success_message)

        # NFCタグIDエントリーにUIDを設定
        self.nfc_uid_entry.entry.configure(state=ctk.NORMAL)
        self.nfc_uid_entry.entry.delete(0, ctk.END)
        self.nfc_uid_entry.entry.insert(0, uid)
        self.nfc_uid_entry.entry.configure(state=ctk.DISABLED)

    # それぞれのエントリーが空白でない場合に登録ボタンを有効化 (ループで監視)
    def _observe_entries(self) -> None:
        nfc_uid: str = self.nfc_uid_entry.entry.get().strip()
        user_name: str = self.user_name_entry.entry.get().strip()

        if nfc_uid != '' and user_name != '':
            self.register_button.configure(state=ctk.NORMAL)
        else:
            self.register_button.configure(state=ctk.DISABLED)
        self.id_entries_observer = self.after(100, self._observe_entries)


# ユーザー登録ビューのコンポーネント
class RegisterUserView(ctk.CTkFrame):
    master: MainView
    root_dir: str
    width: int
    height: int
    add_new_user_button: AddNewUserButton
    def __init__(self, master: MainView, root_dir: str, width: int, height: int) -> None:
        super(RegisterUserView, self).__init__(master=master, width=width, height=height)
        self.root_dir = root_dir
        self.width = width
        self.height = height

        # 新規ユーザー追加ボタンの作成
        button_width: int = int(height * 0.075)
        button_height: int = int(height * 0.075)
        self.add_new_user_button = AddNewUserButton(
            master=self,
            root_dir=root_dir,
            width=button_width,
            height=button_height
        )
        self.add_new_user_button.place(relx=0.95, rely=0.05, anchor=ctk.NE)

        # フレームのサイズ変更を防止
        self.pack_propagate(False)

    # 新規ユーザー登録詳細ウィンドウへ切り替え
    def switch_to_register_user_detail_window(self) -> None:
        # 新規ユーザー登録詳細ウィンドウの表示　 (メインウィンドウは非表示)
        from ..windows import RegisterUserDetailWindow
        RegisterUserDetailWindow(
            master=self.master,
            root_dir=self.root_dir,
            width=self.width,
            height=self.height
        )