vcpkg_from_github(
    OUT_SOURCE_PATH SOURCE_PATH
    REPO willmh93/fltx
    REF "v${VERSION}"
    SHA512 2ce8f28917bfe922913ce0dbcd2adf9733b83fee517f049680c3a16d035d9a6c49387329cedaa02770043b368c757252118f5abeb1714cb93ff91361f84e9c59
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