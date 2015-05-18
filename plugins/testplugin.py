from plugin_template import IRCPlugin


class MyPlugin(IRCPlugin):
    def load(self):
        self.bot.print("hello")