SublimeRemoteGDB
======================

A plugin for [Sublime Text 3](http://www.sublimetext.com/) that debug local or remote process.

## Feature

* Can debug local or remote process.
* Can debug multi-hop remote process.
* Can debug exec, attach and coredump.

## Installation

Go to Preference -> Browse Packages, then git clone [https://github.com/summerwinter/SublimeRemoteGDB.git](https://github.com/summerwinter/SublimeRemoteGDB.git).
After that, restart Sublime Text.

# Configuration

This plugin is based on [SublimeGDB](https://github.com/quarnster/SublimeGDB), so please refer to common configurations in SublimeGDB.

In this plugin, every folder in Sublime Text is considered as a project. When you are in a file which is in one folder opened in Sublime Text, press <kbd>F5</kbd> to start debugging, this plugin will promot you to config as follows.

```
{
  // you should copy this file to your project dir, and then configure related terms

  // if no set, default is /usr/local/bin/gdb. In mac, you may need to add sudo
  "gdb_path": "/usr/local/bin/gdb",
  // local or remote
  "local_remote_mode": "local",
  // exec, attach or coredump
  "debug_mode": "exec",
  // if debug_mode is exec
  "exec": {
    // if workingdir is not specified, you should specify executable_file with absolute path
    "workingdir": "/home/test",
    "executable_file": "hello",
    "arguments": ""
  },
  // if debug_mode is attach
  "attach": {
    // if attach_id is sepcified, I will attach it directly
    "attach_id": "",
    // if attach_id is not specified, I will search by attach_keywork, and if find multiple results, I will let you choose
    "attach_keyword": ""
  },
  // if debug_mode is coredump
  "coredump": {
    // both should be absolute path
    "executable_file": "",
    "coredump_file": ""
  },
  // if local_remote_mode is remote
  // if remote_host is specified, I will find it from /etc/ssh/ssh_config or ~/.ssh/config
  "remote_host": "",
  // if remote_host is not sepcified, you should specify the nested remote_ssh_config
  // some terms may be empty or deleted, you should ensure that you can connect the remote host by the path you specified
  "remote_ssh_config": [
    {
      "hostname": "",
      "port": 22,
      "username": "",
      "password": "",
      "identityfile": ""
    }
  ],
  // if local_remote_mode is remote, you should either specify substitute_path or set auto_substitute to 1
  // substitute_path is used to transform between local source code paths and remote source code paths
  "substitute_path": ["/local/codepath", "/remote/codepath"],
  // if auto_substitute is set to 1, I will establish the index file, and auto transform souce code paths
  "auto_substitute": 0
}

```

This plugin replaces the simple configuration in SublimeGDB with more complex but more functional configuation.

## Usage

Each time if you want to debug one project, drag it into Sublime Text as one folder. Open any file in that folder, then start debugging. You should ensure the local source code is consistent with the remote source code.

## Contributors

* Xiaomei Liu
* Danshuang Li
* Dan Wu
* Chaochao Liang
* Lei Wang
* summerwinterwang

(This plugin is produced by hackathon, so it isn't perfect! Let us imporve it together and make Sublime Text a C/C++ IDE like Visual Studio!)

## Thanks

* [quarnster](https://github.com/quarnster/SublimeGDB)
* [jlegewie](https://github.com/jlegewie/sublime-paramiko)
* [bblanchon](https://github.com/bblanchon/SublimeText-HighlightBuildErrors)
