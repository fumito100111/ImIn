from __future__ import annotations
from typing import TYPE_CHECKING
import customtkinter as ctk
from PIL import Image
from ...utils import UserState, UserAction
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
    def __init__(self, master: RegisterUserDetailWindow, root_dir: str, width: int, height: int) -> None:
        super(RegisterUserDetailView, self).__init__(master=master, width=width, height=height)
        self.root_dir = root_dir
        self.width = width
        self.height = height

        # フレームのサイズ変更を防止
        self.pack_propagate(False)

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