from __future__ import annotations
import enum
import keyring
from slack_bolt import App as SlackApp
from slack_sdk.web import SlackResponse
from slack_sdk.errors import SlackApiError

# Slackのトークンの種類を定義する列挙型
class SlackTokens(enum.IntEnum):
    BOT_TOKEN: int = enum.auto()
    CANVAS_ID: int = enum.auto()

# Slackのトークンが登録されているか確認する
def is_registered_slack_tokens(service: str) -> bool:
    for token in sorted(SlackTokens):
        if keyring.get_password(service, token.name) is None:
            return False
    return True

# Slackのトークンが有効か確認する
def is_valid_slack_tokens(service: str) -> bool:
    # Slackのトークンが登録されていない場合は無効とする
    if not is_registered_slack_tokens(service):
        return False

    # Slackのトークンを取得する
    bot_token: str = keyring.get_password(service, SlackTokens.BOT_TOKEN.name)
    canvas_id: str = keyring.get_password(service, SlackTokens.CANVAS_ID.name)

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