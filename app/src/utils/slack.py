from __future__ import annotations
from typing import Literal
import os
import enum
import keyring
from urllib.parse import urlparse
from slack_bolt import App as SlackApp
from slack_sdk.web import SlackResponse
from slack_sdk.errors import SlackApiError
from ..utils import UserState, USER_STATE_LABELS
from ..utils.db import get_users_by_state

# SlackのセットアップについてのドキュメントURL
SLACK_SETUP_DOCUMENT_URL: str = 'https://github.com/fumito100111/ImIn/blob/main/docs/SLACK_SETUP.md'

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
    # Canvas IDがURL形式の場合はID部分を抽出する
    if '/' in canvas_id:
        canvas_id = os.path.basename(urlparse(canvas_id).path)

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
        if key == SlackTokens.SLACK_CANVAS_ID:
            # Canvas IDがURL形式の場合はID部分を抽出する
            if '/' in token:
                token = os.path.basename(urlparse(token).path)
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

# Slackのキャンバスを置き換える
def replace_slack_canvas(service: str, content: str) -> bool:
    # Slackトークンが登録されていない場合はFalseを返す
    if not is_registered_slack_tokens(service):
        return False

    # Slackトークンが無効な場合はFalseを返す
    if not is_valid_slack_tokens(
        get_slack_tokens(service)[SlackTokens.SLACK_BOT_TOKEN],
        get_slack_tokens(service)[SlackTokens.SLACK_CANVAS_ID]
    ):
        return False

    # 連携済みのSlackのキャンパスを置き換える.
    try:
        # Slackトークンを取得する
        tokens: dict[SlackTokens, str] = get_slack_tokens(service)

        # Slackアプリを初期化する
        slack_app: SlackApp = SlackApp(token=tokens[SlackTokens.SLACK_BOT_TOKEN])

        # Canvasの内容を置き換える
        response: SlackResponse = slack_app.client.canvases_edit(
            canvas_id=tokens[SlackTokens.SLACK_CANVAS_ID],
            changes=[{
                'operation': 'replace',
                'document_content': {
                    'type': 'markdown',
                    'markdown': content
                }
            }]
        )

    except SlackApiError as e:
        return False

    except Exception as e:
        return False

    return True

# データベースの情報をもとに, Slackのキャンパスの内容を置き換える
def update_slack_canvas_from_db(root_dir: str, service: str) -> bool:
    # ユーザー情報を取得する
    in_users: list[dict[str, str]] = get_users_by_state(root_dir=root_dir, state=UserState.IN)
    out_users: list[dict[str, str]] = get_users_by_state(root_dir=root_dir, state=UserState.OUT)

    # Slackのキャンバスの内容を作成する
    content: str = ''
    # 在室ユーザー情報の追加
    content += f'## {USER_STATE_LABELS[UserState.IN]}\n'
    for user in in_users:
        content += f'- {user['name']}\n'

    content += '\n'

    # 不在ユーザー情報の追加
    content += f'\n## {USER_STATE_LABELS[UserState.OUT]}\n'
    for user in out_users:
        content += f'- {user['name']}\n'

    # Slackのキャンバスを置き換える
    return replace_slack_canvas(service=service, content=content)