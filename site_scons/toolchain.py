# -*- coding: utf-8 -*-
from SCons.Script import *
import socket
from cpuinfo import get_cpu_info
import os
import sys
import subprocess
from datetime import datetime

def initCppToolChain(genv):
    ########### use different toolchain on centos #############################
    os_release = "Windows"
    if os.path.exists("/etc/os-release"):
        os_release = subprocess.Popen(['cat /etc/os-release | grep ^NAME'],stdout=subprocess.PIPE,shell=True).communicate()[0].strip()
    print(" OS: {}".format(os_release))
    genv.Append(CPPPATH=['%s/sys/include'%genv['ROOT']])
    genv.Append(LIBPATH=['%s/sys/lib'%genv['ROOT']])
    toolchain = "gcc10"
    if "CentOS" in str(os_release) or "Red Hat" in str(os_release):
        if GetOption('icc'):
            print("\033[1;33micc is not supported yet\033[0m")
            toolchain = "icc"
            exit(0)
        elif GetOption('gcc8'):
            genv.Replace(CXX="/opt/rh/devtoolset-8/root/usr/bin/g++")
            genv.Replace(CC="/opt/rh/devtoolset-8/root/usr/bin/gcc")
            genv.Replace(AR="/opt/rh/devtoolset-8/root/usr/bin/gcc-ar")
            genv.Replace(RANLIB="/opt/rh/devtoolset-8/root/usr/bin/gcc-ranlib")
            genv.Append(CPPPATH=['%s/sys/centos/include'%genv['ROOT']])
            genv.Append(LIBPATH=['%s/sys/centos/lib'%genv['ROOT']])
            toolchain = "gcc8"
        elif GetOption('gcc10'):
            genv.Replace(CXX="/opt/rh/devtoolset-10/root/usr/bin/g++")
            genv.Replace(CC="/opt/rh/devtoolset-10/root/usr/bin/gcc")
            genv.Replace(AR="/opt/rh/devtoolset-10/root/usr/bin/gcc-ar")
            genv.Replace(RANLIB="/opt/rh/devtoolset-10/root/usr/bin/gcc-ranlib")
            genv.Append(CPPPATH=['%s/sys/centos/include'%genv['ROOT']])
            genv.Append(LIBPATH=['%s/sys/centos/lib'%genv['ROOT']])
            toolchain = "gcc10"
        elif GetOption('gcc6'):
            genv.Replace(CXX="/opt/rh/devtoolset-6/root/usr/bin/g++")
            genv.Replace(CC="/opt/rh/devtoolset-6/root/usr/bin/gcc")
            genv.Replace(AR="/opt/rh/devtoolset-6/root/usr/bin/gcc-ar")
            genv.Replace(RANLIB="/opt/rh/devtoolset-6/root/usr/bin/gcc-ranlib")
            genv.Append(CPPPATH=['%s/sys/centos/include'%genv['ROOT']])
            genv.Append(LIBPATH=['%s/sys/centos/lib'%genv['ROOT']])
            toolchain = "gcc6"
        elif GetOption('mingw64'):
            genv.Replace(CXX="x86_64-w64-mingw32-c++")
            genv.Replace(CC="x86_64-w64-mingw32-gcc")
            genv.Replace(AR="x86_64-w64-mingw32-gcc-ar")
            genv.Replace(RANLIB="x86_64-w64-mingw32-gcc-ranlib")
            genv.Append(CPPPATH=['%s/sys/mingw64/include'%genv['ROOT']])
            genv.Append(LIBPATH=['%s/sys/mingw64/lib'%genv['ROOT']])
            genv['WINDOWS'] = True
            toolchain = "mingw64"
        else:
            genv.Replace(CXX="/opt/rh/devtoolset-10/root/usr/bin/g++")
            genv.Replace(CC="/opt/rh/devtoolset-10/root/usr/bin/gcc")
            genv.Replace(AR="/opt/rh/devtoolset-10/root/usr/bin/gcc-ar")
            genv.Replace(RANLIB="/opt/rh/devtoolset-10/root/usr/bin/gcc-ranlib")
            genv.Append(CPPPATH=['%s/sys/centos/include'%genv['ROOT']])
            genv.Append(LIBPATH=['%s/sys/centos/lib'%genv['ROOT']])
            toolchain = "gcc10"
    elif "Ubuntu" in str(os_release):
        genv.Replace(CXX='g++')
        genv.Replace(CC='gcc')
        genv.Append(CPPPATH=['%s/sys/ubuntu16/include'%genv['ROOT']])
        genv.Append(LIBPATH=['%s/sys/ubuntu16/lib'%genv['ROOT']])
        genv.Append(LIBPATH=['/usr/lib/x86_64-linux-gnu/'])
        toolchain = "gcc"
    else:
        ## Windows, windows版本的mingw64需要已经安装且已经在环境变量中添加，推荐版本x86_64-4.9.3-posix-seh-rt_v4-rev1，跟centos7上的mingw64版本类似
        genv['WINDOWS'] = True
        genv.Append(CPPPATH=['%s/sys/mingw64/include'%genv['ROOT']])
        genv.Append(LIBPATH=['%s/sys/mingw64/lib'%genv['ROOT']])
        toolchain = "mingw64"
        pass
    print(" Toolchain: {}".format(toolchain))

    genv['ASMLIB'] = False
    for sysLibPath in genv['LIBPATH']:
        if os.path.exists("%s/libaelf64o.a"%sysLibPath):
            genv['ASMLIB'] = True
            
    if GetOption('printver') == False:
        genv['__GOURD_BUILDTIME__'] = "UNKNOWN"
    else:
        if GetOption('verstr') != "UNKNOWN":
            genv['__GOURD_BUILDTIME__'] = GetOption('verstr')
        else:
            genv['__GOURD_BUILDTIME__'] = datetime.now().strftime("%Y_%m_%d_%H.%M.%S")
    genv['__GOURD_HOSTNAME__'] = str(socket.gethostname())
    genv['__GOURD_CPUBRAND__'] = "UNKNOWN"
    genv['__GOURD_CPUFLAGS__'] = []
    for key, value in get_cpu_info().items():
        #print("{0}: {1}".format(key, value))
        if key == "brand_raw":
            cpuBrand = value.replace(" ", "_")
            genv['__GOURD_CPUBRAND__'] = cpuBrand
        elif key == "flags":
            genv['__GOURD_CPUFLAGS__'] = value
    genv.Append(CPPDEFINES="__GOURD2__")
    if GetOption('release'):
        genv.Append(CPPDEFINES=[])
    else:
        genv.Append(CPPDEFINES='__GOURD_DEBUG__')
    genv.Append(CPPDEFINES={'__GOURD_HOSTNAME__': u'\'"%s"\'' % genv['__GOURD_HOSTNAME__'],
                            '__GOURD_BUILDTIME__': u'\'"%s"\''  % genv['__GOURD_BUILDTIME__'],
                            '__GOURD_CPUBRAND__': u'\'"%s"\''  % genv['__GOURD_CPUBRAND__']
                            })
    if toolchain in ["gcc8", "gcc10"]:
        genv.Append(CCFLAGS='-std=c++17 -fPIC')
    else:
        if genv['WINDOWS']:
            genv.Append(CCFLAGS='-std=c++14')
        else:
            genv.Append(CCFLAGS='-std=c++14 -fPIC')
    
    # disabe all avx512 by default 
    genv.Append(CCFLAGS='-mno-avx512f')
    genv.Append(CCFLAGS='-mno-avx512pf')
    genv.Append(CCFLAGS='-mno-avx512er')
    genv.Append(CCFLAGS='-mno-avx512cd')
    genv.Append(CCFLAGS='-mno-avx512vl')
    genv.Append(CCFLAGS='-mno-avx512bw')
    genv.Append(CCFLAGS='-mno-avx512dq')
    genv.Append(CCFLAGS='-mno-avx512ifma')
    genv.Append(CCFLAGS='-mno-avx512vbmi')
    if toolchain in ["gcc8", "gcc10"]:
        genv.Append(CCFLAGS='-mno-avx512vbmi2')
        genv.Append(CCFLAGS='-mno-avx512vpopcntdq')
        genv.Append(CCFLAGS='-mno-avx5124fmaps')
        genv.Append(CCFLAGS='-mno-avx512vnni')
        genv.Append(CCFLAGS='-mno-avx5124vnniw')
    if toolchain == 'gcc10':
        genv.Append(CCFLAGS='-mno-avx512bf16')
        genv.Append(CCFLAGS='-mno-avx512vp2intersect')
    # genv.Append(CCFLAGS='-mno-avx512fp16')

    if GetOption('compatible') == False:
        if "avx2" in genv['__GOURD_CPUFLAGS__']:
            genv.Append(CCFLAGS='-mavx2')

    if GetOption('release'):
        # -fopt-info-vec-optimized: the compiler will log which loops (by line N°) are being vector optimized.
        # -fopt-info-inline-optimized: similar with -fopt-info-vec-optimized
        genv.Append(CCFLAGS='-O3')
        if GetOption('optInfo'):
            genv.Append(CCFLAGS='-fopt-info-vec-optimized -fopt-info-inline-optimized')
        if GetOption('g'):
            '''
            https://stackoverflow.com/questions/40743372/gcc-lto-appears-to-strip-debugging-symbols
            "Combining -flto with -g is currently experimental and expected to produce unexpected results." When you use -flto, the -g will be ignored.
            '''
            genv.Append(CCFLAGS='-g')
        else:
            # https://gcc.gnu.org/onlinedocs/gcc/Optimize-Options.html
            # -flto linktime opt
            if GetOption('asan') == False and GetOption('lsan') == False and GetOption('tsan') == False and GetOption('ubsan') == False and genv['WINDOWS'] == False:
                ## 当sanitizer打开的时候，找不到lto
                if GetOption("nolto") is False:
                    genv.Append(CCFLAGS='-flto')
                pass
        if GetOption('compatible') == False:
            genv.Append(CCFLAGS='-march=%s -mtune=%s' %
                        (GetOption('arch'), GetOption('tune')))
    else:
        genv.Append(CCFLAGS='-g')
        # turn on warnings
        # TODO -Wundef : too many warnings in ctp header files
        # TODO -Wextra : too many warnings in ctp header files
        # TODO -Wshadow
        genv.Append(CCFLAGS='-Wall -Wfloat-equal -Wcast-align -Wwrite-strings -Wlogical-op -Wmissing-declarations -Wredundant-decls  -Woverloaded-virtual')
    if GetOption('asan') == True:
        genv.Append(CCFLAGS=' -fsanitize=address ')
    if GetOption('lsan') == True:
        genv.Append(CCFLAGS=' -fsanitize=leak ')
    if GetOption('tsan') == True:
        genv.Append(CCFLAGS=' -fsanitize=thread ')
    if GetOption('ubsan') == True:
        genv.Append(CCFLAGS=' -fsanitize=undefined ')
    genv.Append(CCFLAGS='%s' % GetOption('ccflags'))
