# portfile.cmake

# 1. Fetch the Bitloop source from GitHub
vcpkg_from_github(
    OUT_SOURCE_PATH  SOURCE_PATH
    REPO             willmh93/bitloop
    REF              v${VERSION}
    SHA512           d996438ae8b7083edd2e640848a83dcd3670fb5fa4c628ff16e9596e807666239a49a1a8ce81c04d4bf44d407a3e9ad5402f94c69c71e0ce5ba12ad112b7c75a
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
