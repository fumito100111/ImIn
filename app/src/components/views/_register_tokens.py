from __future__ import annotations
from typing import TYPE_CHECKING, Callable
import webbrowser
import tkinter as tk
import customtkinter as ctk
from PIL import Image
from ...utils.slack import SlackTokens, is_registered_slack_tokens, get_slack_tokens, is_valid_slack_tokens, save_slack_tokens, SLACK_BOT_TOKEN_SCOPES_DESCRIPTION, SLACK_SETUP_DOCUMENT_URL
if TYPE_CHECKING:
    from ..windows import SetupWindow
    from ..views import MainView

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
        label_width: int = int(self.width * 0.4)
        label_height: int = int(self.height / 7.5)
        label_font: ctk.CTkFont = ctk.CTkFont(size=int(min(label_width, label_height) / 1.25))
        self.label = ctk.CTkLabel(master=self, text=text, width=label_width, height=label_height, corner_radius=int(label_height / 4), font=label_font, anchor=ctk.W)
        self.label.place(relx=0.05, rely=0.2, anchor=ctk.NW)

        # エントリーの作成
        entry_width: int = int(self.width * 0.7)
        entry_height: int = int(self.height / 6)
        entry_font: ctk.CTkFont = ctk.CTkFont(size=int(min(entry_width, entry_height) / 2))
        self.entry = ctk.CTkEntry(master=self, width=entry_width, height=entry_height, corner_radius=int(entry_height / 4), font=entry_font, show=show, justify=ctk.CENTER)
        self.entry.place(relx=0.5, rely=0.5, anchor=ctk.N)

        # 説明ラベルの作成
        description_font: ctk.CTkFont = ctk.CTkFont(size=int(self.height / 20))
        self.description = ctk.CTkLabel(master=self, text=description, font=description_font)
        self.description.place(relx=0.95, rely=0.75, anchor=ctk.NE)

        # フレームのサイズ変更を防止
        self.pack_propagate(False)

# 登録ボタン
class RegisterButton(ctk.CTkButton):
    master: RegisterTokensView
    def __init__(self, master: RegisterTokensView, width: int, height: int, text: str, command: Callable[[], None] | None = None) -> None:
        super(RegisterButton, self).__init__(master=master, width=width, height=height, font=ctk.CTkFont(size=int(height / 3)), text=text, command=command, hover=False)

# トークン登録ビューのコンポーネント
class RegisterTokensView(ctk.CTkFrame):
    master: SetupWindow | MainView
    root_dir: str
    width: int
    height: int
    help_label: ctk.CTkLabel
    bot_token_entry: RegisterEntry
    canvas_id_entry: RegisterEntry
    register_button: RegisterButton
    id: str
    def __init__(self, master: SetupWindow | MainView, root_dir: str, width: int, height: int) -> None:
        super(RegisterTokensView, self).__init__(master=master, width=width, height=height)
        self.root_dir = root_dir
        self.width = width
        self.height = height

        # Slackセットアップヘルプリンクの作成
        image: ctk.CTkImage = ctk.CTkImage(
            light_image=Image.open(f'{root_dir}/assets/icons/light/help.png'),
            dark_image=Image.open(f'{root_dir}/assets/icons/dark/help.png'),
            size=(int(height * 0.03), int(height * 0.03))
        )
        self.help_label = ctk.CTkLabel(
            master=self,
            text='',
            image=image,
            width=int(height * 0.05),
            height=int(height * 0.05)
        )
        self.help_label.bind('<Button-1>', lambda event: webbrowser.open_new_tab(SLACK_SETUP_DOCUMENT_URL))
        self.help_label.place(relx=0.99, rely=0.01, anchor=ctk.NE)

        # エントリーの設定
        register_entry_width: int = width
        register_entry_height: int = int(height * 0.4)

        # Slackのボットトークンのエントリーを作成
        self.bot_token_entry = RegisterEntry(master=self, width=register_entry_width, height=register_entry_height, text='Slack Bot トークン', description=SLACK_BOT_TOKEN_SCOPES_DESCRIPTION, show="*")
        self.bot_token_entry.place(relx=0.5, rely=0.05, anchor=ctk.N)

        # CanvasのIDエントリーを作成
        self.canvas_id_entry = RegisterEntry(master=self, width=register_entry_width, height=register_entry_height, text='Canvas ID')
        self.canvas_id_entry.place(relx=0.5, rely=0.45, anchor=ctk.N)

        # 登録ボタンを作成
        self.register_button = RegisterButton(master=self, width=int(width * 0.2), height=int(height * 0.1), text='登録', command=self.register_tokens)
        self.register_button.place(relx=0.95, rely=0.95, anchor=ctk.SE)

        # エントリーの監視を開始
        self._observe_entries()

        # 最初のエントリーにフォーカスを設定
        self.bot_token_entry.entry.focus_set()

        # トークンが既に登録されている場合はエントリーに表示
        service: str = f'{self.master.master.pyproject['project']['name']}-Service'
        if is_registered_slack_tokens(service=service):
            tokens: dict[SlackTokens, str] = get_slack_tokens(service=service)
            self.bot_token_entry.entry.insert(0, tokens[SlackTokens.SLACK_BOT_TOKEN])
            self.canvas_id_entry.entry.insert(0, tokens[SlackTokens.SLACK_CANVAS_ID])

    def register_tokens(self, event: tk.Event | None = None) -> None:
        # エントリー監視を停止
        self.after_cancel(self.id)

        # 登録ボタンを無効化
        self.register_button.configure(state=ctk.DISABLED)

        # エントリーからトークンを取得
        bot_token: str = self.bot_token_entry.entry.get().strip()
        canvas_id: str = self.canvas_id_entry.entry.get().strip()

        # トークンの検証
        if is_valid_slack_tokens(bot_token=bot_token, canvas_id=canvas_id):
            # トークンの保存
            from ..windows import SetupWindow
            service: str = f'{self.master.master.pyproject['project']['name']}-Service'
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

            else:
                # 成功メッセージの表示
                self.canvas_id_entry.description.configure(text='トークンが正常に登録されました.', text_color='green')

                # 一定時間後に成功メッセージをクリア (2秒後)
                def _clear_success_message() -> None:
                    self.canvas_id_entry.description.configure(text='', text_color=self.bot_token_entry.description.cget('text_color'))
                self.after(2000, _clear_success_message)

                # エントリーに登録したトークンを表示
                service: str = f'{self.master.master.pyproject['project']['name']}-Service'
                tokens: dict[SlackTokens, str] = get_slack_tokens(service=service)
                self.bot_token_entry.entry.delete(0, ctk.END)
                self.bot_token_entry.entry.insert(0, tokens[SlackTokens.SLACK_BOT_TOKEN])
                self.canvas_id_entry.entry.delete(0, ctk.END)
                self.canvas_id_entry.entry.insert(0, tokens[SlackTokens.SLACK_CANVAS_ID])

                # 最初のエントリーにフォーカスを設定
                self.bot_token_entry.entry.focus_set()

                # エントリーの監視を再開
                self._observe_entries()

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

            # 既にトークンが登録されている場合はエントリーに表示
            service: str = f'{self.master.master.pyproject['project']['name']}-Service'
            if is_registered_slack_tokens(service=service):
                tokens: dict[SlackTokens, str] = get_slack_tokens(service=service)
                self.bot_token_entry.entry.insert(0, tokens[SlackTokens.SLACK_BOT_TOKEN])
                self.canvas_id_entry.entry.insert(0, tokens[SlackTokens.SLACK_CANVAS_ID])

            # 最初のエントリーにフォーカスを設定
            self.bot_token_entry.entry.focus_set()

            # エントリーの監視を再開
            self._observe_entries()

    # それぞれのエントリーが空白でない場合に登録ボタンを有効化 (ループで監視)
    def _observe_entries(self) -> None:
        bot_token: str = self.bot_token_entry.entry.get().strip()
        canvas_id: str = self.canvas_id_entry.entry.get().strip()

        if bot_token and canvas_id and bot_token:
            # 既にトークンが登録されている場合は変更がある場合のみ有効化
            service: str = f'{self.master.master.pyproject['project']['name']}-Service'
            if is_registered_slack_tokens(service=service):
                tokens: dict[SlackTokens, str] = get_slack_tokens(service=service)
                if bot_token != tokens[SlackTokens.SLACK_BOT_TOKEN] or canvas_id != tokens[SlackTokens.SLACK_CANVAS_ID]:
                    self.register_button.configure(state=ctk.NORMAL)
                else:
                    self.register_button.configure(state=ctk.DISABLED)
            else:
                self.register_button.configure(state=ctk.NORMAL)
        else:
            self.register_button.configure(state=ctk.DISABLED)
        self.id = self.after(100, self._observe_entries)