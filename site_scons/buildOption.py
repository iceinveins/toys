# -*- coding: utf-8 -*-
from SCons.Script import *

def initBuildOption():
    ########### compile options  ##############################################
    AddOption(
        '--release',
        action='store_true',
        help='enable release build',
        default=False)
    AddOption(
        '--printver',
        action='store_true',
        help='enable version def',
        default=False)
    AddOption(
        '--optInfo',
        action='store_true',
        help='ask compile to print optimization info',
        default=False)
    AddOption('--verstr',
        dest='verstr',
        type='string',
        nargs=1,
        action='store',
        metavar='VERSION STRING',
        default="UNKNOWN",
        help='specify version string from cmdline like `date +%Y/%m/%d_%H:%M:%S`')
    AddOption(
        '--icc',
        action='store_true',
        help='use intel compiler',
        default=False)
    AddOption(
        '--gcc6',
        action='store_true',
        help='use gcc6 instead of default gcc10',
        default=False)
    AddOption(
        '--gcc8',
        action='store_true',
        help='use gcc8 instead of default gcc10',
        default=False)
    AddOption(
        '--gcc10',
        action='store_true',
        help='use gcc10 instead of default gcc10',
        default=False)
    AddOption(
        '--mingw64',
        action='store_true',
        help='use mingw64 instead of default gcc10 for windows build',
        default=False)
    AddOption(
        '--compatible',
        action='store_true',
        help='use safest compile flags, disable avx2 which is enabled by default',
        default=False)
    AddOption(
        '--g',
        action='store_true',
        help='enable debug info',
        default=False)
    AddOption(
        '--commitinfo',
        action='store_true',
        help='refresh git commit info',
        default=False)
    AddOption('--arch',
        dest='arch',
        type='string',
        nargs=1,
        action='store',
        metavar='CPU_TYPE',
        default="native",
        help='specify arch for -march')
    AddOption('--tune',
        dest='tune',
        type='string',
        nargs=1,
        action='store',
        metavar='CPU_TYPE',
        default="native",
        help='specify arch for -tune')
    AddOption(
        '--asan',
        action='store_true',
        help='enable address sanitizer',
        default=False)
    AddOption(
        '--lsan',
        action='store_true',
        help='enable leak sanitizer',
        default=False)
    AddOption(
        '--tsan',
        action='store_true',
        help='enable thread sanitizer',
        default=False)
    AddOption(
        '--ubsan',
        action='store_true',
        help='enable undefined behavior sanitizer',
        default=False)
    AddOption(
        '--nolto',
        action='store_true',
        help='disable link time optimizer (add -flto). release mode only',
        default=False)
    AddOption('--ccflags',
        dest='ccflags',
        type='string',
        nargs=1,
        action='store',
        metavar='CC_FLAGS',
        default="",
        help='extra ccflags')
    AddOption('--ldflags',
        dest='ldflags',
        type='string',
        nargs=1,
        action='store',
        metavar='LD_FLAGS',
        default="",
        help='extra ldflags')
    AddOption('--dep_search_c',
        dest='dep_search_c',
        type='string',
        nargs=1,
        action='store',
        default="",
        help='search which components directly depends the specified component')
    AddOption('--dep_search_d',
        dest='dep_search_d',
        type='string',
        nargs=1,
        action='store',
        default="",
        help='search which components directly depends the specified 3rd party dependency')
    AddOption(
            '--a',
            action='store_true',
            help='build all components and projects',
            default=False)
    AddOption(
            '--ac',
            action='store_true',
            help='build all components',
            default=False)
    AddOption('--ac_with_proj',
                    dest='ac_with_proj',
                    type='string',
                    nargs=1,
                    action='store',
                    help='extra projects build list file for --ac mode')
    AddOption('--p',
                    dest='project',
                    type='string',
                    nargs=1,
                    action='store',
                    metavar='PACKAGE.PROJECT',
                    help='build specified project')
    AddOption('--c',
                    dest='component',
                    type='string',
                    nargs=1,
                    action='store',
                    metavar='PACKAGE.COMPONENT',
                    help='build specified component (static lib only)')
    # AddOption(
    #         '--cs',
    #         action='store_true',
    #         help='build shared lib for component specified by --c option',
    #         default=False)
    AddOption('--pack',
                    dest='pack',
                    type='string',
                    nargs=1,
                    action='store',
                    metavar='PACK_CONFIG',
                    help='pack package')
    AddOption(
            '--vscode_config',
            action='store_true',
            help='generate vscode c_cpp_properity file to config include path',
            default=False)
