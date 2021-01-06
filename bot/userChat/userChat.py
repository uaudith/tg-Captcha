from bot.Exceptions import USERCHAT_STR_WRONG_FORMAT


class userChat:
    def __init__(self, userId: int, chatId: int):
        self.userId = userId
        self.chatId = chatId

    @classmethod
    def parseStr(cls, userChatStr: str):
        splited = userChatStr.split('-')
        if '-' not in userChatStr or (len(splited) != 2):
            raise USERCHAT_STR_WRONG_FORMAT(userChatStr)
        return cls.__init__(*splited)
