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
