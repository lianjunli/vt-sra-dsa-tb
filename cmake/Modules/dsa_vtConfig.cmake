INCLUDE(FindPkgConfig)
PKG_CHECK_MODULES(PC_DSA_VT dsa_vt)

FIND_PATH(
    DSA_VT_INCLUDE_DIRS
    NAMES dsa_vt/api.h
    HINTS $ENV{DSA_VT_DIR}/include
        ${PC_DSA_VT_INCLUDEDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/include
          /usr/local/include
          /usr/include
)

FIND_LIBRARY(
    DSA_VT_LIBRARIES
    NAMES gnuradio-dsa_vt
    HINTS $ENV{DSA_VT_DIR}/lib
        ${PC_DSA_VT_LIBDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/lib
          ${CMAKE_INSTALL_PREFIX}/lib64
          /usr/local/lib
          /usr/local/lib64
          /usr/lib
          /usr/lib64
)

INCLUDE(FindPackageHandleStandardArgs)
FIND_PACKAGE_HANDLE_STANDARD_ARGS(DSA_VT DEFAULT_MSG DSA_VT_LIBRARIES DSA_VT_INCLUDE_DIRS)
MARK_AS_ADVANCED(DSA_VT_LIBRARIES DSA_VT_INCLUDE_DIRS)

