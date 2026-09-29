cmake_minimum_required(VERSION 3.25)
project(riscv-emu LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

option(ENABLE_SANITIZERS "ASan + UBSan" OFF)

add_executable(emu
    emu/main.cpp
    emu/decode/decoder.cpp
    emu/exec/execute.cpp
    emu/run/run.cpp
    emu/run/syscall.cpp
)
target_include_directories(emu PRIVATE emu)
target_compile_options(emu PRIVATE -Wall -Wextra -Wpedantic -Werror)

if(ENABLE_SANITIZERS)
  target_compile_options(emu PRIVATE -fsanitize=address,undefined -fno-omit-frame-pointer)
  target_link_options(emu PRIVATE -fsanitize=address,undefined)
endif() 