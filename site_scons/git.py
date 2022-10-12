import os

def shell(cmd):
    result = os.popen(cmd).read()
    return result

def get_git_commit(path):
    return shell("cd {} && git log -n 1 --pretty=format:%h . 2>/dev/null".format(path))

def get_git_update(path):
    return shell("cd {} && git log -n 1 --pretty=format:%ci . 2>/dev/null".format(path))

# get_git_commit("../")
# print(get_git_update("packages/base/components/configManager1"))