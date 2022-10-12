# -*- coding: utf-8 -*-
import os
import filesOps as fileOps
from SCons.Script import *
from compiler import *
import copy


def _remove_duplicates(seq):
    seq.reverse()
    seen = set()
    seen_add = seen.add
    ret = [x for x in seq if not (x in seen or seen_add(x))]
    return ret[::-1]


def createEnvForBuild(genv, env, deps, components, staticlibs, sharedlibs, outputFolder=None):
    srcFolder = "src"
    if '_SRC_FOLDER' in env:
        srcFolder = env['_SRC_FOLDER']
        if srcFolder == "":
            srcFolder = "src"
    winSuffix = ""
    if genv['WINDOWS']:
        winSuffix = "_win"
    if GetOption('release'):
        VariantDir('.intermediate%s'%winSuffix, srcFolder, duplicate=0)
        VariantDir('release%s'%winSuffix, '.', duplicate=0)
    else:
        VariantDir('.intermediate_debug%s'%winSuffix, srcFolder, duplicate=0)
        VariantDir('debug%s'%winSuffix, '.', duplicate=0)

    env.Replace(CXX=genv['CXX'])
    env.Replace(CC=genv['CC'])
    env.Replace(AR=genv['AR'])
    env.Replace(RANLIB=genv['RANLIB'])
    tmp = os.path.split(os.getcwd())[0]
    tmp = os.path.split(tmp)[0]

    packageName = os.path.split(tmp)[1]
    componentName = os.path.split(os.getcwd())[1]
    componentFullName = "%s.%s" % (packageName, componentName)
    rootPath = genv['ROOT']

    cpp_srcfiles = fileOps.listFilesIterative(srcFolder, "cpp")
    cpp_srcfiles += fileOps.listFilesIterative(srcFolder, "cxx")
    if GetOption('release'):
        cpp_srcfiles = fileOps.addPrefixFolder('.intermediate%s'%winSuffix, cpp_srcfiles)
    else:
        cpp_srcfiles = fileOps.addPrefixFolder(
            '.intermediate_debug%s'%winSuffix, cpp_srcfiles)

    c_srcfiles = fileOps.listFilesIterative(srcFolder, "c")
    c_srcfiles += fileOps.listFilesIterative(srcFolder, "cc")
    c_srcfiles += fileOps.listFilesIterative(srcFolder, "S")
    c_srcfiles += fileOps.listFilesIterative(srcFolder, "s")
    if GetOption('release'):
        c_srcfiles = fileOps.addPrefixFolder(".intermediate%s"%winSuffix, c_srcfiles)
    else:
        c_srcfiles = fileOps.addPrefixFolder(".intermediate_debug%s"%winSuffix, c_srcfiles)

    env.Replace(CCFLAGS=genv['CCFLAGS'])
    if os.path.exists(Dir('inc').abspath):
        env.Append(CPPPATH=['inc'])
    if os.path.exists(Dir('inc_protected').abspath):
        env.Append(CPPPATH=['inc_protected'])

    env.Replace(CPPDEFINES=genv['CPPDEFINES'])

    env.Append(LIBPATH=genv['LIBPATH'])
    if outputFolder is not None:
        env.Append(LIBPATH=[outputFolder])
    env.Append(LINKFLAGS='-Wl,-rpath,. -pthread -static-libgcc -static-libstdc++')
    env.Append(LINKFLAGS=' %s'%GetOption('ldflags'))

    env.Append(CPPPATH=genv['CPPPATH'])
    # append global deps inc folder
    for dep in deps:
        depSplit = dep.split(".", 1)
        if len(depSplit) == 1:
            # in root/deps
            externalDepAbsPath = '%s/deps/%s' % (rootPath, dep)
            externalDepIncAbsPath = externalDepAbsPath + "/inc"
            if os.path.exists(externalDepIncAbsPath):
                env.Append(CPPPATH=['%s/deps/%s/inc' % (rootPath, dep)])
        else:
            # in package/deps
            depPackage = depSplit[0]
            depName = depSplit[1]
            externalDepAbsPath = '%s/packages/%s/deps/%s' % (
                rootPath, depPackage, depName)
            externalDepIncAbsPath = externalDepAbsPath + "/inc"
            if os.path.exists(externalDepIncAbsPath):
                env.Append(CPPPATH=[externalDepIncAbsPath])

    # append depended component inc folder

    # print(components)
    for comp in components:
        tmp = comp.split(".")
        compPackage = tmp[0]
        compName = tmp[-1]
        if os.path.exists(Dir('%s/packages/%s/components/%s/inc' % (rootPath, compPackage, compName)).abspath):
            env.Append(CPPPATH=['%s/packages/%s/components/%s/inc' %
                                (rootPath, compPackage, compName)])
        if compPackage == packageName:
            if os.path.exists(Dir('%s/packages/%s/components/%s/inc_protected' % (rootPath, compPackage, compName)).abspath):
                env.Append(CPPPATH=[
                           '%s/packages/%s/components/%s/inc_protected' % (rootPath, compPackage, compName)])
        else:
            if comp in genv['COMP_FRIENDS']:
                if componentFullName in genv['COMP_FRIENDS'][comp]:
                    if os.path.exists(Dir('%s/packages/%s/components/%s/inc_protected' % (rootPath, compPackage, compName)).abspath):
                        env.Append(CPPPATH=[
                                   '%s/packages/%s/components/%s/inc_protected' % (rootPath, compPackage, compName)])

    # append global deps lib, add *.so in dep/lib to sharedlibs
    for dep in deps:
        libnames = fileOps.getSlibListInDepLibFolder(rootPath, dep)
        sharedlibs.extend(libnames)

    _staticlibs = []
    _wholeArchiveLibs = []
    for comp in components:
        tmp = comp.split(".")
        compPackage = tmp[0]
        compName = tmp[-1]
        if genv['WINDOWS']:
            compName = compName + "_win"
        if GetOption('release'):
            _staticlibs.append(compName)
        else:
            _staticlibs.append("%s_d" % compName)
        
        if comp in genv['_WHOLE_ARCHIVE_LIST']:
            if GetOption('release'):
                _wholeArchiveLibs.append(compName)
            else:
                _wholeArchiveLibs.append("%s_d" % compName)

    _staticlibs.extend(staticlibs)
    if genv['ASMLIB']:
        _staticlibs.append("aelf64")
    staticlibs = _staticlibs
    # append depended component lib
    for comp in components:
        tmp = comp.split(".")
        compPackage = tmp[0]
        compName = tmp[-1]
        env.Append(LIBPATH=['%s/packages/%s/components/%s' %
                            (rootPath, compPackage, compName)])
    for dep in deps:
        depSplit = dep.split(".", 1)
        if len(depSplit) == 1:
            if os.path.exists('%s/deps/%s/lib' % (rootPath, dep)):
                env.Append(LIBPATH=['%s/deps/%s/lib' % (rootPath, dep)])
            if os.path.exists('%s/deps/%s/lib_nocopy' % (rootPath, dep)):
                env.Append(LIBPATH=['%s/deps/%s/lib_nocopy' % (rootPath, dep)])
        else:
            depPackage = depSplit[0]
            depName = depSplit[1]
            if os.path.exists('%s/packages/%s/deps/%s/lib' %
                              (rootPath, depPackage, depName)):
                env.Append(LIBPATH=['%s/packages/%s/deps/%s/lib' %
                                    (rootPath, depPackage, depName)])
            if os.path.exists('%s/packages/%s/deps/%s/lib_nocopy' %
                              (rootPath, depPackage, depName)):
                env.Append(LIBPATH=['%s/packages/%s/deps/%s/lib_nocopy' %
                                    (rootPath, depPackage, depName)])

    env['STATICLIBS'] = []
    env['SHAREDLIBS'] = []
    env['WHOLE_ARCHIVE_STATIC_LIBS'] = []
    if GetOption('asan') == True:
        env.Append(STATICLIBS='asan')
    if GetOption('tsan') == True:
        env.Append(STATICLIBS='tsan')
    if GetOption('ubsan') == True:
        env.Append(STATICLIBS='ubsan')
    if GetOption('lsan') == True:
        env.Append(STATICLIBS='lsan')
    if GetOption('asan') or GetOption('tsan') or GetOption('ubsan') or GetOption('lsan'):
        env.Append(SHAREDLIBS='dl')
    for sharedlib in sharedlibs:
        env.Append(SHAREDLIBS=sharedlib)
    if genv['WINDOWS'] == False:
        env.Append(SHAREDLIBS='rt')
    # env.Append(SHAREDLIBS='z')
    for staticlib in staticlibs:
        env.Append(STATICLIBS=staticlib)
    for staticlib in _wholeArchiveLibs:
        env.Append(WHOLE_ARCHIVE_STATIC_LIBS=staticlib)
    
    env.Append(
        _LIBFLAGS=' -Wl,--whole-archive ${_stripixes(LIBLINKPREFIX, WHOLE_ARCHIVE_STATIC_LIBS, LIBLINKSUFFIX, LIBPREFIXES, LIBSUFFIXES, __env__)} -Wl,--no-whole-archive')
    env.Append(
        _LIBFLAGS=' -Wl,-Bstatic ${_stripixes(LIBLINKPREFIX, STATICLIBS, LIBLINKSUFFIX, LIBPREFIXES, LIBSUFFIXES, __env__)}')
    env.Append(
        _LIBFLAGS=' -Wl,-Bdynamic ${_stripixes(LIBLINKPREFIX, SHAREDLIBS, LIBLINKSUFFIX, LIBPREFIXES, LIBSUFFIXES, __env__)}')

    if genv['WINDOWS']:
        componentName = componentName + "_win"
    if GetOption('release'):
        pass
    else:
        componentName = componentName + "_d"
    return env, componentName, cpp_srcfiles + c_srcfiles

def currentComponentName():
    tmp = os.path.split(os.getcwd())[0]
    tmp = os.path.split(tmp)[0]
    packageName = os.path.split(tmp)[1]
    componentName = os.path.split(os.getcwd())[1]
    comp = "%s.%s" % (packageName, componentName)
    return comp

def parseDependency(genv, env, deps, components, staticlibs, sharedlibs, friends):
    comp = currentComponentName()
    if comp not in genv['COMP_DEPS']:
        genv['COMP_DEPS'][comp] = deps
    if comp not in genv['COMP_COMP']:
        genv['COMP_COMP'][comp] = components
    if comp not in genv['COMP_DLIBS']:
        genv['COMP_DLIBS'][comp] = sharedlibs
    if comp not in genv['COMP_SLIBS']:
        genv['COMP_SLIBS'][comp] = staticlibs
    if comp not in genv['COMP_FRIENDS']:
        genv['COMP_FRIENDS'][comp] = friends
    ver = "no_ver"
    if "VERSION" in env: ver = env["VERSION"]
    auther = "no_auther"
    if "AUTHER" in env: auther = env["AUTHER"]

    cwd = os.getcwd()
    if GetOption("commitinfo"):
        import json
        from git import get_git_commit, get_git_update
        commit = get_git_commit(cwd)
        update = get_git_update(cwd)
        with open("{}/_commit_.json".format(cwd), "w") as f:
            json.dump({"commit": commit, "update": update}, f)
    else:
        try:
            import json
            with open("{}/_commit_.json".format(cwd), "r") as f:
                j = json.load(f)
                commit = j["commit"]
                update = j["update"]
        except:
            commit = ""
            update = ""
    # print(os.getcwd(), commit, update)
    genv['_VERSION'][comp] = (auther, ver, commit, update)

def buildComponent(genv, env, deps, components, staticlibs, sharedlibs, friends=[]):
    if genv['_PARSE'] is True:
        parseDependency(genv, env, deps, components,
                        staticlibs, sharedlibs, friends)
        return

    tmp = os.path.split(os.getcwd())[0]
    tmp = os.path.split(tmp)[0]
    packageName = os.path.split(tmp)[1]
    componentName = os.path.split(os.getcwd())[1]
    compFullName = "%s.%s" % (packageName, componentName)
    if compFullName in genv['_COMP_2RD_PARSED']:  # 第二遍扫描过的component，不再扫描
        return
    genv['_COMP_2RD_PARSED'].add(compFullName)

    deps, components, staticlibs, sharedlibs = extractProjectDependencies(
        genv, deps, components, staticlibs, sharedlibs)

    if "WHOLE_ARCHIVE" in env and env["WHOLE_ARCHIVE"]:
        genv["_WHOLE_ARCHIVE_LIST"].add(compFullName)

    rootPath = genv['ROOT']
    for comp in components:
        if comp in genv['_COMP_2RD_PARSED']:  # 第二遍扫描过的component，不再扫描
            continue
        # genv['_COMP_2RD_PARSED'].add(comp)
        tmp = comp.split(".")
        compPackage = tmp[0]
        compName = tmp[-1]
        if os.path.exists("%s/packages/%s/components/%s/SConscript" % (rootPath, compPackage, compName)):
            
            SConscript("%s/packages/%s/components/%s/SConscript" %
                       (rootPath, compPackage, compName), exports='genv')
        else:
            print("\033[1;33m%s.%s: component %s doesn't exist due to path %s/packages/%s/components/%s/SConscript missing! \033[0m" %
                  (packageName, componentName, comp, rootPath, compPackage, compName))

    env, target, sources = createEnvForBuild(genv, env, genv['COMP_DEPS'][compFullName],
                                             genv['COMP_COMP'][compFullName],
                                             genv['COMP_SLIBS'][compFullName],
                                             genv['COMP_DLIBS'][compFullName])

    if len(sources) == 0:
        return
    output = env.StaticLibrary(target=target, source=sources)
    # if genv['_BUILD_SHARED'] is True:
    #     output1 = env.SharedLibrary(target=target, source=sources)
    for comp in components:
        tmp = comp.split(".")
        compPackage = tmp[0]
        compName = tmp[-1]
        compLibName = compName
        if genv['WINDOWS']:
            compLibName = compLibName + "_win"
        filName = '%s/packages/%s/components/%s/lib%s_d.a' % (
            rootPath, compPackage, compName, compLibName)
        if GetOption('release'):
            filName = '%s/packages/%s/components/%s/lib%s.a' % (
                rootPath, compPackage, compName, compLibName)
        _staticlib = File(filName)
        genv.Depends(output, _staticlib)
        # if genv['_BUILD_SHARED'] is True:
        #     filName2 = '%s/packages/%s/components/%s/lib%s_d.so' % (
        #         rootPath, compPackage, compName, compLibName)
        #     if GetOption('release'):
        #         filName2 = '%s/packages/%s/components/%s/lib%s.so' % (
        #             rootPath, compPackage, compName, compLibName)
        #     _sharedlib = File(filName2)
        #     genv.Depends(output1, _sharedlib)

def generate_ver_file(genv, projFullName, components):
    packageName, projectName = projFullName.split(".")[0:2]
    versions = []
    for c in components:
        if c in genv['_VERSION']:
            versions.append((c, genv['_VERSION'][c]))
        else:
            versions.append((c, ("no_auther", "no_version", "no_commit", "no_update")))
    version_strs = ["{\"%s\", {\"%s\", \"%s\", \"%s\", \"%s\"}}"%(c, v[0], v[1], v[2], v[3]) for c, v in versions]
    version_str = ",\n".join(version_strs)
    rootPath = genv['ROOT']
    # outputPath = '%s/packages/%s/projects/%s/src/_version_.cpp' % (
    #     rootPath, packageName, projectName)
    outputPath = 'src/_version_.cpp'
    myver = genv['_VERSION'][projFullName]
    with open(outputPath,"w") as f:
        f.write("/* Auto Generated by Gourd Build System */" + "\n")
        f.write("#include <map>" + "\n")
        f.write("#include <string>" + "\n")
        f.write("#include <tuple>" + "\n")
        f.write("std::pair<std::string, std::tuple<std::string, std::string, std::string, std::string>> get_my_version();" + "\n")
        f.write("std::pair<std::string, std::tuple<std::string, std::string, std::string, std::string>> get_my_version(){" + "\n")
        f.write("std::pair<std::string, std::tuple<std::string, std::string, std::string, std::string>> ver = " + "\n")
        f.write("{\"%s\", {\"%s\", \"%s\", \"%s\", \"%s\"}};"%(projFullName, myver[0], myver[1], myver[2], myver[3]) + "\n")
        f.write("return std::move(ver);}" + "\n")
        f.write("" + "\n")
        f.write("std::map<std::string, std::tuple<std::string, std::string, std::string, std::string>> get_components_version();" + "\n")
        f.write("std::map<std::string, std::tuple<std::string, std::string, std::string, std::string>> get_components_version(){" + "\n")
        f.write("std::map<std::string, std::tuple<std::string, std::string, std::string, std::string>> ver = {" + "\n")
        f.write("%s"%version_str + "\n")
        f.write("};return std::move(ver);}" + "\n")

def buildProject(genv, env, deps, components, staticlibs, sharedlibs, friends=[], buildSharedLib = False):
    if genv['_PARSE'] is True:
        parseDependency(genv, env, deps, components,
                        staticlibs, sharedlibs, friends)
        return
    cwd = os.getcwd()

    tmp = os.path.split(cwd)[0]
    tmp = os.path.split(tmp)[0]
    packageName = os.path.split(tmp)[1]
    projectName = os.path.split(cwd)[1]
    projFullName = "%s.%s" % (packageName, projectName)
    rootPath = genv['ROOT']
    winSuffix = ""

    ver = "no_ver"
    if "VERSION" in env: ver = env["VERSION"]
    auther = "no_auther"
    if "AUTHER" in env: auther = env["AUTHER"]
    try:
        from git import get_git_commit, get_git_update
        commit = get_git_commit(cwd)
        update = get_git_update(cwd)
    except:
        commit = "no_commit"
        update = "no_update"
        pass
    genv['_VERSION'][projFullName] = (auther, ver, commit, update)

    if genv['WINDOWS']:
        winSuffix = "_win"
    outputFolder = '%s/output/%s/%s/debug%s' % (
        rootPath, packageName, projFullName, winSuffix)
    if GetOption('release'):
        outputFolder = '%s/output/%s/%s/release%s' % (
            rootPath, packageName, projFullName, winSuffix)

    print("solving dependency..")
    deps, components, staticlibs, sharedlibs = extractProjectDependencies(
        genv, deps, components, staticlibs, sharedlibs)

    generate_ver_file(genv, projFullName, components)
    print("parsing depended components..")
    for comp in components:
        if comp in genv['_COMP_2RD_PARSED']:  # 第二遍扫描过的component，不再扫描
            continue
        tmp = comp.split(".")
        compPackage = tmp[0]
        compName = tmp[-1]

        # print("  parsing %s.%s" %(compPackage, compName))
        if os.path.exists("%s/packages/%s/components/%s/SConscript" % (rootPath, compPackage, compName)):
            SConscript("%s/packages/%s/components/%s/SConscript" %
                       (rootPath, compPackage, compName), exports='genv')
        else:
            print("\033[1;33m%s.%s: component %s doesn't exist due to path %s/packages/%s/components/%s/SConscript missing! \033[0m" %
                  (packageName, projectName, comp, rootPath, compPackage, compName))

    env, target, sources = createEnvForBuild(
        genv, env, deps, components, staticlibs, sharedlibs, outputFolder)
    if len(sources) == 0:
        return

    if buildSharedLib:
        output = env.SharedLibrary(target=target, source=sources)
    else:
        if genv['WINDOWS']:    
            output = env.Program(target=target + ".exe", source=sources)
        else:
            output = env.Program(target=target + ".bin", source=sources)

    
    def install_for_mingw(target):
        for root, dirnames, filenames in os.walk("/usr/x86_64-w64-mingw32/sys-root/mingw/bin"):
            for filename in filenames:
                s = os.path.join(root, filename)
                env.Install(target, s)
    
    if GetOption('mingw64'):
        install_for_mingw(outputFolder)

    def recursive_install(target, source, env):
        source_dirname = os.path.dirname(source)
        installed = []
        for root, dirnames, filenames in os.walk(source):
            for filename in filenames:
                if filename.split(".")[-1] == "a":  # .a 文件不拷贝
                    continue
                t = os.path.join(
                    target, os.path.relpath(root, os.path.dirname(source)))
                s = os.path.join(root, filename)
                if os.path.islink(s):   # link不拷贝
                    continue
                install = env.Install(t, s)
                installed.append(install)
        return installed

    # install Dlib In Deps
    for dep in deps:
        if dep == "":
            continue
        depAbsPath = fileOps.getDepPath(rootPath, dep)
        depLibAbsPath = depAbsPath + "/lib/"
        installed = recursive_install(outputFolder, depLibAbsPath, genv)
        ''' 安装过的文件在genv中注册一下。当这个文件被多个模块依赖的时候，如果没有这一部，scons会有warn, dupliated xxx '''
        for install in installed:
            genv.Depends(output, install)

        '''
        _libfiles, fileNames = fileOps.getSlibListInDepLibFolder(rootPath, dep)
        for i in range(0, len(fileNames)):
            depSplit = dep.split(".", 1)
            if len(depSplit) == 1:
                env.Append(LIBPATH=['%s/deps/%s/lib' % (rootPath, dep)])
            else:
                depPackage = depSplit[0]
                depName = depSplit[1]
                fileNode = File('%s/packages/%s/deps/%s/lib/%s' %
                                (rootPath, depPackage, depName, fileNames[i]))

            tmpOutput = None
            tmpOutput = genv.Install(outputFolder, fileNode)
            genv.Depends(output, tmpOutput)
        '''

    for comp in components:
        tmp = comp.split(".")
        compPackage = tmp[0]
        compName = tmp[-1]
        compLibName = compName
        if genv['WINDOWS']:
            compLibName = compLibName + "_win"
        filName = '%s/packages/%s/components/%s/lib%s_d.a' % (
            rootPath, compPackage, compName, compLibName)
        if GetOption('release'):
            filName = '%s/packages/%s/components/%s/lib%s.a' % (
                rootPath, compPackage, compName, compLibName)
        _staticlib = File(filName)
        genv.Depends(output, _staticlib)

    env.Install(outputFolder, output)

def buildShared(genv, env, deps, components, staticlibs, sharedlibs, friends=[]):
    buildProject(genv, env, deps, components, staticlibs, sharedlibs, friends=friends, buildSharedLib = True)

def getDepComponentRecusive(compName, compMap):
    ret = []
    if compName not in compMap:
        return ret
    for comp in compMap[compName]:
        ret.append(comp)
        ret.extend(getDepComponentRecusive(comp, compMap))
    return ret

def extractProjectDependencies(genv, deps, components, staticlibs, sharedlibs):
    newdeps = copy.copy(deps)
    newcomps = copy.copy(components)
    newslibs = copy.copy(staticlibs)
    newdlibs = copy.copy(sharedlibs)
    for comp in components:
        if comp in genv['COMP_COMP']:
            newcomps.extend(genv['COMP_COMP'][comp])
        if comp in genv['COMP_DEPS']:
            newdeps.extend(genv['COMP_DEPS'][comp])
        if comp in genv['COMP_SLIBS']:
            newslibs.extend(genv['COMP_SLIBS'][comp])
        if comp in genv['COMP_DLIBS']:
            newdlibs.extend(genv['COMP_DLIBS'][comp])
    newdeps = _remove_duplicates(newdeps)
    newcomps = _remove_duplicates(newcomps)
    newslibs = _remove_duplicates(newslibs)
    newdlibs = _remove_duplicates(newdlibs)
    return newdeps, newcomps, newslibs, newdlibs

def solveComponentsDependencies(compMap, depMap, slibMap, dlibMap):
    newCompMap = {}
    for comp in compMap:
        newCompMap[comp] = getDepComponentRecusive(comp, compMap)
        newCompMap[comp] = _remove_duplicates(newCompMap[comp])
    # print()
    # print(newCompMap)

    newDepMap = {}
    for comp in newCompMap:
        newDepMap[comp] = copy.copy(depMap[comp])
        for compDep in newCompMap[comp]:
            if compDep in depMap:
                newDepMap[comp].extend(depMap[compDep])
        newDepMap[comp] = _remove_duplicates(newDepMap[comp])
    # print()
    # print(newDepMap)

    newslibMap = {}
    for comp in newCompMap:
        newslibMap[comp] = copy.copy(slibMap[comp])
        for compDep in newCompMap[comp]:
            if compDep in slibMap:
                newslibMap[comp].extend(slibMap[compDep])
        newslibMap[comp] = _remove_duplicates(newslibMap[comp])
    # print()
    # print(newslibMap)

    newdlibMap = {}
    for comp in newCompMap:
        newdlibMap[comp] = copy.copy(dlibMap[comp])
        for compDep in newCompMap[comp]:
            if compDep in dlibMap:
                newdlibMap[comp].extend(dlibMap[compDep])
        newdlibMap[comp] = _remove_duplicates(newdlibMap[comp])
    # print()
    # print(newdlibMap)

    return newCompMap, newDepMap, newslibMap, newdlibMap
