Import("env")

env = DefaultEnvironment()
platform = env.PioPlatform()

from genericpath import exists
import os
import sys
from os.path import join
import requests
import shutil
import subprocess

sys.path.append(join(platform.get_package_dir("tool-esptoolpy")))
import esptool

FRAMEWORK_DIR = platform.get_package_dir("framework-arduinoespressif32")
variants_dir = join(FRAMEWORK_DIR, "variants", "tasmota")

def esp32_create_chip_string(chip):
    tasmota_platform = env.subst("$BUILD_DIR").split(os.path.sep)[-1]
    tasmota_platform = tasmota_platform.split('-')[0]
    if 'tasmota' + chip[3:] not in tasmota_platform: # quick check for a valid name like 'tasmota' + '32c3'
        print('Unexpected naming conventions in this build environment -> Undefined behavior for further build process!!')
        print("Expected build environment name like 'tasmota32-whatever-you-want'")
    return tasmota_platform

def esp32_build_filesystem(fs_size):
    files = env.GetProjectOption("custom_files_upload").splitlines()
    filesystem_dir = join(env.subst("$BUILD_DIR"),"littlefs_data")
    if not os.path.exists(filesystem_dir):
        os.makedirs(filesystem_dir)
    print("Creating filesystem with content:")
    for file in files:
        if "no_files" in file:
            continue
        if "http" and "://" in file:
            response = requests.get(file)
            if response.ok:
                target = join(filesystem_dir,file.split(os.path.sep)[-1])
                open(target, "wb").write(response.content)
            else:
                print("Failed to download: ",file)
            continue
        shutil.copy(file, filesystem_dir)
    if not os.listdir(filesystem_dir):
        print("No files added -> will NOT create littlefs.bin and NOT overwrite fs partition!")
        return False
    env.Replace( MKSPIFFSTOOL=platform.get_package_dir("tool-mklittlefs") + '/mklittlefs' )
    tool = env.subst(env["MKSPIFFSTOOL"])
    cmd = (tool,"-c",filesystem_dir,"-s",fs_size,join(env.subst("$BUILD_DIR"),"littlefs.bin"))
    returncode = subprocess.call(cmd, shell=False)
    # print(returncode)
    return True

def esp32_create_combined_bin(source, target, env):
    #print("Generating combined binary for serial flashing")

    # The offset from begin of the file where the app0 partition starts
    # This is defined in the partition .csv file
    # factory_offset = -1      # error code value - currently unused
    app_offset = 0x10000     # default value for "old" scheme
    fs_offset = -1           # error code value
    new_file_name = env.subst("$BUILD_DIR/${PROGNAME}-factory.bin")
    sections = env.subst(env.get("FLASH_EXTRA_IMAGES"))
    firmware_name = env.subst("$BUILD_DIR/${PROGNAME}.bin")
    chip = env.get("BOARD_MCU")
    tasmota_platform = esp32_create_chip_string(chip)
    flash_size = env.BoardConfig().get("upload.flash_size", "4MB")
    flash_freq = env.BoardConfig().get("build.f_flash", "40000000L")
    flash_freq = str(flash_freq).replace("L", "")
    flash_freq = str(int(int(flash_freq) / 1000000)) + "m"
    flash_mode = env.BoardConfig().get("build.flash_mode", "dout")
    if flash_mode == "qio":
        flash_mode = "dio"
    elif flash_mode == "qout":
        flash_mode = "dout"
    cmd = [
        "--chip",
        chip,
        "merge_bin",
        "-o",
        new_file_name,
        "--flash_mode",
        flash_mode,
        "--flash_freq",
        flash_freq,
        "--flash_size",
        flash_size,
    ]

    print("    Offset | File")
    for section in sections:
        sect_adr, sect_file = section.split(" ", 1)
        print(f" -  {sect_adr} | {sect_file}")
        cmd += [sect_adr, sect_file]

    # "main" firmware to app0 - mandatory, except we just built a new safeboot bin locally
    if("safeboot" not in firmware_name):
        print(f" - {hex(app_offset)} | {firmware_name}")
        cmd += [hex(app_offset), firmware_name]

    if(fs_offset != -1):
        fs_bin = join(env.subst("$BUILD_DIR"),"littlefs.bin")
        if exists(fs_bin):
            before_reset = env.BoardConfig().get("upload.before_reset", "default_reset")
            after_reset = env.BoardConfig().get("upload.after_reset", "hard_reset")
            print(f" - {hex(fs_offset)}| {fs_bin}")
            cmd += [hex(fs_offset), fs_bin]
            env.Replace(
                UPLOADERFLAGS=[
                    "--chip", chip,
                    "--port", '"$UPLOAD_PORT"',
                    "--baud", "$UPLOAD_SPEED",
                    "--before", before_reset,
                    "--after", after_reset,
                    "write_flash", "-z",
                    "--flash_mode", "${__get_board_flash_mode(__env__)}",
                    "--flash_freq", "${__get_board_f_flash(__env__)}",
                    "--flash_size", flash_size
                ],
                UPLOADCMD='"$PYTHONEXE" "$UPLOADER" $UPLOADERFLAGS ' + " ".join(cmd[7:])
            )
            print("Will use custom upload command for flashing operation to add file system defined for this build target.")

    # print('Using esptool.py arguments: %s' % ' '.join(cmd))

    esptool.main(cmd)

env.AddPostAction("$BUILD_DIR/${PROGNAME}.bin", esp32_create_combined_bin)