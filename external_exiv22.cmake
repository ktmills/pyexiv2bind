include(ExternalProject)
ExternalProject_Add(project_zlib
        URL https://zlib.net/zlib-1.2.11.tar.gz
        URL_HASH SHA256=c3e5e9fdd5004dcb542feda5ee4f0ff0744628baf8ed2dd5d66f8ca1197cb1a1
        CMAKE_ARGS
            -DCMAKE_INSTALL_PREFIX=<INSTALL_DIR>
            -DCMAKE_BUILD_TYPE=Release

        BUILD_BYPRODUCTS
            <INSTALL_DIR>/lib/zlib${CMAKE_STATIC_LIBRARY_SUFFIX}
            <INSTALL_DIR>/lib/zlibstatic${CMAKE_STATIC_LIBRARY_SUFFIX}
            <INSTALL_DIR>/bin/zlibs${CMAKE_SHARED_LIBRARY_SUFFIX}
        )
ExternalProject_Get_Property(project_zlib install_dir)
add_library(zlib::zlib STATIC IMPORTED)
add_dependencies(zlib::zlib project_zlib)
set_target_properties(zlib::zlib PROPERTIES
        INCLUDE_DIRECTORIES ${install_dir}/include
        IMPORTED_LOCATION_RELEASE ${install_dir}/lib/${CMAKE_STATIC_LIBRARY_PREFIX}zlibstatic${CMAKE_STATIC_LIBRARY_SUFFIX}
        )

###########################################################################################
ExternalProject_Add(project_libexpat
        URL https://github.com/libexpat/libexpat/archive/R_2_2_3.zip
        SOURCE_SUBDIR expat
        CMAKE_ARGS
        -DBUILD_examples=off
        -DBUILD_shared=off
        -DBUILD_tests=off
        # -DBUILD_tests=$<$<CONFIG:Debug>:1, 0>
        -DBUILD_tools=off
        -DCMAKE_INSTALL_PREFIX=<INSTALL_DIR>
        -DCMAKE_BUILD_TYPE=$<CONFIG>
        -DCMAKE_EXPORT_COMPILE_COMMANDS=OFF

        # TEST_BEFORE_INSTALL $<$<CONFIG:Debug>1, 0>
        LOG_CONFIGURE 1
        BUILD_BYPRODUCTS
            <INSTALL_DIR>/lib/expat${CMAKE_STATIC_LIBRARY_SUFFIX}
        )
ExternalProject_Get_Property(project_libexpat install_dir)
add_library(libexpat::libexpat STATIC IMPORTED)
add_dependencies(libexpat::libexpat project_libexpat)
set_target_properties(libexpat::libexpat PROPERTIES
        INCLUDE_DIRECTORIES ${install_dir}/include
        IMPORTED_LOCATION_DEBUG ${install_dir}/lib/${CMAKE_STATIC_LIBRARY_PREFIX}expatd${CMAKE_STATIC_LIBRARY_SUFFIX}
        IMPORTED_LOCATION_RELEASE ${install_dir}/lib/${CMAKE_STATIC_LIBRARY_PREFIX}expat${CMAKE_STATIC_LIBRARY_SUFFIX}
        )
###################################################
ExternalProject_Add(project_gtest
        URL https://github.com/google/googletest/archive/release-1.8.0.tar.gz
        CMAKE_ARGS
        -DCMAKE_INSTALL_PREFIX=<INSTALL_DIR>
        -DBUILD_GMOCK=OFF
        -DBUILD_GTEST=ON
        -DBUILD_SHARED_LIBS=ON
#        -Dgtest_force_shared_crt=ON
        -DCMAKE_BUILD_TYPE=$<CONFIG>
        BUILD_BYPRODUCTS
            <INSTALL_DIR>/lib/gtest${CMAKE_SHARED_LIBRARY_SUFFIX}
            <INSTALL_DIR>/lib/gtest${CMAKE_LINK_LIBRARY_SUFFIX}
            <INSTALL_DIR>/lib/gtest_main${CMAKE_SHARED_LIBRARY_SUFFIX}
            <INSTALL_DIR>/lib/gtest_main${CMAKE_LINK_LIBRARY_SUFFIX}
        )

ExternalProject_Get_Property(project_gtest install_dir)
add_library(googletest::googletest STATIC IMPORTED)
add_library(googletest::googletest_main STATIC IMPORTED)
set_target_properties(googletest::googletest PROPERTIES
        INCLUDE_DIRECTORIES ${install_dir}/include
        IMPORTED_LOCATION ${install_dir}/lib/gtest${CMAKE_STATIC_LIBRARY_SUFFIX}
        )
set_target_properties(googletest::googletest_main PROPERTIES
        IMPORTED_LOCATION ${install_dir}/lib/gtest_main${CMAKE_STATIC_LIBRARY_SUFFIX}
        )

set(googletest_root ${install_dir})
add_dependencies(googletest::googletest project_gtest)

#########################################################################################
ExternalProject_Add(project_libexiv2
        GIT_REPOSITORY https://github.com/Exiv2/exiv2.git
        CMAKE_ARGS
            -DEXIV2_ENABLE_PNG:BOOL=OFF
        CMAKE_ARGS
            -DCMAKE_BUILD_TYPE=$<CONFIG>
            -DEXIV2_BUILD_EXIV2_COMMAND:BOOL=ON
            -DEXIV2_ENABLE_DYNAMIC_RUNTIME=ON
            -DCMAKE_INSTALL_PREFIX=<INSTALL_DIR>
            -DBUILD_SHARED_LIBS:BOOL=OFF
            -DEXIV2_BUILD_SAMPLES:BOOL=OFF
#            -DEXIV2_ENABLE_TOOLS:BOOL=OFF
#            -DEXIV2_ENABLE_CURL:BOOL=ON
#            -DEXIV2_ENABLE_PNG:BOOL=OFF
            -DEXIV2_ENABLE_XMP:BOOL=ON
            -DEXIV2_BUILD_UNIT_TESTS=ON
            -DGTEST_ROOT="${googletest_root}"
            -DGTEST_INCLUDE_DIR=$<TARGET_PROPERTY:googletest::googletest,INCLUDE_DIRECTORIES>
            -DGTEST_LIBRARY=$<TARGET_FILE:googletest::googletest>
            -DGTEST_MAIN_LIBRARY=$<TARGET_FILE:googletest::googletest_main>
            -DEXIV2_ENABLE_WIN_UNICODE:BOOL=ON
            -DEXPAT_INCLUDE_DIR=$<TARGET_PROPERTY:libexpat::libexpat,INCLUDE_DIRECTORIES>
            -DEXPAT_LIBRARY=$<TARGET_FILE:libexpat::libexpat>
            -DZLIB_INCLUDE_DIR=$<TARGET_PROPERTY:zlib::zlib,INCLUDE_DIRECTORIES>
            -DZLIB_LIBRARY=$<TARGET_FILE:zlib::zlib>
            # -DICONV_INCLUDE_DIR=""
            # -DICONV_LIBRARY=""
        DEPENDS
            project_libexpat
            project_zlib
            project_gtest

        BUILD_BYPRODUCTS
            <INSTALL_DIR>/lib/exiv2${CMAKE_STATIC_LIBRARY_SUFFIX}
            <INSTALL_DIR>/lib/xmp${CMAKE_STATIC_LIBRARY_SUFFIX}
        )
ExternalProject_Add_Step(project_libexiv2 add_gtest_libs
        COMMENT "Adding GoogleTest libraries to BUILD PATH"
        COMMAND ${CMAKE_COMMAND} -E copy_directory ${googletest_root}/lib/ <BINARY_DIR>/bin/
        DEPENDEES build
        )
ExternalProject_Add_Step(project_libexiv2 run_gtest
        COMMENT "Running googletest"
        COMMAND unit_tests${CMAKE_EXECUTABLE_SUFFIX}
        WORKING_DIRECTORY <BINARY_DIR>/bin
        ALWAYS 1
        DEPENDEES add_gtest_libs
        DEPENDERS install
        )
add_library(exiv2lib STATIC IMPORTED)

ExternalProject_Get_Property(project_libexiv2 install_dir)

set_target_properties(exiv2lib PROPERTIES
        INCLUDE_DIRECTORIES ${install_dir}/include
        IMPORTED_LOCATION_DEBUG ${install_dir}/lib/${CMAKE_STATIC_LIBRARY_PREFIX}exiv2d${CMAKE_STATIC_LIBRARY_SUFFIX}
        IMPORTED_LOCATION_RELEASE ${install_dir}/lib/${CMAKE_STATIC_LIBRARY_PREFIX}exiv2${CMAKE_STATIC_LIBRARY_SUFFIX}
        INTERFACE_LINK_LIBRARIES "${install_dir}/lib/${CMAKE_STATIC_LIBRARY_PREFIX}xmp${CMAKE_STATIC_LIBRARY_SUFFIX};$<TARGET_FILE:libexpat::libexpat>"
        CXX_STANDARD 98
        )

add_dependencies(exiv2lib project_libexiv2)
#add_library(exiv2lib ALIAS exiv2::exiv2)