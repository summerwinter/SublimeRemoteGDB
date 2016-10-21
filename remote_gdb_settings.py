import json
import os
import sublime
from SublimeRemoteGDB.gdb_process.plugin_ssh_config import PluginSSHConfig

class RemoteGDBSettings:

    def __init__(self, project_dir=None):
        self.data = None
        if project_dir:
            self.load_settings(project_dir)

    def load_settings(self, project_dir):
        project_setting_file = os.path.join(project_dir, ".remotegdb.json")
        if not os.path.exists(project_setting_file):
            return False

        with open(project_setting_file) as data_file:
            self.data = json.load(data_file)

        return True

    def get(self, key, default_value=None):
        keys = key.split(".")
        try:
            res = self.data
            for item in keys:
                if item in res.keys():
                    res = res[item]
                else:
                    raise
                if not res:
                    return default_value
            return res
        except Exception:
            return sublime.load_settings("SublimeRemoteGDB.sublime-settings").get(key, default_value)

        return sublime.load_settings("SublimeRemoteGDB.sublime-settings").get(key, default_value)

    def __get(self, dic, key):
        try:
            if key in dic.keys():
                val = dic[key]
                if val:
                    return val
            return None
        except KeyError:
            # print "Invalid Key: ", e
            return None

    def get_ssh_configs(self):
        try:
            remote_ssh_configs = self.data["remote_ssh_config"]
            if(len(remote_ssh_configs) <= 0):
                return None
            config_parent =  PluginSSHConfig(
                    self.__get(remote_ssh_configs[0], "host"),
                    self.__get(remote_ssh_configs[0], "hostname"),
                    self.__get(remote_ssh_configs[0], "port"),
                    self.__get(remote_ssh_configs[0], "username"),
                    self.__get(remote_ssh_configs[0], "password"),
                    self.__get(remote_ssh_configs[0], "identityfile"))
            for index in range(len(remote_ssh_configs)):
                if index > 0:
                    config = PluginSSHConfig(
                        self.__get(remote_ssh_configs[index], "host"),
                        self.__get(remote_ssh_configs[index], "hostname"),
                        self.__get(remote_ssh_configs[index], "port"),
                        self.__get(remote_ssh_configs[index], "username"),
                        self.__get(remote_ssh_configs[index], "password"),
                        self.__get(remote_ssh_configs[index], "identityfile"))
                    config_parent.add_config(config)

            return config_parent

        except Exception as err:
            print(err)
            return None
