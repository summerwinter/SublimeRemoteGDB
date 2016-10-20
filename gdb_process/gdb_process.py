import os, sys

from . import local_process
from . import remote_process
import subprocess

class GDBProcess:

	def __init__(self):
		self._remote = False
		self._process = None
		self._workingdir = None

	def set_local_debug(self, gdb_path="/usr/local/bin/gdb"):
		self._remote = False
		self._process = local_process.LocalProcess()
		self._gdb_command = "%s --interpreter=mi" % gdb_path

	def set_remote_debug(self, host=None, plugin_ssh_config=None, timeout=None):
		new_process = remote_process.RemoteProcess(host, plugin_ssh_config, timeout)
		if self._remote == True and self._process._plugin_ssh_config == new_process._plugin_ssh_config:
			return

		self._remote = True
		self._process = new_process
		self._gdb_command = "gdb --interpreter=mi"

	def debug_by_executable_file(self, workingdir, executable_file):
		if workingdir:
			workingdir = os.path.expanduser(workingdir)
			self._workingdir = workingdir
			if self._remote == False:
				self._commandline = "%s %s" % (self._gdb_command, executable_file)
			else:
				self._commandline = "%s %s" % (self._gdb_command, os.path.join(os.path.expanduser(workingdir), executable_file))
		else:
			self._commandline = "%s %s" % (self._gdb_command, executable_file)

	def debug_by_attach(self, pid):
		self._commandline = "%s attach %d" % (self._gdb_command, pid)

	def debug_by_coredump(self, executable_file_path, coredump_file_path):
		self._commandline = "%s %s %s" % (self._gdb_command, executable_file_path, coredump_file_path)

	def connect(self):
		self._process.connect()

	def start(self):
		self._process.start(self._commandline, self._workingdir)

	def stop(self):
		if self._process:
			self._process.stop()

	def pipe(self):
		if not self._process:
			raise Exception("not inited!")
		
		return self.pipe()

	def is_running(self):
		return self._process and self._process.is_running()

	def exec_command(self, command):
		if not self._process:
			raise Exception("not inited!")
		
		return self._process.exec_command(command)
	
	def find_pids(self, keyword):
		if self._remote == False:
			results = subprocess.check_output("ps -ef | grep '%s' | grep -v grep | awk '{print $2}'" % keyword, shell=True)
		else:
			results = self._process.exec_command("ps -ef | grep '%s' | grep -v grep | awk '{print $2}'" % keyword)
		
		pids = []
		for line in results.splitlines():
			line = line.strip()
			if len(line) == 0:
				continue

			pids.append(int(line))

		return pids
