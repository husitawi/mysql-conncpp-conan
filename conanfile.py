import os
from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps
from conan.tools.files import get, copy, save
from conan.tools.build import check_max_cppstd, check_min_cppstd
# from conan.tools.microsoft import is_msvc, is_msvc_static_runtime
from conan.tools.files import rename, get, apply_conandata_patches, replace_in_file, rmdir, rm, export_conandata_patches, mkdir
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime

required_conan_version = ">=1.64.1"

class MysqlCppConnRecipe(ConanFile):
    name = "mysql-concpp"
    version = "9.0.0"
    package_type = "library"
    short_paths = True

    # Optional metadata
    license = "GPL-2.0"
    author = "Hussein Itawi hus@michealscottsoftwarecompany.com"
    url = "https://github.com/husitawi/mysql-conncpp-conan"
    description = "A MySQL client library for C++ development"
    topics = ("mysql", "sql", "connector", "database", "c++", "cpp")

    # Binary configuration
    settings = "os", "compiler", "build_type", "arch"
    options = { 
               "shared": [True, False], 
               "fPIC": [True, False],
               }

    default_options = { "shared": False, "fPIC": True }

    # generators = "CMakeDeps"

    def export_sources(self):
        export_conandata_patches(self)
    
    def validate(self):
        check_min_cppstd(self, "17")
        
        # if self.settings.build_type == "Debug":
            # raise ConanInvalidConfiguration("Debug builds of the library are not available.")
    
    def requirements(self):
        self.requires("lz4/1.9.4", force=True)
        self.requires("openssl/3.2.2", force=True)
        self.requires("boost/1.85.0", force=True)
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

        # Random
        tc.cache_variables["BUILD_STATIC"] = not self.options.shared
        tc.cache_variables["BUILD_SHARED_LIBS"] = self.options.shared
        # tc.cache_variables["mysql-concpp_DIR"] = self.package
        
        if is_msvc(self):
            tc.cache_variables["WINDOWS_RUNTIME_MD"] = not is_msvc_static_runtime(self)
        # set(OPENSSL_USE_STATIC_LIBS TRUE)
        tc.cache_variables["OPENSSL_USE_STATIC_LIBS"] = "ON"
        # # LZ4 patches
        tc.cache_variables["WITH_LZ4"] = self._package_folder_dep("lz4")
        tc.cache_variables["LZ4_DIR"] = self._package_folder_dep("lz4")
        # Boost patches
        tc.cache_variables["BOOST_DIR"] = self._package_folder_dep("boost")
        # OpenSSL patches
        tc.cache_variables["WITH_SSL"] = self._package_folder_dep("openssl")
        # set OPENSSL_LIB_DIR
        tc.cache_variables["OPENSSL_LIB_DIR"] = self._lib_folder_dep("openssl")
        # Set OPENSSL ROOT DIR
        tc.cache_variables["OPENSSL_ROOT_DIR"] = self._package_folder_dep("openssl")
        
        tc.generate()
        
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()
        
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        
    def package_info(self):
        # Set the VS version
        if self.settings.os == "Windows":
            msvc_toolset_version = self.settings.get_safe("compiler.toolset")
            msvc_version = self.settings.get_safe("compiler.version")

            if msvc_toolset_version:
                vs_version = msvc_toolset_version[1:3]
            elif msvc_version:
                vs_version = msvc_version[:2]
                if vs_version == "18":
                    vs_version = "12"
                elif vs_version == "19":
                    vs_version = "14"
            else:
                self.output.warn("MSVC_TOOLSET_VERSION or MSVC_VERSION not defined")
                vs_version = "unknown"

            self.output.info(f"VS Version: {vs_version}")
            self.vs_version = vs_version
            self.vs = f"vs{vs_version}"
        
        self.cpp_info.libdirs = ["lib/vs14", "lib/debug/vs14", "lib64/vs14", "lib64/debug/vs14"]
        self.cpp_info.bindirs = ["lib64", "lib64/debug", "lib", "lib/debug"]
        # self.cpp_info.bindirs = ["lib64"]
        # self.cpp_info.libdirs = ["lib", "lib64", "lib64/vs14", "lib64/debug"]
        # self.cpp_info.includedirs = ["include"]
        # if self.options.shared:
        #     if self.settings.os == "Windows":
        #         self.cpp_info.libs = [f"mysqlcppconnx-2-{self.vs}"]
        #         # add crypt32 to system_libs
        #         self.cpp_info.system_libs.extend(["crypt32"])
        #     elif is_apple_os(self):
        #         self.cpp_info.libs = ["mysqlcppconnx"]
        #         self.cpp_info.system_libs.extend(["resolv"])
        #     else:
        #         self.cpp_info.libs = ["mysqlcppconnx"]
        # else:
        #     self.cpp_info.libs = ["mysqlcppconnx-static"]
        
        if is_apple_os(self):
            self.cpp_info.system_libs.extend(["resolv"])
        elif self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["m", "resolv"])
        
        target = "concpp-xdevapi" if self.options.shared else "concpp-xdevapi-static"
        target_alias = "concpp" if self.options.shared else "concpp-static"
        
        if self.settings.build_type == "Debug":
            target += "-debug"
            target_alias += "-debug"
        
        self.cpp_info.set_property("cmake_target_name", f"mysql::{target}")
        self.cpp_info.set_property("cmake_target_aliases", [f"mysql::{target_alias}"] )
        
        lib = "mysqlcppconnx" if self.options.shared else "mysqlcppconnx-static"
        if is_msvc(self) and not self.options.shared and is_msvc_static_runtime(self):
            lib = "mysqlcppconnx-static-mt"
        # elif self.options.shared and is_msvc(self):
            # lib = f"mysqlcppconnx-2-{self.vs}"
        
        self.cpp_info.libs = [lib]
        
        print(f"RESULTING LIB: {lib}")
        print(f"Resulting TARGET: {target}")
        
        if not self.options.shared:
            self.cpp_info.defines = ["MYSQL_STATIC"]
        
        self.cpp_info.set_property("cmake_find_package", "mysql-concpp")
        self.cpp_info.set_property("cmake_find_package_multi", "mysql-concpp")
        self.cpp_info.set_property("cmake_config_file", "mysql-concpp-config.cmake")
        
