cmake_minimum_required(VERSION 3.14)
project(feelink)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Optional: pick up vcpkg toolchain automatically
if(DEFINED ENV{VCPKG_ROOT})
    set(CMAKE_TOOLCHAIN_FILE "$ENV{VCPKG_ROOT}/scripts/buildsystems/vcpkg.cmake"
        CACHE STRING "Vcpkg toolchain file")
endif()

# Headers
include_directories(include)

# Sources
set(SOURCES
    src/main.cpp
    src/network.cpp
    src/bridge.cpp
    src/ring_buffer.cpp
    src/Utils.cpp
)

add_executable(feelink ${SOURCES})

# Dependencies
find_package(asio CONFIG REQUIRED)
find_package(nlohmann_json CONFIG REQUIRED)

target_link_libraries(feelink PRIVATE asio nlohmann_json::nlohmann_json)

# Windows needs ws2_32 for sockets (MSVC)
if (WIN32)
    target_link_libraries(feelink PRIVATE ws2_32)
endif()
