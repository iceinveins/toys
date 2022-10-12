# -*- coding: utf-8 -*-
from SCons.Script import *

def build(genv):
    if GetOption('project') is not None:
        project = GetOption('project')
        if project in genv['all_projs']:
            print("start to build project %s"%project)
            package, projName = project.split(".")
            SConscript('%s/packages/%s/projects/%s/SConscript'%(genv['ROOT'], package, projName), exports='genv')
        else:
            print("\033[1;33mNo project named %s\033[0m"%project)
    elif GetOption('component') is not None:
        component=GetOption('component')
        print("start to build component %s"%component)
        # if GetOption('cs'):
        #     print("build shared lib as well as static lib")
        #     genv['_BUILD_SHARED']=True
        # else:
        #     print("build static lib as only")
        if component in genv['all_comps']:
            package, componentName = component.split(".")
            SConscript('%s/packages/%s/components/%s/SConscript'%(genv['ROOT'], package, componentName), exports='genv')
        else:
            print("\033[1;33mNo component named %s\033[0m"%component)
    elif GetOption('ac'):
        ## build all components
        print("build all components and leave projects there")
        for comp in genv['all_comps']:
            package, compName = comp.split(".") 
            SConscript('%s/packages/%s/components/%s/SConscript'%(genv['ROOT'], package, compName), exports='genv')
    elif GetOption('ac_with_proj'):
        print("build all components and projects specified by the input project list file")
        for comp in genv['all_comps']:
            package, compName = comp.split(".") 
            SConscript('%s/packages/%s/components/%s/SConscript'%(genv['ROOT'], package, compName), exports='genv')
        if os.path.exists(GetOption('ac_with_proj')):
            import json
            plists = json.load(open(GetOption('ac_with_proj'), "r"))
            for package in plists:
                plist = plists[package]
                for p in plist:
                    print("build extra project {}.{} by ac_with_proj option".format(package, p))
                    SConscript('%s/packages/%s/projects/%s/SConscript'%(genv['ROOT'], package, p), exports='genv')        
    elif GetOption('a'):
        print("build all components and projects")
        ## build all components and projects
        for comp in genv['all_comps']:
            package, compName = comp.split(".")
            SConscript('%s/packages/%s/components/%s/SConscript'%(genv['ROOT'], package, compName), exports='genv')
        for project in genv['all_projs']:
            package, projName = project.split(".")
            SConscript('%s/packages/%s/projects/%s/SConscript'%(genv['ROOT'], package, projName), exports='genv')        
    else:
        print("\033[1;33mDo nothing\033[0m")