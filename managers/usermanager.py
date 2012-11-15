from user import User
class commands:
    def __init__(self, main):
        self.main = main
        self.main.commandmanager.AddCommand("setadmin",self.SetAdmin,80)
        self.main.commandmanager.AddCommand("setgender",self.SetGender,10)
        self.main.commandmanager.AddCommand("settag",self.SetTag,10)
        self.main.commandmanager.AddCommand("load",self.Load,80)
        self.main.commandmanager.AddCommand("reload",self.Load,80)
        self.main.commandmanager.AddCommand("unload",self.Unload,80)
        self.main.commandmanager.AddCommand("register",self.Register)
        self.main.commandmanager.AddCommand("login",self.Login)
        self.main.commandmanager.AddCommand("reloaduser",self.Reload,80)

    def SetGender(self,command):
        split = command.message.split(" ")
        user = self.main.usermanager.users[command.nick]
        if len(split) < 1:
            self.main.b.Msg(command.source,"I am unable to set your gender if you do not specify one, {}".format(user.RandTag()))
        elif split[0] not in usermanager.genders:
            self.main.b.Msg(command.source,"That is not a valid gender, {}, please choose {}, {} or {}.".format(user.RandTag(),usermanager.genders[0],usermanager.genders[1],usermanager.genders[2]))
        else:
            user.gender = split[0]
            cur = self.main.pluginmanager.GetPlugin("MySQL").conn.cursor()
            cur.execute("UPDATE `bot_users` SET `user_gender`=%s WHERE `user_id`=%s",(split[0],user.id))
            cur.close()
            self.main.b.Msg(command.source,"I have successfully set your gender, {}".format(user.RandTag()))

    def SetTag(self,command):
        split = command.message.split(" ")
        user = self.main.usermanager.users[command.nick]
        if len(split) < 1:
            user.SetTag(self, None)
            self.main.b.Msg(command.source,"I have reset your tag, {}".format(user.RandTag()))
        else:
            user.SetTag(self, split[0])
            self.main.b.Msg(command.source,"I have successfully set your tag, {}".format(user.RandTag()))

    def SetAdmin(self,command):
        split = command.message.split(" ")
        user = self.main.usermanager.users[command.nick]
        if len(split) == 2:
            user.SetLevel(split[0], int(split[1]))
            self.main.b.Msg(command.source, "I have successfully set {}'s user level to {}, {}".format(split[0], split[1], user.RandTag()))
        else:
            self.main.b.Msg(command.source, "Please use: {}SetAdmin <name> <level>, {}".format(self.main.commandmanager.commandtag, user.RandTag()))

    def LoggedIn(self, user):
        self.main.b.Msg(user.nick,"You have successfully logged in at access level: {}, {}".format(user.level, user.RandTag()))
        cur = self.main.pluginmanager.GetPlugin("MySQL").conn.cursor()
        cur.execute("UPDATE `bot_users` SET `user_host`=%s WHERE `user_id`=%s",(user.hostmask, user.id))
        cur.close()
        self.main.eventmanager.Login(user)

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
        self.commands = commands(main)
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