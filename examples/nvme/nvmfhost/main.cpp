#include <ctype.h>
#include <errno.h>
#include <fcntl.h>
#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/epoll.h>
#include <sys/socket.h>
#include <sys/un.h>
#include <unistd.h>
#include <memory>

#include <rte_lcore.h>
#include <spdk/env.h>
#include <spdk/nvme.h>
#include <spdk/nvme_intel.h>
#include <spdk/queue.h>
#include <spdk/stdinc.h>
#include <spdk/util.h>

#include <iostream>



using namespace std;



int main(int argc, char **argv) {
  int ret;
  uint32_t master_core;
  struct spdk_env_opts opts;

  
  spdk_env_opts_init(&opts);
  opts.name = "nvmfhost";
  opts.core_mask = "0xc";
  if (spdk_env_init(&opts) < 0) {
	  std::cout << "spdk_env_init failed";
    return -1;
  }
  master_core = spdk_env_get_current_core();
  std::cout << "SPDK master core id: " << master_core;


  return 0;
}

