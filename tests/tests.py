#!/usr/bin/python3
import sys
import subprocess
import os
import io
from contextlib import redirect_stdout

test_failed = 0

def run_info(command: str, capture_output=False) -> None:
    print(f"[INFO] {' '.join(command)}")
    return subprocess.run(command, capture_output)

def compile_file_and_get_stdout_from_execution(file: str) -> str:
    test_file_name = f"{file}.test"
    test_file_asm_name = f"{file}.test.asm"
    result_cmp = subprocess.run(["../main.py", file, test_file_name], capture_output=True)
    if result_cmp.returncode > 0:
        string = result_cmp.stdout.decode()
        string += "\n----------\n"
        string += f"{result_cmp.returncode}"
    else:
        result = subprocess.run([f"./{test_file_name}"], capture_output=True)
        string = result.stdout.decode() + "\n----------\n"
        string += f"{result.returncode}"
        run_info(["rm", f"./{test_file_name}"])
    run_info(["rm", f"./{test_file_asm_name}"])
    return string
    


def run_test_for_file(file:str):
    global test_failed
    res_file = f"{file}.res"
    if not os.path.exists(res_file):
        print(f"[ERROR]: {res_file} does not exists, skipping test for {file}.", file=sys.stderr)
        return
    r = open(res_file, "r")
    res_as_string = r.read()
    r.close() 
    
    file_as_string = compile_file_and_get_stdout_from_execution(file)

    if file_as_string != res_as_string:
        print(f"[ERROR]: the test for {file} failed.", file=sys.stderr)
        test_failed += 1

def record_test_for_file(file:str):
    res_file = f"{file}.res"
    r = open(res_file, "w")
    file_as_string = compile_file_and_get_stdout_from_execution(file)
    r.write(file_as_string)
    r.close() 


def run_test_on_dir(dir: str) -> None:
    for file in os.listdir(file):
        if os.path.isdir(file):
            run_test_on_dir(file)
        if file.endswith('.aw'):
            run_test_for_file(file)

def run_test_on(file: str) -> None:
    if os.path.isdir(file):
        run_test_on_dir(file)
    elif file.endswith('.aw'):
        run_test_for_file(file)
    else:
        print("[ERROR]: nothing to run. Exiting", file=sys.stdout)
        exit(1)

def record_test_on_dir(dir: str) -> None:
    for file in os.listdir('.'):
        if os.path.isdir(file):
            record_test_on_dir(file)
        if file.endswith('.aw'):
            record_test_for_file(file)

def record_test_on(file: str) -> None:
    if os.path.isdir(file):
        record_test_on_dir(file)
    elif file.endswith('.aw'):
        record_test_for_file(file)
    else:
        print("[ERROR]: nothing to record. Exiting", file=sys.stdout)
        exit(1)


def main():
    if len(sys.argv) != 3:
        print("ERROR: not enought arguments", file=sys.stderr)
        print("    usage: ./test.py -rec <file or dir>",file=sys.stderr)
        print("    usage: ./test.py -run <file or dir>",file=sys.stderr)
        exit(1)
    if sys.argv[1] == "-rec":
        record_test_on(sys.argv[2])
    if sys.argv[1] == "-run":
        run_test_on(sys.argv[2])
    
    print(f"Test failed: {test_failed}")

if __name__ == '__main__':
    main()
