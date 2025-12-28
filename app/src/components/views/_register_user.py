from __future__ import annotations
from typing import TYPE_CHECKING, Literal
import tkinter as tk
import customtkinter as ctk
from PIL import Image
from ...utils import UserState, UserAction, DEFAULT_USER_STATE, USER_STATE_LABELS
from ...utils.nfc import UID, NFC
from ...utils.db import (
    is_registered_user,
    register_user,
    get_users_by_state
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

                # ユーザーリストビューを更新
                if isinstance(self.master.master.bodyview, RegisterUserView):
                    self.master.master.bodyview.update_users_list()

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



# ユーザー情報フレーム (編集, 削除ボタンなどを含む)
class UserInfoFrame(ctk.CTkFrame):
    master: UsersList
    root_dir: str
    width: int
    height: int
    name: str
    hashed_uid: str    # NFCタグIDのSHA256ハッシュ値
    def __init__(self, master: UsersList, root_dir: str, width: int, height: int, name: str, hashed_uid: str) -> None:
        super(UserInfoFrame, self).__init__(
            master=master,
            width=width,
            height=height,
            fg_color=ctk.ThemeManager.theme['CTkFrame']['fg_color'],
            bg_color='transparent',
            corner_radius=int(min(width, height) * 0.1)
        )
        self.root_dir = root_dir
        self.width = width
        self.height = height
        self.name = name
        self.hashed_uid = hashed_uid

        # ユーザー名ラベルの作成
        self.name_label = ctk.CTkLabel(
            master=self,
            text=f'名前: {self.name}',
            font=ctk.CTkFont(size=int(min(width, height) * 0.15))
        )
        self.name_label.place(relx=0.05, rely=0.5, anchor=ctk.W)


# ユーザー一覧スクロールフレーム
class UsersList(ctk.CTkScrollableFrame):
    master: ctk.CTkCanvas                                           # CT_kScrollableFrameのmasterはCTkCanvas型になるため
    _master: UsersTabView                                           # 親ビューの参照
    root_dir: str
    width: int
    height: int
    user_state: UserState                                           # ユーザー状態フィルター
    user_info_frames: list[UserInfoFrame] = list[UserInfoFrame]()   # ユーザー情報フレームのリスト (状態の更新順)
    def __init__(self, master: UsersTabView, root_dir: str, width: int, height: int, user_state: UserState = DEFAULT_USER_STATE) -> None:
        super(UsersList, self).__init__(
            master=master,
            width=width,
            height=height,
            label_font=ctk.CTkFont(size=int(min(width, height) * 0.1)),
            corner_radius=int(min(width, height) * 0.02),
            bg_color='transparent'
        )
        self._master = master
        self.root_dir = root_dir
        self.width = width
        self.height = height
        self.user_state = user_state

        # ユーザー一覧を初期化
        users: list[dict[str, str]] = get_users_by_state(root_dir, user_state)
        for index, user in enumerate(users):
            user_info_frame = UserInfoFrame(
                master=self,
                root_dir=root_dir,
                width=int(width * 0.9),
                height=int(height * 0.1),
                name=user['name'],
                hashed_uid=user['id']
            )
            user_info_frame.pack(pady=int(height * 0.02))
            self.user_info_frames.append(user_info_frame)

    # ユーザー一覧を更新
    def update_users_list(self, user_state: UserState | None = None) -> None:
        # ユーザー状態フィルターを更新 (Noneの場合は変更しない. ユーザーの状態が変わった場合などに使用)
        if user_state is not None:
            self.user_state = user_state

        # 古いユーザー一覧をクリア
        for user_info_frame in self.user_info_frames:
            user_info_frame.destroy()
        self.user_info_frames = list[UserInfoFrame]()

        # ここにユーザー一覧を再取得して表示するコードを追加
        users: list[dict[str, str]] = get_users_by_state(self.root_dir, self.user_state)
        for index, user in enumerate(users):
            user_info_frame = UserInfoFrame(
                master=self,
                root_dir=self.root_dir,
                width=int(self.width * 0.9),
                height=int(self.height * 0.1),
                name=user['name'],
                hashed_uid=user['id']
            )
            user_info_frame.pack(pady=int(self.height * 0.02))
            self.user_info_frames.append(user_info_frame)
        self.update_idletasks()

# ユーザータブボタンのコンポーネント
class TabButton(ctk.CTkButton):
    master: TabFrame
    root_dir: str
    width: int
    height: int
    user_state: UserState
    def __init__(self, master: UsersTabView, root_dir: str, width: int, height: int, text: str = '', user_state: UserState = UserState.IN) -> None:
        super(TabButton, self).__init__(
            master=master,
            width=width,
            height=height,
            text=text,
            font=ctk.CTkFont(size=int(min(width, height) * 0.5)),
            command=self._command,
            fg_color=ctk.ThemeManager.theme['CTkButton']['fg_color'] if user_state == DEFAULT_USER_STATE else 'transparent',
            bg_color='transparent',
            hover=True
        )
        self.root_dir = root_dir
        self.width = width
        self.height = height
        self.user_state = user_state

    # タブがクリックされたときの動作
    def _command(self) -> None:
        # ユーザー一覧を更新
        self.master.master.update_users_list(self.user_state)

# タブフレームのコンポーネント
class TabFrame(ctk.CTkFrame):
    master: UsersTabView
    root_dir: str
    width: int
    height: int
    height: int
    tabs: dict[UserState, TabButton] = dict[UserState, TabButton]() # タブボタンの辞書
    tab_labels: dict[UserState, str] = {
        UserState.IN: f'{USER_STATE_LABELS[UserState.IN]}者',
        UserState.OUT: f'{USER_STATE_LABELS[UserState.OUT]}者'
    }
    def __init__(self, master: UsersTabView, root_dir: str, width: int, height: int) -> None:
        super(TabFrame, self).__init__(
            master=master,
            width=width,
            height=height,
            corner_radius=int(min(width, height) * 0.1),
            fg_color='transparent',
            bg_color='transparent'
        )
        self.root_dir = root_dir
        self.width = width
        self.height = height

        # タブボタンの作成
        padding: int = int(width * 0.075) # タブボタン間の余白
        button_width: int = int((width - padding * (len(self.tab_labels) + 1)) / len(self.tab_labels))
        button_height: int = int(height * 0.9)
        for index, user_state in enumerate(sorted(self.tab_labels.keys(), key=lambda _user_state: _user_state.value), start=0):
            self.tabs[user_state] = TabButton(
                master=self,
                root_dir=root_dir,
                width=button_width,
                height=button_height,
                text=self.tab_labels[user_state],
                user_state=user_state
            )
            self.tabs[user_state].place(relx=(index * button_width + (index + 1) * padding) / width, rely=0.05, anchor=ctk.NW)

    # ユーザー一覧を更新
    def update_users_list(self, user_state: UserState | None = None) -> None:
        # タブの状態を更新
        for _user_state, tab in self.tabs.items():
            # 更新対象のタブの場合は無効化
            if _user_state == user_state or (_user_state == self.master.users_list.user_state and user_state is None):
                tab.configure(state=ctk.DISABLED)
                tab.configure(fg_color=ctk.ThemeManager.theme['CTkButton']['fg_color'])
            else:
                tab.configure(state=ctk.NORMAL)
                tab.configure(fg_color='transparent')

# ユーザータブビューのコンポーネント (在室者・不在者タブ)
class UsersTabView(ctk.CTkFrame):
    master: RegisterUserView
    root_dir: str
    width: int
    tab_frame: TabFrame     # タブフレーム (在室者・不在者タブ)
    users_list: UsersList   # ユーザー一覧 (現在のタブに対応)
    def __init__(self, master: RegisterUserView, root_dir: str, width: int, height: int) -> None:
        super(UsersTabView, self).__init__(
            master=master,
            width=width,
            height=height,
            fg_color='transparent',
            bg_color='transparent'
        )
        self.root_dir = root_dir
        self.width = width
        self.height = height

        # タブフレームの作成
        tab_frame_width: int = int(width * 0.9)
        tab_frame_height: int = int(height * 0.1)
        self.tab_frame = TabFrame(
            master=self,
            root_dir=root_dir,
            width=tab_frame_width,
            height=tab_frame_height
        )
        self.tab_frame.place(relx=0.5, rely=0, anchor=ctk.N)

        # ユーザー一覧の作成 (初期状態は在室者タブ)
        self.users_list = UsersList(
            master=self,
            root_dir=root_dir,
            width=int(width * 0.9),
            height=int(height * 0.8),
            user_state=UserState.IN
        )
        self.users_list.place(relx=0.5, rely=0.55, anchor=ctk.CENTER)

    # ユーザー一覧を更新
    def update_users_list(self, user_state: UserState | None = None) -> None:
        # タブフレームの状態を更新
        self.tab_frame.update_users_list(user_state)

        # ユーザー一覧を更新
        self.users_list.update_users_list(user_state)

# ユーザー登録ビューのコンポーネント
class RegisterUserView(ctk.CTkFrame):
    master: MainView
    root_dir: str
    width: int
    height: int
    add_new_user_button: AddNewUserButton   # 新規ユーザー追加ボタン
    users_tab_view: UsersTabView            # ユーザータブビュー
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

        # ユーザータブビューの作成
        self.users_tab_view = UsersTabView(
            master=self,
            root_dir=root_dir,
            width=int(width * 0.8),
            height=int(height * 0.8)
        )
        self.users_tab_view.place(relx=0.5, rely=0.55, anchor=ctk.CENTER)

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

    # ユーザー一覧を更新
    def update_users_list(self, user_state: UserState | None = None) -> None:
        # ユーザータブビューのユーザー一覧を更新
        self.users_tab_view.update_users_list(user_state)
        self.update_idletasks()