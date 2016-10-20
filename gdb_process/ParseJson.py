import json
import sublime
from plugin_ssh_config import PluginSSHConfig

class RemoteGDBSettings:

    def __init__(self, jsonfile):
        self.loadSettings(jsonfile)

    def load_settings(self, jsonfile):
        with open(jsonfile) as data_file:
            self.data = json.load(data_file)

    def get(self, key):
        keys = key.split(".")
        res = self.data
        try:
            for item in keys:
                if res[item]:
                    res = res[item]
            return res
        except KeyError:
            return sublime.load_settings("SublimeGDB.sublime-settings").get(key, None)

    def get(self, dic, key):
        try:
            return dic[key]
        except KeyError, e:
            print "Invalid Key: ", e

    def get_ssh_configs(self):
        try:
            remote_ssh_configs = self.data["remote_ssh_config"]
            if(len(remote_ssh_configs) <= 0):
                return None
            config_parent =  PluginSSHConfig(
                    self.get(remote_ssh_configs[0], "host"),
                    self.get(remote_ssh_configs[0], "hostname"),
                    self.get(remote_ssh_configs[0], "port"),
                    self.get(remote_ssh_configs[0], "username"),
                    self.get(remote_ssh_configs[0], "password"),
                    self.get(remote_ssh_configs[0], "identityfile"))
            for index in range(len(remote_ssh_configs)):
                if index > 0:
                    config = PluginSSHConfig(
                        self.get(remote_ssh_configs[index], "host"),
                        self.get(remote_ssh_configs[index], "hostname"),
                        self.get(remote_ssh_configs[index], "port"),
                        self.get(remote_ssh_configs[index], "username"),
                        self.get(remote_ssh_configs[index], "password"),
                        self.get(remote_ssh_configs[index], "identityfile"))
                    config_parent.add_config(config)


if __name__ == '__main__':
    settings = RemoteGDBSettings("test.json")
    print settings.get("fe")
