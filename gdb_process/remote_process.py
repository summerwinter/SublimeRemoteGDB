import os, sys

import local_process
import nested_paramiko
from plugin_ssh_config import *

last_nested_paramiko = {"config": None, "nested_paramiko": None}

class RemoteProcess(local_process.SelfDefinedProcess):

	def __init__(self, host=None, plugin_ssh_config=None, timeout=None):
		self._client = None
		self._host = host
		self._plugin_ssh_config = plugin_ssh_config
		if self._host is not None:
			self._plugin_ssh_config = PluginSSHConfig.load_from_system_ssh_config(host)
		self._timeout = timeout

		self._nested_paramiko = None

		if self._plugin_ssh_config is None:
			raise Exception("no host and plugin_ssh_config!")

		self._stdin, self._stdout, self._stderr = None, None, None

		print(self._plugin_ssh_config)

	def connect(self):
		if last_nested_paramiko["config"] is not None and last_nested_paramiko["config"] == self._plugin_ssh_config and last_nested_paramiko["nested_paramiko"].is_active():
			self._nested_paramiko = last_nested_paramiko["nested_paramiko"]
			return

		self._nested_paramiko = nested_paramiko.NestedParamiko(self._plugin_ssh_config)
		self._nested_paramiko.connect(self._timeout)

		if last_nested_paramiko["config"]:
			del last_nested_paramiko["nested_paramiko"]

		last_nested_paramiko["config"] = self._plugin_ssh_config
		last_nested_paramiko["nested_paramiko"] = self._nested_paramiko

	def start(self, commandline, workingdir=None):
		if not self._nested_paramiko:
			raise Exception("nested paramiko not start!")

		self._stdin, self._stdout, self._stderr = self._nested_paramiko._client.exec_command(commandline
			)

	def stop(self):
		if self._nested_paramiko:
			# del self._nested_paramiko
			self._nested_paramiko = None

	def pipe(self):
		return self._stdin, self._stdout, self._stderr

	def is_running(self):
		return self._nested_paramiko is not None

	def exec_command(self, command):
		if not self._nested_paramiko:
			raise Exception("nested paramiko not start!")

		stdin, stdout, stderr = self._nested_paramiko._client.exec_command(command)
		return stdout.read()
