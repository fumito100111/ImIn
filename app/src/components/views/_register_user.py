from __future__ import annotations
from typing import TYPE_CHECKING
import customtkinter as ctk
from PIL import Image
from ...utils import UserState, UserAction
from ...utils.nfc import UID
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
            description='',
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
            # command=self.register_user
        )
        self.register_button.place(relx=0.95, rely=0.95, anchor=ctk.SE)

        # 名前エントリーにフォーカスを設定
        self.user_name_entry.entry.focus_set()

        # エントリーの監視を開始
        self._observe_entries()

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