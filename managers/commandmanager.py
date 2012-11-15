import sys
import constants
from command import Command
from user import User

class stdout:
    def __init__(self, main):
        self.main = main
        self.channel = None

    def write(self, toprint):
        if self.channel:
            print(toprint, file=sys.__stdout__)
        elif toprint != "\n":
            self.main.b.Msg(self.channel,toprint)

class commandmanager:
    def __init__(self, main):
        self.main = main
        self.commandtag = constants.commandtag
        self.commands = {}
        sys.stdout = stdout(main)
        if constants.commandtype == "both" or constants.commandtype == "privmsg":
            self.main.b.ircevents.PrivMsg += self.UserCommandCheck
        if constants.commandtype == "both" or constants.commandtype == "chanmsg":
            self.main.b.ircevents.ChanMsg += self.ChannelCommandCheck

    def AddCommand(self, command, callback, level = None, helptext = "", usage = ""):
        if command not in self.commands.keys():
            self.commands[command] = Command(command)
        if helptext != "":
            self.commands[command].helptext = helptext
        if usage != "":
            self.commands[command].usage = usage
        self.commands[command].AddListener(callback, level)

    def RemoveCommand(self,command,callback):
        if command in self.commands.keys() and callback in self.commands[command].callbacks:
            self.commands[command].callbacks.remove(callback)

    def UserCommandCheck(self,nick,message):
        self.CheckForCommand(nick,nick,message)

    def ChannelCommandCheck(self,channel,nick,message):
        self.CheckForCommand(channel,nick,message)

    def CheckForCommand(self,source,nick,message):
        if nick==self.main.nick:
            self.main.b.Msg(source,"I am not allowed to run commands.")
            return
        split = message.split(" ")
        try:
            user = self.main.usermanager.users[nick]
            if len(split) > 1 and split[0] == (user.nick + ","):
                if split[1] in self.commands.keys() and self.CheckCommandAccess(user, split[1]):
                    if len(split) > 2:
                        message = " ".join(split[2:])
                    else:
                        message = ""
                    self.RunCommand(split[1], source, user, message)
                elif len(split) > 2 and split[1] == "please" and split[2] in self.commands.keys() and self.CheckCommandAccess(user, split[2]):
                    if len(split) > 3:
                        message = " ".join(split[3:])
                    else:
                        message = ""
                    self.RunCommand(split[2], source, user, message)
            elif split[0][0] == self.commandtag and split[0].lstrip(self.commandtag) in self.commands.keys() and self.CheckCommandAccess(user, split[0].lstrip(self.commandtag)):
                if len(split) > 1:
                    message = " ".join(split[1:])
                else:
                    message = ""
                self.RunCommand(split[0].lstrip(self.commandtag), source, user, message)
            else:
                if source != self.main.nick:
                    self.main.eventmanager.ChanMsg(source, user, message)
                else:
                    self.main.eventmanager.PrivMsg(user, message)
        except:
            self.main.LogError()

    def RunCommand(self,command,source,nick,message):
        user = self.main.usermanager.users[nick]
        self.commands[command].source = source
        self.commands[command].user = user
        self.commands[command].message = message
        sys.stdout.channel = source
        if len(self.commands[command].callbacks) > 0:
            for i in self.commands[command].callbacks:
                try:
                    i(self.commands[command])
                except:
                    self.main.LogError()
        else:
            self.main.b.Msg(source,"I'm sorry, {}, but I have no handlers for that command.".format(user.RandTag()))
        sys.stdout.channel = None

    def CheckCommandAccess(self, user, command):
        if not isinstance(user, User):
            user = self.main.usermanager.users[user]
        if user.level >= self.commands[command].level:
            return True
        else:
            return False

    def CheckLevelAccess(self, level, command):
        if level >= self.commands[command].level:
            return True
        else:
            return False