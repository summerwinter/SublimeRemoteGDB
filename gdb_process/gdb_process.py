import os, sys

from . import local_process
from . import remote_process
import subprocess

class GDBProcess:

	def __init__(self):
		self._remote = False
		self._process = None
		self._workingdir = None
		self.stdin = self.stdout = self.stderr = None
		self._commandline = None
		self._running = False
		self._debug_ready = False

	def set_local_debug(self, gdb_path="/usr/local/bin/gdb"):
		self._remote = False
		self._process = local_process.LocalProcess()
		self._gdb_command = "%s --interpreter=mi" % gdb_path
		self._commandline = None

	def set_remote_debug(self, host=None, plugin_ssh_config=None, timeout=None):
		self._remote = True
		self._process = remote_process.RemoteProcess(host, plugin_ssh_config, timeout)
		self._gdb_command = "gdb --interpreter=mi"
		self._commandline = None

	def debug_by_executable_file(self, workingdir, executable_file, arguments=None):
		if workingdir:
			workingdir = os.path.expanduser(workingdir)
			self._workingdir = workingdir
		else:
			self._workingdir = None
			
		self._commandline = "%s %s" % (self._gdb_command, executable_file)

		self._arguments = arguments

	def debug_by_attach(self, pid):
		self._commandline = "%s attach %d" % (self._gdb_command, pid)
		self._pid = pid

	def debug_by_coredump(self, executable_file_path, coredump_file_path):
		self._commandline = "%s %s %s" % (self._gdb_command, executable_file_path, coredump_file_path)

	def valid(self):
		return self._commandline is not None

	def debug_ready(self, ready=None):
		if ready is None:
			return self._debug_ready

		self._debug_ready = ready

	def connect(self):
		self._process.connect()

	def start(self):
		self._process.start(self._commandline, self._workingdir)
		self._running = True

	def stop(self):
		if self._process:
			self._process.stop()

	def pipe(self):
		if not self._process:
			raise Exception("not inited!")
		
		self.stdin, self.stdout, self.stderr = self._process.pipe()
		return self.stdin, self.stdout, self.stderr

	def is_running(self):
		return self._running
		return self._process and self._process.is_running()

	def poll(self):
		if self.is_running():
			return None

		return 1

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

			pids.append(line.decode(sys.getdefaultencoding()))

		return pids
