#!/usr/bin/env python3
import os

class RemoteGDBSourcePath:
    dictionary = None
    def __init__(self):
        pass

    def init(self, debug_mode="local", auto_substitute=False, prefix_postfix_list=None, project_path=""):
        self.debug_mode = debug_mode
        self.auto_substitute = auto_substitute
        if prefix_postfix_list is not None:
            self.local_prefix_path = prefix_postfix_list[0]
            self.remote_prefix_path = prefix_postfix_list[1]
        self.project_path = project_path

        if self.auto_substitute == True:
            if self.dictionary is None:
                self.dictionary = self.build_dictionary(project_path)

    def translate_local_path(self,local_path):
        # print("11local path: %s" % local_path)
        if self.debug_mode == "local":
            # print("local local path: %s" % local_path)
            return local_path
        elif self.auto_substitute == False:
            translated_path = str(local_path).replace(self.local_prefix_path, self.remote_prefix_path, 1)
            self.simplifyPath(translated_path)
            # print("local translated path: %s" % translated_path)
            # return translated_path.split("/")[-1]
            return translated_path
        else:
            print("local local local path: haha")
            path_list = local_path.split("/")
            return path_list[-1]


    def translate_remote_path(self, remote_path):
        # print("11remote path: %s" % remote_path)
        if self.debug_mode == "local":
            # print("remote remote path: %s" % remote_path)
            return remote_path
        elif self.auto_substitute == False:
            translated_path = remote_path.replace(self.remote_prefix_path, self.local_prefix_path, 1)
            self.simplifyPath(translated_path)
            # print("remote translate path: %s" % translated_path)
            return translated_path
        else:
            # print("remote remote remote path: haha")
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
                str_list = name.split(".")
                suffix = str_list[-1]
                source_file_suffix_list = ["c", "C", "cc", "cpp", "cxx", "h", "hpp", "inl"]
                if suffix in source_file_suffix_list:
                    fileinfo.write(name + " " + os.path.join(root, name) + '\n')


    def build_dictionary(self, project_path):
        dictionary_file = project_path + "/.SublimeRemoteGDB.index"
        fileinfo = None
        #dictionary = None
        dictionary = {}
        if os.path.isfile(dictionary_file) == False:
            fileinfo = open(dictionary_file,"w+")
            self.walk_dir(project_path, fileinfo)
            fileinfo.close()
            #fileinfo.flush()
        #if fileinfo == None:
        fileinfo = open(dictionary_file, 'r')
        for line in fileinfo:
            line=line.strip('\n')
            list = line.split(" ")
            dictionary[list[0]] = list[1]
        fileinfo.close()
        return dictionary

    def update_dictionary_file(self, project_path):
        dictionary_file = project_path + "/.SublimeRemoteGDB.index"
        fileinfo = open(dictionary_file, "w+")
        self.walk_dir(project_path, fileinfo)
        for line in fileinfo:
            line = line.strip('\n')
            list = line.split(" ")
            this.dictionary[list[0]] = list[1]
        fileinfo.close()
        return


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
"""

"""
#obj1 = RemoteGDBSourcePath("remote", True, "/Users/leiwang", "/home/leiwang", "/Users/leiwang/ht/dir");
obj1 = RemoteGDBSourcePath("remote", True, "/Users/leiwang", "/home/leiwang", "/Users/leiwang/Documents/code/common");
path = obj1.translate_remote_path("/home/leiwang/ht/../../Users/leiwang/ht/dir/common/src/select/Ads_Selector.cpp")
path = obj1.simplifyPath(path);
print(path)

#obj1 = RemoteGDBSourcePath("remote", True, "/Users/leiwang", "/home/leiwang", "/Users/leiwang/ht/dir");
obj1 = RemoteGDBSourcePath()
prefix_postfix_list = ["/Users/leiwang", "/home/leiwang"]
obj1.init("remote", True, prefix_postfix_list, "/Users/leiwang/ht/dir");
path = obj1.translate_local_path("/Users/leiwang/ht/../../Users/leiwang/ht/dir/1.cpp")
print(path)
obj1.update_dictionary_file("/Users/leiwang/ht/dir")
"""
