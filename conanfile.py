from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps
from conan.tools.files import get
from conan.tools.build import check_max_cppstd, check_min_cppstd


class mysqlcppconnRecipe(ConanFile):
    name = "mysqlcppconn"
    version = "1.0"
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
               "with_jdbc": [True, False],
               "with_lz4": ["system", "bundled"],
               "with_tests": [True, False],
               }
    
    default_options = { 
                       "shared": False, 
                       "fPIC": True,
                       "with_jdbc": False,
                       "with_lz4": "bundled",
                       "with_tests": False
                       }
    
    generators = "CMakeDeps"

    # Sources are located in the same place as this recipe, copy them to the recipe
    # exports_sources = "CMakeLists.txt", "src/*", "include/*"
    
    def validate(self):
        check_min_cppstd(self, "17")
    
    def requirements(self):
        self.requires("lz4/1.9.4", visible=True, force=True, libs=True)
        self.requires("openssl/3.2.2", visible=True, force=True, libs=True)
        self.requires("boost/1.85.0", visible=True, force=True, libs=True)
        # self.requires("libmysqlclient/8.1.0", libs=True)
    
    def source(self):
        get(self, "https://github.com/mysql/mysql-connector-cpp/archive/refs/tags/9.0.0.zip", strip_root=True)

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self)
    
    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_SHARED_LIBS"] = False
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libdirs = ["lib", "lib64"]
        self.cpp_info.includedirs = ["include"]
        if not self.options.shared:
            self.cpp_info.libs = ["mysqlcppconnx"]
        else:
            self.cpp_info.libs = ["mysqlcppconnx-static"]

        self.cpp_info.set_property("cmake_target_name", "mysqlcppconn::cppconn")

