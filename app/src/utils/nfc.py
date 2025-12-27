from __future__ import annotations
from typing import Callable
import time
import hashlib
import dataclasses
import threading
from smartcard.System import readers
from smartcard.CardType import CardType, AnyCardType
from smartcard.CardRequest import CardRequest
from smartcard.PassThruCardService import PassThruCardService
from smartcard.Exceptions import NoCardException, CardRequestException
from smartcard.util import toHexString

# NFCタグのUIDを表す型 (SHA-256でハッシュ化するメソッドを実装)
class UID(str):
    def sha256(self) -> str:
        return hashlib.sha256(self.encode('utf-8')).hexdigest()

# NFCリーダーとの通信に使用するコマンド
COMMAND_GET_UID = [0xFF, 0xCA, 0x00, 0x00, 0x00] # NFCタグのUIDを取得するコマンド

# 各種タイムアウト設定
DEFAULT_TIMEOUT_NFC_WAIT: float = 10e-2 # NFC読み取りのデフォルトの待機タイムアウト時間 (秒)
DEFAULT_TIMEOUT_SAME_UID: float = 5.0   # 同じUIDを無視するデフォルトのタイムアウト時間 (秒)

# NFCのレスポンスを表すデータクラス
@dataclasses.dataclass
class NFCResponse(object):
    status: bool | None
    uid: UID | None
    error_message: Exception | None
    timestamp: float

# NFCセッションを管理するクラス
class NFCSession(object):
    card_type: CardType                 # NFCカードのタイプ
    card_request: CardRequest           # NFCカードリクエスト
    _session: threading.Thread | None   # NFCセッション用のスレッド
    response: NFCResponse               # NFCのレスポンス情報
    is_running: bool                    # NFCセッションが実行中かどうか
    is_changed: bool                    # NFCタグの状態が変化したかどうか
    def __init__(self, response: NFCResponse | None = None) -> None:
        super(NFCSession, self).__init__()
        self.card_type = AnyCardType()
        self.card_request = CardRequest(cardType=self.card_type, timeout=DEFAULT_TIMEOUT_NFC_WAIT)
        self._session = None
        if response is None:
            self.response = NFCResponse(
                status=None,
                uid=None,
                error_message=None,
                timestamp=time.time()
            )
        else:
            self.response = response
        self.is_running = False
        self.is_changed = False

    # NFCセッションを開始するメソッド
    def start(self) -> None:
        if not self.is_running:
            self.is_running = True
            self._session = threading.Thread(target=self._read_uid_loop, name='NFCSession-Thread')
            self._session.start()

    # NFCセッションのスレッドが終了するのを待機するメソッド
    def join(self) -> None:
        if self._session is not None:
            self._session.join()

    # NFCセッションを停止するメソッド
    def stop(self) -> None:
        if self.is_running:
            self.is_running = False
            if self._session is not None:
                self._session.join()

    # UIDを読み取るか想定外の例外が発生するまでループするメソッド
    def _read_uid_loop(self) -> None:
        while self.is_running:
            try:
                # NFCタグを検知するまで待機 (タイムアウトあり)
                service: PassThruCardService = self.card_request.waitforcard()
                connection = service.connection
                connection.connect()
                data, sw1, sw2 = connection.transmit(COMMAND_GET_UID)

                # UIDの取得に成功した場合
                if sw1 == 0x90 and sw2 == 0x00:
                    uid: UID = UID(toHexString(data).replace(' ', ''))

                    # 直前と同じUIDが読み取られ、かつタイムアウト時間内の場合は無視
                    if self.response.uid == uid and time.time() < self.response.timestamp + DEFAULT_TIMEOUT_SAME_UID:
                        continue # 続行

                    # 新しいUIDが読み取られた場合、レスポンスを更新
                    self.response = NFCResponse(
                        status=True,
                        uid=uid,
                        error_message=None,
                        timestamp=time.time()
                    )
                    self.is_changed = True
                    break

            # カードがリーダーにない場合の例外処理
            except NoCardException:
                continue # 続行

            # タイムアウト例外の処理
            except CardRequestException:
                continue # 続行

            # その他の例外処理
            except Exception as e:
                self.response = NFCResponse(
                    status=False,
                    uid=None,
                    error_message=e,
                    timestamp=time.time()
                )
                break

# NFCを制御するためのクラス
class NFC(object):
    card_type: CardType                 # NFCカードのタイプ
    card_request: CardRequest           # NFCカードリクエスト
    command: Callable[[], None] | None  # NFCタグが読み取られたときに実行するコマンド
    only_once: bool                     # 一度だけNFC読み取りを行うかどうか (Trueの場合は一度読み取ったら停止, Falseの場合は継続的に読み取る) (デフォルト: False)
    session: threading.Thread | None    # 一度だけNFCを読み取るセッション
    response: NFCResponse               # 最新のNFCのレスポンス情報
    is_running: bool                    # NFCメインセッションが実行中かどうか
    is_changed: bool                    # NFCタグの状態が変化したかどうか
    def __init__(self, command: Callable[[], None] | None = None, only_once: bool = False) -> None:
        super(NFC, self).__init__()
        self.card_type = AnyCardType()
        self.card_request = CardRequest(cardType=self.card_type, timeout=DEFAULT_TIMEOUT_NFC_WAIT)
        self.command = command
        self.only_once = only_once
        self.session = None
        self.response = NFCResponse(
            status=None,
            uid=None,
            error_message=None,
            timestamp=time.time()
        )
        self.is_running = False
        self.is_changed = False

    # NFCメインセッションを開始するメソッド
    def start(self) -> None:
        if not self.is_running:
            self.is_running = True
            self.session = threading.Thread(target=self._main_read_uid_loop, name='NFC-Main-Thread')
            self.session.start()

    # NFCメインセッションのスレッドが終了するのを待機するメソッド
    def join(self) -> None:
        if self.session is not None:
            self.session.join()

    # NFCメインセッションを停止するメソッド
    def stop(self) -> None:
        if self.is_running:
            self.is_running = False
            if self.session is not None:
                self.session.join()

    # NFCメインセッションのUID読み取りループ
    def _main_read_uid_loop(self) -> None:
        while self.is_running:
            # 一度だけNFCを読み取るセッションを開始 (前回のレスポンスを引き継ぐ)
            session: NFCSession = NFCSession(response=self.response)
            session.start()
            session.join()

            # セッションの状態を更新
            self.is_changed = session.is_changed

            # 状態が変化していればレスポンスを更新
            if self.is_changed:
                self.response = session.response

            # UIDが正常に読み取られ、かつ状態が変化していればコマンドを実行
            if self.response.status and self.is_changed:
                if self.command is not None:
                    self.command()

                # 一度だけ読み取りモードの場合、UIDが読み取られたらセッションを停止
                if self.only_once:
                    self.is_running = False
                    break

    # NFCリーダーが接続されているかどうかを確認するメソッド
    def is_connected(self) -> bool:
        # 利用可能なリーダーの一覧を取得
        available_readers: list[str] = readers()

        # リーダーが一つ以上存在すれば接続されていると判断
        return len(available_readers) > 0