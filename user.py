import constants
import random
class User:
    def __init__(self, host, main):
        self.main = main
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
        cur = self.main.pluginmanager.GetPlugin("MySQL").conn.cursor()
        if self.tag:
            cur.execute("UPDATE `bot_users` SET `user_tag`=%s WHERE `user_id`=%s",(tag, self.id,))
        else:
            cur.execute("UPDATE `bot_users` SET `user_tag`=Null WHERE `user_id`=%s",(self.id,))
        cur.close()

    def SetLevel(self, level):
        self.level = level
        cur = self.main.pluginmanager.GetPlugin("MySQL").conn.cursor()
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