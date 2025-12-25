from __future__ import annotations
from typing import TYPE_CHECKING, Callable
import webbrowser
import tkinter as tk
import customtkinter as ctk
from PIL import Image
from ...utils.slack import SlackTokens, is_valid_slack_tokens, save_slack_tokens, SLACK_BOT_TOKEN_SCOPES_DESCRIPTION, SLACK_SETUP_DOCUMENT_URL
if TYPE_CHECKING:
    from ...app import App
    from ..windows import SetupWindow

# 登録用エントリーのコンポーネント
class RegisterEntry(ctk.CTkFrame):
    master: RegisterTokensView
    width: int
    height: int
    label: ctk.CTkLabel
    entry: ctk.CTkEntry
    description: ctk.CTkLabel
    def __init__(self, master: RegisterTokensView, width: int, height: int, text: str, description: str = '', show: str | None = None) -> None:
        super(RegisterEntry, self).__init__(master=master, width=width, height=height, fg_color='transparent')
        self.width = width
        self.height = height

        # ラベルの作成
        label_width: int = self.width // 3
        label_height: int = int(self.height // 7.5)
        label_font: ctk.CTkFont = ctk.CTkFont(size=label_height // 2)
        self.label = ctk.CTkLabel(master=self, text=text, width=label_width, height=label_height, corner_radius=label_height // 4, font=label_font)
        self.label.place(relx=0.05, rely=0.2, anchor=ctk.NW)

        # エントリーの作成
        entry_width: int = int(self.width * 0.7)
        entry_height: int = int(self.height // 7.5)
        entry_font: ctk.CTkFont = ctk.CTkFont(size=entry_height // 2)
        self.entry = ctk.CTkEntry(master=self, width=entry_width, height=entry_height, corner_radius=entry_height // 4, font=entry_font, show=show, justify=ctk.CENTER)
        self.entry.place(relx=0.5, rely=0.5, anchor=ctk.N)

        # 説明ラベルの作成
        description_font: ctk.CTkFont = ctk.CTkFont(size=int(self.height // 20))
        self.description = ctk.CTkLabel(master=self, text=description, font=description_font)
        self.description.place(relx=0.95, rely=0.75, anchor=ctk.NE)

        # フレームのサイズ変更を防止
        self.pack_propagate(False)

# 登録ボタン
class RegisterButton(ctk.CTkButton):
    master: RegisterTokensView
    def __init__(self, master: RegisterTokensView, width: int, height: int, text: str, command: Callable[[], None] | None = None) -> None:
        super(RegisterButton, self).__init__(master=master, width=width, height=height, font=ctk.CTkFont(size=height // 3), text=text, command=command)


class RegisterTokensView(ctk.CTkFrame):
    master: App | SetupWindow
    root_dir: str
    help_label: ctk.CTkLabel
    bot_token_entry: RegisterEntry
    canvas_id_entry: RegisterEntry
    register_button: RegisterButton
    def __init__(self, master: App | SetupWindow, root_dir: str) -> None:
        super(RegisterTokensView, self).__init__(master=master, width=master.width, height=master.height)
        self.root_dir = root_dir

        # Slackセットアップヘルプリンクの作成
        image: ctk.CTkImage = ctk.CTkImage(
            light_image=Image.open(f'{root_dir}/assets/icons/light/help.png'),
            dark_image=Image.open(f'{root_dir}/assets/icons/dark/help.png'),
            size=(int(master.height * 0.03), int(master.height * 0.03))
        )
        self.help_label = ctk.CTkLabel(
            master=self,
            text='',
            image=image,
            width=int(master.height * 0.05),
            height=int(master.height * 0.05)
        )
        self.help_label.bind('<Button-1>', lambda event: webbrowser.open_new_tab(SLACK_SETUP_DOCUMENT_URL))
        self.help_label.place(relx=0.99, rely=0.01, anchor=ctk.NE)

        # Slackのボットトークンのエントリーを作成
        self.bot_token_entry = RegisterEntry(master=self, width=master.width, height=int(master.height * 0.4), text='Slack Bot トークン', description=SLACK_BOT_TOKEN_SCOPES_DESCRIPTION, show="*")
        self.bot_token_entry.place(relx=0.5, rely=0.05, anchor=ctk.N)

        # CanvasのIDエントリーを作成
        self.canvas_id_entry = RegisterEntry(master=self, width=master.width, height=int(master.height * 0.4), text='Canvas ID')
        self.canvas_id_entry.place(relx=0.5, rely=0.45, anchor=ctk.N)

        # 登録ボタンを作成
        self.register_button = RegisterButton(master=self, width=int(master.width * 0.2), height=int(master.height * 0.1), text='登録', command=self.register_tokens)
        self.register_button.place(relx=0.95, rely=0.95, anchor=ctk.SE)

        # それぞれのエントリーが空白でない場合に登録ボタンを有効化 (ループで監視)
        def _observe_entries() -> None:
            bot_token: str = self.bot_token_entry.entry.get().strip()
            canvas_id: str = self.canvas_id_entry.entry.get().strip()
            if bot_token and canvas_id:
                self.register_button.configure(state=ctk.NORMAL)
            else:
                self.register_button.configure(state=ctk.DISABLED)
            self.after(100, _observe_entries)
        _observe_entries()

        # 最初のエントリーにフォーカスを設定
        self.bot_token_entry.entry.focus_set()

    def register_tokens(self, event: tk.Event | None = None) -> None:
        # 登録ボタンを無効化
        self.register_button.configure(state=ctk.DISABLED)

        # エントリーからトークンを取得
        bot_token: str = self.bot_token_entry.entry.get().strip()
        canvas_id: str = self.canvas_id_entry.entry.get().strip()

        # トークンの検証
        if is_valid_slack_tokens(bot_token=bot_token, canvas_id=canvas_id):
            # トークンの保存
            from ..windows import SetupWindow
            service: str = f'{self.master.master.pyproject['project']['name']}-Service' if isinstance(self.master, SetupWindow) else f'{self.master.pyproject['project']['name']}-Service'
            save_slack_tokens(service=service, tokens={
                SlackTokens.SLACK_BOT_TOKEN: bot_token,
                SlackTokens.SLACK_CANVAS_ID: canvas_id
            })

            if isinstance(self.master, SetupWindow):
                # セットアップウィンドウの終了
                self.master.destroy()

                # メインウィンドウの表示
                self.master.master.deiconify()

                # メインウィンドウにフォーカスを設定
                def _focus() -> None:
                    self.master.master.lift()
                    self.master.master.focus_force()
                self.master.master.after(100, _focus)

        # トークンが無効な場合はエラーメッセージを表示して, 再度トークンの入力を促す
        else:
            # エラーメッセージの表示
            self.canvas_id_entry.description.configure(text='\'Slack Bot トークン\'か\'Canvas ID\'が無効, または権限が不足しています.', text_color='red')

            # 一定時間後にエラーメッセージをクリア (2秒後)
            def _clear_error_message() -> None:
                self.canvas_id_entry.description.configure(text='', text_color=self.bot_token_entry.description.cget('text_color'))
            self.after(2000, _clear_error_message)

            # エントリーをクリア
            self.bot_token_entry.entry.delete(0, ctk.END)
            self.canvas_id_entry.entry.delete(0, ctk.END)

            # 最初のエントリーにフォーカスを設定
            self.bot_token_entry.entry.focus_set()