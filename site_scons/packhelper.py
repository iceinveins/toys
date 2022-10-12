from SCons.Script import *
import json
import os, shutil
import time, datetime
import glob
from filesOps import listFolders

TMP_PACK_FOLDER="output_pack/.tmp"

def _remove_duplicates(seq):
    seq.reverse()
    seen = set()
    seen_add = seen.add
    ret = [x for x in seq if not (x in seen or seen_add(x))]
    return ret[::-1]

def preparePack():
    if os.path.exists(TMP_PACK_FOLDER):
        shutil.rmtree(TMP_PACK_FOLDER)
    os.makedirs(TMP_PACK_FOLDER)
    shutil.copyfile("SConstruct", "%s/SConstruct"%TMP_PACK_FOLDER)
    os.makedirs("%s/site_scons"%TMP_PACK_FOLDER)

    for file in glob.glob(r'site_scons/*.py'):
        shutil.copy(file, "%s/site_scons/"%TMP_PACK_FOLDER)
    # shutil.copyfile("site_scons/buildhelper.py", "%s/site_scons/buildhelper.py"%TMP_PACK_FOLDER)
    # shutil.copyfile("site_scons/filesOps.py", "%s/site_scons/filesOps.py"%TMP_PACK_FOLDER)
    # shutil.copyfile("site_scons/packhelper.py", "%s/site_scons/packhelper.py"%TMP_PACK_FOLDER)
    shutil.copytree("site_scons/cpuinfo", "%s/site_scons/cpuinfo"%TMP_PACK_FOLDER)
    os.makedirs("%s/scripts"%TMP_PACK_FOLDER)
    shutil.copytree("scripts/gourd_sh", 
                        "%s/scripts/gourd_sh"%(TMP_PACK_FOLDER))

def copyPackage(genv, packageCfg):
    package = packageCfg["name"]
    deps = listFolders("packages/%s/deps/"%(package))
    deps = ["{}.{}".format(package, d) for d in deps]
    os.makedirs("%s/packages/%s"%(TMP_PACK_FOLDER, package))

    if "binary" in packageCfg:
        if "components" in packageCfg["binary"]:
            components = packageCfg["binary"]["components"]
            comp_exists = listFolders("packages/%s/components/"%(package))
            for comp in comp_exists:
                if comp not in components:
                    components.append(comp)
            for component in components:
                if os.path.exists("packages/%s/components/%s/SConscript"%(package, component)):
                    os.makedirs("%s/packages/%s/components/%s"%(TMP_PACK_FOLDER, package, component))
                    shutil.copyfile("packages/%s/components/%s/SConscript"%(package, component), 
                        "%s/packages/%s/components/%s/SConscript"%(TMP_PACK_FOLDER, package, component))
                    try:
                        shutil.copyfile("packages/%s/components/%s/_commit_.json"%(package, component), 
                            "%s/packages/%s/components/%s/_commit_.json"%(TMP_PACK_FOLDER, package, component))
                    except:
                        pass
                    if os.path.exists("packages/%s/components/%s/inc"%(package, component)):
                        shutil.copytree("packages/%s/components/%s/inc"%(package, component), 
                        "%s/packages/%s/components/%s/inc"%(TMP_PACK_FOLDER, package, component))
                    if os.path.exists("packages/%s/components/%s/lib%s.a"%(package, component, component)):
                        shutil.copyfile("packages/%s/components/%s/lib%s.a"%(package, component, component), 
                        "%s/packages/%s/components/%s/lib%s.a"%(TMP_PACK_FOLDER, package, component, component))
                    if os.path.exists("packages/%s/components/%s/lib%s_d.a"%(package, component, component)):
                        shutil.copyfile("packages/%s/components/%s/lib%s_d.a"%(package, component, component), 
                        "%s/packages/%s/components/%s/lib%s_d.a"%(TMP_PACK_FOLDER, package, component, component))
                    if os.path.exists("packages/%s/components/%s/lib%s_win.a"%(package, component, component)):
                        shutil.copyfile("packages/%s/components/%s/lib%s_win.a"%(package, component, component), 
                        "%s/packages/%s/components/%s/lib%s_win.a"%(TMP_PACK_FOLDER, package, component, component))
                    if os.path.exists("packages/%s/components/%s/lib%s_win_d.a"%(package, component, component)):
                        shutil.copyfile("packages/%s/components/%s/lib%s_win_d.a"%(package, component, component), 
                        "%s/packages/%s/components/%s/lib%s_win_d.a"%(TMP_PACK_FOLDER, package, component, component))
                    if os.path.exists("packages/%s/components/%s/lib%s.so"%(package, component, component)):
                        shutil.copyfile("packages/%s/components/%s/lib%s.so"%(package, component, component), 
                        "%s/packages/%s/components/%s/lib%s.so"%(TMP_PACK_FOLDER, package, component, component))
                    if os.path.exists("packages/%s/components/%s/lib%s_d.so"%(package, component, component)):
                        shutil.copyfile("packages/%s/components/%s/lib%s_d.so"%(package, component, component), 
                        "%s/packages/%s/components/%s/lib%s_d.so"%(TMP_PACK_FOLDER, package, component, component))
                    if os.path.exists("packages/%s/components/%s/lib%s_win.so"%(package, component, component)):
                        shutil.copyfile("packages/%s/components/%s/lib%s_win.so"%(package, component, component), 
                        "%s/packages/%s/components/%s/lib%s_win.so"%(TMP_PACK_FOLDER, package, component, component))
                    if os.path.exists("packages/%s/components/%s/lib%s_win_d.so"%(package, component, component)):
                        shutil.copyfile("packages/%s/components/%s/lib%s_win_d.so"%(package, component, component), 
                        "%s/packages/%s/components/%s/lib%s_win_d.so"%(TMP_PACK_FOLDER, package, component, component))
                    compFullName = "%s.%s"%(package, component)
                    # deps.extend(genv['COMP_DEPS'][compFullName])

    if "src" in packageCfg:
        if "components" in packageCfg["src"]:
            components = packageCfg["src"]["components"]
            for component in components:
                if os.path.exists("packages/%s/components/%s/SConscript"%(package, component)):
                    if os.path.exists("%s/packages/%s/components/%s"%(TMP_PACK_FOLDER, package, component)) == False :
                        os.makedirs("%s/packages/%s/components/%s"%(TMP_PACK_FOLDER, package, component))
                    shutil.copyfile("packages/%s/components/%s/SConscript"%(package, component), 
                        "%s/packages/%s/components/%s/SConscript"%(TMP_PACK_FOLDER, package, component))
                    if os.path.exists("packages/%s/components/%s/inc"%(package, component)):
                        if os.path.exists("%s/packages/%s/components/%s/inc"%(TMP_PACK_FOLDER, package, component)) == False :
                            shutil.copytree("packages/%s/components/%s/inc"%(package, component), 
                            "%s/packages/%s/components/%s/inc"%(TMP_PACK_FOLDER, package, component))
                    if os.path.exists("packages/%s/components/%s/inc_protected"%(package, component)):
                        shutil.copytree("packages/%s/components/%s/inc_protected"%(package, component), 
                        "%s/packages/%s/components/%s/inc_protected"%(TMP_PACK_FOLDER, package, component))
                    if os.path.exists("packages/%s/components/%s/src"%(package, component)):
                        shutil.copytree("packages/%s/components/%s/src"%(package, component), 
                        "%s/packages/%s/components/%s/src"%(TMP_PACK_FOLDER, package, component))
                    compFullName = "%s.%s"%(package, component)
                    # deps.extend(genv['COMP_DEPS'][compFullName])

        if "projects" in packageCfg["src"]:
            projects = packageCfg["src"]["projects"]
            for project in projects:
                if os.path.exists("packages/%s/projects/%s/SConscript"%(package, project)):
                    os.makedirs("%s/packages/%s/projects/%s"%(TMP_PACK_FOLDER, package, project))
                    shutil.copyfile("packages/%s/projects/%s/SConscript"%(package, project), 
                        "%s/packages/%s/projects/%s/SConscript"%(TMP_PACK_FOLDER, package, project))
                    if os.path.exists("packages/%s/projects/%s/inc"%(package, project)):
                        shutil.copytree("packages/%s/projects/%s/inc"%(package, project), 
                        "%s/packages/%s/projects/%s/inc"%(TMP_PACK_FOLDER, package, project))
                    if os.path.exists("packages/%s/projects/%s/src"%(package, project)):
                        shutil.copytree("packages/%s/projects/%s/src"%(package, project), 
                        "%s/packages/%s/projects/%s/src"%(TMP_PACK_FOLDER, package, project))
    return deps

def copyDeps(depList):
    if len(depList) > 0:
        os.makedirs("%s/deps/"%(TMP_PACK_FOLDER))
    for dep in depList:
        if dep != "":
            depSplit = dep.split(".", 1)
            if len(depSplit) == 1:
                # in root/deps
                shutil.copytree("deps/%s"%dep, "%s/deps/%s"%(TMP_PACK_FOLDER, dep))
            else:
                depPackage = depSplit[0]
                depName = depSplit[1]
                shutil.copytree("packages/%s/deps/%s"%(depPackage, depName), "%s/packages/%s/deps/%s"%(TMP_PACK_FOLDER, depPackage, depName))

def copyOutput(genv, outputCfg):
    print(outputCfg)
    for package in outputCfg:
        plist = outputCfg[package]
        for p in plist:
            print("pack extra project {}.{} by ac_with_proj option".format(package, p))
            pfullname = "{}.{}".format(package, p)
            os.makedirs("%s/output/%s"%(TMP_PACK_FOLDER, package))
            if os.path.exists("output/%s/%s/"%(package, pfullname)):
                shutil.copytree("output/%s/%s/"%(package, pfullname), 
                    "%s/output/%s/%s"%(TMP_PACK_FOLDER, package, pfullname))
    pass

def pack(genv, file, timestampStr = ""):
    preparePack()
    f = open(file)
    data = json.load(f)
    packages = data["packages"]
    packagePrefix = data["name"]
    deps = listFolders("deps")
    for packageJson in packages:
        dep = copyPackage(genv, packageJson)
        deps.extend(dep)
    deps = _remove_duplicates(deps)
    print(deps)
    copyDeps(deps)
    outputCfg = data["output"]
    copyOutput(genv, outputCfg)


    now = datetime.datetime.now()
    timestamp=now.strftime("%Y_%m_%d_%H.%M.%S")
    if timestampStr == "":
        packName = "pack_%s_%s"%(packagePrefix, timestamp)
    else:
        packName = "pack_%s_%s"%(packagePrefix, timestampStr)
    os.system("mv output_pack/.tmp output_pack/%s"%(packName))
    os.system("cd output_pack && zip %s.zip %s -ry"%(packName, packName))
    os.system("rm -rf output_pack/%s"%(packName))
    pass