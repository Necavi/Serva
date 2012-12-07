from plugintemplate import plugin
import hashlib
import pymysql

class usercommands(plugin):
    def OnEnable(self):
        self.main.commandmanager.AddCommand("setadmin",self.SetAdmin,80)
        self.main.commandmanager.AddCommand("setgender",self.SetGender,10)
        self.main.commandmanager.AddCommand("settag",self.SetTag,10)
        self.main.commandmanager.AddCommand("register",self.Register)
        self.main.commandmanager.AddCommand("login",self.Login)
        self.main.commandmanager.AddCommand("reloaduser",self.Reload,80)
        self.loginsalt = b"hugalugalugalug"

    def Reload(self, command):
        pass

    def SetGender(self, command):
        split = command.message.split(" ")
        usermanager = self.main.usermanager
        user = usermanager.users[command.nick]
        if len(split) < 1:
            print(command.source,"I am unable to set your gender if you do not specify one, {}".format(user.RandTag()))
        elif split[0] not in self.main.usermanager.genders:
            print(command.source,"That is not a valid gender, {}, please choose {}, {} or {}.".format(user.RandTag(),usermanager.genders[0],usermanager.genders[1],usermanager.genders[2]))
        else:
            user.gender = split[0]
            cur = self.main.mysqlmanager.conn.cursor()
            cur.execute("UPDATE `bot_users` SET `user_gender`=%s WHERE `user_id`=%s",(split[0],user.id))
            cur.close()
            print(command.source,"I have successfully set your gender, {}".format(user.RandTag()))

    def SetTag(self,command):
        split = command.message.split(" ")
        user = self.main.usermanager.users[command.nick]
        if len(split) < 1:
            user.SetTag(self, None)
            print(command.source,"I have reset your tag, {}".format(user.RandTag()))
        else:
            user.SetTag(self, split[0])
            print(command.source,"I have successfully set your tag, {}".format(user.RandTag()))

    def SetAdmin(self,command):
        split = command.message.split(" ")
        user = self.main.usermanager.users[command.nick]
        if len(split) == 2:
            user.SetLevel(split[0], int(split[1]))
            print(command.source, "I have successfully set {}'s user level to {}, {}".format(split[0], split[1], user.RandTag()))
        else:
            print(command.source, "Please use: {}SetAdmin <name> <level>, {}".format(self.main.commandmanager.commandtag, user.RandTag()))

    def Login(self, command):
        if not command.user.loggedin:
            split = command.message.split(" ")
            if len(split) == 2:
                cur = self.main.mysqlmanager.conn.cursor()
                try:
                    cur.execute("SELECT `user_admin`,`user_password`,`user_id`,`user_gender`,`user_tag` FROM `bot_users` WHERE `user_name`=%s",(split[0],))
                    answer = cur.fetchone()
                    h = hashlib.sha512(self.main.usermanager.loginsalt + split[1].encode('utf-8'))
                    if h.hexdigest() == answer[1]:
                        self.level = answer[0]
                        self.name = split[0]
                        self.id = answer[2]
                        self.gender = answer[3]
                        self.tag = answer[4]
                        self.loggedin = True
                    else:
                        print(command.nick,"That password was incorrect, {}".format(command.user.RandTag()))
                except:
                    print(command.nick, "I was unable to find your account, {}, please try again.".format(command.user.RandTag()))
                    self.main.LogError()
                finally:
                    cur.close()
            else:
                print(command.nick, "Please use: {}login <name> <password>, {}".format(self.main.commandmanager.commandtag, command.user.RandTag()))
        else:
            print(command.nick,"You are already logged in, {}".format(command.user.RandTag()))

    def Register(self, command):
        if not command.user.loggedin:
            split = command.message.split(" ")
            if len(split) == 2:
                cur = self.main.mysqlmanager.conn.cursor()
                hash = hashlib.sha512(self.salt + split[1].encode('utf-8'))
                try:
                    cur.execute("INSERT INTO `bot_users`(`user_name`,`user_password`) values(%s,%s)",(split[0], hash.hexdigest()))
                    command.user.SetLevel(10)
                    command.user.name = split[0]
                    command.user.id = cur.lastrowid
                    self.LoggedIn(command.user)
                except pymysql.err.IntegrityError:
                    print(command.nick, "That name is already taken, please choose a different one, {}.".format(command.user.RandTag()))
                finally:
                    cur.close()
            else:
                print(command.nick,"Please use: {}register <name> <password>, {}.".format(self.main.commandmanager.commandtag,command.user.RandTag()))
        else:
            print(command.nick,"You are already logged in, {}.".format(command.user.RandTag()))

    def LoggedIn(self, user):
        print(user.nick,"You have successfully logged in at access level: {}, {}.".format(user.level, user.RandTag()))
        cur = self.main.mysqlmanager.conn.cursor()
        cur.execute("UPDATE `bot_users` SET `user_host`=%s WHERE `user_id`=%s",(user.hostmask, user.id))
        cur.close()