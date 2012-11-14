class User:
    def __init__(self,host):
        self.level = 0
        self.userid = None
        self.username = None
        self.usergender = None
        self.usertags = None
        self.hostmask = host
        self.nick,bang,identhost = host.partition("!")
        self.ident,bang,self.host = identhost.partition("@")
        self.channels = []
        self.chanmodes = {}
        
    def __getattr__(self,attribute):
        if(attribute == "hostmask"):
            return self.nick + "!" + self.ident + "@" + self.host
        else:
            raise AttributeError("object '{}' has no attribute '{}'".format(self.__class__.__name__,attribute))
            
    def __repr__(self):
        return self.nick
        
class main:
    def __init__(self,main):
        self.main = main 
        self.main.users = {}
        self.main.b.ircevents.Numeric += self.NewChannel
        self.main.b.ircevents.Join += self.Join
        self.main.b.ircevents.Part += self.Part
        self.main.b.ircevents.Quit += self.Quit
        self.main.b.ircevents.Nick += self.Nick
    
    def Join(self,channel,nick):
        if(nick.nick not in self.main.users.keys()):
            self.main.users[nick.nick] = User(nick.host)
        self.main.users[nick.nick].channels.append(channel)
    
    def Part(self,channel,nick):
        if(nick.nick in self.main.users.keys()):
            self.main.users[nick.nick].channels.remove(channel)
            del self.main.users[nick.nick].chanmodes[channel]
            if(len(self.main.users[nick.nick].channels)==0):
                del self.main.users[nick.nick]
    
    def Quit(self,nick):
        if(nick.nick in self.main.users.keys()):
            del self.main.users[nick.nick]
    
    def Nick(self,oldnick,newnick):
        if(oldnick.nick in self.main.users.keys()):
            self.main.users[newnick.nick] = self.main.users[oldnick.nick]
            del self.main.users[oldnick.nick]
    
    def NewChannel(self,numeric,message):
        if(numeric == 352):
            message = message.split(" ")
            if(message[5] not in self.main.users.keys()):
                host = message[5] + "!" + message[2] + "@" + message[3]
                self.main.users[message[5]] = User(host)
            self.main.users[message[5]].channels.append(message[1])
            if("*" in message[6]):
                self.main.users[message[5]].IRCop = True
            self.main.users[message[5]].chanmodes[message[1]] = message[6].lstrip("GH*")