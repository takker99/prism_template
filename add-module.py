# add a new module
import os
import re
import glob
import subprocess
import pathlib
import sys
import argparse

# format:
#  add-module.py module {module_name}  --solution_file {solution_file} --view {view1} {view2}
#  add-module.py view {view1} {view2} --module_namespace {module_name}

# file structure
#   {args.module_name}/
#   ├{args.module_name}.csproj
#   ├{args.module_name}.cs         <- namespace {arg.module_name}
#   ├Views/
#   │├{args.view_name}.xaml      <- namespace {arg.module_name}.Views
#   │└{args.view_name}.xaml.cs   <- namespace {arg.module_name}.Views
#   └ViewModels/
#     └{args.view_name}.cs       <- namespace {arg.module_name}.VieModels


def create_file_from_template(target_file_path: "作成したいファイルへのパス", template_file_path: "型となるファイルへのパス", replace_function: "テンプレートファイル内の文字列を置換するための函数") -> "nothing":
    print("Create {0}...".format(target_file_path), end="")
    with open(target_file_path, "w") as result:
        with open(template_file_path) as temp:
            result.write(replace_function(temp.read()))
    print("done")


def check_file(file_path):
    print("Check if {0} exists...".format(file_path), end="")
    if os.path.isfile(file_path):
        print("found")
    else:
        print("not found")
        raise ValueError(f"No {file_path} exists.")

# add-module.py module の処理


def module(args):
    print(f"Add the module \"{args.module_name}\"")

    solution_file_path = pathlib.Path(args.solution_file).resolve()
    template_files = {"proj": "template/Project.csproj",
                      "module": "template/Module.cs", }
    target_files = {"proj": f"{args.module_name}.csproj",
                    "module": f"{args.module_name}.cs", }
    view_files = dict()

    # view/viewmodel の作成が指定されている場合
    if args.view_names:
        template_files["view_xaml"] = f"template/VVM/View.xaml"
        template_files["view_cs"] = f"template/VVM/View.xaml.cs"
        template_files["view_model"] = f"template/VVM/ViewModel.cs"
        for view in args.view_names:
            view_files[view] = {"view_xaml": f"Views/{view}.xaml",
                                "view_cs": f"Views/{view}.xaml.cs",
                                "view_model": f"ViewModels/{view}.cs", }

    # current directory の変更の影響を受けないように、相対パスを絶対パスに変換している。
    template_files = {k: pathlib.Path(v).resolve()
                      for k, v in template_files.items()}
    target_files = {k: pathlib.Path(os.path.dirname(
        solution_file_path)+f"/{args.module_name}/"+v).resolve() for k, v in target_files.items()}
    view_files = {l: {k: pathlib.Path(os.path.dirname(
        solution_file_path)+f"/{args.module_name}/"+v).resolve() for k, v in view.items()} for l, view in view_files.items()}

    # 必要なテンプレートファイルが存在するか確認する
    # 必要なファイル；
    # - Project.csproj
    # - Module.cs
    # - VVM/MainWindow.xaml
    # - VVM/MainWindow.cs.xaml
    # - VVM/MainWindow.cs
    for key in template_files:
        check_file(template_files[key])

    # directory を掘る
    module_path = os.path.dirname(solution_file_path)+"/"+args.module_name
    os.makedirs(module_path, exist_ok=True)
    os.chdir(module_path)
    if args.view_names:
        os.makedirs("Views", exist_ok=True)
        os.makedirs("ViewModels", exist_ok=True)

    # module files のデータを用意する
    def replace_func(file_text): return file_text.replace(
        "MODULE_NAMESPACE", args.module_name).replace("OUTPUT_TYPE", "Library").replace("TOPTAG", "UserControl")
    for key in target_files:
        create_file_from_template(target_files[key], template_files[key],
                                  replace_func)
    for view in view_files:
        for key in view_files[view]:
            create_file_from_template(view_files[view][key], template_files[key], lambda file_text: replace_func(file_text).replace(
                "VIEW", view))

    # dotnet の設定を行う
    subprocess.check_call(["dotnet.exe", "add", "package", "Prism.Unity"])
    subprocess.check_call(["dotnet.exe", "add", "package", "ReactiveProperty"])
    print("add {0} to {1}...".format(target_files["proj"], solution_file_path))
    os.chdir(os.path.dirname(solution_file_path))
    subprocess.check_call(
        ["dotnet.exe", "sln", "add", args.module_name+"/"+args.module_name+".csproj"])
    print("Successfully finished!")

# add-module.py view の処理
def views(args):
    if not os.path.isdir(args.output_dir):
        raise ValueError(f"--output_dir must be a directory path.")

    print("Add the views: \"{0}\"".format(', '.join(args.view_names)))

    template_files=dict()
    template_files["view_xaml"] = f"template/VVM/View.xaml"
    template_files["view_cs"] = f"template/VVM/View.xaml.cs"
    template_files["view_model"] = f"template/VVM/ViewModel.cs"
    view_files = dict()
    for view in args.view_names:
        view_files[view] = {"view_xaml": f"Views/{view}.xaml",
                            "view_cs": f"Views/{view}.xaml.cs",
                            "view_model": f"ViewModels/{view}.cs", }

    # current directory の変更の影響を受けないように、相対パスを絶対パスに変換している。
    template_files = {k: pathlib.Path(v).resolve()
                      for k, v in template_files.items()}
    view_files = {l: {k: pathlib.Path(pathlib.PurePath(args.output_dir).joinpath(
        v)).resolve() for k, v in view.items()} for l, view in view_files.items()}

    # 必要なテンプレートファイルが存在するか確認する
    # 必要なファイル；
    # - VVM/MainWindow.xaml
    # - VVM/MainWindow.cs.xaml
    # - VVM/MainWindow.cs
    for key in template_files:
        check_file(template_files[key])

    # directory を掘る
    os.chdir(args.output_dir)
    os.makedirs("Views", exist_ok=True)
    os.makedirs("ViewModels", exist_ok=True)

    # module files のデータを用意する
    for view in view_files:
        for key in view_files[view]:
            create_file_from_template(view_files[view][key], template_files[key], lambda file_text: file_text.replace(
                "MODULE_NAMESPACE", args.module_namespace).replace("TOPTAG", "UserControl").replace(
                "VIEW", view))

    print("Successfully finished!")


parser = argparse.ArgumentParser(
    description='Make files used for Prism application')
subparsers = parser.add_subparsers(help='sub-command help')

# module command
module_parser = subparsers.add_parser('module', help='make a module')
module_parser.add_argument(
    "module_name", help="the name of a module you want to add")
module_parser.add_argument(
    "solution_file", help="the solution file which you want to add a new module to")
module_parser.add_argument(
    "-v", "--view_names", nargs="*", help="set the view names if you want")
module_parser.set_defaults(func=module)

# module command
view_parser = subparsers.add_parser('view', help='make views')
view_parser.add_argument(
    "view_names", nargs="*", help="the name of views you want to add")
view_parser.add_argument(
    "-m", "--module_namespace", help="the namespace of the module you want to add views to", default=pathlib.PurePath(os.getcwd()).parts[-1])
view_parser.add_argument(
    "-o", "--output_dir", help="the directory which Views/ and ViewModels/ will be made under", default=os.getcwd())
view_parser.set_defaults(func=views)

args = parser.parse_args()
args.func(args)
