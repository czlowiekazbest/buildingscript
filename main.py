#!/usr/bin/python3


import argparse
from ast import Not
from datetime import date
import os
import re
import sys
import git
import time


GIT_LOCAL_DIR = "Source_aux"
REMOTE_URL = "https://github.com/czlowiekazbest/TestProj.git"
BRANCH = "main"


def recognize_os():
    if os.name == "nt":
        os_name = "windows"
        os_copy = "copy"
        os_rm = "rmdir /s /q"
        os_7z = "7z"
        python_int = "python "
        d = "\\"
    if os.name == "posix":
        os_name = "linux"
        os_copy = "cp"
        os_rm = "rm -rf"
        os_7z = "7zz"
        d = "/"
        python_int = ""
    return d, os_name, os_copy, os_rm, os_7z, python_int


# OS dependent path delimiter
dlr, os_name, os_copy, os_rm, os_7z, python_int = recognize_os()
# build setup variables
root_dir = os.getcwd() + dlr
setup_dirs = [
    root_dir + "Output" + dlr,
    root_dir + "Temp" + dlr,
    root_dir + "Source" + dlr,
]
header_file = setup_dirs[2] + "header.h"
header_file_bak = header_file + ".bak"
sln_file = setup_dirs[2] + "sampleProject.sln"
ini_file = root_dir + "ps5config.ini"
builder_name = root_dir + "Builder.py"
ps5package_name = root_dir + "ps5package.py"
ps5config_ini = root_dir + "ps5config.ini"
network_share = root_dir + "server" + dlr + "builds" + dlr + "sampleProject" + dlr
info_list = []

# errors info
err_revision = "Revision with given ID not found!"
err_setup_dirs = "Directory not found! Create proper directory:"
err_io = "File input/output error"


def confArgparser():
    parser = argparse.ArgumentParser(description="Parameters")
    # OPTIONAL
    parser.add_argument(
        "-r",
        "--revision",
        default=None,
        help="the ID of a particular revision, sets to HEAD when left empty, the syntax is like /-r 1c002dd4b536e7479f/",
    )
    # OPTIONAL
    parser.add_argument(
        "-a",
        "--action",
        choices=["build", "rebuild", "clean"],
        default="build",
        help="The complete rebuild flag",
    )
    # MANDATORY
    parser.add_argument(
        "-p", "--platform", choices=["x64", "PS5"], help="Platform choice"
    )
    # MANDATORY
    parser.add_argument(
        "-c",
        "--configuration",
        choices=["dev", "prod", "shipping"],
        default="dev",
        help="sets the environment",
    )
    return parser


def change_entry(datetime1, datetime2, changelist1, changelist2, filepath):
    os.system(os_copy + " " + filepath + " " + header_file_bak)
    file = open(filepath, "r")
    content = file.read()
    file.close()
    content = re.sub(datetime1, datetime2, content)
    content = re.sub(changelist1, changelist2, content)
    file = open(filepath, "w+")
    file.write(content)
    file.close()

    print(content)


def revert_entry():
    os.system(os_copy + " " + header_file_bak + " " + header_file)


def build(action, platform, env, srcdir, outdir):
    try:
        os_cmd = (
            python_int + builder_name
            + " -a "
            + action
            + " -p "
            + platform
            + " -c "
            + env
            + " "
            + srcdir
            + " "
            + outdir
        )
        if os.system(os_cmd) != 0:
            raise Exception("Can't perform command: " + os_cmd)
        build_status = "BUILD SUCCESSFUL"

    except Exception as e:
        print("Error: ", str(e))
        print("Build failed")
        build_status = "BUILD FAILED"
        send_email(build_status, info_list)
        sys.exit(30)

    return build_status


def create_package(platform, outdir, tempdir):

    # create tempdir if not present
    try:
        if not os.path.exists(tempdir):
            os.makedirs(tempdir)
            print(tempdir + " created\n")
    except Exception as e:
        msg = "Cannot create " + tempdir + str(e)
        print(msg)
        send_email("BUILD FAILED: " + msg, info_list)
        sys.exit(12)

    # create package depending on platform
    current_build = read_filename(sln_file)
    if platform == "x64":
        try:
            current_build = read_filename(sln_file)
            os_cmd = (
                os_7z + " a "
                + re.sub(re.escape(outdir), re.escape(tempdir), current_build)
                + ".7z "
                + current_build
            )
            if os.system(os_cmd) != 0:
                raise Exception("Can't perform command: " + os_cmd)
        except Exception as e:
            msg = "Package x64 creation failed: " + str(e)
            print(msg)
            send_email("BUILD FAILED: " + msg, info_list)
            sys.exit(32)

    if platform == "PS5":
        try:
            # run ps5package.exe file
            os_cmd = (
                python_int + ps5package_name + " -c " + ps5config_ini + " " + outdir + " " + tempdir
            )
            if os.system(os_cmd) != 0:
                raise Exception("Can't perform command: " + os_cmd)

        except Exception as e:
            msg = "Package creation failed: " + str(e)
            print(msg)
            send_email("BUILD FAILED: " + msg, info_list)
            sys.exit(31)

    return setup_dirs[1] + find_latest_file(tempdir)


def read_filename(sln_file):
    # return the last line of .sln file which is the current build name
    try:
        f = open(sln_file, "r")
    except Exception as e:
        print(" Cannot open .sln file: ", str(e))
        exit(90)

    content = ""
    for line in f:
        content = line
    f.close()
    return content


def find_latest_file(path):
    # hint:
    # linux: ls -1rt - reversed chrono.order
    # linux: ls -1t - chrono. order
    # windows: dir /b /a-d /od -- reversed chrono.order
    # windows: dir /b /a-d /o-d -- chrono. order
    try:
        if os_name == "windows":
            files = os.popen("dir /b /a-d /o-d " + path).read().splitlines()
        else:
            files = os.popen("ls -1t " + path).read().splitlines()
        return files[0]
    except Exception as e:
        print("\nFAILED, probably empty " + path + " directory\n" + str(e) + "\n")


def upload_package(package, destination):
    if not os.path.exists(destination):
        os.makedirs(destination)
        print(destination)
    os.system(os_copy + " " + package + " " + destination)
    escaped_temp = re.escape(setup_dirs[1])
    print(destination + dlr + re.sub(escaped_temp, "", package))
    info_list.append(destination + dlr + re.sub(escaped_temp, "", package))


def send_email(status, location_info):
    print("\n\nsending fake email:....\n")
    print(status)
    print(location_info)

if __name__ == "__main__":

    parser = confArgparser()
    parameters = parser.parse_args()

    info_list.append({parameters.action, parameters.platform, parameters.configuration})

    # create directory if doesn't exist
    if not os.path.exists(GIT_LOCAL_DIR):
        os.makedirs(GIT_LOCAL_DIR)

    # if empty directory make a clone from GitHub
    if len(os.listdir(GIT_LOCAL_DIR)) == 0:
        git.Repo.clone_from(REMOTE_URL, GIT_LOCAL_DIR, branch=BRANCH)
        print("Cloning repo...")
    else:
        # if directory isn't empty update to a particular revision, newest by default
        g = git.Git(GIT_LOCAL_DIR)
        g.pull(REMOTE_URL, BRANCH)

    if parameters.revision != None:
        try:
            g = git.Git(GIT_LOCAL_DIR)
            print(
                "Synchronizing local repository to particular revision: "
                + parameters.revision
            )
            g.checkout(parameters.revision)
            # working example of valid sha: 1e0803e7aeaf07d643a576eac19d190844023d94
        except Exception:
            print(err_revision)
            sys.exit(32)

    # checking and cleaning setup directories
    if parameters.action == "rebuild" or parameters.action == "clean":
        for i in range(2):
            if os.path.exists(setup_dirs[i]):
                os.system(os_rm + " " + setup_dirs[i])
                print(setup_dirs[i] + " deleted recursively")
    if parameters.action == "clean":
        print("Exiting.")
        sys.exit(0)

    # changing timestamp and commit tag in the headerfile

    # accessing the git commit tag
    try:
        repo = git.Repo(GIT_LOCAL_DIR)
        sha = repo.head.object.hexsha
    except Exception as e:
        print("Build failed due to exception: " + str(e))
        exit

    # accessing the system date and time
    try:
        timestamp = time.strftime("%H:%M:%S %d-%m-%Y")
    except Exception as e:
        print("Build failed due to exception: " + str(e))
        sys.exit(60)

    info_list.append(timestamp)

    try:
        change_entry("DATETIME", timestamp, "CHANGELIST", sha, header_file)
        print("changing headerfile: " + header_file)
    except Exception as e:
        print(err_io + " : " + str(e))
        sys.exit(61)

    # BUILD & PACKAGE section

    build_status = build(
        parameters.action,
        parameters.platform,
        parameters.configuration,
        setup_dirs[2],
        setup_dirs[0],
    )
    current_package = create_package(
        parameters.platform, setup_dirs[0], setup_dirs[1]
    )
    info_list.append(current_package)

    day_a = time.strftime("%Y%m%d")

    if parameters.revision == None:
        recent_revision = sha
    else:
        recent_revision = parameters.revision
    info_list.append("git rev.:" + recent_revision)

    upload_package(
        current_package,
        network_share
        + parameters.platform
        + dlr
        + parameters.configuration
        + dlr
        + day_a
        + dlr
        + recent_revision,
    )

    revert_entry()

    send_email(build_status, info_list)
