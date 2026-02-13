# portfile.cmake

# 1. Fetch the Bitloop source from GitHub
vcpkg_from_github(
    OUT_SOURCE_PATH  SOURCE_PATH
    REPO             willmh93/bitloop
    REF              v${VERSION}
    SHA512           d7ae2531790abf5f57b68576f667a543f0bbca17025df9cd623f7bbd45f556af0ce383029b0ad63d9db9ee144b0bb8099c34287b730247adce68c8ed327f4c43
)

vcpkg_check_features(OUT_FEATURE_OPTIONS FEATURE_OPTS
    FEATURES
        ffmpeg       BITLOOP_WITH_FFMPEG
        ffmpeg-x265  BITLOOP_WITH_FFMPEG_X265
)

# If ffmpeg-x265 is selected, also force BITLOOP_WITH_FFMPEG=ON
if(BITLOOP_WITH_FFMPEG_X265)
    list(APPEND FEATURE_OPTS -DBITLOOP_WITH_FFMPEG=ON)
endif()

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
