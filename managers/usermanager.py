from user import User

class usermanager:
    genders = ["male","female","neutral"]
    tags = {"Mistress":"female"}
    cleantags = {"sir":"male"}
    def __init__(self, main):
        self.main = main
        self.users = {}
        self.main.b.ircevents.Numeric += self.NewChannel
        self.main.b.ircevents.Join += self.Join
        self.main.b.ircevents.Part += self.Part
        self.main.b.ircevents.Quit += self.Quit
        self.main.b.ircevents.Nick += self.Nick
        self.loginsalt = b"hugalugalugalug"
    
    def Join(self, channel, nick):
        if nick.nick not in self.users.keys():
            self.users[nick.nick] = User(nick.host, self.main)
        self.users[nick.nick].channels.append(channel)
    
    def Part(self, channel, nick):
        if nick.nick in self.users.keys():
            self.users[nick.nick].channels.remove(channel)
            del self.users[nick.nick].chanmodes[channel]
            if len(self.users[nick.nick].channels)==0:
                del self.users[nick.nick]
    
    def Quit(self, nick):
        if nick.nick in self.users.keys():
            del self.users[nick.nick]
    
    def Nick(self, oldnick, newnick):
        if oldnick.nick in self.users.keys():
            self.users[newnick.nick] = self.users[oldnick.nick]
            del self.users[oldnick.nick]
    
    def NewChannel(self, numeric, message):
        if numeric == 352:
            message = message.split(" ")
            if message[5] not in self.users.keys():
                host = message[5] + "!" + message[2] + "@" + message[3]
                self.users[message[5]] = User(host, self.main)
            self.users[message[5]].channels.append(message[1])
            if "*" in message[6]:
                self.users[message[5]].IRCop = True
            self.users[message[5]].chanmodes[message[1]] = message[6].lstrip("GH*")