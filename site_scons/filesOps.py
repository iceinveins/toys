# -*- coding: utf-8 -*-
import os
from collections import Counter
from SCons.Script import *

def listFiles(base, suffix):
    ''' 获取指定目录下的所有指定后缀的文件名 '''
    if os.path.exists(base) == False:
        return []
    ret = []
    f_list = os.listdir(base)
    for i in f_list:
        if os.path.isfile("%s/%s" % (base, i)):
            # os.path.splitext():分离文件名与扩展名
            if os.path.splitext(i)[1] == '.%s' % suffix:
                ret.append("%s" % (i))
    return ret


def listSoFiles(base):
    ''' 获取指定目录下所有动态连接库名,需要支持liba.so, liba.so.1.1这种形式 '''
    if os.path.exists(base) == False:
        return []
    ret = []
    f_list = os.listdir(base)
    for i in f_list:
        if os.path.isfile("%s/%s" % (base, i)):
            # os.path.splitext():分离文件名与扩展名
            # print("%s.so" % i.split(".")[0])
            if "%s.so" % i.split(".")[0] in i:
                ret.append("%s" % (i))
    # print(ret)
    return ret


def listFilesIterative(base, suffix):
    ''' 获取指定目录下的所有指定后缀的文件名，包括子目录 '''
    ret = listFiles(base, suffix)
    f_folder = listFolders(base)
    for f in f_folder:
        ret.extend(addPrefixFolder("%s" %
                                   (f), listFilesIterative("%s/%s" % (base, f), suffix)))
    return ret


def addPrefixFolder(base, files):
    ret = []
    for f in files:
        ret.append("%s/%s" % (base, f))
    return ret


def listFolders(base):
    ret = []
    if os.path.exists(base) == False:
        return []
    f_list = os.listdir(base)
    for i in f_list:
        if os.path.isdir("%s/%s" % (base, i)):
            ret.append("%s" % (i))
    return ret


def getSoLibName(fileName):
    if fileName.split(".")[1] == "so":
        if fileName[0:3] == "lib":
            return fileName.split(".")[0][3:]
    return None


'''
input components path or project path
'''


def getPackage(folderPath):
    if os.path.isdir(folderPath):
        folder = os.path.dirname(folderPath)
        folder = os.path.dirname(folder)
        folder = os.path.basename(folder)
        return folder
    return ""

def loadAllComponents(root):
    components = []
    packages = listFolders("%s/packages"%root)
    for package in packages:
        comps = listFolders("%s/packages/%s/components" % (root, package))
        for comp in comps:
            if os.path.isfile("%s/packages/%s/components/%s/SConscript" % (root, package, comp)):
                components.append(
                        "%s.%s" % (package, comp))
    return components


def loadAllProjects(root):
    projects = []
    packages = listFolders("%s/packages"%root)
    for package in packages:
        comps = listFolders("%s/packages/%s/projects" % (root, package))
        for comp in comps:
            if os.path.isfile("%s/packages/%s/projects/%s/SConscript" % (root, package, comp)):
                projects.append(
                        "%s.%s" % (package, comp))
    return projects


def checkSameNameFilePath(filepaths):
    fileNames = []
    for filen in filepaths:
        fileNames.append(os.path.basename(filen))
    counts = Counter(fileNames)
    for key in counts:
        if counts[key] > 1:
            print("Has %d components named %s" % (counts[key], key))
            return False
    return True

def _remove_duplicates(seq):
    seq.reverse()
    seen = set()
    seen_add = seen.add
    ret = [x for x in seq if not (x in seen or seen_add(x))]
    return ret[::-1]

def getDepPath(rootPath, dep):
    depSplit = dep.split(".", 1)
    depAbsPath = ""
    if len(depSplit) == 1:
        # in root/deps
        depAbsPath = '%s/deps/%s' % (rootPath, dep)
    else:
        # in package/deps
        depPackage = depSplit[0]
        depName = depSplit[1]
        depAbsPath = '%s/packages/%s/deps/%s' % (rootPath, depPackage, depName)
    return depAbsPath

def getSlibListInDepLibFolder(rootPath, dep):
    ''' 
    libNames为目录下所有动态连接库名字(liba.so和liba.so.1.1均返回a)， 
    libNames: liba.so=>a, liba.so.1.1=>a
    '''
    depAbsPath = getDepPath(rootPath, dep)
    libNames = []
    depLibAbsPath = depAbsPath + "/lib"
    if os.path.exists(depLibAbsPath):
        libfiles = listSoFiles(depLibAbsPath)
        if os.path.exists(depAbsPath + "/SConscript"):
            libNames, _alibs = SConscript(depAbsPath + "/SConscript")
        else:
            for libfile in libfiles:
                libName = getSoLibName(libfile)
                if libName is not None:
                    libNames.append(libName)
    libNames = _remove_duplicates(libNames)
    return libNames
