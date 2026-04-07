vcpkg_from_github(
    OUT_SOURCE_PATH SOURCE_PATH
    REPO willmh93/fltx
    REF "v${VERSION}"
    SHA512 f59c5f966b11087212f8b850e4379f859bd0edf9e16ffacfd4cdb154a5bfb6d3eccf20828c257caa37c4674c9098bb0f5cd124b9b86804d641ccd20a79d13498
    HEAD_REF main
)

vcpkg_cmake_configure(
    SOURCE_PATH "${SOURCE_PATH}"
)

vcpkg_cmake_install()

vcpkg_cmake_config_fixup(
    PACKAGE_NAME fltx
    CONFIG_PATH lib/cmake/fltx
)

file(REMOVE_RECURSE "${CURRENT_PACKAGES_DIR}/debug")
file(INSTALL "${CMAKE_CURRENT_LIST_DIR}/usage" DESTINATION "${CURRENT_PACKAGES_DIR}/share/${PORT}")
vcpkg_install_copyright(FILE_LIST "${SOURCE_PATH}/LICENSE")