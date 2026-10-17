cmake_minimum_required(VERSION 3.25)
project(riscv-emu LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

option(ENABLE_SANITIZERS "ASan + UBSan" OFF)

add_library(emu_core
    emu/decode/decoder.cpp
    emu/exec/execute.cpp
    emu/run/run.cpp
    emu/run/syscall.cpp
)
target_include_directories(emu_core PUBLIC emu)
target_compile_options(emu_core PUBLIC -Wall -Wextra -Wpedantic -Werror)

if(ENABLE_SANITIZERS)
  target_compile_options(emu_core PUBLIC -fsanitize=address,undefined -fno-omit-frame-pointer)
  target_link_options(emu_core PUBLIC -fsanitize=address,undefined)
endif()

add_executable(emu emu/main.cpp)
target_link_libraries(emu PRIVATE emu_core)

# Tests
include(FetchContent)
FetchContent_Declare(doctest
    URL https://github.com/doctest/doctest/archive/refs/tags/v2.4.12.tar.gz
    DOWNLOAD_EXTRACT_TIMESTAMP TRUE)
FetchContent_MakeAvailable(doctest)

enable_testing()
add_executable(emu_tests tests/test_execute.cpp)
target_link_libraries(emu_tests PRIVATE emu_core doctest::doctest)
add_test(NAME emu_tests COMMAND emu_tests)