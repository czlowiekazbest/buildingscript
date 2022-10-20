#!/usr/bin/python3

import argparse
import sys, os
import time

# OS dependent path delimiter
dlr = "/"
root_dir = os.getcwd() + dlr


def confArgparser():
    parser = argparse.ArgumentParser(description="Parameters")
    parser.add_argument(
        "-a",
        "--action",
        choices=["build", "rebuild", "clean"],
        help="build type",
    )
    parser.add_argument(
        "-p", "--platform", choices=["x64", "PS5"], help="Platform choice"
    )
    parser.add_argument(
        "-c",
        "--configuration",
        choices=["dev", "prod", "shipping"],
        help="sets the environment",
    )
    parser.add_argument("solution_path", nargs="?")  # Source dir
    parser.add_argument("output_path", nargs="?")  # Output dir
    return parser


def append_solution(sln_file, message, build_file):
    try:
        timestamp = time.strftime("%H:%M:%S %d-%m-%Y")
        f = open(sln_file, "a")
        f.write("\n\n===\n\n" + message + ": " + timestamp + "\n" + build_file)
        f.close()
    except Exception as e:
        print("I/O error in Builder: " + str(e))
        sys.exit(40)


def recognize_os():
    if os.name == "nt":
        # windows
        dlr = "\\"
        root_dir = os.getcwd() + dlr
    if os.name == "posix":
        # linux
        dlr = "/"
        root_dir = os.getcwd() + dlr


# create output_path and solution_path if doesn't exist

parser = confArgparser()
parameters = parser.parse_args()
recognize_os()

sln_file = parameters.solution_path + "sampleProject.sln"

# create output_path and solution_path if doesn't exist
try:
    if not os.path.exists(parameters.solution_path):
        os.makedirs(parameters.solution_path)
        print(parameters.solution_path + " created\n")
    if not os.path.exists(parameters.output_path):
        os.makedirs(parameters.output_path)
        print(parameters.output_path + " created\n")

except Exception as e:
    print(
        "Can not create directories: "
        + parameters.solution_path
        + " "
        + parameters.output_path
    )
    sys.exit(10)

timestamp = time.strftime("%H-%M-%S-%d-%m-%Y")
try:
    # creating build
    path = (
        parameters.output_path
        + "build-"
        + parameters.platform
        + "-"
        + timestamp
        + ".build"
    )
    print("creating build: " + path)
    f = open(path, "w+")
    f.write(timestamp)
    f.write("\n\n========\nHere goes some binary content of the build\n========\n")
    f.close()
    append_solution(sln_file, "Build successfully created", path)

except Exception as e:
    print("Cannot create build file: " + str(e))
    append_solution(sln_file, "Build FAILED!!!", "no file created")
    sys.exit(11)


sys.exit(0)
