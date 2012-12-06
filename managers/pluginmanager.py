import inspect
import imp
import plugintemplate
import glob
import sys
import os

class pluginmanager:
    def __init__(self, main):
        self.main = main
        self.instances = {}
        sys.path.append(os.getcwd() + "/plugins")
        self.main.commandmanager.AddCommand("load", self.LoadCommand, 80)
        self.main.commandmanager.AddCommand("reload", self.LoadCommand, 80)
        self.main.commandmanager.AddCommand("unload", self.UnloadCommand,80)

    def LoadPlugins(self):
        modules = glob.glob("plugins/*.py")
        loaded = 0
        for i in modules:
            split = i.split("/")
            name = split[len(split)-1].split(".")[0]
            if self.Load(name):
                loaded += 1
        return loaded

    def UnloadPlugins(self):
        size = len(self.instances)
        for i in self.instances.keys():
            self.Unload(i)
        return size

    def Load(self, name):
        success = False
        try:
            file = imp.find_module(name)
            if file:
                try:
                    module = imp.load_module(name, file[0], file[1], file[2])
                    for i, value in inspect.getmembers(module, inspect.isclass):
                        if issubclass(value, plugintemplate.plugin):
                            self.instances[name] = value(self.main)
                            self.instances[name].main = self.main
                            self.instances[name].OnEnable()
                            success = True
                            break
                except:
                    self.main.LogError()
                finally:
                    file[0].close()
        except ImportError:
            self.main.LogError()
        return success

    def Unload(self, name):
        if name in self.instances.keys():
            self.instances[name].OnDisable()
            del self.instances[name]

    def FindPlugin(self, name):
        if name in self.instances.keys():
            return self.instances[name]

    def PluginExists(self, name):
        return name in self.instances.keys()

    def LoadCommand(self, command):
        split = command.message.split(" ")
        user = self.main.usermanager.users[command.nick]
        if split[0] == "@all":
            self.main.b.Msg(command.source,"I have successfully loaded {} plugins for you, {}.".format(self.LoadPlugins(),user.RandTag()))
        else:
            if self.Load(split[0]):
                self.main.b.Msg(command.source,"I have successfully loaded the module: {} for you, {}.".format(split[0], user.RandTag()))
            else:
                self.main.b.Msg(command.source,"I was unable to load that module, {}, perhaps it does not exist?".format(user.RandTag()))

    def UnloadCommand(self, command):
        split = command.message.split(" ")
        user = self.main.usermanager.users[command.nick]
        if split[0] == "@all":
            self.main.b.Msg(command.source,"I have successfully unloaded {} plugins for you, {}.".format(self.UnloadPlugins(), user.RandTag()))
        else:
            if self.Unload(split[0]):
                self.main.b.Msg(command.source,"I have successfully unloaded the module: {} for you, {}.".format(split[0], user.RandTag()))
            else:
                self.main.b.Msg(command.source,"I was unable to unload that module, {}, perhaps it does not exist?".format(user.RandTag()))

    def Unload(self,command):
        split = command.message.split(" ")
        user = self.main.usermanager.users[command.nick]
        if split[0] in self.instances.keys():
            self.Unload(split[0])
            self.main.b.Msg(command.source,"I have successfully unloaded the module you requested, {}!".format(user.RandTag()))
