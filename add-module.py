# add a new module
import os
import re
import glob
import subprocess
import pathlib
import sys

# format:
#  add-module.py {solution_dir} {module_name} with-view-viewmodel [view_name]
# .sln ファイルがないdirectoryで実行すると失敗するようにする

if sys.argv[3] != "with-view-viewmodel" and sys.argv[3] != "":
    raise ValueError("Invalid argument")

module_name = sys.argv[2]
solution_file_path = pathlib.Path(sys.argv[1]).resolve()
has_view_viewmodel = sys.argv[3] == "with-view-viewmodel"
view_name = sys.argv[4] if has_view_viewmodel else ""
template_directory = "template"
template_files = {"proj": "template/Project.csproj", "module": "template/Module.cs",
                  "view_xaml": "template/VVM/View.xaml", "view_cs": "template/VVM/View.xaml.cs", "view_model": "template/VVM/ViewModel.cs"}
template_files = {k: pathlib.Path(v).resolve()
                  for k, v in template_files.items()}
target_files = {"proj": f"{module_name}.csproj", "module": f"{module_name}.cs",
                "view_xaml": f"Views/{view_name}.xaml", "view_cs": f"Views/{view_name}.xaml.cs", "view_model": f"ViewModels/{view_name}.cs"}
target_files = {k: pathlib.Path(os.path.dirname(
    solution_file_path)+f"/{module_name}/"+v).resolve() for k, v in target_files.items()}

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

print(f"Add the module \"{module_name}\"")

# directory を掘る
module_path = os.path.dirname(solution_file_path)+"/"+module_name
os.makedirs(module_path, exist_ok=True)
os.chdir(module_path)
if has_view_viewmodel:
    os.makedirs("Views", exist_ok=True)
    os.makedirs("ViewModels", exist_ok=True)

# module files のデータを用意する
for key in template_files:
    create_file_from_template(target_files[key], template_files[key],
                              lambda file_text: file_text.replace("NAMESPACE", module_name).replace(
                                  "CLASS", view_name).replace("TOPTAG", "UserControl"))


print("Created these files:")
for key in target_files:
    print(f"\t{target_files[key]}")

# dotnet の設定を行う
subprocess.check_call(["dotnet.exe", "add", "package", "Prism.Unity"])
print("add {0} to {1}...".format(target_files["proj"], solution_file_path))
subprocess.check_call(
    ["dotnet.exe", "sln", solution_file_path, "add", "project", target_files["proj"]])
print("Success.")

print("Successfully finished!")

#   {module_name}/
#   ├{module_name}.csproj
#   ├{module_name}.cs
#   ├Views/
#   │├{view_name}.xaml
#   │└{view_name}.xaml.cs
#   └ViewModels/
#     └{view_name}.cs
