import os, sys
import shlex
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

class PluginSSHConfig:

	def __init__(self, host=None, hostname=None, port=None, username=None, password=None, identityfile=None):
		self._cfg = {}
		self._cfg["host"] = host
		self._cfg["hostname"] = hostname
		self._cfg["port"] = port if port is not None else 22
		self._cfg["username"] = username
		self._cfg["password"] = password
		if identityfile is None:
			identityfile = []
		elif isinstance(identityfile, string_types):
			identityfile = [identityfile]
		else:
			identityfile = identityfile
		self._cfg["identityfile"] = identityfile
		self._cfg["nested_config"] = None
		self._cfg["proxy_command"] = None

	def __getitem__(self, key):
		return self._cfg[key]

	def add_config(self, config):
		if not isinstance(config, PluginSSHConfig):
			return

		if self._cfg["nested_config"] is None:
			self._cfg["nested_config"] = config
			self._cfg["proxy_command"] = "nc %s %d" % (config["hostname"], config["port"]) 
		else:
			self._cfg["nested_config"].add_config(config)

	def export_config_chain(self):
		chain = [self]
		if self._cfg["nested_config"] is None:
			return chain

		return self._cfg["nested_config"].export_config_chain() + chain

	def __eq__(self, other):
		for key in self._cfg.keys():
			if self._cfg[key] != other._cfg[key]:
				return False

		return True

	@staticmethod
	def load_from_system_ssh_config(host):
		import paramiko
		paramiko_SSHClient_proxy_config = paramiko.SSHConfig()
		merged_config = StringIO()
		for conf_file in [os.path.join(os.path.sep, 'etc', 'ssh', 'ssh_config'), os.path.join(os.getenv('HOME','/tmp'), '.ssh', 'config')]:
			try:
				config = open(conf_file)
				merged_config.write(config.read())
				merged_config.write('\n')
				config.close()
				del config

			except IOError as e:
				pass

		merged_config.seek(0,0)
		paramiko_SSHClient_proxy_config.parse(merged_config)
		del merged_config

		return PluginSSHConfig.__rescurive_load_from_system_ssh_config(paramiko_SSHClient_proxy_config, host)

	@staticmethod
	def __rescurive_load_from_system_ssh_config(paramiko_SSHClient_proxy_config, host, last_plugin_ssh_config=None):
		config = paramiko_SSHClient_proxy_config.lookup(host)
		hostname = config.get("hostname")
		username = config.get("user")
		port = config.get("port", "22")
		identityfile = config.get("identityfile", None)
		proxy_command = config.get("proxycommand", None)

		plugin_ssh_config = PluginSSHConfig(hostname=hostname, username=username, port = int(port), identityfile=identityfile)
		plugin_ssh_config.add_config(last_plugin_ssh_config)

		if proxy_command is None:
			return plugin_ssh_config

		command_args = [] + shlex.split(proxy_command)
		remote_host = command_args[1]
		return PluginSSHConfig.__rescurive_load_from_system_ssh_config(paramiko_SSHClient_proxy_config, remote_host, plugin_ssh_config)

	def __str__(self):
		if self._cfg["nested_config"] is None:
			return self._cfg.__str__() + "\n"

		return self._cfg.__str__() + "\n" + self._cfg["nested_config"].__str__()