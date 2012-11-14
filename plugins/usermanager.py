import plugin
import random
import constants
class User:
    def __init__(self,host):
        self.level = 0
        self.id = None
        self.name = None
        self.gender = None
        self.tag = None
        self.nick,bang,identhost = host.partition("!")
        self.ident,bang,self.host = identhost.partition("@")
        self.channels = []
        self.chanmodes = {}

    def RandTag(self):
        if self.tag:
            return self.tag
        elif self.gender:
            return self.RandTagGender(self.gender)
        if constants.kinky:
            return random.choice(list(self.tags.keys()))
        else:
            return random.choice(self.cleantags)

    def RandTagGender(self, gender):
        tag = ""
        for i in range(1,20):
            tag = random.choice(list(self.tags.keys()))
            if self.tags[tag] == gender:
                break
        return tag

    def SetTag(self, tag):
        self.tag = tag
        cur = self.main.pm.GetPlugin("MySQL").conn.cursor()
        if self.tag:
            cur.execute("UPDATE `bot_users` SET `user_tag`=%s WHERE `user_id`=%s",(tag, self.id,))
        else:
            cur.execute("UPDATE `bot_users` SET `user_tag`=Null WHERE `user_id`=%s",(self.id,))
        cur.close()

    def SetLevel(self, level):
        self.level = level
        cur = self.main.pm.GetPlugin("MySQL").conn.cursor()
        try:
            cur.execute("UPDATE `bot_users` SET `user_admin`=%s WHERE `user_id`=%s",(level, self.id))
        except:
            pass
        finally:
            cur.close()

    def __getattr__(self,attribute):
        if attribute == "hostmask":
            return self.nick + "!" + self.ident + "@" + self.host
        else:
            raise AttributeError("object '{}' has no attribute '{}'".format(self.__class__.__name__,attribute))
            
    def __repr__(self):
        return self.nick

class commands:
    def __init__(self, main):
        self.main = main

    def SetGender(self,command):
        split = command.message.split(" ")
        user = self.main.um.users[command.nick]
        if len(split) < 1:
            self.main.b.Msg(command.source,"I am unable to set your gender if you do not specify one, {}".format(user.RandTag()))
        elif split[0] not in usermanager.genders:
            self.main.b.Msg(command.source,"That is not a valid gender, {}, please choose {}, {} or {}.".format(user.RandTag(),usermanager.genders[0],usermanager.genders[1],usermanager.genders[2]))
        else:
            user.gender = split[0]
            cur = self.main.pm.GetPlugin("MySQL").conn.cursor()
            cur.execute("UPDATE `bot_users` SET `user_gender`=%s WHERE `user_id`=%s",(split[0],user.id))
            cur.close()
            self.main.b.Msg(command.source,"I have successfully set your gender, {}".format(user.RandTag()))

    def SetTag(self,command):
        split = command.message.split(" ")
        user = self.main.um.users[command.nick]
        if len(split) < 1:
            user.SetTag(self, None)
            self.main.b.Msg(command.source,"I have reset your tag, {}".format(user.RandTag()))
        else:
            user.SetTag(self, split[0])
            self.main.b.Msg(command.source,"I have successfully set your tag, {}".format(user.RandTag()))

    def SetAdmin(self,command):
        split = command.message.split(" ")
        user = self.main.um.users[command.nick]
        if len(split) == 2:
            user.SetLevel(split[0], int(split[1]))
            self.main.b.Msg(command.source, "I have successfully set {}'s user level to {}, {}".format(split[0], split[1], user.RandTag()))
        else:
            self.main.b.Msg(command.source, "Please use: {}SetAdmin <name> <level>, {}".format(commandmanager.commandtag, user.RandTag()))

class usermanager(plugin.plugin):
    genders = ["male","female","neuter"]
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
        self.commands = commands(self)
    
    def Join(self, channel, nick):
        if nick.nick not in self.users.keys():
            self.users[nick.nick] = User(nick.host)
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
                self.users[message[5]] = User(host)
            self.users[message[5]].channels.append(message[1])
            if "*" in message[6]:
                self.users[message[5]].IRCop = True
            self.users[message[5]].chanmodes[message[1]] = message[6].lstrip("GH*")