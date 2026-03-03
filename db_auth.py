"""
db_auth.py — 用户认证 + 阈值模板持久化（SQLite）
"""
import sqlite3
import hashlib
import os
import json
import secrets
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "app_data.db")


# ──────────────────────────────────────────────
# 初始化数据库
# ──────────────────────────────────────────────
def init_db():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            username      TEXT    UNIQUE NOT NULL,
            password_hash TEXT    NOT NULL,
            salt          TEXT    NOT NULL,
            created_at    TEXT    DEFAULT (datetime('now','localtime'))
        );

        CREATE TABLE IF NOT EXISTS threshold_profiles (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id      INTEGER NOT NULL,
            profile_name TEXT    NOT NULL,
            thresholds   TEXT    NOT NULL,
            updated_at   TEXT    DEFAULT (datetime('now','localtime')),
            FOREIGN KEY (user_id) REFERENCES users(id),
            UNIQUE(user_id, profile_name)
        );
    """)
    con.commit()
    con.close()


# ──────────────────────────────────────────────
# 密码工具
# ──────────────────────────────────────────────
def _hash_password(password: str, salt: str) -> str:
    return hashlib.sha256((salt + password).encode()).hexdigest()


def _new_salt() -> str:
    return secrets.token_hex(16)


# ──────────────────────────────────────────────
# 用户注册 / 登录
# ──────────────────────────────────────────────
def register_user(username: str, password: str) -> tuple[bool, str]:
    """返回 (success, message)"""
    if not username.strip() or not password.strip():
        return False, "用户名和密码不能为空"
    if len(password) < 6:
        return False, "密码至少 6 位"
    salt = _new_salt()
    pwd_hash = _hash_password(password, salt)
    try:
        con = sqlite3.connect(DB_PATH)
        con.execute(
            "INSERT INTO users (username, password_hash, salt) VALUES (?, ?, ?)",
            (username.strip(), pwd_hash, salt)
        )
        con.commit()
        con.close()
        return True, "注册成功，请登录"
    except sqlite3.IntegrityError:
        return False, "用户名已存在"


def login_user(username: str, password: str) -> tuple[bool, str, int | None]:
    """返回 (success, message, user_id)"""
    con = sqlite3.connect(DB_PATH)
    row = con.execute(
        "SELECT id, password_hash, salt FROM users WHERE username = ?",
        (username.strip(),)
    ).fetchone()
    con.close()
    if not row:
        return False, "用户名不存在", None
    uid, stored_hash, salt = row
    if _hash_password(password, salt) != stored_hash:
        return False, "密码错误", None
    return True, "登录成功", uid


# ──────────────────────────────────────────────
# 阈值模板 CRUD
# ──────────────────────────────────────────────
def get_profiles(user_id: int) -> list[dict]:
    """获取用户所有模板，返回列表 [{id, profile_name, thresholds_dict, updated_at}]"""
    con = sqlite3.connect(DB_PATH)
    rows = con.execute(
        "SELECT id, profile_name, thresholds, updated_at FROM threshold_profiles "
        "WHERE user_id = ? ORDER BY updated_at DESC",
        (user_id,)
    ).fetchall()
    con.close()
    return [
        {"id": r[0], "profile_name": r[1],
         "thresholds": json.loads(r[2]), "updated_at": r[3]}
        for r in rows
    ]


def save_profile(user_id: int, profile_name: str, thresholds: dict) -> tuple[bool, str]:
    """新建或覆盖同名模板"""
    if not profile_name.strip():
        return False, "模板名不能为空"
    payload = json.dumps(thresholds, ensure_ascii=False)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        con = sqlite3.connect(DB_PATH)
        con.execute(
            """INSERT INTO threshold_profiles (user_id, profile_name, thresholds, updated_at)
               VALUES (?, ?, ?, ?)
               ON CONFLICT(user_id, profile_name)
               DO UPDATE SET thresholds=excluded.thresholds, updated_at=excluded.updated_at""",
            (user_id, profile_name.strip(), payload, now)
        )
        con.commit()
        con.close()
        return True, f"已保存模板「{profile_name.strip()}」"
    except Exception as e:
        return False, str(e)


def rename_profile(user_id: int, old_name: str, new_name: str) -> tuple[bool, str]:
    if not new_name.strip():
        return False, "新名称不能为空"
    try:
        con = sqlite3.connect(DB_PATH)
        affected = con.execute(
            "UPDATE threshold_profiles SET profile_name=? WHERE user_id=? AND profile_name=?",
            (new_name.strip(), user_id, old_name)
        ).rowcount
        con.commit()
        con.close()
        if affected == 0:
            return False, "模板不存在"
        return True, f"已重命名为「{new_name.strip()}」"
    except sqlite3.IntegrityError:
        return False, "新名称已存在"


def delete_profile(user_id: int, profile_name: str) -> tuple[bool, str]:
    con = sqlite3.connect(DB_PATH)
    affected = con.execute(
        "DELETE FROM threshold_profiles WHERE user_id=? AND profile_name=?",
        (user_id, profile_name)
    ).rowcount
    con.commit()
    con.close()
    if affected == 0:
        return False, "模板不存在"
    return True, f"已删除模板「{profile_name}」"


def find_matching_profile(user_id: int, filename: str) -> dict | None:
    """根据文件名（去扩展名）查找同名模板，找到返回模板 dict，否则 None"""
    stem = os.path.splitext(filename)[0].strip()
    profiles = get_profiles(user_id)
    for p in profiles:
        if p["profile_name"].strip() == stem:
            return p
    return None
