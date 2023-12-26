import json
import subprocess
import sys
import os
import zipfile

# Note: Requires pip to work


def upload_editable_requirement_from_current_venv():
    for requirement_dir in get_editable_requirements():
        add_lib_to_spark_context(requirement_dir)


def add_lib_to_spark_context(py_dir):
    py_archive = os.path.join(
        "/Users/main/Documents/Code/Test",
        os.path.basename(py_dir) + '.zip'
    )

    with zipfile.ZipFile(py_archive, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(py_dir):
            for file in files:
                if file.endswith(".py"):
                    zipf.write(
                        os.path.join(root, file),
                        os.path.join(
                            os.path.basename(py_dir),
                            os.path.basename(root), file
                        )
                        if root != py_dir
                        else os.path.join(
                            os.path.basename(root),
                            file
                        )
                    )
    #spark_context.addPyFile(py_archive)


def get_editable_requirements():
    def _get(name):
        pkg = __import__(name.replace("-", "_"))
        return os.path.dirname(pkg.__file__)
    return [_get(package["name"]) for package in _get_packages(True)]


def _get_packages(editable):
    editable_mode = "-e" if editable else "--exclude-editable"
    results = subprocess.check_output([f"{sys.executable}", "-m", "pip", "list", "-l", f"{editable_mode}", "--format", "json"]).decode()

    parsed_results = json.loads(results)

    # https://pip.pypa.io/en/stable/reference/pip_freeze/?highlight=freeze#cmdoption--all
    # freeze hardcodes to ignore those packages: wheel, distribute, pip, setuptools
    # To be iso with freeze we also remove those packages
    return [element for element in parsed_results
            if element["name"] not in
            ["distribute", "wheel", "pip", "setuptools"]]
    


