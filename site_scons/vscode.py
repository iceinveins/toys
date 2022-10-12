import os, datetime, json

def backup_vscode_c_cpp_properties():
    if os.path.exists(".vscode/c_cpp_properties.json"):
        os.rename(".vscode/c_cpp_properties.json", ".vscode/c_cpp_properties_{}.json".format(datetime.datetime.now().strftime("%Y_%m_%d_%H.%M.%S")))
    pass

def gen_vscode_c_cpp_properties(genv):
    backup_vscode_c_cpp_properties()
    if "GOURD_MIRROR" in os.environ:
        mirrorPath = "~/.config/gourd/{}/".format(os.environ["GOURD_MIRROR"])
    else:
        mirrorPath = "~/.config/gourd/mirror/"
    
    config = {
            "env":{
                "mirror": mirrorPath
            },
            "configurations": [
                {
                    "name": "Linux",
                    "includePath": [
                        "${default}"
                    ],
                }
            ],
            "version": 4
        }

    # gen_vscode_include_path
    for comp in genv['all_comps']:
        p = comp.split(".")[0]
        c = comp.split(".")[1]
        config["configurations"][0]["includePath"].append("${{mirror}}/packages/{}/components/{}/inc".format(p, c))
    
    if os.path.exists(".vscode") is False:
        os.mkdir(".vscode")
    with open(".vscode/c_cpp_properties.json", "w") as of:
        of.write(json.dumps(config, indent = 4))
    pass