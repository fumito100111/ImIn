from __future__ import annotations
from typing import TYPE_CHECKING, Callable
import enum
import customtkinter as ctk
from PIL import Image
from..views import RegisterUserView, RegisterTokensView, AppInfoView, OSSLicenseView
from ..windows._entry_exit_log import EntryExitLogWindow
if TYPE_CHECKING:
    from ...app import App

# メインビューの状態を定義する列挙型
class ViewState(enum.IntEnum):
    NONE: int = -1                      # 無効な状態
    ENTER_EXIT_LOG: int = enum.auto()   # 入退室記録
    REGISTER_USER: int = enum.auto()    # ユーザー登録
    REGISTER_TOKENS: int = enum.auto()  # Slack連携
    APP_INFO: int = enum.auto()         # アプリ情報
    OSS_LICENSE: int = enum.auto()      # OSSライセンス

# メインビューのデフォルト状態
VIEW_STATE_DEFAULT: ViewState = ViewState.REGISTER_USER

# 各ビューの情報を格納する辞書
VIEW_INFO: dict[ViewState, dict[str, str]] = {
    ViewState.ENTER_EXIT_LOG: {
        'text': '入退室記録',
        'icon': 'login.png'
    },
    ViewState.REGISTER_USER: {
        'text': 'ユーザー登録',
        'icon': 'person_add.png'
    },
    ViewState.REGISTER_TOKENS: {
        'text': 'Slack連携',
        'icon': 'webhook.png'
    },
    ViewState.APP_INFO: {
        'text': 'アプリ情報',
        'icon': 'info.png'
    },
    ViewState.OSS_LICENSE: {
        'text': 'OSSライセンス',
        'icon': 'license.png'
    }
}

# ナビゲーションボタンのコンポーネント
class NavigationButton(ctk.CTkButton):
    master: SideBar
    width: int
    height: int
    def __init__(self, master: SideBar, width: int, height: int, text: str, icon: str, command: Callable[[], None] | None = None) -> None:
        super(NavigationButton, self).__init__(
            master=master,
            width=width,
            height=height,
            text=text,
            image=self._load_icon_to_CTkImage(
                root_dir=master.root_dir,
                icon=icon,
                size=(int(height / 4), int(height / 4)),
                left_padding=int(height / 6),
                right_padding=int(height / 8)
            ),
            command=command,
            font=ctk.CTkFont(size=int(min(width, height) / 4)),
            fg_color='transparent',
            bg_color='transparent',
            anchor=ctk.W,
            hover=False
        )
        self.width = width
        self.height = height

    # アイコン画像の左右に隙間を追加
    def _load_icon_to_CTkImage(self, root_dir: str, icon: str, size: tuple[int, int], left_padding: int | None = None, right_padding: int | None = None) -> ctk.CTkImage:
        # 隙間を追加しない場合, そのままCTkImageを返す
        if left_padding is None and right_padding is None:
            return ctk.CTkImage(
                light_image=Image.open(f'{root_dir}/assets/icons/light/{icon}'),
                dark_image=Image.open(f'{root_dir}/assets/icons/dark/{icon}'),
                size=size
            )
        else:
            if left_padding is None:
                left_padding = 0
            if right_padding is None:
                right_padding = 0
            icon_width, icon_height = size                              # アイコン画像の元のサイズ
            icon_left_padding: int = left_padding                       # アイコン画像の左隙間
            icon_right_padding: int = right_padding                     # アイコン画像の右隙間
            icon_padding: int = icon_left_padding + icon_right_padding  # アイコン画像全体の横幅に追加する隙間の合計

            # ライトモード用アイコン画像の読み込みと加工
            light_image_original: Image.Image = Image.open(f'{root_dir}/assets/icons/light/{icon}')         # 元画像の読み込み
            image_left_padding: int = int(icon_left_padding * (light_image_original.width / icon_width))    # 画像の左隙間の計算
            image_right_padding: int = int(icon_right_padding * (light_image_original.width / icon_width))  # 画像の右隙間の計算
            image_padding: int = image_left_padding + image_right_padding                                   # 画像全体の横幅に追加する隙間の合計
            light_image: Image.Image = Image.new(light_image_original.mode, (light_image_original.width + image_padding, light_image_original.height), (0, 0, 0, 0))
            light_image.paste(light_image_original, (image_left_padding, 0), mask=light_image_original)

            # ダークモード用アイコン画像の読み込みと加工
            dark_image_original: Image.Image = Image.open(f'{root_dir}/assets/icons/dark/{icon}')           # 元画像の読み込み
            image_left_padding = int(icon_left_padding * (dark_image_original.width / icon_width))          # 画像の左隙間の計算
            image_right_padding = int(icon_right_padding * (dark_image_original.width / icon_width))        # 画像の右隙間の計算
            image_padding = image_left_padding + image_right_padding                                        # 画像全体の横幅に追加する隙間の合計
            dark_image: Image.Image = Image.new(dark_image_original.mode, (light_image_original.width + image_padding, light_image_original.height), (0, 0, 0, 0))
            dark_image.paste(dark_image_original, (image_left_padding, 0), mask=dark_image_original)

            return ctk.CTkImage(
                light_image=light_image,
                dark_image=dark_image,
                size=(icon_width + icon_padding, icon_height)
            )

# メインビューのサイドバーのコンポーネント
class SideBar(ctk.CTkFrame):
    master: MainView
    root_dir: str
    width: int
    height: int
    navigation_buttons: dict[ViewState, NavigationButton] = dict[ViewState, NavigationButton]()
    def __init__(self, master: MainView, root_dir: str, width: int, height: int) -> None:
        super(SideBar, self).__init__(master=master, width=width, height=height, fg_color='transparent', bg_color='transparent')
        self.root_dir = root_dir
        self.width = width
        self.height = height

        # ナビゲーションボタンの作成
        button_width: int = self.width
        button_height: int = int(self.height / 8)
        for state in sorted(ViewState):
            # 無効状態のボタンは作成しない
            if state == ViewState.NONE:
                continue
            self.navigation_buttons[state] = NavigationButton(
                master=self,
                width=button_width,
                height=button_height,
                text=VIEW_INFO[state]['text'],
                icon=VIEW_INFO[state]['icon'],
                command=lambda _state=state: self.master.switch_view(_state)
            )
            self.navigation_buttons[state].place(
                relx=0.0,
                rely=(state * button_height) / self.height,
                anchor=ctk.NW
            )

# メインビューのコンポーネント
class MainView(ctk.CTkFrame):
    master: App
    width: int
    height: int
    sidebar: SideBar
    bodyview: RegisterUserView | RegisterTokensView | AppInfoView | OSSLicenseView
    state: ViewState = ViewState.NONE
    def __init__(self, master: App) -> None:
        super(MainView, self).__init__(master=master, width=master.width, height=master.height, fg_color='transparent', bg_color='transparent')
        self.width = master.width
        self.height = master.height

        # サイドバーの作成
        self.sidebar = SideBar(
            master=self,
            root_dir=self.master.root_dir,
            width=int(self.width / 4),
            height=self.height
        )
        self.sidebar.place(relx=0.0, rely=0.0, anchor=ctk.NW)

        # メインビューのボディ部分の作成
        self.switch_view(VIEW_STATE_DEFAULT)

    # メインビューの状態を切り替え
    def switch_view(self, state: ViewState) -> None:
        if self.state != state:
            # 既存のボディビューを削除
            if hasattr(self, 'bodyview'):
                self.bodyview.destroy()

            # 以前の状態のナビゲーションボタンの有効化 (入退室記録ビューの場合は無効化しない)
            if state != ViewState.ENTER_EXIT_LOG and self.state in self.sidebar.navigation_buttons.keys():
                self.sidebar.navigation_buttons[self.state].configure(state=ctk.NORMAL)

            # 新しい状態のナビゲーションボタンの無効化
            if state in self.sidebar.navigation_buttons.keys():
                # 入退室記録ビューの場合は無効化しない (ウィンドウが別途開くため)
                if state != ViewState.ENTER_EXIT_LOG:
                    self.sidebar.navigation_buttons[state].configure(state=ctk.DISABLED)

            # 新しいボディビューの作成
            if state == ViewState.NONE:
                pass

            elif state == ViewState.ENTER_EXIT_LOG:
                EntryExitLogWindow(
                    master=self.master,
                    width=self.master.winfo_screenwidth(),
                    height=self.master.winfo_screenheight()
                )

            elif state == ViewState.REGISTER_USER:
                self.bodyview = RegisterUserView(
                    master=self,
                    root_dir=self.master.root_dir,
                    width=int(self.width * (3 / 4)),
                    height=self.height
                )
                self.bodyview.place(
                    relx=self.sidebar.width / self.width,
                    rely=0.0,
                    anchor=ctk.NW
                )

            elif state == ViewState.REGISTER_TOKENS:
                self.bodyview = RegisterTokensView(
                    master=self,
                    root_dir=self.master.root_dir,
                    width=int(self.width * (3 / 4)),
                    height=self.height
                )
                self.bodyview.place(
                    relx=self.sidebar.width / self.width,
                    rely=0.0,
                    anchor=ctk.NW
                )

            elif state == ViewState.APP_INFO:
                self.bodyview = AppInfoView(
                    master=self,
                    root_dir=self.master.root_dir,
                    width=int(self.width * (3 / 4)),
                    height=self.height
                )
                self.bodyview.place(
                    relx=self.sidebar.width / self.width,
                    rely=0.0,
                    anchor=ctk.NW
                )

            elif state == ViewState.APP_INFO:
                self.bodyview = AppInfoView(
                    master=self,
                    root_dir=self.master.root_dir,
                    width=int(self.width * (3 / 4)),
                    height=self.height
                )
                self.bodyview.place(
                    relx=self.sidebar.width / self.width,
                    rely=0.0,
                    anchor=ctk.NW
                )

            elif state == ViewState.OSS_LICENSE:
                self.bodyview = OSSLicenseView(
                    master=self,
                    root_dir=self.master.root_dir,
                    width=int(self.width * (3 / 4)),
                    height=self.height
                )
                self.bodyview.place(
                    relx=self.sidebar.width / self.width,
                    rely=0.0,
                    anchor=ctk.NW
                )

            # メインビューの更新
            self.update_idletasks()

            # メインビューの状態を更新 (入退室記録ビューの場合は更新しない. 戻るときに元の状態で再描画するため)
            if state != ViewState.ENTER_EXIT_LOG:
                self.state = state

    # メインビューの再描画
    def redraw_view(self) -> None:
        old_state: ViewState = self.state
        self.state = ViewState.NONE
        self.switch_view(old_state)