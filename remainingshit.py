
        self.salt = b"hugalugalugalug"
        self.AddCommand("load",self.Load,80)
        self.AddCommand("reload",self.Load,80)
        self.AddCommand("unload",self.Unload,80)
        self.AddCommand("register",self.Register)
        self.AddCommand("login",self.Login)
        self.AddCommand("reloaduser",self.Reload,80)
        self.AddCommand("setadmin",self.SetAdmin,80)
        self.AddCommand("setgender",self.SetGender,10)
        self.AddCommand("settag",self.SetTag,10)
        self.channels = constants.channels
        self.events = BotEvents()
        if(constants.commandtype == "both" or constants.commandtype == "privmsg"):
            self.b.ircevents.PrivMsg += self.CommandCheck
        if(constants.commandtype == "both" or constants.commandtype == "chanmsg"):
            self.b.ircevents.ChanMsg += self.CommandCheck2
        self.commandtag = "!"
        self.commands = {}
        sys.stdout = stdout(sys.stdout,self)
        self.b.ircevents.Connected += self.Join

    def AddCommand(self,command,callback,level = None):
        if(command not in self.commands.keys()):
            self.commands[command] = self.GetCommand(command)
        self.commands[command].AddListener(callback,level)
    def GetCommand(self,name):
        return Command(name)
    def RemoveCommand(self,command,callback):
        if(command in self.commands.keys() and callback in self.commands[command].callbacks):
            self.commands[command].callbacks.remove(callback)
    def CommandCheck(self,nick,message):
        self.Check(nick,nick,message)
    def CommandCheck2(self,channel,nick,message):
        self.Check(channel,nick,message)
    def Check(self,source,nick,message):
        if(nick==self.nick):
            self.b.Msg(source,"I am not allowed to run commands, {}.".format(self.RandTag(command.nick)))
            return
        split = message.split(" ")
        try:
            if(len(split)>1 and split[0] == (self.nick + ",")):
                if(split[1] in self.commands.keys() and self.CheckCommandAccess(nick,split[1])):
                    if(len(split)>2):
                        message = " ".join(split[2:])
                    else:
                        message = ""
                    self.RunCommand(split[1],source,nick,message)
                elif(len(split)>2 and split[1] == "please" and split[2] in self.commands.keys() and self.CheckCommandAccess(nick,split[2])):
                    if(len(split)>3):
                        message = " ".join(split[3:])
                    else:
                        message = ""
                    self.RunCommand(split[2],source,nick,message)
            elif(split[0][0] == self.commandtag and split[0].lstrip(self.commandtag) in self.commands.keys() and self.CheckCommandAccess(nick,split[0].lstrip(self.commandtag))):
                if(len(split)>1):
                    message = " ".join(split[1:])
                else:
                    message = ""
                self.RunCommand(split[0].lstrip(self.commandtag),source,nick,message)
            else:
                if(source!=self.nick):
                    self.events.ChanMsg(source,nick,message)
                else:
                    self.events.PrivMsg(nick,message)
        except:
                self.LogError()
    def RunCommand(self,command,source,nick,message):
        self.commands[command].source = source
        self.commands[command].nick = nick
        self.commands[command].message = message
        sys.stdout.channel = source
        if(len(self.commands[command].callbacks)>0):
            for i in self.commands[command].callbacks:
                try:
                    i(self.commands[command])
                except:
                    self.LogError()
        else:
            self.b.Msg(source,"I'm sorry, {}, but I have no handlers for that command.".format(self.RandTag(command.nick)))
        sys.stdout.channel = None
    def CheckCommandAccess(self,nick,command):
        if(self.GetLevel(nick) >= self.commands[command].level):
            return True
        else:
            return False
    def CheckLevelAccess(self,level,command):
        if(level >= self.commands[command].level):
            return True
        else:
            return False
    def SQLCheck(self,channel,nick):
        c = self.conn.cursor()
        try:
            mask = self.b.GetNickMask(nick)
            c.execute("SELECT `user_admin`,`user_name`,`user_id`,`user_gender`,`user_tag` FROM `bot_users` WHERE `user_host`=%s",(mask,))
            answer = c.fetchone()
            if(answer != None):
                self.users[mask] = answer[0]
                self.usernames[mask] = answer[1]
                self.userids[mask] = answer[2]
                self.usergender[mask] = answer[3]
                self.usertags[mask] = answer[4]
                self.LoggedIn(nick,answer[0])
        except:
            self.LogError()
        finally:
            c.close()
    def Login(self,command):
        mask = self.b.GetNickMask(command.nick)
        if(mask not in self.users.keys()):
            split = command.message.split(" ")
            if(len(split)==2):
                c = self.conn.cursor()
                try:
                    c.execute("SELECT `user_admin`,`user_password`,`user_id`,`user_gender`,`user_tag` FROM `bot_users` WHERE `user_name`=%s",(split[0],))
                    answer = c.fetchone()
                    h = hashlib.sha512(self.salt + split[1].encode('utf-8'))
                    if(h.hexdigest()==answer[1]):
                        self.users[mask] = answer[0]
                        self.usernames[mask] = split[0]
                        self.userids[mask] = answer[2]
                        self.usergender[mask] = answer[3]
                        self.usertags[mask] = answer[4]
                        self.LoggedIn(command.nick,answer[0])
                    else:
                        self.b.Msg(command.nick,"That password was incorrect, {}".format(self.RandTag(command.nick)))
                except:
                    self.b.Msg(command.nick, "I was unable to find your account, {}, please try again.".format(self.RandTag(command.nick)))
                    self.LogError()
                finally:
                    c.close()
            else:
                self.b.Msg(command.nick, "Please use: {}login <name> <password>, {}".format(self.commandtag,self.RandTag(command.nick)))
        else:
            self.b.Msg(command.nick,"You are already logged in, {}".format(self.RandTag(command.nick)))
    def Register(self,command):
        if(self.b.GetNickMask(command.nick) not in self.users.keys()):
            split = command.message.split(" ")
            if(len(split)==2):
                c = self.conn.cursor()
                h = hashlib.sha512(self.salt + split[1].encode('utf-8'))
                try:
                    c.execute("INSERT INTO `bot_users`(`user_name`,`user_password`) values(%s,%s)", (split[0],h.hexdigest()))
                    self.users[self.b.GetNickMask(command.nick)] = 10
                    self.usernames[self.b.GetNickMask(command.nick)] = split[0]
                    self.userids[self.b.GetNickMask(command.nick)] = c.lastrowid
                    self.LoggedIn(command.nick,10)
                except pymysql.err.IntegrityError:
                    self.b.Msg(command.nick, "That name is already taken, please choose a different one, {}".format(self.RandTag(command.nick)))
                finally:
                    c.close()
            else:
                self.b.Msg(command.nick,"Please use: {}register <name> <password>, {}".format(self.commandtag,self.RandTag(command.nick)))
        else:
            self.b.Msg(command.nick,"You are already logged in, {}".format(self.RandTag(command.nick)))
    def Reload(self,command):
        split = command.message.split(" ")
        name = self.FindNameKey(split[0])
        if(name != None):
            c = self.conn.cursor()
            try:
                c.execute("SELECT `user_admin` FROM `bot_users` WHERE `user_id`=%s",(self.userids[name],))
                answer = c.fetchone()
                self.users[name] = answer[0]
            except:
                pass
            finally:
                c.close()
    def LoggedIn(self,nick,level):
        self.b.Msg(nick,"You have successfully logged in at access level: {}, {}".format(level,self.RandTag(nick)))
        c = self.conn.cursor()
        c.execute("UPDATE `bot_users` SET `user_host`=%s WHERE `user_id`=%s",(self.b.GetNickMask(nick),self.userids[self.b.GetNickMask(nick)]))
        c.close()
        self.events.Login(nick,level)
    def ForceLoad(self,name):
        success = False
        try:
            file = imp.find_module(name)
            if(file):
                try:
                    self.instances[name].Exit()
                except KeyError:
                    pass
                except AttributeError:
                    pass
                except:
                    self.LogError()
                try:
                    index = 0
                    for i in self.commands.values():
                        for j in i.modules:
                            if(j == self.instances[name]):
                                index = i.modules.index(j)
                                i.modules.pop(index)
                                i.callbacks.pop(index)
                except KeyError:
                    pass
                except IndexError:
                    pass
                except:
                    self.LogError()
                try:
                    module = imp.load_module(name,file[0],file[1],file[2])
                    self.instances[name] = module.main(self)
                    success = True
                except:
                    self.LogError()
                finally:
                    file[0].close()
        except ImportError:
            success = False
            self.LogError()
        return success

class BotEvents():
    def __init__(self):
        self.ChanMsg = event.Event()
        self.PrivMsg = event.Event()
        self.Login = event.Event()
        
    def ChanMsg(self,channel,nick,message):
        self.ChanMsg(channel, nick, message)
    
    def PrivMsg(self,nick,message):
        self.PrivMsg(nick,message)
    
    def Login(self,nick,level):
        self.Login(nick,level)