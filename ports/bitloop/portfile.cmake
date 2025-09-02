# portfile.cmake

# 1. Fetch the Bitloop source from GitHub
vcpkg_from_github(
    OUT_SOURCE_PATH  SOURCE_PATH
    REPO             willmh93/bitloop
    REF              v${VERSION}
    SHA512           f02d39108790e6b11f88243f83af6c2ce9e32299ab1896815a58b074b9d1c1ccbb681deda5758c18b04b265309afb7131a72b1a2ef6750a749849782be839fb5
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
