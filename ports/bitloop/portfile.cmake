# portfile.cmake

include(vcpkg_common_functions)

# 1. Fetch the Bitloop source from GitHub
vcpkg_from_github(
    OUT_SOURCE_PATH  SOURCE_PATH
    REPO             willmh93/bitloop
    REF              v${PORT_VERSION_STRING}
    SHA512           61c7955c648016c39777ee6f6294e25f9d5345564291dd0121801510987147121af92c9c57f51e0e87e20dfa3f67be2558d26d1d2f35757f8df2262a1432a80e
)

# 3. Configure your Bitloop
vcpkg_configure_cmake(
  SOURCE_PATH    "${SOURCE_PATH}/framework"
  PREFER_NINJA
  OPTIONS
    "-DCMAKE_POSITION_INDEPENDENT_CODE=ON"
)

# 4. Install it into vcpkg’s staging area
vcpkg_install_cmake()

# 5. Export the targets so find_package(bitloop) works
vcpkg_fixup_cmake_targets(CONFIG_PATH share/bitloop)
