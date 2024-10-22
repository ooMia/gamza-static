import os
import re
import subprocess

from etherscan.unichain import store_all_dependencies, store_remappings, foundry_dir, store_foundry_toml


def run_cli(_command: str, capture_output=False) -> str | None:
    return subprocess.run(_command, shell=True, capture_output=capture_output, text=True).stdout


def format_code(_path: str) -> str:
    diff: str = run_cli(f"forge fmt {_path} --check", True)
    # print(diff)
    if len(diff) > 0:
        # print("Code not formatted properly")
        run_cli(f"forge fmt {_path}", False)
    else:
        # print("Code formatted properly")
        pass
    return diff


def store_unichain_contract(_address: str) -> str:
    """
    Get the source unichain of an address.
    :param _address: The address to get the source unichain of.
    :return: path where the target contract code is stored
    """
    _paths = store_all_dependencies(_address)
    store_remappings(_address)
    store_foundry_toml()
    return _paths[0]


def lint_code(_rel_path: str) -> list[str]:
    """
    Compile the contract using slither.
    :param _rel_path: The relative path to the contract to compile.
    :return: The output of the compilation.
    """
    _origin_dir = os.getcwd()
    os.chdir(foundry_dir)
    set_solc_version_by_sol(_rel_path)
    _res = subprocess.run([
        "slither",
        _rel_path,
    ], capture_output=True, encoding="utf-8")
    os.chdir(_origin_dir)
    return [_res.stderr, _res.stdout]


def set_solc_version_by_sol(_path: str) -> str:
    """
    Set the solc version from the solidity file.
    :param _path: The path to the solidity file.
    :return: The version of the solidity file.
    """
    with open(_path, "r") as f:
        _content = f.read()
        _version = re.search(r"pragma\s+solidity\s+(?:\W+)?([\d.]+);", _content).group(1)
        set_solc_version(_version)
        return _version


def set_solc_version(_version: str) -> None:
    is_installed = re.search(_version, run_cli(
        "solc-select versions",
        capture_output=True
    ))
    if not is_installed:
        run_cli(f"solc-select install {_version}")
    run_cli(f"solc-select use {_version}")
