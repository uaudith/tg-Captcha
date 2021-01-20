from pyrogram.types import Message
from ..helpers import SafeDict, mentionStr


def getFillings(m: Message):
    fillings = SafeDict()
    fillings.update({'first': m.from_user.first_name or '',
                     'last': m.from_user.last_name or '',
                     'fullname': m.from_user.first_name or ''+' '+m.from_user.last_name or '',
                     'username': m.from_user.username or mentionStr(m.from_user),
                     'mention': mentionStr(m.from_user),
                     'id': m.from_user.id,
                     'chatname': m.chat.title or 'Chat'
                     })
    return fillings
