class NOT_COMPLETED_TEST_EXISISTS(Exception):
    def __init__(self, uid):
        self.uid = uid
        super().__init__(f"user {uid} has tried to enter anotherchat, ignoring previous verification in short time "
                         f"period")


class USERCHAT_STR_WRONG_FORMAT(Exception):
    def __init__(self, ucStr):
        self.ucstr = ucStr
        super().__init__(f"{ucStr} Wrong Format")
