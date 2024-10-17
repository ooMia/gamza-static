import os
import subprocess

from etherscan.unichain import store_all_dependencies, store_remappings, _unichain_dir


def run_cli(_command: str, capture_output=False) -> str | None:
    return subprocess.run(_command, shell=True, capture_output=capture_output, text=True).stdout


def format_code(_path: str):
    res: str = run_cli(f"forge fmt {_path} --check", True)
    print(res)
    if len(res) > 0:
        print("Code is not formatted properly")
        run_cli("forge fmt code/0xe8e23e97fa135823143d6b9cba9c699040d51f70.sol", False)
    else:
        print("Code is formatted properly")


def store_unichain_contract(_address: str) -> str:
    """
    Get the source unichain of an address.
    :param _address: The address to get the source unichain of.
    :return path where the target contract code is stored
    """
    _paths = store_all_dependencies(_address)
    store_remappings(_address)
    return _paths[0]


def compile_slither(_path: str) -> list[str]:
    """
    Compile the contract using slither.
    :param _path: The path to the contract to compile.
    :return: The output of the compilation.
    """
    _origin_dir = os.getcwd()
    os.chdir(_unichain_dir)
    _res = subprocess.run([
        "slither",
        _path,
    ], capture_output=True, encoding="utf-8")
    os.chdir(_origin_dir)
    return [_res.stderr, _res.stdout]


if __name__ == "__main__":
    _address: str = "0x38EB8B22Df3Ae7fb21e92881151B365Df14ba967"
    _path = store_unichain_contract(_address)
    [_stdout, _stderr] = compile_slither(_path)
    format_code(_path)
    print(_stdout)
    print(_stderr)
