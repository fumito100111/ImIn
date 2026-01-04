from __future__ import annotations
import getpass
import platform

# サービス名を格納する変数 (デフォルトは 'ImIn-Service', APIキーの格納などに使用)
APP_NAME: str = 'ImIn'
SERVICE: str = f'{APP_NAME}-Service'

# サービス名を設定する関数
def set_service(service: str) -> None:
    global SERVICE
    SERVICE = service

# サービス名を取得する関数
def get_service() -> str:
    return SERVICE

# OSごとにデータ保存先のディレクトリを取得する関数
def get_data_dir() -> str:
    # macOSの場合
    if platform.system() == 'Darwin':
        return f'/Users/{getpass.getuser()}/Library/Application Support/{APP_NAME}'

    # Linuxの場合
    elif platform.system() == 'Linux':
        return f'/home/{getpass.getuser()}/.local/share/{APP_NAME}'