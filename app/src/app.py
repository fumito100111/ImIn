from __future__ import annotations
from typing import Any
import tomllib
import customtkinter as ctk
from .components.windows import SetupWindow
from .utils.slack import is_registered_slack_tokens

WIDTH_RATIO: int = 4                # アプリケーションウィンドウの幅の比率
HEIGHT_RATIO: int = 3               # アプリケーションウィンドウの高さの比率
RATIO_TO_MAX_SCREEN: float = 0.8    # ディスプレイに対するアプリケーションウィンドウの最大比率

class App(ctk.CTk):
    root_dir: str
    width: int
    height: int
    pyproject: dict[str, Any]
    def __init__(self, root_dir: str) -> None:
        super(App, self).__init__()
        # アプリケーションウィンドウの非表示
        self.withdraw()

        # インスタンス変数の初期化
        self.root_dir = root_dir
        self.width, self.height = self.size()

        # pyproject.tomlの読み込み
        with open(f'{self.root_dir}/pyproject.toml', 'rb') as f:
            self.pyproject = tomllib.load(f)

        # アプリケーションの設定
        self.title(self.pyproject['project']['name'])
        self.geometry(
            f'{self.width}x{self.height}+{int((self.winfo_screenwidth() - self.width) / 2)}+{int((self.winfo_screenheight() - self.height) / 2)}'
        )
        self.update_idletasks()
        self.resizable(False, False)

        # イベントの設定
        self.protocol('WM_DELETE_WINDOW', self.destroy)

        # 初回起動時のSlackトークンの確認
        if not is_registered_slack_tokens(f'{self.pyproject['project']['name']}-Service'):
            SetupWindow(self)

        # Slackトークンが登録されている場合
        else:
            # アプリケーションのウィンドウを表示
            self.deiconify()

            # アプリケーションウィンドウにフォーカスを設定
            def _focus() -> None:
                self.lift()
                self.focus_force()
            self.after(100, _focus)

    # アプリケーションの終了
    def destroy(self) -> None:
        super(App, self).destroy()

    # アプリケーションの実行
    def run(self) -> None:
        self.mainloop()

    # 画面サイズに基づいてアプリケーションウィンドウのサイズを計算
    def size(self) -> tuple[int, int]:
        width: int = self.winfo_screenwidth()
        height: int = self.winfo_screenheight()
        if int(width / WIDTH_RATIO * HEIGHT_RATIO) > height:
            height = int(height * RATIO_TO_MAX_SCREEN)
            width = int(height / HEIGHT_RATIO * WIDTH_RATIO)
        else:
            width = int(width * RATIO_TO_MAX_SCREEN)
            height = int(width / WIDTH_RATIO * HEIGHT_RATIO)
        return width, height