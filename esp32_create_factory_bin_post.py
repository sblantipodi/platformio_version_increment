#
#  Copyright (C) 2022  Davide Perini
#  Thanks to TD-er (ESPeasy) and to Jason2866 (Tasmota),
#  this script, takes inspiration from their post_esp32.py script
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy of
#  this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
#  You should have received a copy of the MIT License along with this program.
#  If not, see <https://opensource.org/licenses/MIT/>.
#
Import("env")

env = DefaultEnvironment()
platform = env.PioPlatform()

from genericpath import exists
import sys
from os.path import join

sys.path.append(join(platform.get_package_dir("tool-esptoolpy")))
import esptool

FRAMEWORK_DIR = platform.get_package_dir("framework-arduinoespressif32")
variants_dir = join(FRAMEWORK_DIR, "variants", "luciferin")

def esp32_create_combined_bin(source, target, env):
    #print("Generating combined binary for serial flashing")
    # factory_offset = -1      # error code value - currently unused
    app_offset = 0x10000     # default value for "old" scheme
    fs_offset = -1           # error code value
    new_file_name = env.subst("$BUILD_DIR/${PROGNAME}-factory.bin")
    sections = env.subst(env.get("FLASH_EXTRA_IMAGES"))
    firmware_name = env.subst("$BUILD_DIR/${PROGNAME}.bin")
    chip = env.get("BOARD_MCU")
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

    # "main" firmware to app0 - mandatory
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