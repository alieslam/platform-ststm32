# Copyright 2014-present PlatformIO <contact@platformio.org>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
Arduino

Arduino Wiring-based Framework allows writing cross-platform software to
control devices attached to a wide range of Arduino boards to create all
kinds of creative coding, interactive objects, spaces or physical experiences.

http://www.stm32duino.com
"""

from os import walk
from os.path import isdir, join

from SCons.Script import DefaultEnvironment

env = DefaultEnvironment()
platform = env.PioPlatform()
board = env.BoardConfig()

FRAMEWORK_DIR = join(platform.get_package_dir("framework-arduinoststm32"), "STM32F2")

assert isdir(FRAMEWORK_DIR)

ldscript = "app_no_bootloader.ld"
variant = board.get("build.variant")


env.Append(
    ASFLAGS=["-x", "assembler-with-cpp"],

    CFLAGS=["-std=gnu99",
		"-mapcs-frame",
		"-mthumb-interwork",
        "-MD",
        "-Os",
        "-mthumb",
		"-w",
		"-nostartfiles",
		"-ffunction-sections",
		"-fdata-sections",
        "-mcpu=%s" % env.BoardConfig().get("build.cpu")],

    CXXFLAGS=[
        "-std=c++11",
    ],

    CCFLAGS=[
		"-mapcs-frame",
		"-mthumb-interwork",
        "-MD",
        "-Os",
        "-mthumb",
		"-w",
		"-ffunction-sections",
		"-fdata-sections",
        "-mcpu=%s" % env.BoardConfig().get("build.cpu")
    ],

    CPPDEFINES=[
		("STM32F205xx"),
		("PLATFORM_THREADING"),
		("USE_STDPERIPH_DRIVER"),
		("STM32F2XX"),
		("RELEASE_BUILD"),
		("PLATFORM_ID",10),
		("MODULE_FUNCTION",2),
		("MODULE_DEPENDENCY"),
		("MODULE_DEPENDENCY2"),
		("MODULE_VERSION",110),
		("BOOTLOADER_VERSION",201),
        ("__STACKSIZE__", 1400),
        ("F_CPU", "$BOARD_F_CPU"),
    ],

    CPPPATH=[
        join(FRAMEWORK_DIR, "cores", "elkrem"),
        join(FRAMEWORK_DIR, "cores", "elkrem", "decentlib","src"),
        join(FRAMEWORK_DIR, "cores", "elkrem", "dynalib","inc"),
        join(FRAMEWORK_DIR, "cores", "elkrem", "hal", "inc"),
		join(FRAMEWORK_DIR, "cores", "elkrem", "hal", "shared"),
		join(FRAMEWORK_DIR, "cores", "elkrem", "hal", "src","stm32f2xx"),
		join(FRAMEWORK_DIR, "cores", "elkrem", "hal", "src","stm32"),
		join(FRAMEWORK_DIR, "cores", "elkrem", "hal", "shared"),
		join(FRAMEWORK_DIR, "cores", "elkrem", "hal", "src","electron"),
		join(FRAMEWORK_DIR, "cores", "elkrem", "hal", "src","electron","rtos","FreeRTOSv8.2.2","FreeRTOS","Source","portable","GCC","ARM_CM3"),
		join(FRAMEWORK_DIR, "cores", "elkrem", "hal", "src","electron","rtos","FreeRTOSv8.2.2","FreeRTOS","Source","include"),
		join(FRAMEWORK_DIR, "cores", "elkrem", "hal", "src","gcc"),
        join(FRAMEWORK_DIR, "cores", "elkrem", "services","inc"),
		join(FRAMEWORK_DIR, "cores", "elkrem", "system","inc"),
		join(FRAMEWORK_DIR, "cores", "elkrem", "wiring","inc"),
		join(FRAMEWORK_DIR, "cores", "elkrem", "platform","shared","inc"),
		join(FRAMEWORK_DIR, "cores", "elkrem", "platform","MCU","shared","STM32","inc"),
		join(FRAMEWORK_DIR, "cores", "elkrem", "platform","MCU","STM32F2xx","CMSIS","Device","ST","Include"),
		join(FRAMEWORK_DIR, "cores", "elkrem", "platform","MCU","STM32F2xx","CMSIS","Include"),	
		join(FRAMEWORK_DIR, "cores", "elkrem", "platform","MCU","STM32F2xx","STM32_StdPeriph_Driver","inc"),
		join(FRAMEWORK_DIR, "cores", "elkrem", "platform","MCU","STM32F2xx","SPARK_Firmware_Driver","inc"),
        join(FRAMEWORK_DIR, "system", "elkrem"),
    ],

    LINKFLAGS=[
		"-mcpu=%s" % env.BoardConfig().get("build.cpu"),
		"-mthumb",
		"-mthumb-interwork",
		"-nostartfiles",
		"-lm",
		"-lstdc++",
		"-Wl,-Map=firmware.map",
        "--specs=nosys.specs",
		"-Wl,--gc-sections",
	],

    
	LIBPATH=[join(FRAMEWORK_DIR, "variants", variant, "ld")],

    LIBS=["gcc", "m"]
)


# copy CCFLAGS to ASFLAGS (-x assembler-with-cpp mode)
env.Append(ASFLAGS=env.get("CCFLAGS", [])[:])



# remap ldscript
env.Replace(
		LDSCRIPT_PATH=ldscript,
		_LIBFLAGS="-Wl,--whole-archive, ${_stripixes(LIBLINKPREFIX, LIBS, LIBLINKSUFFIX, LIBPREFIXES, LIBSUFFIXES, __env__)} -Wl,--no-whole-archive",
		UPLOADER=platform.get_package_dir("tool-elkrem"),
		UPLOADCMD='node "$UPLOADER" --board '+"$BOARD_MCU"+' --binary '+"$SOURCE "+ (('--partitions '+env['FLASH_EXTRA_IMAGES'][1][1]) if (env["BOARD_MCU"]=='esp32') else "") +' --host ' + "$UPLOAD_PORT"
	)

#
# Target: Build Core Library
#

libs = []

if "build.variant" in board:
    env.Append(
        CPPPATH=[join(FRAMEWORK_DIR, "variants", variant)]
    )
    libs.append(env.BuildLibrary(
        join("$BUILD_DIR", "FrameworkArduinoVariant"),
        join(FRAMEWORK_DIR, "variants", variant)
    ))

libs.append(env.BuildLibrary(
    join("$BUILD_DIR", "FrameworkArduino"),
    join(FRAMEWORK_DIR, "cores", "elkrem")
))

env.Prepend(LIBS=libs)
