# from local_process import *
# from remote_process import *
# from nested_paramiko import *
# from plugin_ssh_config import *

# localProcess = LocalProcess("/Users/xdwang/test", "/usr/local/bin/gdb --interpreter=mi ./a.out")
# localProcess.start()

# print "sumemr"

# stdin, stdout, stderr = localProcess.pipe()
# stdin.write('15-break-insert "\"/Users/xdwang/test/test.cpp\":18"\n')
# stdin.flush()
# print "winter"
# print stdout.readline()

from gdb_process import *

gdb_process = GDBProcess()
gdb_process.set_remote_debug(host="139server")
gdb_process.connect()
print(gdb_process.find_pids("docker"))

gdb_process.set_remote_debug(host="139server")
gdb_process.connect()
print(gdb_process.find_pids("docker"))