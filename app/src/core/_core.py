from __future__ import annotations

# サービス名を格納する変数 (デフォルトは 'ImIn-Service', APIキーの格納などに使用)
SERVICE: str = 'ImIn-Service'

def set_service(service: str) -> None:
    global SERVICE
    SERVICE = service

def get_service() -> str:
    return SERVICE