import os, sys

class SelfDefinedProcess:

	def connect(self):
		raise Exception("not implemented connect!")

	def start(self, commandline, workingdir=None):
		raise Exception("not implemented start!")

	def stop(self):
		raise Exception("not implemented stop!")

	def pipe(self):
		raise Exception("not implemented pipe!")

	def is_running(self):
		raise Exception("not implemented is_running!")

	def exec_command(self, command):
		raise Exception("not implemented exec_command")

	def __del__(self):
		self.stop()

class LocalProcess(SelfDefinedProcess):

	def __init__(self):
		self._process = None

	def connect(self):
		pass

	def start(self, commandline, workingdir=None):
		import subprocess
		self._process = subprocess.Popen(commandline, shell=True, cwd=workingdir,
                            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

	def stop(self):
		if self._process:
			self._process.terminate()
			self._process = None

	def pipe(self):
		if self._process:
			return self._process.stdin, self._process.stdout, self._process.stderr

		return None, None, None

	def is_running(self):
		return self._process is not None and self._process.poll() is None

	def exec_command(self, command):
		if not self._process:
			raise Exception("process not start!")

		self._process.stdin.write(command)
		self._process.stdin.write("\n")
		self._process.stdin.flush()

		return self._process.stdout.read()
