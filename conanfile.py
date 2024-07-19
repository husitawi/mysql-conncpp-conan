import os
from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps
from conan.tools.files import get
from conan.tools.build import check_max_cppstd, check_min_cppstd
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime
from conan.tools.files import rename, get, apply_conandata_patches, replace_in_file, rmdir, rm, export_conandata_patches, mkdir

required_conan_version = ">=2.0"

class mysqlcppconnRecipe(ConanFile):
    name = "mysqlcppconn"
    version = "9.0"
    package_type = "library"
    short_paths = True

    # Optional metadata
    license = "GPL-2.0"
    author = "Hussein Itawi hus@michealscottsoftwarecompany.com"
    url = "https://github.com/conan-io/conan-center-index"
    description = "A MySQL client library for C++ development"
    topics = ("mysql", "sql", "connector", "database", "c++", "cpp")

    # Binary configuration
    settings = "os", "compiler", "build_type", "arch"
    options = { 
               "shared": [True, False], 
               "fPIC": [True, False],
               }

    default_options = { "shared": False, "fPIC": True }

    generators = "CMakeDeps"

    # Sources are located in the same place as this recipe, copy them to the recipe
    # exports_sources = "CMakeLists.txt", "src/*", "include/*"
    
    def export_sources(self):
        export_conandata_patches(self)
    
    def validate(self):
        check_min_cppstd(self, "17")
    
    def requirements(self):
        # self.requires("lz4/1.9.4", libs=True, force=True)
        self.requires("openssl/3.2.2", libs=True, headers=True, force=True)
        # self.requires("boost/1.85.0", libs=True, force=True)
        # self.requires("libmysqlclient/8.1.0")
    
    def source(self):
        get(self, **self.conan_data["sources"][self.version])

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self)
        
    def _package_folder_dep(self, dep):
        return self.dependencies[dep].package_folder.replace("\\", "/")

    def _include_folder_dep(self, dep):
        return self.dependencies[dep].cpp_info.includedirs[0].replace("\\", "/")

    def _lib_folder_dep(self, dep):
        return self.dependencies[dep].cpp_info.libdirs[0].replace("\\", "/")
    
    def generate(self):
        tc = CMakeToolchain(self)

        # tc.variables["CMAKE_BUILD_TYPE"] = "Release"
        # tc.cache_variables["CMAKE_BUILD_TYPE"] = "Release"
        
        # if self.options.shared:
        #     tc.cache_variables["BUILD_SHARED_LIBS"] = "ON"
        #     tc.cache_variables["BUILD_STATIC"] = "OFF"
        #     self.options["openssl"].shared = True
        # else:
        #     tc.cache_variables["BUILD_SHARED_LIBS"] = "OFF"
        #     tc.cache_variables["BUILD_STATIC"] = "ON"
        #     self.options["openssl"].shared = False

        # tc.cache_variables["STATIC_MSVCRT"] = "ON"
        
        # set(OPENSSL_USE_STATIC_LIBS TRUE)
        tc.cache_variables["OPENSSL_USE_STATIC_LIBS"] = "ON"

        # # LZ4 patches
        # tc.cache_variables["LZ4_DIR"] = self._package_folder_dep("lz4")

        # # Boost patches
        # tc.cache_variables["BOOST_DIR"] = self._package_folder_dep("boost")

        # # OpenSSL patches
        tc.cache_variables["WITH_SSL"] = self._package_folder_dep("openssl")
        # set OPENSSL_LIB_DIR
        tc.cache_variables["OPENSSL_LIB_DIR"] = self._lib_folder_dep("openssl")
        # Set OPENSSL ROOT DIR
        tc.cache_variables["OPENSSL_ROOT_DIR"] = self._package_folder_dep("openssl")
        
        # # if is_msvc(self):
        #     # tc.cache_variables["WINDOWS_RUNTIME_MD"] = not is_msvc_static_runtime(self)

        # # Protobuf patches
        # # tc.cache_variables["WITH_PROTOBUF"] = self._package_folder_dep("protobuf")

        # # General patches
        # tc.cache_variables["MYSQLCLIENT_STATIC_LINKING"] = "ON"
        # tc.cache_variables["BUNDLE_DEPENDENCIES"] = "ON"
        # # tc.cache_variables["BUILD_SHARED_LIBS"] = "OFF"
        # tc.cache_variables["BUILD_STATIC"] = "ON"
        
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        
        # # Patches
        # if self.settings.os == "Windows":
        #     self.cpp_info.system_libs.extend(["dnsapi", "secur32", "crypt32", "ws2_32", "advapi32", "user32", "bcrypt"])
        
        # if self.settings.os == "Windows":
        #     self.cpp_info.components["crypto"].system_libs.extend(["crypt32", "ws2_32", "advapi32", "user32", "bcrypt"])
        
        # self.cpp_info.system_libs.extend(["mysqlclient", "mysqlclient_r", "ws2_32", "advapi32", "user32", "bcrypt"])
        
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()
        
    def package_info(self):
        # Set the VS version
        msvc_toolset_version = self.settings.get_safe("compiler.toolset")
        msvc_version = self.settings.get_safe("compiler.version")

        if msvc_toolset_version:
            vs_version = msvc_toolset_version[1:3]
        elif msvc_version:
            vs_version = msvc_version[:2]
            if vs_version == "12":
                vs_version = "18"
            elif vs_version == "14":
                vs_version = "19"
        else:
            self.output.warn("MSVC_TOOLSET_VERSION or MSVC_VERSION not defined")
            vs_version = "unknown"

        self.output.info(f"VS Version: {vs_version}")
        self.vs_version = vs_version
        self.vs = f"vs{vs_version}"
        
        self.cpp_info.libdirs = ["lib", "lib64", "lib64/vs14"]
        self.cpp_info.includedirs = ["include"]
        if self.options.shared:
            self.cpp_info.libs = [f"mysqlcppconnx-2-{self.vs}"]
            # add crypt32 to system_libs
            self.cpp_info.system_libs.extend(["crypt32"])
        else:
            self.cpp_info.libs = ["mysqlcppconnx-static"]
            
        self.cpp_info.set_property("cmake_target_name", "mysqlcppconn::cppconn")

