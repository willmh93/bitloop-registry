# portfile.cmake

include(vcpkg_common_functions)

# 1. Fetch the Bitloop source from GitHub
vcpkg_from_github(
    OUT_SOURCE_PATH  SOURCE_PATH
    REPO             willmh93/bitloop
    REF              v${VERSION}
    SHA512           a02b7c355bae5a31816330cc87abab0910beb2b3cf4a25b9187b59a2d6142a4d544efaac03d6e5010e5915c012a2901a948a6e0cbd130ca1fde30e712af8c9ec
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
