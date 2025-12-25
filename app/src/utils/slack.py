from __future__ import annotations
import enum
import keyring
from slack_bolt import App as SlackApp
from slack_sdk.web import SlackResponse
from slack_sdk.errors import SlackApiError

# Slackのボットトークンのスコープ説明文
SLACK_BOT_TOKEN_SCOPES_DESCRIPTION: str = '※ \'files:read\', \'canvases:write\'の権限が必要です.'

# Slackのトークンの種類を定義する列挙型
class SlackTokens(enum.IntEnum):
    SLACK_BOT_TOKEN: int = enum.auto()
    SLACK_CANVAS_ID: int = enum.auto()

# Slackのトークンが登録されているか確認する
def is_registered_slack_tokens(service: str) -> bool:
    for token in sorted(SlackTokens):
        if keyring.get_password(service, token.name) is None:
            return False
    return True

# Slackのトークンが有効か確認する
def is_valid_slack_tokens(bot_token: str, canvas_id: str) -> bool:
    # Slackとの接続を試みる
    try:
        # Slackアプリを初期化する
        slack_app: SlackApp = SlackApp(token=bot_token)

        # Canvasの情報を取得する
        response: SlackResponse = slack_app.client.files_info(file=canvas_id)

        # 接続が成功した場合は有効とする
        return response['ok']

    # Slack APIエラーが発生した場合は無効とする
    except SlackApiError as e:
        return False

    # その他の例外が発生した場合は無効とする
    except Exception as e:
        return False

# Slackのトークンを保存する
def save_slack_tokens(service: str, tokens: dict[SlackTokens, str]) -> None:
    for key, token in tokens.items():
        keyring.set_password(service, key.name, token)

# Slackのトークンを取得する
def get_slack_tokens(service: str) -> dict[SlackTokens, str]:
    tokens: dict[SlackTokens, str] = dict[SlackTokens, str]()
    for key in sorted(SlackTokens):
        token: str | None = keyring.get_password(service, key.name)
        tokens[key] = token if token is not None else ''
    return tokens

# Slackのトークンを削除する
def delete_slack_tokens(service: str, tokens: dict[SlackTokens, str]) -> None:
    for key in tokens.keys():
        keyring.delete_password(service, key.name)