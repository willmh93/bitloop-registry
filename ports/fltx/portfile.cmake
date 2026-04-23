vcpkg_from_github(
    OUT_SOURCE_PATH SOURCE_PATH
    REPO willmh93/fltx
    REF "v${VERSION}"
    SHA512 94b5dd44646f64d12babe3ef693fccbd7b0c0ea50b86fb9d5563b4a5556ca4ad209af6145545193feeb4aa0e3a5ad067ba7557ac14ad22d4eb77d2c4bea1db54
    HEAD_REF main
)

vcpkg_cmake_configure(
    SOURCE_PATH "${SOURCE_PATH}"
    OPTIONS
        -DFLTX_BUILD_TESTS=OFF
        -DFLTX_BUILD_EXAMPLES=OFF
        -DBUILD_TESTING=OFF
)

vcpkg_cmake_install()

vcpkg_cmake_config_fixup(
    PACKAGE_NAME fltx
    CONFIG_PATH lib/cmake/fltx
)

file(REMOVE_RECURSE "${CURRENT_PACKAGES_DIR}/debug")
file(INSTALL "${CMAKE_CURRENT_LIST_DIR}/usage" DESTINATION "${CURRENT_PACKAGES_DIR}/share/${PORT}")
vcpkg_install_copyright(FILE_LIST "${SOURCE_PATH}/LICENSE")