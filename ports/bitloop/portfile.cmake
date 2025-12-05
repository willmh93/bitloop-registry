# portfile.cmake

# 1. Fetch the Bitloop source from GitHub
vcpkg_from_github(
    OUT_SOURCE_PATH  SOURCE_PATH
    REPO             willmh93/bitloop
    REF              v${VERSION}
    SHA512           ad3c2a191fab25144bfa16619a5ad586e5665edc8966460947f7ec23b2461f72f42d104e31eecac5c57ad9da0cb731d81800fbdad3925e47a18058cafa3a5420
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
