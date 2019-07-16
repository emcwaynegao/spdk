cmake_minimum_required(VERSION 2.8.9)
set (CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=gnu++11 -static -O0 -ggdb3 -Wall -DBOOST_LOG_DYN_LINK -DBOOST_LOG_USE_NATIVE_SYSLOG")
project (nvmfhost)

include_directories(/home/wayne/delivery/spdk/dpdk/lib/librte_eal/common/include/)

include_directories(/home/wayne/delivery/spdk/dpdk/build/include/)

include_directories(/home/wayne/delivery/spdk/include/)

include_directories(${CMAKE_SOURCE_DIR})

set(COMMLIBS uuid numa pthread dl)

add_executable(nvmfhost main.cpp)

target_link_libraries(nvmfhost ${COMMLIBS})
