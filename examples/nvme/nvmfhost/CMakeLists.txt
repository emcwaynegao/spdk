project(nvmfhost)
cmake_minimum_required(VERSION 3.1)
SET(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++14 -fno-strict-aliasing -march=native -m64 -D_GNU_SOURCE -fPIC -fstack-protector -DNDEBUG")
SET(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} -Wl,-z,relro,-z,now -Wl,-z,noexecstack")

#set (CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=gnu++11 -static -O0 -ggdb3 -Wall -DBOOST_LOG_DYN_LINK -DBOOST_LOG_USE_NATIVE_SYSLOG")

include_directories(${CMAKE_SOURCE_DIR}/../../../dpdk/lib/librte_eal/common/include/)

include_directories(${CMAKE_SOURCE_DIR}/../../../dpdk/build/include/)

include_directories(${CMAKE_SOURCE_DIR}/../../../include)

include_directories(${CMAKE_SOURCE_DIR})
link_directories(${CMAKE_SOURCE_DIR}/../../../build/lib)
set(COMMLIBS uuid numa pthread dl)

link_libraries(spdk_app_rpc)
link_libraries(spdk_bdev)
link_libraries(spdk_bdev_aio)
link_libraries(spdk_bdev_error)
link_libraries(spdk_bdev_gpt)
link_libraries(spdk_bdev_lvol)
link_libraries(spdk_bdev_malloc)
link_libraries(spdk_bdev_null)
link_libraries(spdk_bdev_nvme)
link_libraries(spdk_bdev_passthru)
link_libraries(spdk_bdev_raid)
link_libraries(spdk_bdev_rpc)
link_libraries(spdk_bdev_split)
link_libraries(spdk_bdev_virtio)
link_libraries(spdk_blob)
link_libraries(spdk_blob_bdev)
link_libraries(spdk_blobfs)
link_libraries(spdk_conf)
link_libraries(spdk_copy)
link_libraries(spdk_copy_ioat)
link_libraries(spdk_event)
link_libraries(spdk_event_copy)
link_libraries(spdk_event_iscsi)
link_libraries(spdk_event_nbd)
link_libraries(spdk_event_net)
link_libraries(spdk_event_nvmf)
link_libraries(spdk_event_scsi)
link_libraries(spdk_event_vhost)
link_libraries(spdk_ioat)
link_libraries(spdk_iscsi)
link_libraries(spdk_json)
link_libraries(spdk_jsonrpc)
link_libraries(spdk_log)
link_libraries(spdk_log_rpc)
link_libraries(spdk_lvol)
link_libraries(spdk_nbd)
link_libraries(spdk_net)
link_libraries(spdk_notify)
link_libraries(spdk_nvme)
link_libraries(spdk_nvmf)
link_libraries(spdk_rpc)
link_libraries(spdk_scsi)
link_libraries(spdk_sock)
link_libraries(spdk_sock_posix)
link_libraries(spdk_thread)
link_libraries(spdk_trace)
link_libraries(spdk_trace_rpc)
link_libraries(spdk_util)
link_libraries(spdk_ut_mock)
link_libraries(spdk_vhost)
link_libraries(spdk_virtio)
link_libraries(spdk_env_dpdk)

set(THREADS_PREFER_PTHREAD_FLAG ON)
find_package(Threads REQUIRED)
link_libraries(Threads::Threads)

SET(CMAKE_EXPORT_COMPILE_COMMANDS ON)


add_executable(nvmfhost main.cpp)
link_directories(${CMAKE_SOURCE_DIR}/../../../build/lib/ ${CMAKE_SOURCE_DIR}/../../../dpdk/build/lib/)
target_link_libraries(nvmfhost ${COMMLIBS} ${CMAKE_SOURCE_DIR}/../../../build/lib/libspdk_env_dpdk.a
        ${CMAKE_SOURCE_DIR}/../../../dpdk/build/lib/librte_eal.a
        ${CMAKE_SOURCE_DIR}/../../../dpdk/build/lib/librte_mempool.a
        ${CMAKE_SOURCE_DIR}/../../../dpdk/build/lib/librte_ring.a numa
	${CMAKE_SOURCE_DIR}/../../../dpdk/build/lib/librte_pci.a
	${CMAKE_SOURCE_DIR}/../../../dpdk/build/lib/librte_bus_pci.a
	${CMAKE_SOURCE_DIR}/../../../dpdk/build/lib/librte_bus_vdev.a
	${CMAKE_SOURCE_DIR}/../../../dpdk/build/lib/librte_mempool_ring.a
	${CMAKE_SOURCE_DIR}/../../../dpdk/build/lib/librte_kvargs.a)
