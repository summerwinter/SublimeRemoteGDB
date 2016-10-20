#!/usr/bin/env python3
import os

class RemoteGDBSourcePath:
    #dictionary = {}
    def __init__(self, debug_mode="local", auto_substitute=False, local_prefix_path=None, remote_prefix_path=None, project_path=""):
        self.debug_mode = debug_mode
        self.auto_substitute = auto_substitute
        self.local_prefix_path = local_prefix_path
        self.remote_prefix_path = remote_prefix_path
        self.auto_subsitute = auto_substitute
        if self.auto_substitute == True:
            self.dictionary = self.build_dictionary(project_path)


    def translate_local_path(self,local_path):
        if self.debug_mode == "local":
            return local_path
        elif self.auto_substitute == False:
            translated_path = str(local_path).replace(self.local_prefix_path, self.remote_prefix_path, 1)
            self.simplifyPath(translated_path)
            return translated_path
        else:
            return local_path.split("/")[-1]


    def translate_remote_path(self, remote_path):
        if self.debug_mode == "local":
            return remote_path
        elif self.auto_substitute == False:
            translated_path = remote_path.replace(self.remote_prefix_path, self.local_prefix_path, 1)
            self.simplifyPath(translated_path)
            return translated_path
        else:
            path = remote_path.split("/")[-1]
            return self.dictionary.get(path, "")

    def simplifyPath(self, path):
        stack = []
        i = 0
        res = ''
        while i < len(path):
            end = i+1
            while end < len(path) and path[end] != "/":
                end += 1
            sub=path[i+1:end]
            if len(sub) > 0:
                if sub == "..":
                    if stack != []: stack.pop()
                elif sub != ".":
                    stack.append(sub)
            i = end
        if stack == []: return "/"
        for i in stack:
            res += "/"+i
        return res

    def walk_dir(self, dir,fileinfo,topdown=True):
        for root, dirs, files in os.walk(dir, topdown):
            for name in files:
                if name.endswith(".c") or name.endswith(".C") or name.endswith(".cc") or name.endswith(".cpp") or name.endswith(".cxx") or name.endswith(".h") or name.endswith(".hpp") or name.endswith(".inl"):
                    fileinfo.write(name + " " + os.path.join(root,name) + '\n')


    def build_dictionary(self, project_path):
        dictionary_file = project_path + "/index.txt"
        fileinfo = None
        #dictionary = None
        dictionary = {}
        if os.path.isfile(dictionary_file) == False:
            fileinfo = open(dictionary_file,"w+")
            self.walk_dir(project_path, fileinfo)
        if fileinfo == None:
            fileinfo = open(dictionary_file, 'r')
        for line in fileinfo:
            line=line.strip('\n')
            list = line.split(" ")
            dictionary[list[0]] = list[1]
        fileinfo.close()
        return dictionary


"""
obj1 = RemoteGDBSourcePath("remote", False, "/Users/leiwang", "/home/leiwang");
path = obj1.translate_local_path("/home/leiwang/src/1.cpp")
#path = obj1.translate_local_path("/Users/leiwang/ht/../../Users/leiwang/ht/dir/1.cpp")
print(path)
"""
"""
obj1 = RemoteGDBSourcePath("remote", False, "/Users/leiwang", "/home/leiwang");
path = obj1.translate_remote_path("/home/leiwang/ht/../../Users/leiwang/ht/dir/1.cpp")
path = obj1.simplifyPath(path);
print(path)

obj1 = RemoteGDBSourcePath("remote", True, "/Users/leiwang", "/home/leiwang", "/Users/leiwang/ht/dir");
path = obj1.translate_remote_path("/home/leiwang/ht/../../Users/leiwang/ht/dir/1.cpp")
path = obj1.simplifyPath(path);
print(path)

obj1 = RemoteGDBSourcePath("remote", True, "/Users/leiwang", "/home/leiwang", "/Users/leiwang/ht/dir");
path = obj1.translate_local_path("/Users/leiwang/ht/../../Users/leiwang/ht/dir/1.cpp")
print(path)
"""
