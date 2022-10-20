#!/usr/bin/python3

import argparse
import sys, os
import time

def conf_argparser():
    parser = argparse.ArgumentParser(description="Parameters")
    parser.add_argument(
        "-c",
        "--config",
        help="config path",
    )
    parser.add_argument("data_path", nargs="?")  # Temp dir
    parser.add_argument("output_path", nargs="?")  # Output dir
    return parser


def read_config(config_full_path):
    # this function should return the last line of the .ini file which is an imaginary configuration token
    try:
        f = open(config_full_path, "r")
    except Exception as e:
        print(" Cannot open file: ", str(e))
        exit(18)

    content = ""
    for line in f:
        content = line
    f.close()
    return content


def write_config(config_full_path, content):
    try:
        f = open(config_full_path, "w")
        f.write(content)
        f.close()
    except Exception as e:
        print(" I/O file error: ", str(e))
        exit(20)


# create output_path and solution_path if doesn't exist

parser = conf_argparser()
parameters = parser.parse_args()

# create data_path and solution_path if doesn't exist
try:
    if not os.path.exists(parameters.data_path):
        os.makedirs(parameters.data_path)
        print(parameters.data_path + " created\n")
    if not os.path.exists(parameters.output_path):
        os.makedirs(parameters.output_path)
        print(parameters.output_path + " created\n")
except Exception as e:
    print(
        "Can not create directories: "
        + parameters.data_path
        + " "
        + parameters.output_path
    )
    sys.exit(21)

timestamp = time.strftime("%d-%m-%Y-%H-%M-%S")


try:
    package_path = parameters.output_path + "package-PS5-" + timestamp + ".PS5_package"
    open(package_path, "w+").close()
    print("creating PS5 package: " + package_path)

    try:
        write_config(
            package_path,
            "timestamp: " + timestamp + "\n" + read_config(parameters.config),
        )
    except Exception as e:
        print("Cannot write to PS5 package file: ", str(e))
        sys.exit(22)

except Exception as e:
    print("Cannot create PS5 package: ", str(e))
    sys.exit(23)

sys.exit(0)
