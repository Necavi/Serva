import os
import inspect

from glob import glob
from importlib.machinery import SourceFileLoader

from biblib import biblib
from configobj import ConfigObj
from validate import Validator
from plugin_template import IRCPlugin


class Serva(object):
    def __init__(self):
        self.config = None
        self.bot = None
        self.plugins = {}
        self.load()

    def load(self):
        config = ConfigObj("serva.ini", configspec="config_spec.ini")
        self.config = config
        config.validate(Validator(), copy=True)
        config.write()
        self.bot = biblib.Bot((config["hostname"], config["port"]), config["name"], usessl=config["ssl"])
        self.bot.events.Connected += self.connected
        self.load_all_plugins()
        self.bot.connect()

    def load_all_plugins(self):
        if not os.path.exists("plugins"):
            os.mkdir("plugins")
        for module in glob("plugins/*.py"):
            print(module)
            print(self.load_plugin(module))

    def load_plugin(self, module):
        name = os.path.splitext(os.path.basename(module))[0]
        if name == "__init__":
            return False
        loader = SourceFileLoader("plugins." + name, module)
        try:
            plugin = loader.load_module()
        except ImportError:
            self.log_error()
            return False
        for i, cls in inspect.getmembers(plugin, inspect.isclass):
            if issubclass(cls, IRCPlugin) and cls is not IRCPlugin:
                print(cls)
                self.plugins[name] = cls(self)
                self.plugins[name].load()
                return True
        return False

    def connected(self):
        for channel in self.config["channels"]:
            self.bot.join(channel)

if __name__ == "__main__":
    Serva()