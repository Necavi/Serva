import threading
import socket
import time
import traceback
import sys

from Libraries import event
from datetime import datetime
from collections import deque

class nickclass:
    def __init__(self, nick, host):
        self.nick = nick
        self.host = host
        
    def __repr__(self):
        return self.nick
        
    def __str__(self):
        return self.nick
        
    def __eq__(self, other):
        if isinstance(other, str):
            return self.nick == other
        else:
            return super(object, self).__eq__(other)
        
class IRCEvents:
    def __init__(self):
        self.Connected = event.Event()
        self.Msg = event.Event()
        self.ChanMsg = event.Event()
        self.PrivMsg = event.Event()
        self.Join = event.Event()
        self.Part = event.Event()
        self.Quit = event.Event()
        self.Nick = event.Event()
        self.CTCP = event.Event()
        self.Raw = event.Event()
        self.Numeric = event.Event()

    def Connected(self):
        self.Connected()

    def Msg(self, target, message):
        self.Msg(target, message)

    def ChanMsg(self, channel, nick, message):
        self.ChanMsg(channel, nick, message)

    def PrivMsg(self, nick, message):
        self.PrivMsg(nick, message)

    def Join(self, channel, nick):
        self.Join(channel, nick)

    def Part(self, channel, nick):
        self.Part(channel, nick)

    def Quit(self, channel, nick):
        self.Quit(channel, nick)

    def Nick(self, oldnick, newnick):
        self.Nick(oldnick, newnick)
    
    def CTCP(self, source, nick, type, message):
        self.CTCP(source, nick, type, message)
        
    def Raw(self, message):
        self.Raw(message)
    
    def Numeric(self,number,message):
        self.Numeric(number,message)
        
class bot:
    def __init__(self):
        self.recv_thread = threading.Thread(target=self.RecvMgr, name="receive-thread")
        self.send_thread = threading.Thread(target=self.SendMgr, name="send-thread")
        self.ircevents = IRCEvents()
        self.messagequeue = deque()
        if sys.__stdout__ is None:
            self.stdout = sys.stdout
        else:
            self.stdout = sys.__stdout__
        
    def Join(self, channel):
        message = "JOIN " + channel
        self.SendMsg(message)
        message = "WHO " + channel
        self.SendMsg(message)

    def Part(self, channel, message = ""):
        self.Print(message)
		message = "PART {} :{}".format(channel, message)
        self.SendMsg(message)

    def Action(self, target, message):
        message = "PRIVMSG {} :\x01ACTION {}\x01".format(target, message)
        self.SendMsg(message)

    def Msg(self, target, message):
        message = "PRIVMSG {} :{}".format(target, message)
        self.SendMsg(message)

    def Notice(self, target, message):
        message = "NOTICE {} :{}".format(target, message)
        self.SendMsg(message)

    def Mode(self, channel, mode, message):
		message = "MODE {} {} {}".format(channel, mode, message)
        self.SendMsg(message)
    
    def SendMsg(self, message):
        self.messagequeue.appendleft(message)

    def SendMgr(self):
        while True:
            if(len(self.messagequeue) > 0):
                message = self.messagequeue.pop()
                if(len(message) > 510):
                    split = message.split(" ")
                    message2 = "{} {} {}".format(split[0],split[1],message[:510])
                    message = message[510:]
                    self.messagequeue.appendleft(message2)
                self.Print(message)
                try:
                    self.tsocket.send(bytes(message + "\r\n", "utf-8"))
                except OSError:
                    self.PrintErr(traceback.format_exc())
            time.sleep(0.5)

    def Print(self, message):
        time = datetime.now().replace(microsecond=0)
        self.stdout.write("[{}] {}\n".format(time, message))

    def PrintErr(self, message):
        time = datetime.now().replace(microsecond=0)
        sys.stderr.write("[{}] {}\n".format(time, message))

    def ParseMessage(self, message):
        self.ircevents.Raw(message)
        command = message.split(" ")
        if(command[0] == "PING"):
            message = 'PONG ' + command[1]
            self.SendMsg(message)
        elif(command[1] == "PRIVMSG" or command[1] == "NOTICE"):
            if(command[3].lstrip(":").startswith("\x01") and command[3].lstrip(":").endswith("\x01")):
                self.ircevents.CTCP(command[2],self.ParseName(command[0]),command[3].lstrip(":").strip('\x01'),' '.join(command[4:]))
            else:
                message = command[3].lstrip(':')
                for i in range(4,len(command)):
                    message = message + ' ' + command[i]
                nick = self.ParseName(command[0])
                self.ircevents.Msg(command[0], message)
                nick = self.ParseName(command[0])
                if(command[2].startswith("#")):
                    self.ircevents.ChanMsg(command[2], nick, message)
                elif(command[2] == self.nick):
                    self.ircevents.PrivMsg(nick, message)
        elif(command[1].isnumeric()):
            self.ircevents.Numeric(int(command[1])," ".join(command[2:]))
            if(command[1] == '001'):
                self.ircevents.Connected()
        elif(command[1] == 'JOIN'):
            nick = self.StripTags(self.ParseName(command[0]))
            self.ircevents.Join(command[2], nick)
        elif(command[1] == 'PART'):
            nick = self.ParseName(command[0])
            self.ircevents.Part(command[2], nick)
        elif(command[1] == 'QUIT'):
            nick = self.ParseName(command[0])
            self.ircevents.Quit(command[2], nick)
        elif(command[1] == 'NICK'):
            self.ircevents.Nick(self.ParseName(command[0]), self.ParseName(command[2]))
            
    def StripTags(self, name):
        name.nick = name.nick.lstrip("@+:")
        return name

    def ParseName(self, name):
        nick,ban,identhost = name.partition("!")
        nick = nick.lstrip(":")
        return nickclass(nick,name)

    def RecvMgr(self):
        while True:
            try:
                data = self.fsocket.readline().strip().rstrip('\r\n')
                if not data:
                    time.sleep(0.1)
                    break
                self.Print(data)
                self.ParseMessage(data)
            except OSError:
                self.PrintErr(traceback.print_exc())
            time.sleep(0.01)

    def Identify(self, password):
        self.Msg("nickserv", "IDENTIFY {!s}".format(password)) 

    def nickserv(self):
        self.Identify(self.identify)
            
    def initconnection(self, connection, nick, useSSL = False, identify = None):
        self.connection = connection
        self.tsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if(useSSL):
            try:
                import ssl
            except ImportError:
                self.Print("Unable to initiated SSL for this server")
            else:
                self.tsocket = ssl.wrap_socket(self.tsocket)
        if(identify != None):
            self.identify = identify
            self.ircevents.Connected += self.nickserv
        self.tsocket.connect(self.connection)
        self.fsocket = self.tsocket.makefile()
        self.nick = nick
        print(self.tsocket)
        self.SendMsg('NICK {}'.format(self.nick))
        self.SendMsg('USER {0} {0} {0} :{0}'.format(self.nick))
        self.recv_thread.start()
        self.send_thread.start()
                
