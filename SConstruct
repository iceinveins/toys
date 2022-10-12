# -*- coding: utf-8 -*-
from datetime import datetime
from toolchain import initCppToolChain
from buildOption import initBuildOption
from build import build

AddOption('--ext',
            dest='ext',
            type='string',
            nargs=1,
            action='store',
            metavar='GOURD_BASE_FOLDER',
            help='external gourd build')

if GetOption('ext') is None:
    root = Dir('#').abspath
else:
    root = ext
    sys.path.append('%s/site_scons'%root)

import filesOps as fileOps
import buildhelper as bhelper
import packhelper as phelper

initBuildOption()
pack=GetOption('pack')

########### global envrioment  ############################################
genv = Environment()
Export({"genv":genv})
genv['ROOT'] = root
genv['WINDOWS'] = False

print("initializing toolchain..")
initCppToolChain(genv)

################## global variables used for build system #################
genv['GOURD_VER'] = 2
genv['COMP_COMP'] = {}
genv['COMP_DEPS'] = {}
genv['COMP_SLIBS'] = {}
genv['COMP_DLIBS'] = {}
genv['COMP_FRIENDS'] = {}
genv['COMP_ENV_FLAG'] = []  # 扫描过的模块放到这个list里面，避免再次被扫描
genv['_COMP_2RD_PARSED'] = set()    # 记录second phase中已经parse过的components，避免重复遍历
genv['_VERSION'] = {}   # 各component和project的版本信息 name -> (version, auther)

########################### first phase, parse dependency #################
#### project and component name are in the same namespace.
genv['_PARSE']=True
genv['all_comps']=fileOps.loadAllComponents(genv['ROOT'])
genv['all_projs']=fileOps.loadAllProjects(genv['ROOT'])

print("parsing all components for preparation..")
# import thread
# from concurrent.futures import ThreadPoolExecutor
# from concurrent.futures import wait

# with ThreadPoolExecutor(max_workers=GetOption("num_jobs")) as pool:
#     futures = []
#     for comp in genv['all_comps']:
#         package, compName = comp.split(".")
#         futures.append(pool.submit(SConscript, ('%s/packages/%s/components/%s/SConscript'%(genv['ROOT'], package, compName)), {"exports": 'genv'}))
#     wait(futures)

for comp in genv['all_comps']:
    package, compName = comp.split(".")
    SConscript('%s/packages/%s/components/%s/SConscript'%(genv['ROOT'], package, compName), exports='genv')

if GetOption('a'):
    print("parsing all projects for preparation..")
    # no need to parse all project unless build all with "--a"
    for proj in genv['all_projs']:
        package, projName = proj.split(".")
        SConscript('%s/packages/%s/projects/%s/SConscript'%(genv['ROOT'], package, projName), exports='genv')

### dep_search_c
if GetOption("dep_search_c"):
    print("compoment {} is directly depended by ".format(GetOption("dep_search_c")))
    for a in genv['COMP_COMP']:
        if GetOption("dep_search_c") in genv['COMP_COMP'][a]:
            print(" {}".format(a))
    exit(0)
### dep_search_d
if GetOption("dep_search_d"):
    print("3rdparty dep {} is directly depended by ".format(GetOption("dep_search_d")))
    for a in genv['COMP_DEPS']:
        if GetOption("dep_search_d") in genv['COMP_DEPS'][a]:
            print(" {}".format(a))
    exit(0)

genv['COMP_COMP'], genv['COMP_DEPS'], genv['COMP_SLIBS'], genv['COMP_DLIBS'] = bhelper.solveComponentsDependencies(genv['COMP_COMP'], genv['COMP_DEPS'], genv['COMP_SLIBS'], genv['COMP_DLIBS'])

########### pack build ####################################################
if pack is not None:
    packTimestampStr = ""
    if GetOption('verstr') != "UNKNOWN":
        packTimestampStr = GetOption('verstr')
    else:
        packTimestampStr = datetime.now().strftime("%Y_%m_%d_%H.%M.%S")
    phelper.pack(genv, pack, packTimestampStr)
    exit(0)
### vscode config
if GetOption("vscode_config"):
    from vscode import gen_vscode_c_cpp_properties
    gen_vscode_c_cpp_properties(genv)
    exit(0)
########################### second phase, build ###########################
genv['_PARSE']=False
# genv['_BUILD_SHARED']=False

# https://gamedev.stackexchange.com/questions/37813/variables-in-static-library-are-never-initialized-why
genv['_WHOLE_ARCHIVE_LIST'] = set() # 记录需要WHOLE_ARCHIVE的模块
build(genv)