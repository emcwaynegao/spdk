cmake_minimum_required(VERSION 2.8.9)
set (CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=gnu++11 -static -O0 -ggdb3 -Wall -DBOOST_LOG_DYN_LINK -DBOOST_LOG_USE_NATIVE_SYSLOG")
project (nvmfhost)

include_directories(${CMAKE_SOURCE_DIR})

set(COMMLIBS uuid numa pthread dl
    spdk_nvme spdk_util spdk_env_dpdk dpdk spdk_log spdk_sock boost_thread boost_system boost_log_setup boost_log)

add_executable(nvmfhost main.cpp)

target_link_libraries(nvmfhost ${COMMLIBS})
