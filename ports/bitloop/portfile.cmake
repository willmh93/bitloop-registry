# portfile.cmake

# 1. Fetch the Bitloop source from GitHub
vcpkg_from_github(
    OUT_SOURCE_PATH  SOURCE_PATH
    REPO             willmh93/bitloop
    REF              v${VERSION}
    SHA512           a8c583f5bc99b78b4b6295996679fb2e6bdf2e6c2ef2371a382ef2c67a6dae018f63908ceddb41c9534a0a35599ad11676c3ebb3e8c296031c21c5c04d208345
)

vcpkg_check_features(OUT_FEATURE_OPTIONS FEATURE_OPTS
    FEATURES
        ffmpeg        BITLOOP_WITH_FFMPEG
        ffmpeg-x265   BITLOOP_WITH_FFMPEG
        ffmpeg-x265   BITLOOP_WITH_FFMPEG_X265
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
