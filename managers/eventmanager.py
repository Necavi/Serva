from Libraries import event
class eventmanager:
    def __init__(self, main):
        self.ChanMsg = event.Event()
        self.PrivMsg = event.Event()
        self.Login = event.Event()

    def ChanMsg(self,channel,user, message):
        self.ChanMsg(channel, user, message)

    def PrivMsg(self, user, message):
        self.PrivMsg(user, message)

    def Login(self, user):
        self.Login(user)