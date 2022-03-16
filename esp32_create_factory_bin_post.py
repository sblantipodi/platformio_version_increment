Import("env")

#
#  Copyright (C) 2022  Davide Perini
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

def esp32_create_factory_bin(source, target, env):
    print("Generating factory bin for genuine esp units")
    #offset = 0x1000
    offset = 0x0
    new_file_name = env.subst("$BUILD_DIR/${PROGNAME}-factory.bin")
    sections = env.subst(env.get('FLASH_EXTRA_IMAGES'))
    new_file = open(new_file_name,"wb")
    for section in sections:
        sect_adr,sect_file = section.split(" ",1)
        source = open(sect_file,"rb")
        new_file.seek(int(sect_adr,0)-offset)
        new_file.write(source.read());
        source.close()

    firmware = open(env.subst("$BUILD_DIR/${PROGNAME}.bin"),"rb")
    new_file.seek(0x10000-offset)
    new_file.write(firmware.read())
    new_file.close()
    firmware.close()

env.AddPostAction("$BUILD_DIR/${PROGNAME}.bin", esp32_create_factory_bin)