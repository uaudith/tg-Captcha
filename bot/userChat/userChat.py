from bot.Exceptions import USERCHAT_STR_WRONG_FORMAT


class userChat:
    def __init__(self, userId: int, chatId: int):
        self.userId = int(userId)
        self.chatId = int(chatId)

    @classmethod
    def parseStr(cls, userChatStr: str):
        splited = userChatStr.split('_')
        if '_' not in userChatStr or (len(splited) != 2):
            raise USERCHAT_STR_WRONG_FORMAT(userChatStr)
        return cls(*splited)
