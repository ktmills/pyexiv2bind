import os

from conans import ConanFile, CMake

class Exiv2BindConan(ConanFile):
    requires = [
        "Exiv2/0.27@piponazo/stable",
    ]
    settings = "os", "arch", "compiler", "build_type"

    generators = ["json"]
    default_options = {
        "Exiv2:shared": False
    }

    def imports(self):
        self.copy("*.dll", dst="bin", src="bin") # From bin to bin
        self.copy("*.dylib*", dst="bin", src="lib") # From lib to bin
        self.copy("*.a", dst="lib", src="lib")
        self.copy("*.lib", dst="lib", src="lib")
        self.copy("*", dst="include", src="include") # From lib to bin
    #
    # def configure(self):
    #     pass
        # if self.settings.os == "Linux":
        #     self.options["ffmpeg"].vorbis = False

    # def build(self):
    #     cmake = CMake(self)
    #     cmake_toolchain_file = os.path.join(self.build_folder, "conan_paths.cmake")
    #     assert os.path.exists(cmake_toolchain_file)
    #     cmake.definitions["CMAKE_TOOLCHAIN_FILE"] = cmake_toolchain_file
    #     cmake.configure()
    #     cmake.build()
