# portfile.cmake

# 1. Fetch the Bitloop source from GitHub
vcpkg_from_github(
    OUT_SOURCE_PATH  SOURCE_PATH
    REPO             willmh93/bitloop
    REF              v${VERSION}
    SHA512           e3b49792e7558e1af8c5a1a030b061dac47087ffa3e4c01ed23a9fa47b0cf44b5941a38aa45420b0d2cef68611bf40e68ac7c168ebedfea85c83464b2345093a
)

vcpkg_check_features(OUT_FEATURE_OPTIONS FEATURE_OPTS
    FEATURES
        ffmpeg        BITLOOP_WITH_FFMPEG
        ffmpeg-x265   BITLOOP_WITH_FFMPEG BITLOOP_WITH_FFMPEG_X265
)


# 3. Configure your Bitloop
vcpkg_configure_cmake(
  SOURCE_PATH    "${SOURCE_PATH}"
  PREFER_NINJA
  OPTIONS
    "-DCMAKE_POSITION_INDEPENDENT_CODE=ON"
    ${FEATURE_OPTS}
)

# 4. Install it into vcpkg’s staging area
vcpkg_install_cmake()

# 5. Export the targets so find_package(bitloop) works
vcpkg_fixup_cmake_targets(CONFIG_PATH share/bitloop)
