import constants
import plugintemplate
class joinchannels(plugintemplate.plugin):
    def OnEnable(self):
        self.main.b.Join(", ".join(constants.channels))