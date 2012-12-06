from Libraries import biblib
from threading import Timer
import constants
import os
import traceback
from managers import pluginmanager, usermanager, commandmanager, eventmanager, mysqlmanager

class main:
    def __init__(self):
        self.b = biblib.bot()
        self.nick = constants.nick
        self.b.initconnection(constants.ircinfo,self.nick)
        logpath = os.getcwd() + "/logs/"
        if not os.path.isdir(logpath):
            os.mkdir(logpath)
        self.t = Timer(5.0,self.Flush)
        self.t.start()
        self.errorlog = open(logpath + "bot.txt","a")
        self.b.ircevents.Connected += self.Connected
        self.mysqlmanager = mysqlmanager.mysqlmanager(self)
        self.eventmanager = eventmanager.eventmanager(self)
        self.commandmanager = commandmanager.commandmanager(self)
        self.usermanager = usermanager.usermanager(self)
        self.pluginmanager = pluginmanager.pluginmanager(self)

    def Connected(self):
        self.b.Print("Successfully loaded {} plugins!".format(self.pluginmanager.LoadPlugins()))

    def LogError(self):
        error = traceback.format_exc()
        self.b.PrintErr(error)
        self.errorlog.write(error)

    def Flush(self):
        self.errorlog.flush()
        self.t = Timer(5.0, self.Flush)
        self.t.start()

main()
