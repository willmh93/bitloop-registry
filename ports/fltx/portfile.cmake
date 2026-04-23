vcpkg_from_github(
    OUT_SOURCE_PATH SOURCE_PATH
    REPO willmh93/fltx
    REF "v${VERSION}"
    SHA512 f562e3efbf78f23a8bd26777ea400b4c023bc8dd7768ed622a3195fb242b0e7017c4bf6b7ab94f74819b4bf8611fc5c32dbb39aee0b05ac53b60e731690dffd3
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