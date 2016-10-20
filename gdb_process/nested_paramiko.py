import os, sys
import paramiko
from paramiko.resource import ResourceManager
from paramiko.transport import Transport
from paramiko.ssh_exception import SSHException, BadHostKeyException
import socket

from plugin_ssh_config import *

class NestedParamiko:

	def __init__(self, plugin_ssh_config):
		self._plugin_ssh_config = plugin_ssh_config
		self._client = paramiko.SSHClient()
		self._client.load_system_host_keys()
		self._client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		self._chained_transports = []

	def connect(self, timeout=None):
		if self._plugin_ssh_config is None:
			raise Exception("no config!")

		if self._plugin_ssh_config["nested_config"] is None:
			try:
				self._client.connect(hostname=self._plugin_ssh_config["hostname"], port=self._plugin_ssh_config["port"], 
					username=self._plugin_ssh_config["username"], password=self._plugin_ssh_config["password"], key_filename=self._plugin_ssh_config["identityfile"], timeout=timeout)
			except Exception as e:
				print(e)
				raise Exception("connect failed!")

			return

		def __create_and_connect_transport(transport_sock, username, password, identityfile):
			t = self._client._transport = Transport(transport_sock)
			self._chained_transports.append(t)

			t.start_client()
			# ResourceManager.register(self._client, t)

			if self._client._log_channel is not None:
				t.set_log_channel(self._client._log_channel)

			self._client._auth(username, password, None, identityfile, True, True, None, None, None, None)

		config_chain = self._plugin_ssh_config.export_config_chain()
		plugin_ssh_config = config_chain.pop()
		try:
			sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			if timeout is not None:
				sock.settimeout(timeout)
			sock.connect((plugin_ssh_config["hostname"], plugin_ssh_config["port"]))

			transport_sock = sock
			while config_chain:
				__create_and_connect_transport(transport_sock, plugin_ssh_config["username"], plugin_ssh_config["password"], plugin_ssh_config["identityfile"])
				
				transport_sock = self._client._transport.open_session()
				transport_sock.exec_command(plugin_ssh_config["proxy_command"])

				plugin_ssh_config = config_chain.pop()

			__create_and_connect_transport(transport_sock, plugin_ssh_config["username"], plugin_ssh_config["password"], plugin_ssh_config["identityfile"])

		except Exception as e:
			print(e)
			raise Exception("connect failed!")

	def is_active(self):
		return self._client.get_transport() and self._client.get_transport().is_active()

	def __del__(self):
		if self._chained_transports:
			self._client._transport = None
			while self._chained_transports:
				t = self._chained_transports.pop(0).close()
				del t

		del self._client

