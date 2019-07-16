cmake_minimum_required(VERSION 2.8.9)
set (CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=gnu++11 -static -O0 -ggdb3 -Wall -DBOOST_LOG_DYN_LINK -DBOOST_LOG_USE_NATIVE_SYSLOG")
project (nvmfhost)

include_directories(${CMAKE_SOURCE_DIR}/../../../dpdk/lib/librte_eal/common/include/)

include_directories(${CMAKE_SOURCE_DIR}/../../../dpdk/build/include/)

include_directories(${CMAKE_SOURCE_DIR}/../../../include/)

include_directories(${CMAKE_SOURCE_DIR})

set(COMMLIBS uuid numa pthread dl)

add_executable(nvmfhost main.cpp)
link_directories(${CMAKE_SOURCE_DIR}/../../../build/lib/ ${CMAKE_SOURCE_DIR}/../../../dpdk/build/lib/)
target_link_libraries(nvmfhost ${COMMLIBS} ${CMAKE_SOURCE_DIR}/../../../build/lib/libspdk_env_dpdk.a ${CMAKE_SOURCE_DIR}/../../../dpdk/build/lib/librte_eal.a) 
