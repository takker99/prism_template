# add a new module
import os
import re
import glob
import subprocess
import pathlib
import sys
import argparse

# format:
#  add-module.py {solution_dir} {module_name} --view-name [view_name]
parser = argparse.ArgumentParser()
parser.add_argument(
    "solution_file", help="the solution file which you want to add a new module to")
parser.add_argument("module_name", help="the name of a module you want to add")
parser.add_argument("-v", "--view_name", help="set the view name if you want")
args = parser.parse_args()

solution_file_path = pathlib.Path(args.solution_file).resolve()
template_directory = "template"
template_files = {"proj": "template/Project.csproj", "module": "template/Module.cs",}
target_files = {"proj": f"{args.module_name}.csproj",
                "module": f"{args.module_name}.cs", }

# view/viewmodel の作成が指定されている場合
if args.view_name:
    template_files["view_xaml"] = f"template/VVM/View.xaml"
    template_files["view_cs"] = f"template/VVM/View.xaml.cs"
    template_files["view_model"] = f"template/VVM/ViewModel.cs"
    target_files["view_xaml"] = f"Views/{args.view_name}.xaml"
    target_files["view_cs"] = f"Views/{args.view_name}.xaml.cs"
    target_files["view_model"] = f"ViewModels/{args.view_name}.cs"


# current directory の変更の影響を受けないように、相対パスを絶対パスに変換している。
template_files = {k: pathlib.Path(v).resolve()
                  for k, v in template_files.items()}
target_files = {k: pathlib.Path(os.path.dirname(
    solution_file_path)+f"/{args.module_name}/"+v).resolve() for k, v in target_files.items()}

# template file から file を生成する。


def create_file_from_template(target_file_path: "作成したいファイルへのパス", template_file_path: "型となるファイルへのパス", replace_function: "テンプレートファイル内の文字列を置換するための函数") -> "nothing":
    with open(target_file_path, "w") as result:
        with open(template_file_path) as temp:
            result.write(replace_function(temp.read()))


def check_file(file_path):
    print("Check if {0}...".format(file_path), end="")
    if os.path.isfile(file_path):
        print("found")
    else:
        print("not found")
        raise ValueError(f"No {file_path} exists.")


# 必要なテンプレートファイルが存在するか確認する
# 必要なファイル；
# - Project.csproj
# - Module.cs
# - VVM/MainWindow.xaml
# - VVM/MainWindow.cs.xaml
# - VVM/MainWindow.cs
for key in template_files:
    check_file(template_files[key])

# # .sln ファイルが存在するか調べる。
# print("Check if the sln file exists...", end="")
# # *.sln ファイルがあることを調べる。存在しなかったり複数あったりした場合はエラーになる
# list_sln = glob.glob(solution_dir+"*.sln")
# if len(list_sln) < 1:
#     raise ValueError("No sln file is available.")
# if len(list_sln) > 1:
#     raise ValueError("Could not choose one sln file")

# print("done")
# print(f"The solution file: {list_sln[0]}")

print(f"Add the module \"{args.module_name}\"")

# directory を掘る
module_path = os.path.dirname(solution_file_path)+"/"+args.module_name
os.makedirs(module_path, exist_ok=True)
os.chdir(module_path)
if args.view_name:
    os.makedirs("Views", exist_ok=True)
    os.makedirs("ViewModels", exist_ok=True)

# module files のデータを用意する
for key in template_files:
    create_file_from_template(target_files[key], template_files[key],
                              lambda file_text: file_text.replace("NAMESPACE", args.module_name).replace(
                                  "CLASS", args.view_name if args.view_name else "CLASS" ).replace("TOPTAG", "UserControl"))


print("Created these files:")
for key in target_files:
    print(f"\t{target_files[key]}")

# dotnet の設定を行う
subprocess.check_call(["dotnet.exe", "add", "package", "Prism.Unity"])
print("add {0} to {1}...".format(target_files["proj"], solution_file_path))
# subprocess.check_call(
#     ["dotnet.exe", "sln", solution_file_path, "add", "project", target_files["proj"]])
# print("Success.")

print("Successfully finished!")

#   {args.module_name}/
#   ├{args.module_name}.csproj
#   ├{args.module_name}.cs
#   ├Views/
#   │├{args.view_name}.xaml
#   │└{args.view_name}.xaml.cs
#   └ViewModels/
#     └{args.view_name}.cs
