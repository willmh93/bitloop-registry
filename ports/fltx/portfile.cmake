vcpkg_from_github(
    OUT_SOURCE_PATH SOURCE_PATH
    REPO willmh93/fltx
    REF "v${VERSION}"
    SHA512 802522cb0696080a6b5fdf34ebd0754afb43fe87cdfe4aa1a43d9894f81381636e9d6203fddba183b9a573856748be24079ff3f9356caa453163f4a478648421
    HEAD_REF main
)

vcpkg_cmake_configure(
    SOURCE_PATH "${SOURCE_PATH}"
    OPTIONS
        -DFLTX_BUILD_TESTS=OFF
        -DFLTX_BUILD_EXAMPLES=OFF
        -DFLTX_BUILD_ISOLATED=OFF
        -DBUILD_TESTING=OFF
)

vcpkg_cmake_install()

vcpkg_cmake_config_fixup(
    PACKAGE_NAME fltx
    CONFIG_PATH lib/cmake/fltx
)

file(REMOVE_RECURSE "${CURRENT_PACKAGES_DIR}/debug/include")
vcpkg_copy_pdbs()
file(INSTALL "${CMAKE_CURRENT_LIST_DIR}/usage" DESTINATION "${CURRENT_PACKAGES_DIR}/share/${PORT}")
vcpkg_install_copyright(FILE_LIST "${SOURCE_PATH}/LICENSE")
