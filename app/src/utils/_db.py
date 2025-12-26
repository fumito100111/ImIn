from __future__ import annotations
import os
import sqlite3
import datetime

# データベースの名前
DB_NAME: str = 'test.db'

# データベースに接続する
def connection_db(root_dir: str) -> sqlite3.Connection:
    return sqlite3.connect(f'{root_dir}/db/{DB_NAME}')

# ユーザーテーブルを作成する
def create_users_table(root_dir: str) -> bool:
    try:
        connection: sqlite3.Connection = connection_db(root_dir)
        cursor: sqlite3.Cursor = connection.cursor()
        with open(f'{root_dir}/db/sql/0000_create_users_table.sql', 'r') as f:
            sql: str = f.read()
        cursor.execute(sql)
        connection.commit()
        connection.close()

    # テーブル作成に失敗した場合はFalseを返す
    except Exception as e:
        # すでにテーブルが存在する場合はTrueを返す
        if str(e) == 'table `users` already exists':
            return True
        return False

    return True

# ユーザーを挿入する
def insert_user(root_dir: str, id: str, name: str, state: str, created_at: datetime.datetime | None = None, updated_at: datetime.datetime | None = None) -> bool:
    try:
        connection: sqlite3.Connection = connection_db(root_dir)
        cursor: sqlite3.Cursor = connection.cursor()
        with open(f'{root_dir}/db/sql/0001_insert_user.sql', 'r') as f:
            sql: str = f.read()
        now: datetime.datetime = datetime.datetime.now()
        cursor.execute(sql, {'id': id,
                             'name': name,
                             'state': state,
                             'created_at': now if created_at is None else created_at,
                             'updated_at': now if updated_at is None else updated_at}
                             )
        connection.commit()
        connection.close()

    # 挿入に失敗した場合はFalseを返す
    except Exception as e:
        return False

    return True

# ユーザーの状態を更新する
def update_user_state(root_dir: str, id: str, state: str) -> bool:
    try:
        connection: sqlite3.Connection = connection_db(root_dir)
        cursor: sqlite3.Cursor = connection.cursor()
        with open(f'{root_dir}/db/sql/0002_update_user_state.sql', 'r') as f:
            sql: str = f.read()
        now: datetime.datetime = datetime.datetime.now()
        cursor.execute(sql, {'id': id, 'state': state, 'updated_at': now})
        connection.commit()
        connection.close()

    # 更新に失敗した場合はFalseを返す
    except Exception as e:
        return False

    return True

# ユーザーが登録されているか確認する
def is_registered_user(root_dir: str, id: str) -> bool:
    try:
        connection: sqlite3.Connection = connection_db(root_dir)
        cursor: sqlite3.Cursor = connection.cursor()
        with open(f'{root_dir}/db/sql/0003_select_all_from_users_where_id.sql', 'r') as f:
            sql: str = f.read()
        cursor.execute(sql, {'id': id})
        res: sqlite3.Row | None = cursor.fetchone()
        connection.close()

        if res is None:
            return False
        return True

    # 確認に失敗した場合はFalseを返す
    except Exception as e:
        return False

# ユーザー情報を登録する
def register_user(root_dir: str, id: str, name: str, state: str, created_at: datetime.datetime | None = None, updated_at: datetime.datetime | None = None) -> bool:
    # 登録されていない場合はユーザーを挿入する
    if not is_registered_user(root_dir, id):
        return insert_user(root_dir, id, name, state, created_at, updated_at)

    # 登録されている場合はFalseを返す
    else:
        return False

# ユーザー情報を削除する
def delete_user(root_dir: str, id: str) -> bool:
    try:
        connection: sqlite3.Connection = connection_db(root_dir)
        cursor: sqlite3.Cursor = connection.cursor()
        with open(f'{root_dir}/db/sql/0005_delete_from_users_where_id.sql', 'r') as f:
            sql: str = f.read()
        cursor.execute(sql, {'id': id})
        connection.commit()
        connection.close()

    # 削除に失敗した場合はFalseを返す
    except Exception as e:
        return False

    return True

# ユーザー情報を取得する
def get_user_info(root_dir: str, id: str) -> dict[str, str] | None:
    try:
        connection: sqlite3.Connection = connection_db(root_dir)
        cursor: sqlite3.Cursor = connection.cursor()
        with open(f'{root_dir}/db/sql/0003_select_all_from_users_where_id.sql', 'r') as f:
            sql: str = f.read()
        cursor.execute(sql, {'id': id})
        res: sqlite3.Row | None = cursor.fetchone()
        connection.close()

        # 取得に成功した場合は辞書型で返す
        if res is not None:
            res: dict[str, str] = {
                'id': res[0],
                'name': res[1],
                'state': res[2],
                'created_at': res[3],
                'updated_at': res[4],
            }
        return res

    # 取得に失敗した場合はNoneを返す
    except Exception as e:
        return None

# 特定の状態のユーザー一覧を取得する
def get_users_by_state(root_dir: str, state: str) -> list[dict[str, str]]:
    try:
        connection: sqlite3.Connection = connection_db(root_dir)
        cursor: sqlite3.Cursor = connection.cursor()
        with open(f'{root_dir}/db/sql/0004_select_all_from_users_where_state.sql', 'r') as f:
            sql: str = f.read()
        cursor.execute(sql, {'state': state})
        res: list[sqlite3.Row] = cursor.fetchall()
        connection.close()

        users: list[dict[str, str]] = list[dict[str, str]]()
        for row in res:
            user: dict[str, str] = {
                'id': row[0],
                'name': row[1],
                'state': row[2],
                'created_at': row[3],
                'updated_at': row[4],
            }
            users.append(user)
        return users

    # 取得に失敗した場合はNoneを返す
    except Exception as e:
        return []

# ユーザーのidの変更
def change_user_id(root_dir: str, old_id: str, new_id: str) -> bool:
    # 変更元のユーザーが登録されていない場合はFalseを返す
    if not is_registered_user(root_dir, old_id):
        return False

    # 変更先のユーザーがすでに登録されている場合はFalseを返す
    if is_registered_user(root_dir, new_id):
        return False

    try:
        user_info: dict[str, str] | None = get_user_info(root_dir, old_id)

        # ユーザー情報が取得できない場合はFalseを返す
        if user_info is None:
            return False

        # 新しいidでユーザーを登録する
        return register_user(root_dir=root_dir, id=new_id, name=user_info['name'], state=user_info['state'], created_at=user_info['created_at'], updated_at=datetime.datetime.now())

    except Exception as e:
        return False