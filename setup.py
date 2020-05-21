import os
import sys
import shutil
from setuptools import setup, Extension, Command
from setuptools.command.build_ext import build_ext
import platform
import subprocess
import sysconfig
from urllib import request
import tarfile
PACKAGE_NAME = "py3exiv2bind"
PYBIND11_DEFAULT_URL = \
    "https://github.com/pybind/pybind11/archive/v2.5.0.tar.gz"


class Exiv2Conan(Command):
    user_options = [
        ('conan-exec=', "c", 'conan executable')
    ]

    description = "Get the required dependencies from a Conan package manager"

    def initialize_options(self):
        self.conan_exec = None

    def finalize_options(self):
        if self.conan_exec is None:
            self.conan_exec = shutil.which("conan")
            if self.conan_exec is None:
                raise Exception("missing conan_exec")

    def run(self):
        clib_cmd = self.get_finalized_command("build_clib")
        build_ext_cmd = self.get_finalized_command("build_ext")
        build_dir = clib_cmd.build_temp
        if not os.path.exists(build_dir):
            os.makedirs(build_dir)
        install_command = [
            self.conan_exec,
            "install",
            "--build",
            "missing",
            "-if", os.path.abspath(build_dir),
            os.path.abspath(os.path.dirname(__file__))
        ]

        for extension in build_ext_cmd.extensions:
            extension.include_dirs.append(
                os.path.abspath(os.path.join(build_dir, "include"))
            )
            extension.library_dirs.append(
                os.path.abspath(os.path.join(build_dir, "lib"))
            )

        subprocess.check_call(install_command, cwd=build_dir)


class BuildExiv2Ext(build_ext):
    user_options = build_ext.user_options + [
        ('pybind11-url=', None,
         "Url to download Pybind11")
    ]

    def initialize_options(self):
        super().initialize_options()
        self.pybind11_url = None

    def finalize_options(self):
        self.pybind11_url = self.pybind11_url or PYBIND11_DEFAULT_URL
        super().finalize_options()

    def run(self):
        pybind11_include_path = self.get_pybind11_include_path()

        if pybind11_include_path is not None:
            self.include_dirs.append(pybind11_include_path)

        super().run()

    def find_missing_libraries(self, ext):
        missing_libs = []
        for lib in ext.libraries:
            if self.compiler.find_library_file(self.library_dirs, lib) is None:
                missing_libs.append(lib)
        return missing_libs

    def build_extension(self, ext):
        if self.compiler.compiler_type == "unix":
            ext.extra_compile_args.append("-std=c++14")
        else:
            ext.extra_compile_args.append("/std:c++14")

        missing = self.find_missing_libraries(ext)

        if len(missing) > 0:
            self.announce(f"missing required deps [{', '.join(missing)}]. "
                          f"Trying to get them with conan", 5)
            self.run_command("build_conan")
            ext.include_dirs.append(os.path.abspath(os.path.join(self.build_temp, "include")))
            ext.library_dirs.append(os.path.abspath(os.path.join(self.build_temp, "lib")))
            # self.compiler.find_library_file(
            #     [os.path.join(], "exiv2")

            # self.build_extension(ext)
            # return
            # missing = self.find_missing_libraries(ext)
            # if len(missing) > 0:
            #     print("I qiuote")
            #     exit(1)
        super().build_extension(ext)

    def get_pybind11_include_path(self):
        pybind11_archive_filename = os.path.split(self.pybind11_url)[1]

        pybind11_archive_downloaded = os.path.join(self.build_temp,
                                                   pybind11_archive_filename)

        pybind11_source = os.path.join(self.build_temp, "pybind11")
        if not os.path.exists(self.build_temp):
            os.makedirs(self.build_temp)

        if not os.path.exists(pybind11_source):
            if not os.path.exists(pybind11_archive_downloaded):
                self.announce("Downloading pybind11", level=5)
                request.urlretrieve(
                    self.pybind11_url, filename=pybind11_archive_downloaded)
                self.announce("pybind11 Downloaded", level=5)
            with tarfile.open(pybind11_archive_downloaded, "r") as tf:
                for f in tf:
                    if "pybind11.h" in f.name:
                        self.announce(
                            f"Extract pybind11.h to include path")

                    tf.extract(f, pybind11_source)
        for root, dirs, files in os.walk(pybind11_source):
            for f in files:
                if f == "pybind11.h":
                    return os.path.relpath(
                        os.path.join(root, ".."),
                        os.path.dirname(__file__)
                    )


# class Exiv2Ext(BuildCMakeExt):
#
#     def __init__(self, dist):
#         super().__init__(dist)
#         self.extra_cmake_options += [
#             "-Dpyexiv2bind_generate_venv:BOOL=OFF",
#             "-DBUILD_SHARED_LIBS:BOOL=OFF",
#             # "-DEXIV2_VERSION_TAG:STRING=11e66c6c9eceeddd2263c3591af6317cbd05c1b6",
#             "-DEXIV2_VERSION_TAG:STRING=0.27",
#             "-DBUILD_TESTING:BOOL=OFF",
#         ]


exiv2_extension = Extension(
    "py3exiv2bind.core",
    sources=[
        "py3exiv2bind/core/core.cpp",
        "py3exiv2bind/core/glue/ExifStrategy.cpp",
        "py3exiv2bind/core/glue/glue.cpp",
        "py3exiv2bind/core/glue/Image.cpp",
        "py3exiv2bind/core/glue/IPTC_Strategy.cpp",
        "py3exiv2bind/core/glue/XmpStrategy.cpp",
        "py3exiv2bind/core/glue/MetadataProcessor.cpp",
    ],
    libraries=[
        "exiv2",
        "xmp",
        "expat",
        "zlib",
        "Shell32"
    ],
    include_dirs=[
        "py3exiv2bind/core/glue"
    ],
    language='c++',
    # extra_compile_args=['-std=c++14'],

)

setup(
    packages=['py3exiv2bind'],
    python_requires=">=3.6",
    setup_requires=['pytest-runner'],
    test_suite="tests",
    tests_require=['pytest'],
    ext_modules=[exiv2_extension],
    cmdclass={
        "build_ext": BuildExiv2Ext,
        "build_conan": Exiv2Conan
    },

)
