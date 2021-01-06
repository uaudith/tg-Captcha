from pyrogram.types import User


def mentionStr(user: User):
    name = user.first_name or user.last_name or user.username or 'user'
    return f"[{name}](tg://user?id={user.id})"
