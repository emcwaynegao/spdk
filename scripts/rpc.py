#!/usr/bin/env python3

from rpc.client import print_dict, print_json, JSONRPCException
from rpc.helpers import deprecated_aliases

import logging
import argparse
import rpc
import sys
import shlex
import json

try:
    from shlex import quote
except ImportError:
    from pipes import quote


def print_array(a):
    print(" ".join((quote(v) for v in a)))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='SPDK RPC command line interface')
    parser.add_argument('-s', dest='server_addr',
                        help='RPC domain socket path or IP address', default='/var/tmp/spdk.sock')
    parser.add_argument('-p', dest='port',
                        help='RPC port number (if server_addr is IP address)',
                        default=5260, type=int)
    parser.add_argument('-t', dest='timeout',
                        help='Timeout as a floating point number expressed in seconds waiting for response. Default: 60.0',
                        default=60.0, type=float)
    parser.add_argument('-v', dest='verbose', action='store_const', const="INFO",
                        help='Set verbose mode to INFO', default="ERROR")
    parser.add_argument('--verbose', dest='verbose', choices=['DEBUG', 'INFO', 'ERROR'],
                        help="""Set verbose level. """)
    parser.add_argument('--dry_run', dest='dry_run', action='store_true', help="Display request and exit")
    parser.set_defaults(dry_run=False)
    subparsers = parser.add_subparsers(help='RPC methods', dest='called_rpc_name')

    def start_subsystem_init(args):
        rpc.start_subsystem_init(args.client)

    p = subparsers.add_parser('start_subsystem_init', help='Start initialization of subsystems')
    p.set_defaults(func=start_subsystem_init)

    def wait_subsystem_init(args):
        rpc.wait_subsystem_init(args.client)

    p = subparsers.add_parser('wait_subsystem_init', help='Block until subsystems have been initialized')
    p.set_defaults(func=wait_subsystem_init)

    def rpc_get_methods(args):
        print_dict(rpc.rpc_get_methods(args.client,
                                       current=args.current))

    p = subparsers.add_parser('rpc_get_methods', help='Get list of supported RPC methods', aliases=['get_rpc_methods'])
    p.add_argument('-c', '--current', help='Get list of RPC methods only callable in the current state.', action='store_true')
    p.set_defaults(func=rpc_get_methods)

    def get_spdk_version(args):
        print_json(rpc.get_spdk_version(args.client))

    p = subparsers.add_parser('get_spdk_version', help='Get SPDK version')
    p.set_defaults(func=get_spdk_version)

    def save_config(args):
        rpc.save_config(args.client,
                        sys.stdout,
                        indent=args.indent)

    p = subparsers.add_parser('save_config', help="""Write current (live) configuration of SPDK subsystems and targets to stdout.
    """)
    p.add_argument('-i', '--indent', help="""Indent level. Value less than 0 mean compact mode. Default indent level is 2.
    """, type=int, default=2)
    p.set_defaults(func=save_config)

    def load_config(args):
        rpc.load_config(args.client, sys.stdin)

    p = subparsers.add_parser('load_config', help="""Configure SPDK subsystems and targets using JSON RPC read from stdin.""")
    p.set_defaults(func=load_config)

    def save_subsystem_config(args):
        rpc.save_subsystem_config(args.client,
                                  sys.stdout,
                                  indent=args.indent,
                                  name=args.name)

    p = subparsers.add_parser('save_subsystem_config', help="""Write current (live) configuration of SPDK subsystem to stdout.
    """)
    p.add_argument('-i', '--indent', help="""Indent level. Value less than 0 mean compact mode. Default indent level is 2.
    """, type=int, default=2)
    p.add_argument('-n', '--name', help='Name of subsystem', required=True)
    p.set_defaults(func=save_subsystem_config)

    def load_subsystem_config(args):
        rpc.load_subsystem_config(args.client,
                                  sys.stdin)

    p = subparsers.add_parser('load_subsystem_config', help="""Configure SPDK subsystem using JSON RPC read from stdin.""")
    p.set_defaults(func=load_subsystem_config)

    # app
    def kill_instance(args):
        rpc.app.kill_instance(args.client,
                              sig_name=args.sig_name)

    p = subparsers.add_parser('kill_instance', help='Send signal to instance')
    p.add_argument('sig_name', help='signal will be sent to server.')
    p.set_defaults(func=kill_instance)

    def context_switch_monitor(args):
        enabled = None
        if args.enable:
            enabled = True
        if args.disable:
            enabled = False
        print_dict(rpc.app.context_switch_monitor(args.client,
                                                  enabled=enabled))

    p = subparsers.add_parser('context_switch_monitor', help='Control whether the context switch monitor is enabled')
    p.add_argument('-e', '--enable', action='store_true', help='Enable context switch monitoring')
    p.add_argument('-d', '--disable', action='store_true', help='Disable context switch monitoring')
    p.set_defaults(func=context_switch_monitor)

    # bdev
    def set_bdev_options(args):
        rpc.bdev.set_bdev_options(args.client,
                                  bdev_io_pool_size=args.bdev_io_pool_size,
                                  bdev_io_cache_size=args.bdev_io_cache_size)

    p = subparsers.add_parser('set_bdev_options', help="""Set options of bdev subsystem""")
    p.add_argument('-p', '--bdev-io-pool-size', help='Number of bdev_io structures in shared buffer pool', type=int)
    p.add_argument('-c', '--bdev-io-cache-size', help='Maximum number of bdev_io structures cached per thread', type=int)
    p.set_defaults(func=set_bdev_options)

    def construct_compress_bdev(args):
        print_json(rpc.bdev.construct_compress_bdev(args.client,
                                                    base_bdev_name=args.base_bdev_name,
                                                    pm_path=args.pm_path))
    p = subparsers.add_parser('construct_compress_bdev',
                              help='Add a compress vbdev')
    p.add_argument('-b', '--base_bdev_name', help="Name of the base bdev")
    p.add_argument('-p', '--pm_path', help="Path to persistent memory")
    p.set_defaults(func=construct_compress_bdev)

    def delete_compress_bdev(args):
        rpc.bdev.delete_compress_bdev(args.client,
                                      name=args.name)

    p = subparsers.add_parser('delete_compress_bdev', help='Delete a compress disk')
    p.add_argument('name', help='compress bdev name')
    p.set_defaults(func=delete_compress_bdev)

    def set_compress_pmd(args):
        rpc.bdev.set_compress_pmd(args.client,
                                  pmd=args.pmd)
    p = subparsers.add_parser('set_compress_pmd', help='Set pmd option for a compress disk')
    p.add_argument('-p', '--pmd', type=int, help='0 = auto-select, 1= QAT only, 2 = ISAL only')
    p.set_defaults(func=set_compress_pmd)

    def construct_crypto_bdev(args):
        print_json(rpc.bdev.construct_crypto_bdev(args.client,
                                                  base_bdev_name=args.base_bdev_name,
                                                  name=args.name,
                                                  crypto_pmd=args.crypto_pmd,
                                                  key=args.key))
    p = subparsers.add_parser('construct_crypto_bdev',
                              help='Add a crypto vbdev')
    p.add_argument('-b', '--base_bdev_name', help="Name of the base bdev")
    p.add_argument('-c', '--name', help="Name of the crypto vbdev")
    p.add_argument('-d', '--crypto_pmd', help="Name of the crypto device driver")
    p.add_argument('-k', '--key', help="Key")
    p.set_defaults(func=construct_crypto_bdev)

    def delete_crypto_bdev(args):
        rpc.bdev.delete_crypto_bdev(args.client,
                                    name=args.name)

    p = subparsers.add_parser('delete_crypto_bdev', help='Delete a crypto disk')
    p.add_argument('name', help='crypto bdev name')
    p.set_defaults(func=delete_crypto_bdev)

    def construct_ocf_bdev(args):
        print_json(rpc.bdev.construct_ocf_bdev(args.client,
                                               name=args.name,
                                               mode=args.mode,
                                               cache_bdev_name=args.cache_bdev_name,
                                               core_bdev_name=args.core_bdev_name))
    p = subparsers.add_parser('construct_ocf_bdev',
                              help='Add an OCF block device')
    p.add_argument('name', help='Name of resulting OCF bdev')
    p.add_argument('mode', help='OCF cache mode', choices=['wb', 'wt', 'pt'])
    p.add_argument('cache_bdev_name', help='Name of underlying cache bdev')
    p.add_argument('core_bdev_name', help='Name of unerlying core bdev')
    p.set_defaults(func=construct_ocf_bdev)

    def delete_ocf_bdev(args):
        rpc.bdev.delete_ocf_bdev(args.client,
                                 name=args.name)

    p = subparsers.add_parser('delete_ocf_bdev',
                              help='Delete an OCF block device')
    p.add_argument('name', help='Name of OCF bdev')
    p.set_defaults(func=delete_ocf_bdev)

    def get_ocf_stats(args):
        print_dict(rpc.bdev.get_ocf_stats(args.client,
                                          name=args.name))
    p = subparsers.add_parser('get_ocf_stats',
                              help='Get statistics of chosen OCF block device')
    p.add_argument('name', help='Name of OCF bdev')
    p.set_defaults(func=get_ocf_stats)

    def get_ocf_bdevs(args):
        print_dict(rpc.bdev.get_ocf_bdevs(args.client,
                                          name=args.name))
    p = subparsers.add_parser('get_ocf_bdevs',
                              help='Get list of OCF devices including unregistered ones')
    p.add_argument('name', nargs='?', default=None, help='name of OCF vbdev or name of cache device or name of core device (optional)')
    p.set_defaults(func=get_ocf_bdevs)

    def construct_malloc_bdev(args):
        num_blocks = (args.total_size * 1024 * 1024) // args.block_size
        print_json(rpc.bdev.construct_malloc_bdev(args.client,
                                                  num_blocks=int(num_blocks),
                                                  block_size=args.block_size,
                                                  name=args.name,
                                                  uuid=args.uuid))
    p = subparsers.add_parser('construct_malloc_bdev',
                              help='Add a bdev with malloc backend')
    p.add_argument('-b', '--name', help="Name of the bdev")
    p.add_argument('-u', '--uuid', help="UUID of the bdev")
    p.add_argument(
        'total_size', help='Size of malloc bdev in MB (float > 0)', type=float)
    p.add_argument('block_size', help='Block size for this bdev', type=int)
    p.set_defaults(func=construct_malloc_bdev)

    def delete_malloc_bdev(args):
        rpc.bdev.delete_malloc_bdev(args.client,
                                    name=args.name)

    p = subparsers.add_parser('delete_malloc_bdev', help='Delete a malloc disk')
    p.add_argument('name', help='malloc bdev name')
    p.set_defaults(func=delete_malloc_bdev)

    def construct_null_bdev(args):
        num_blocks = (args.total_size * 1024 * 1024) // args.block_size
        print_json(rpc.bdev.construct_null_bdev(args.client,
                                                num_blocks=num_blocks,
                                                block_size=args.block_size,
                                                name=args.name,
                                                uuid=args.uuid))

    p = subparsers.add_parser('construct_null_bdev',
                              help='Add a bdev with null backend')
    p.add_argument('name', help='Block device name')
    p.add_argument('-u', '--uuid', help='UUID of the bdev')
    p.add_argument(
        'total_size', help='Size of null bdev in MB (int > 0)', type=int)
    p.add_argument('block_size', help='Block size for this bdev', type=int)
    p.set_defaults(func=construct_null_bdev)

    def delete_null_bdev(args):
        rpc.bdev.delete_null_bdev(args.client,
                                  name=args.name)

    p = subparsers.add_parser('delete_null_bdev', help='Delete a null bdev')
    p.add_argument('name', help='null bdev name')
    p.set_defaults(func=delete_null_bdev)

    def construct_aio_bdev(args):
        print_json(rpc.bdev.construct_aio_bdev(args.client,
                                               filename=args.filename,
                                               name=args.name,
                                               block_size=args.block_size))

    p = subparsers.add_parser('construct_aio_bdev',
                              help='Add a bdev with aio backend')
    p.add_argument('filename', help='Path to device or file (ex: /dev/sda)')
    p.add_argument('name', help='Block device name')
    p.add_argument('block_size', help='Block size for this bdev', type=int, nargs='?', default=0)
    p.set_defaults(func=construct_aio_bdev)

    def delete_aio_bdev(args):
        rpc.bdev.delete_aio_bdev(args.client,
                                 name=args.name)

    p = subparsers.add_parser('delete_aio_bdev', help='Delete an aio disk')
    p.add_argument('name', help='aio bdev name')
    p.set_defaults(func=delete_aio_bdev)

    def set_bdev_nvme_options(args):
        rpc.bdev.set_bdev_nvme_options(args.client,
                                       action_on_timeout=args.action_on_timeout,
                                       timeout_us=args.timeout_us,
                                       retry_count=args.retry_count,
                                       nvme_adminq_poll_period_us=args.nvme_adminq_poll_period_us,
                                       nvme_ioq_poll_period_us=args.nvme_ioq_poll_period_us)

    p = subparsers.add_parser('set_bdev_nvme_options',
                              help='Set options for the bdev nvme type. This is startup command.')
    p.add_argument('-a', '--action-on-timeout',
                   help="Action to take on command time out. Valid valies are: none, reset, abort")
    p.add_argument('-t', '--timeout-us',
                   help="Timeout for each command, in microseconds. If 0, don't track timeouts.", type=int)
    p.add_argument('-n', '--retry-count',
                   help='the number of attempts per I/O when an I/O fails', type=int)
    p.add_argument('-p', '--nvme-adminq-poll-period-us',
                   help='How often the admin queue is polled for asynchronous events', type=int)
    p.add_argument('-i', '--nvme-ioq-poll-period-us',
                   help='How often to poll I/O queues for completions', type=int)
    p.set_defaults(func=set_bdev_nvme_options)

    def set_bdev_nvme_hotplug(args):
        rpc.bdev.set_bdev_nvme_hotplug(args.client, enable=args.enable, period_us=args.period_us)

    p = subparsers.add_parser('set_bdev_nvme_hotplug',
                              help='Set hotplug options for bdev nvme type.')
    p.add_argument('-d', '--disable', dest='enable', default=False, action='store_false', help="Disable hotplug (default)")
    p.add_argument('-e', '--enable', dest='enable', action='store_true', help="Enable hotplug")
    p.add_argument('-r', '--period-us',
                   help='How often the hotplug is processed for insert and remove events', type=int)
    p.set_defaults(func=set_bdev_nvme_hotplug)

    def construct_nvme_bdev(args):
        print_array(rpc.bdev.construct_nvme_bdev(args.client,
                                                 name=args.name,
                                                 trtype=args.trtype,
                                                 traddr=args.traddr,
                                                 adrfam=args.adrfam,
                                                 trsvcid=args.trsvcid,
                                                 subnqn=args.subnqn,
                                                 hostnqn=args.hostnqn,
                                                 hostaddr=args.hostaddr,
                                                 hostsvcid=args.hostsvcid,
                                                 prchk_reftag=args.prchk_reftag,
                                                 prchk_guard=args.prchk_guard))

    p = subparsers.add_parser('construct_nvme_bdev',
                              help='Add bdevs with nvme backend')
    p.add_argument('-b', '--name', help="Name of the NVMe controller, prefix for each bdev name", required=True)
    p.add_argument('-t', '--trtype',
                   help='NVMe-oF target trtype: e.g., rdma, pcie', required=True)
    p.add_argument('-a', '--traddr',
                   help='NVMe-oF target address: e.g., an ip address or BDF', required=True)
    p.add_argument('-f', '--adrfam',
                   help='NVMe-oF target adrfam: e.g., ipv4, ipv6, ib, fc, intra_host')
    p.add_argument('-s', '--trsvcid',
                   help='NVMe-oF target trsvcid: e.g., a port number')
    p.add_argument('-n', '--subnqn', help='NVMe-oF target subnqn')
    p.add_argument('-q', '--hostnqn', help='NVMe-oF host subnqn')
    p.add_argument('-i', '--hostaddr',
                   help='NVMe-oF host address: e.g., an ip address')
    p.add_argument('-c', '--hostsvcid',
                   help='NVMe-oF host svcid: e.g., a port number')
    p.add_argument('-r', '--prchk-reftag',
                   help='Enable checking of PI reference tag for I/O processing.', action='store_true')
    p.add_argument('-g', '--prchk-guard',
                   help='Enable checking of PI guard for I/O processing.', action='store_true')
    p.set_defaults(func=construct_nvme_bdev)

    def get_nvme_controllers(args):
        print_dict(rpc.nvme.get_nvme_controllers(args.client,
                                                 name=args.name))

    p = subparsers.add_parser(
        'get_nvme_controllers', help='Display current NVMe controllers list or required NVMe controller')
    p.add_argument('-n', '--name', help="Name of the NVMe controller. Example: Nvme0", required=False)
    p.set_defaults(func=get_nvme_controllers)

    def delete_nvme_controller(args):
        rpc.bdev.delete_nvme_controller(args.client,
                                        name=args.name)

    p = subparsers.add_parser('delete_nvme_controller',
                              help='Delete a NVMe controller using controller name')
    p.add_argument('name', help="Name of the controller")
    p.set_defaults(func=delete_nvme_controller)

    def construct_rbd_bdev(args):
        config = None
        if args.config:
            config = {}
            for entry in args.config:
                parts = entry.split('=', 1)
                if len(parts) != 2:
                    raise Exception('--config %s not in key=value form' % entry)
                config[parts[0]] = parts[1]
        print_json(rpc.bdev.construct_rbd_bdev(args.client,
                                               name=args.name,
                                               user=args.user,
                                               config=config,
                                               pool_name=args.pool_name,
                                               rbd_name=args.rbd_name,
                                               block_size=args.block_size))

    p = subparsers.add_parser('construct_rbd_bdev',
                              help='Add a bdev with ceph rbd backend')
    p.add_argument('-b', '--name', help="Name of the bdev", required=False)
    p.add_argument('--user', help="Ceph user name (i.e. admin, not client.admin)", required=False)
    p.add_argument('--config', action='append', metavar='key=value',
                   help="adds a key=value configuration option for rados_conf_set (default: rely on config file)")
    p.add_argument('pool_name', help='rbd pool name')
    p.add_argument('rbd_name', help='rbd image name')
    p.add_argument('block_size', help='rbd block size', type=int)
    p.set_defaults(func=construct_rbd_bdev)

    def delete_rbd_bdev(args):
        rpc.bdev.delete_rbd_bdev(args.client,
                                 name=args.name)

    p = subparsers.add_parser('delete_rbd_bdev', help='Delete a rbd bdev')
    p.add_argument('name', help='rbd bdev name')
    p.set_defaults(func=delete_rbd_bdev)

    def bdev_delay_create(args):
        print_json(rpc.bdev.bdev_delay_create(args.client,
                                              base_bdev_name=args.base_bdev_name,
                                              name=args.name,
                                              avg_read_latency=args.avg_read_latency,
                                              p99_read_latency=args.nine_nine_read_latency,
                                              avg_write_latency=args.avg_write_latency,
                                              p99_write_latency=args.nine_nine_write_latency))

    p = subparsers.add_parser('bdev_delay_create',
                              help='Add a delay bdev on existing bdev')
    p.add_argument('-b', '--base-bdev-name', help="Name of the existing bdev", required=True)
    p.add_argument('-d', '--name', help="Name of the delay bdev", required=True)
    p.add_argument('-r', '--avg-read-latency', help="Average latency to apply before completing read ops", required=True, type=int)
    p.add_argument('-t', '--nine-nine-read-latency', help="latency to apply to 1 in 100 read ops", required=True, type=int)
    p.add_argument('-w', '--avg-write-latency', help="Average latency to apply before completing write ops", required=True, type=int)
    p.add_argument('-n', '--nine-nine-write-latency', help="latency to apply to 1 in 100 write ops", required=True, type=int)
    p.set_defaults(func=bdev_delay_create)

    def bdev_delay_delete(args):
        rpc.bdev.bdev_delay_delete(args.client,
                                   name=args.name)

    p = subparsers.add_parser('bdev_delay_delete', help='Delete a delay bdev')
    p.add_argument('name', help='delay bdev name')
    p.set_defaults(func=bdev_delay_delete)

    def construct_error_bdev(args):
        print_json(rpc.bdev.construct_error_bdev(args.client,
                                                 base_name=args.base_name))

    p = subparsers.add_parser('construct_error_bdev',
                              help='Add bdev with error injection backend')
    p.add_argument('base_name', help='base bdev name')
    p.set_defaults(func=construct_error_bdev)

    def delete_error_bdev(args):
        rpc.bdev.delete_error_bdev(args.client,
                                   name=args.name)

    p = subparsers.add_parser('delete_error_bdev', help='Delete an error bdev')
    p.add_argument('name', help='error bdev name')
    p.set_defaults(func=delete_error_bdev)

    def construct_iscsi_bdev(args):
        print_json(rpc.bdev.construct_iscsi_bdev(args.client,
                                                 name=args.name,
                                                 url=args.url,
                                                 initiator_iqn=args.initiator_iqn))

    p = subparsers.add_parser('construct_iscsi_bdev',
                              help='Add bdev with iSCSI initiator backend')
    p.add_argument('-b', '--name', help="Name of the bdev", required=True)
    p.add_argument('-i', '--initiator-iqn', help="Initiator IQN", required=True)
    p.add_argument('--url', help="iSCSI Lun URL", required=True)
    p.set_defaults(func=construct_iscsi_bdev)

    def delete_iscsi_bdev(args):
        rpc.bdev.delete_iscsi_bdev(args.client,
                                   name=args.name)

    p = subparsers.add_parser('delete_iscsi_bdev', help='Delete an iSCSI bdev')
    p.add_argument('name', help='iSCSI bdev name')
    p.set_defaults(func=delete_iscsi_bdev)

    def construct_pmem_bdev(args):
        print_json(rpc.bdev.construct_pmem_bdev(args.client,
                                                pmem_file=args.pmem_file,
                                                name=args.name))

    p = subparsers.add_parser('construct_pmem_bdev', help='Add a bdev with pmem backend')
    p.add_argument('pmem_file', help='Path to pmemblk pool file')
    p.add_argument('-n', '--name', help='Block device name', required=True)
    p.set_defaults(func=construct_pmem_bdev)

    def delete_pmem_bdev(args):
        rpc.bdev.delete_pmem_bdev(args.client,
                                  name=args.name)

    p = subparsers.add_parser('delete_pmem_bdev', help='Delete a pmem bdev')
    p.add_argument('name', help='pmem bdev name')
    p.set_defaults(func=delete_pmem_bdev)

    def construct_passthru_bdev(args):
        print_json(rpc.bdev.construct_passthru_bdev(args.client,
                                                    base_bdev_name=args.base_bdev_name,
                                                    name=args.name))

    p = subparsers.add_parser('construct_passthru_bdev',
                              help='Add a pass through bdev on existing bdev')
    p.add_argument('-b', '--base-bdev-name', help="Name of the existing bdev", required=True)
    p.add_argument('-p', '--name', help="Name of the pass through bdev", required=True)
    p.set_defaults(func=construct_passthru_bdev)

    def delete_passthru_bdev(args):
        rpc.bdev.delete_passthru_bdev(args.client,
                                      name=args.name)

    p = subparsers.add_parser('delete_passthru_bdev', help='Delete a pass through bdev')
    p.add_argument('name', help='pass through bdev name')
    p.set_defaults(func=delete_passthru_bdev)

    def get_bdevs(args):
        print_dict(rpc.bdev.get_bdevs(args.client,
                                      name=args.name))

    p = subparsers.add_parser(
        'get_bdevs', help='Display current blockdev list or required blockdev')
    p.add_argument('-b', '--name', help="Name of the Blockdev. Example: Nvme0n1", required=False)
    p.set_defaults(func=get_bdevs)

    def get_bdevs_iostat(args):
        print_dict(rpc.bdev.get_bdevs_iostat(args.client,
                                             name=args.name))

    p = subparsers.add_parser(
        'get_bdevs_iostat', help='Display current I/O statistics of all the blockdevs or required blockdev.')
    p.add_argument('-b', '--name', help="Name of the Blockdev. Example: Nvme0n1", required=False)
    p.set_defaults(func=get_bdevs_iostat)

    def enable_bdev_histogram(args):
        rpc.bdev.enable_bdev_histogram(args.client, name=args.name, enable=args.enable)

    p = subparsers.add_parser('enable_bdev_histogram', help='Enable or disable histogram for specified bdev')
    p.add_argument('-e', '--enable', default=True, dest='enable', action='store_true', help='Enable histograms on specified device')
    p.add_argument('-d', '--disable', dest='enable', action='store_false', help='Disable histograms on specified device')
    p.add_argument('name', help='bdev name')
    p.set_defaults(func=enable_bdev_histogram)

    def get_bdev_histogram(args):
        print_dict(rpc.bdev.get_bdev_histogram(args.client, name=args.name))

    p = subparsers.add_parser('get_bdev_histogram', help='Get histogram for specified bdev')
    p.add_argument('name', help='bdev name')
    p.set_defaults(func=get_bdev_histogram)

    def set_bdev_qd_sampling_period(args):
        rpc.bdev.set_bdev_qd_sampling_period(args.client,
                                             name=args.name,
                                             period=args.period)

    p = subparsers.add_parser('set_bdev_qd_sampling_period', help="Enable or disable tracking of a bdev's queue depth.")
    p.add_argument('name', help='Blockdev name. Example: Malloc0')
    p.add_argument('period', help='Period with which to poll the block device queue depth in microseconds.'
                   ' If set to 0, polling will be disabled.',
                   type=int)
    p.set_defaults(func=set_bdev_qd_sampling_period)

    def set_bdev_qos_limit(args):
        rpc.bdev.set_bdev_qos_limit(args.client,
                                    name=args.name,
                                    rw_ios_per_sec=args.rw_ios_per_sec,
                                    rw_mbytes_per_sec=args.rw_mbytes_per_sec,
                                    r_mbytes_per_sec=args.r_mbytes_per_sec,
                                    w_mbytes_per_sec=args.w_mbytes_per_sec)

    p = subparsers.add_parser('set_bdev_qos_limit', help='Set QoS rate limit on a blockdev')
    p.add_argument('name', help='Blockdev name to set QoS. Example: Malloc0')
    p.add_argument('--rw_ios_per_sec',
                   help='R/W IOs per second limit (>=10000, example: 20000). 0 means unlimited.',
                   type=int, required=False)
    p.add_argument('--rw_mbytes_per_sec',
                   help="R/W megabytes per second limit (>=10, example: 100). 0 means unlimited.",
                   type=int, required=False)
    p.add_argument('--r_mbytes_per_sec',
                   help="Read megabytes per second limit (>=10, example: 100). 0 means unlimited.",
                   type=int, required=False)
    p.add_argument('--w_mbytes_per_sec',
                   help="Write megabytes per second limit (>=10, example: 100). 0 means unlimited.",
                   type=int, required=False)
    p.set_defaults(func=set_bdev_qos_limit)

    def bdev_inject_error(args):
        rpc.bdev.bdev_inject_error(args.client,
                                   name=args.name,
                                   io_type=args.io_type,
                                   error_type=args.error_type,
                                   num=args.num)

    p = subparsers.add_parser('bdev_inject_error', help='bdev inject error')
    p.add_argument('name', help="""the name of the error injection bdev""")
    p.add_argument('io_type', help="""io_type: 'clear' 'read' 'write' 'unmap' 'flush' 'all'""")
    p.add_argument('error_type', help="""error_type: 'failure' 'pending'""")
    p.add_argument(
        '-n', '--num', help='the number of commands you want to fail', type=int, default=1)
    p.set_defaults(func=bdev_inject_error)

    def apply_firmware(args):
        print_dict(rpc.bdev.apply_firmware(args.client,
                                           bdev_name=args.bdev_name,
                                           filename=args.filename))

    p = subparsers.add_parser('apply_firmware', help='Download and commit firmware to NVMe device')
    p.add_argument('filename', help='filename of the firmware to download')
    p.add_argument('bdev_name', help='name of the NVMe device')
    p.set_defaults(func=apply_firmware)

    # iSCSI
    def set_iscsi_options(args):
        rpc.iscsi.set_iscsi_options(
            args.client,
            auth_file=args.auth_file,
            node_base=args.node_base,
            nop_timeout=args.nop_timeout,
            nop_in_interval=args.nop_in_interval,
            disable_chap=args.disable_chap,
            require_chap=args.require_chap,
            mutual_chap=args.mutual_chap,
            chap_group=args.chap_group,
            max_sessions=args.max_sessions,
            max_queue_depth=args.max_queue_depth,
            max_connections_per_session=args.max_connections_per_session,
            default_time2wait=args.default_time2wait,
            default_time2retain=args.default_time2retain,
            first_burst_length=args.first_burst_length,
            immediate_data=args.immediate_data,
            error_recovery_level=args.error_recovery_level,
            allow_duplicated_isid=args.allow_duplicated_isid)

    p = subparsers.add_parser('set_iscsi_options', help="""Set options of iSCSI subsystem""")
    p.add_argument('-f', '--auth-file', help='Path to CHAP shared secret file')
    p.add_argument('-b', '--node-base', help='Prefix of the name of iSCSI target node')
    p.add_argument('-o', '--nop-timeout', help='Timeout in seconds to nop-in request to the initiator', type=int)
    p.add_argument('-n', '--nop-in-interval', help='Time interval in secs between nop-in requests by the target', type=int)
    p.add_argument('-d', '--disable-chap', help="""CHAP for discovery session should be disabled.
    *** Mutually exclusive with --require-chap""", action='store_true')
    p.add_argument('-r', '--require-chap', help="""CHAP for discovery session should be required.
    *** Mutually exclusive with --disable-chap""", action='store_true')
    p.add_argument('-m', '--mutual-chap', help='CHAP for discovery session should be mutual', action='store_true')
    p.add_argument('-g', '--chap-group', help="""Authentication group ID for discovery session.
    *** Authentication group must be precreated ***""", type=int)
    p.add_argument('-a', '--max-sessions', help='Maximum number of sessions in the host.', type=int)
    p.add_argument('-q', '--max-queue-depth', help='Max number of outstanding I/Os per queue.', type=int)
    p.add_argument('-c', '--max-connections-per-session', help='Negotiated parameter, MaxConnections.', type=int)
    p.add_argument('-w', '--default-time2wait', help='Negotiated parameter, DefaultTime2Wait.', type=int)
    p.add_argument('-v', '--default-time2retain', help='Negotiated parameter, DefaultTime2Retain.', type=int)
    p.add_argument('-s', '--first-burst-length', help='Negotiated parameter, FirstBurstLength.', type=int)
    p.add_argument('-i', '--immediate-data', help='Negotiated parameter, ImmediateData.', action='store_true')
    p.add_argument('-l', '--error-recovery-level', help='Negotiated parameter, ErrorRecoveryLevel', type=int)
    p.add_argument('-p', '--allow-duplicated-isid', help='Allow duplicated initiator session ID.', action='store_true')
    p.set_defaults(func=set_iscsi_options)

    def set_iscsi_discovery_auth(args):
        rpc.iscsi.set_iscsi_discovery_auth(
            args.client,
            disable_chap=args.disable_chap,
            require_chap=args.require_chap,
            mutual_chap=args.mutual_chap,
            chap_group=args.chap_group)

    p = subparsers.add_parser('set_iscsi_discovery_auth', help="""Set CHAP authentication for discovery session.""")
    p.add_argument('-d', '--disable-chap', help="""CHAP for discovery session should be disabled.
    *** Mutually exclusive with --require-chap""", action='store_true')
    p.add_argument('-r', '--require-chap', help="""CHAP for discovery session should be required.
    *** Mutually exclusive with --disable-chap""", action='store_true')
    p.add_argument('-m', '--mutual-chap', help='CHAP for discovery session should be mutual', action='store_true')
    p.add_argument('-g', '--chap-group', help="""Authentication group ID for discovery session.
    *** Authentication group must be precreated ***""", type=int)
    p.set_defaults(func=set_iscsi_discovery_auth)

    def add_iscsi_auth_group(args):
        secrets = None
        if args.secrets:
            secrets = [dict(u.split(":") for u in a.split(" ")) for a in args.secrets.split(",")]

        rpc.iscsi.add_iscsi_auth_group(args.client, tag=args.tag, secrets=secrets)

    p = subparsers.add_parser('add_iscsi_auth_group', help='Add authentication group for CHAP authentication.')
    p.add_argument('tag', help='Authentication group tag (unique, integer > 0).', type=int)
    p.add_argument('-c', '--secrets', help="""Comma-separated list of CHAP secrets
<user:user_name secret:chap_secret muser:mutual_user_name msecret:mutual_chap_secret> enclosed in quotes.
Format: 'user:u1 secret:s1 muser:mu1 msecret:ms1,user:u2 secret:s2 muser:mu2 msecret:ms2'""", required=False)
    p.set_defaults(func=add_iscsi_auth_group)

    def delete_iscsi_auth_group(args):
        rpc.iscsi.delete_iscsi_auth_group(args.client, tag=args.tag)

    p = subparsers.add_parser('delete_iscsi_auth_group', help='Delete an authentication group.')
    p.add_argument('tag', help='Authentication group tag', type=int)
    p.set_defaults(func=delete_iscsi_auth_group)

    def add_secret_to_iscsi_auth_group(args):
        rpc.iscsi.add_secret_to_iscsi_auth_group(
            args.client,
            tag=args.tag,
            user=args.user,
            secret=args.secret,
            muser=args.muser,
            msecret=args.msecret)

    p = subparsers.add_parser('add_secret_to_iscsi_auth_group', help='Add a secret to an authentication group.')
    p.add_argument('tag', help='Authentication group tag', type=int)
    p.add_argument('-u', '--user', help='User name for one-way CHAP authentication', required=True)
    p.add_argument('-s', '--secret', help='Secret for one-way CHAP authentication', required=True)
    p.add_argument('-m', '--muser', help='User name for mutual CHAP authentication')
    p.add_argument('-r', '--msecret', help='Secret for mutual CHAP authentication')
    p.set_defaults(func=add_secret_to_iscsi_auth_group)

    def delete_secret_from_iscsi_auth_group(args):
        rpc.iscsi.delete_secret_from_iscsi_auth_group(args.client, tag=args.tag, user=args.user)

    p = subparsers.add_parser('delete_secret_from_iscsi_auth_group', help='Delete a secret from an authentication group.')
    p.add_argument('tag', help='Authentication group tag', type=int)
    p.add_argument('-u', '--user', help='User name for one-way CHAP authentication', required=True)
    p.set_defaults(func=delete_secret_from_iscsi_auth_group)

    def get_iscsi_auth_groups(args):
        print_dict(rpc.iscsi.get_iscsi_auth_groups(args.client))

    p = subparsers.add_parser('get_iscsi_auth_groups',
                              help='Display current authentication group configuration')
    p.set_defaults(func=get_iscsi_auth_groups)

    def get_portal_groups(args):
        print_dict(rpc.iscsi.get_portal_groups(args.client))

    p = subparsers.add_parser(
        'get_portal_groups', help='Display current portal group configuration')
    p.set_defaults(func=get_portal_groups)

    def get_initiator_groups(args):
        print_dict(rpc.iscsi.get_initiator_groups(args.client))

    p = subparsers.add_parser('get_initiator_groups',
                              help='Display current initiator group configuration')
    p.set_defaults(func=get_initiator_groups)

    def get_target_nodes(args):
        print_dict(rpc.iscsi.get_target_nodes(args.client))

    p = subparsers.add_parser('get_target_nodes', help='Display target nodes')
    p.set_defaults(func=get_target_nodes)

    def construct_target_node(args):
        luns = []
        for u in args.bdev_name_id_pairs.strip().split(" "):
            bdev_name, lun_id = u.split(":")
            luns.append({"bdev_name": bdev_name, "lun_id": int(lun_id)})

        pg_ig_maps = []
        for u in args.pg_ig_mappings.strip().split(" "):
            pg, ig = u.split(":")
            pg_ig_maps.append({"pg_tag": int(pg), "ig_tag": int(ig)})

        rpc.iscsi.construct_target_node(
            args.client,
            luns=luns,
            pg_ig_maps=pg_ig_maps,
            name=args.name,
            alias_name=args.alias_name,
            queue_depth=args.queue_depth,
            chap_group=args.chap_group,
            disable_chap=args.disable_chap,
            require_chap=args.require_chap,
            mutual_chap=args.mutual_chap,
            header_digest=args.header_digest,
            data_digest=args.data_digest)

    p = subparsers.add_parser('construct_target_node',
                              help='Add a target node')
    p.add_argument('name', help='Target node name (ASCII)')
    p.add_argument('alias_name', help='Target node alias name (ASCII)')
    p.add_argument('bdev_name_id_pairs', help="""Whitespace-separated list of <bdev name:LUN ID> pairs enclosed
    in quotes.  Format:  'bdev_name0:id0 bdev_name1:id1' etc
    Example: 'Malloc0:0 Malloc1:1 Malloc5:2'
    *** The bdevs must pre-exist ***
    *** LUN0 (id = 0) is required ***
    *** bdevs names cannot contain space or colon characters ***""")
    p.add_argument('pg_ig_mappings', help="""List of (Portal_Group_Tag:Initiator_Group_Tag) mappings
    Whitespace separated, quoted, mapping defined with colon
    separated list of "tags" (int > 0)
    Example: '1:1 2:2 2:1'
    *** The Portal/Initiator Groups must be precreated ***""")
    p.add_argument('queue_depth', help='Desired target queue depth', type=int)
    p.add_argument('-g', '--chap-group', help="""Authentication group ID for this target node.
    *** Authentication group must be precreated ***""", type=int, default=0)
    p.add_argument('-d', '--disable-chap', help="""CHAP authentication should be disabled for this target node.
    *** Mutually exclusive with --require-chap ***""", action='store_true')
    p.add_argument('-r', '--require-chap', help="""CHAP authentication should be required for this target node.
    *** Mutually exclusive with --disable-chap ***""", action='store_true')
    p.add_argument(
        '-m', '--mutual-chap', help='CHAP authentication should be mutual/bidirectional.', action='store_true')
    p.add_argument('-H', '--header-digest',
                   help='Header Digest should be required for this target node.', action='store_true')
    p.add_argument('-D', '--data-digest',
                   help='Data Digest should be required for this target node.', action='store_true')
    p.set_defaults(func=construct_target_node)

    def target_node_add_lun(args):
        rpc.iscsi.target_node_add_lun(
            args.client,
            name=args.name,
            bdev_name=args.bdev_name,
            lun_id=args.lun_id)

    p = subparsers.add_parser('target_node_add_lun', help='Add LUN to the target node')
    p.add_argument('name', help='Target node name (ASCII)')
    p.add_argument('bdev_name', help="""bdev name enclosed in quotes.
    *** bdev name cannot contain space or colon characters ***""")
    p.add_argument('-i', dest='lun_id', help="""LUN ID (integer >= 0)
    *** If LUN ID is omitted or -1, the lowest free one is assigned ***""", type=int, required=False)
    p.set_defaults(func=target_node_add_lun)

    def set_iscsi_target_node_auth(args):
        rpc.iscsi.set_iscsi_target_node_auth(
            args.client,
            name=args.name,
            chap_group=args.chap_group,
            disable_chap=args.disable_chap,
            require_chap=args.require_chap,
            mutual_chap=args.mutual_chap)

    p = subparsers.add_parser('set_iscsi_target_node_auth', help='Set CHAP authentication for the target node')
    p.add_argument('name', help='Target node name (ASCII)')
    p.add_argument('-g', '--chap-group', help="""Authentication group ID for this target node.
    *** Authentication group must be precreated ***""", type=int, default=0)
    p.add_argument('-d', '--disable-chap', help="""CHAP authentication should be disabled for this target node.
    *** Mutually exclusive with --require-chap ***""", action='store_true')
    p.add_argument('-r', '--require-chap', help="""CHAP authentication should be required for this target node.
    *** Mutually exclusive with --disable-chap ***""", action='store_true')
    p.add_argument('-m', '--mutual-chap', help='CHAP authentication should be mutual/bidirectional.',
                   action='store_true')
    p.set_defaults(func=set_iscsi_target_node_auth)

    def add_pg_ig_maps(args):
        pg_ig_maps = []
        for u in args.pg_ig_mappings.strip().split(" "):
            pg, ig = u.split(":")
            pg_ig_maps.append({"pg_tag": int(pg), "ig_tag": int(ig)})
        rpc.iscsi.add_pg_ig_maps(
            args.client,
            pg_ig_maps=pg_ig_maps,
            name=args.name)

    p = subparsers.add_parser('add_pg_ig_maps', help='Add PG-IG maps to the target node')
    p.add_argument('name', help='Target node name (ASCII)')
    p.add_argument('pg_ig_mappings', help="""List of (Portal_Group_Tag:Initiator_Group_Tag) mappings
    Whitespace separated, quoted, mapping defined with colon
    separated list of "tags" (int > 0)
    Example: '1:1 2:2 2:1'
    *** The Portal/Initiator Groups must be precreated ***""")
    p.set_defaults(func=add_pg_ig_maps)

    def delete_pg_ig_maps(args):
        pg_ig_maps = []
        for u in args.pg_ig_mappings.strip().split(" "):
            pg, ig = u.split(":")
            pg_ig_maps.append({"pg_tag": int(pg), "ig_tag": int(ig)})
        rpc.iscsi.delete_pg_ig_maps(
            args.client, pg_ig_maps=pg_ig_maps, name=args.name)

    p = subparsers.add_parser('delete_pg_ig_maps', help='Delete PG-IG maps from the target node')
    p.add_argument('name', help='Target node name (ASCII)')
    p.add_argument('pg_ig_mappings', help="""List of (Portal_Group_Tag:Initiator_Group_Tag) mappings
    Whitespace separated, quoted, mapping defined with colon
    separated list of "tags" (int > 0)
    Example: '1:1 2:2 2:1'
    *** The Portal/Initiator Groups must be precreated ***""")
    p.set_defaults(func=delete_pg_ig_maps)

    def add_portal_group(args):
        portals = []
        for p in args.portal_list.strip().split(' '):
            ip, separator, port_cpumask = p.rpartition(':')
            split_port_cpumask = port_cpumask.split('@')
            if len(split_port_cpumask) == 1:
                port = port_cpumask
                portals.append({'host': ip, 'port': port})
            else:
                port = split_port_cpumask[0]
                cpumask = split_port_cpumask[1]
                portals.append({'host': ip, 'port': port, 'cpumask': cpumask})
        rpc.iscsi.add_portal_group(
            args.client,
            portals=portals,
            tag=args.tag)

    p = subparsers.add_parser('add_portal_group', help='Add a portal group')
    p.add_argument(
        'tag', help='Portal group tag (unique, integer > 0)', type=int)
    p.add_argument('portal_list', help="""List of portals in host:port@cpumask format, separated by whitespace
    (cpumask is optional and can be skipped)
    Example: '192.168.100.100:3260 192.168.100.100:3261 192.168.100.100:3262@0x1""")
    p.set_defaults(func=add_portal_group)

    def add_initiator_group(args):
        initiators = []
        netmasks = []
        for i in args.initiator_list.strip().split(' '):
            initiators.append(i)
        for n in args.netmask_list.strip().split(' '):
            netmasks.append(n)
        rpc.iscsi.add_initiator_group(
            args.client,
            tag=args.tag,
            initiators=initiators,
            netmasks=netmasks)

    p = subparsers.add_parser('add_initiator_group',
                              help='Add an initiator group')
    p.add_argument(
        'tag', help='Initiator group tag (unique, integer > 0)', type=int)
    p.add_argument('initiator_list', help="""Whitespace-separated list of initiator hostnames or IP addresses,
    enclosed in quotes.  Example: 'ANY' or '127.0.0.1 192.168.200.100'""")
    p.add_argument('netmask_list', help="""Whitespace-separated list of initiator netmasks enclosed in quotes.
    Example: '255.255.0.0 255.248.0.0' etc""")
    p.set_defaults(func=add_initiator_group)

    def add_initiators_to_initiator_group(args):
        initiators = None
        netmasks = None
        if args.initiator_list:
            initiators = []
            for i in args.initiator_list.strip().split(' '):
                initiators.append(i)
        if args.netmask_list:
            netmasks = []
            for n in args.netmask_list.strip().split(' '):
                netmasks.append(n)
        rpc.iscsi.add_initiators_to_initiator_group(
            args.client,
            tag=args.tag,
            initiators=initiators,
            netmasks=netmasks)

    p = subparsers.add_parser('add_initiators_to_initiator_group',
                              help='Add initiators to an existing initiator group')
    p.add_argument(
        'tag', help='Initiator group tag (unique, integer > 0)', type=int)
    p.add_argument('-n', dest='initiator_list', help="""Whitespace-separated list of initiator hostnames or IP addresses,
    enclosed in quotes.  This parameter can be omitted.  Example: 'ANY' or '127.0.0.1 192.168.200.100'""", required=False)
    p.add_argument('-m', dest='netmask_list', help="""Whitespace-separated list of initiator netmasks enclosed in quotes.
    This parameter can be omitted.  Example: '255.255.0.0 255.248.0.0' etc""", required=False)
    p.set_defaults(func=add_initiators_to_initiator_group)

    def delete_initiators_from_initiator_group(args):
        initiators = None
        netmasks = None
        if args.initiator_list:
            initiators = []
            for i in args.initiator_list.strip().split(' '):
                initiators.append(i)
        if args.netmask_list:
            netmasks = []
            for n in args.netmask_list.strip().split(' '):
                netmasks.append(n)
        rpc.iscsi.delete_initiators_from_initiator_group(
            args.client,
            tag=args.tag,
            initiators=initiators,
            netmasks=netmasks)

    p = subparsers.add_parser('delete_initiators_from_initiator_group',
                              help='Delete initiators from an existing initiator group')
    p.add_argument(
        'tag', help='Initiator group tag (unique, integer > 0)', type=int)
    p.add_argument('-n', dest='initiator_list', help="""Whitespace-separated list of initiator hostnames or IP addresses,
    enclosed in quotes.  This parameter can be omitted.  Example: 'ANY' or '127.0.0.1 192.168.200.100'""", required=False)
    p.add_argument('-m', dest='netmask_list', help="""Whitespace-separated list of initiator netmasks enclosed in quotes.
    This parameter can be omitted.  Example: '255.255.0.0 255.248.0.0' etc""", required=False)
    p.set_defaults(func=delete_initiators_from_initiator_group)

    def delete_target_node(args):
        rpc.iscsi.delete_target_node(
            args.client, target_node_name=args.target_node_name)

    p = subparsers.add_parser('delete_target_node',
                              help='Delete a target node')
    p.add_argument('target_node_name',
                   help='Target node name to be deleted. Example: iqn.2016-06.io.spdk:disk1.')
    p.set_defaults(func=delete_target_node)

    def delete_portal_group(args):
        rpc.iscsi.delete_portal_group(args.client, tag=args.tag)

    p = subparsers.add_parser('delete_portal_group',
                              help='Delete a portal group')
    p.add_argument(
        'tag', help='Portal group tag (unique, integer > 0)', type=int)
    p.set_defaults(func=delete_portal_group)

    def delete_initiator_group(args):
        rpc.iscsi.delete_initiator_group(args.client, tag=args.tag)

    p = subparsers.add_parser('delete_initiator_group',
                              help='Delete an initiator group')
    p.add_argument(
        'tag', help='Initiator group tag (unique, integer > 0)', type=int)
    p.set_defaults(func=delete_initiator_group)

    def get_iscsi_connections(args):
        print_dict(rpc.iscsi.get_iscsi_connections(args.client))

    p = subparsers.add_parser('get_iscsi_connections',
                              help='Display iSCSI connections')
    p.set_defaults(func=get_iscsi_connections)

    def get_iscsi_global_params(args):
        print_dict(rpc.iscsi.get_iscsi_global_params(args.client))

    p = subparsers.add_parser('get_iscsi_global_params', help='Display iSCSI global parameters')
    p.set_defaults(func=get_iscsi_global_params)

    def get_scsi_devices(args):
        print_dict(rpc.iscsi.get_scsi_devices(args.client))

    p = subparsers.add_parser('get_scsi_devices', help='Display SCSI devices')
    p.set_defaults(func=get_scsi_devices)

    # trace
    def enable_tpoint_group(args):
        rpc.trace.enable_tpoint_group(args.client, name=args.name)

    p = subparsers.add_parser('enable_tpoint_group', help='enable trace on a specific tpoint group')
    p.add_argument(
        'name', help="""trace group name we want to enable in tpoint_group_mask.
        (for example "bdev" for bdev trace group, "all" for all trace groups).""")
    p.set_defaults(func=enable_tpoint_group)

    def disable_tpoint_group(args):
        rpc.trace.disable_tpoint_group(args.client, name=args.name)

    p = subparsers.add_parser('disable_tpoint_group', help='disable trace on a specific tpoint group')
    p.add_argument(
        'name', help="""trace group name we want to disable in tpoint_group_mask.
        (for example "bdev" for bdev trace group, "all" for all trace groups).""")
    p.set_defaults(func=disable_tpoint_group)

    def get_tpoint_group_mask(args):
        print_dict(rpc.trace.get_tpoint_group_mask(args.client))

    p = subparsers.add_parser('get_tpoint_group_mask', help='get trace point group mask')
    p.set_defaults(func=get_tpoint_group_mask)

    # log
    def set_log_flag(args):
        rpc.log.set_log_flag(args.client, flag=args.flag)

    p = subparsers.add_parser('set_log_flag', help='set log flag', aliases=['set_trace_flag'])
    p.add_argument(
        'flag', help='log flag we want to set. (for example "nvme").')
    p.set_defaults(func=set_log_flag)

    def clear_log_flag(args):
        rpc.log.clear_log_flag(args.client, flag=args.flag)

    p = subparsers.add_parser('clear_log_flag', help='clear log flag', aliases=['clear_trace_flag'])
    p.add_argument(
        'flag', help='log flag we want to clear. (for example "nvme").')
    p.set_defaults(func=clear_log_flag)

    def get_log_flags(args):
        print_dict(rpc.log.get_log_flags(args.client))

    p = subparsers.add_parser('get_log_flags', help='get log flags', aliases=['get_trace_flags'])
    p.set_defaults(func=get_log_flags)

    def set_log_level(args):
        rpc.log.set_log_level(args.client, level=args.level)

    p = subparsers.add_parser('set_log_level', help='set log level')
    p.add_argument('level', help='log level we want to set. (for example "DEBUG").')
    p.set_defaults(func=set_log_level)

    def get_log_level(args):
        print_dict(rpc.log.get_log_level(args.client))

    p = subparsers.add_parser('get_log_level', help='get log level')
    p.set_defaults(func=get_log_level)

    def set_log_print_level(args):
        rpc.log.set_log_print_level(args.client, level=args.level)

    p = subparsers.add_parser('set_log_print_level', help='set log print level')
    p.add_argument('level', help='log print level we want to set. (for example "DEBUG").')
    p.set_defaults(func=set_log_print_level)

    def get_log_print_level(args):
        print_dict(rpc.log.get_log_print_level(args.client))

    p = subparsers.add_parser('get_log_print_level', help='get log print level')
    p.set_defaults(func=get_log_print_level)

    # lvol
    def construct_lvol_store(args):
        print_json(rpc.lvol.construct_lvol_store(args.client,
                                                 bdev_name=args.bdev_name,
                                                 lvs_name=args.lvs_name,
                                                 cluster_sz=args.cluster_sz,
                                                 clear_method=args.clear_method))

    p = subparsers.add_parser('construct_lvol_store', help='Add logical volume store on base bdev')
    p.add_argument('bdev_name', help='base bdev name')
    p.add_argument('lvs_name', help='name for lvol store')
    p.add_argument('-c', '--cluster-sz', help='size of cluster (in bytes)', type=int, required=False)
    p.add_argument('--clear-method', help="""Change clear method for data region.
        Available: none, unmap, write_zeroes""", required=False)
    p.set_defaults(func=construct_lvol_store)

    def rename_lvol_store(args):
        rpc.lvol.rename_lvol_store(args.client,
                                   old_name=args.old_name,
                                   new_name=args.new_name)

    p = subparsers.add_parser('rename_lvol_store', help='Change logical volume store name')
    p.add_argument('old_name', help='old name')
    p.add_argument('new_name', help='new name')
    p.set_defaults(func=rename_lvol_store)

    def construct_lvol_bdev(args):
        print_json(rpc.lvol.construct_lvol_bdev(args.client,
                                                lvol_name=args.lvol_name,
                                                size=args.size * 1024 * 1024,
                                                thin_provision=args.thin_provision,
                                                clear_method=args.clear_method,
                                                uuid=args.uuid,
                                                lvs_name=args.lvs_name))

    p = subparsers.add_parser('construct_lvol_bdev', help='Add a bdev with an logical volume backend')
    p.add_argument('-u', '--uuid', help='lvol store UUID', required=False)
    p.add_argument('-l', '--lvs-name', help='lvol store name', required=False)
    p.add_argument('-t', '--thin-provision', action='store_true', help='create lvol bdev as thin provisioned')
    p.add_argument('-c', '--clear-method', help="""Change default data clusters clear method.
        Available: none, unmap, write_zeroes""", required=False)
    p.add_argument('lvol_name', help='name for this lvol')
    p.add_argument('size', help='size in MiB for this bdev', type=int)
    p.set_defaults(func=construct_lvol_bdev)

    def snapshot_lvol_bdev(args):
        print_json(rpc.lvol.snapshot_lvol_bdev(args.client,
                                               lvol_name=args.lvol_name,
                                               snapshot_name=args.snapshot_name))

    p = subparsers.add_parser('snapshot_lvol_bdev', help='Create a snapshot of an lvol bdev')
    p.add_argument('lvol_name', help='lvol bdev name')
    p.add_argument('snapshot_name', help='lvol snapshot name')
    p.set_defaults(func=snapshot_lvol_bdev)

    def clone_lvol_bdev(args):
        print_json(rpc.lvol.clone_lvol_bdev(args.client,
                                            snapshot_name=args.snapshot_name,
                                            clone_name=args.clone_name))

    p = subparsers.add_parser('clone_lvol_bdev', help='Create a clone of an lvol snapshot')
    p.add_argument('snapshot_name', help='lvol snapshot name')
    p.add_argument('clone_name', help='lvol clone name')
    p.set_defaults(func=clone_lvol_bdev)

    def rename_lvol_bdev(args):
        rpc.lvol.rename_lvol_bdev(args.client,
                                  old_name=args.old_name,
                                  new_name=args.new_name)

    p = subparsers.add_parser('rename_lvol_bdev', help='Change lvol bdev name')
    p.add_argument('old_name', help='lvol bdev name')
    p.add_argument('new_name', help='new lvol name')
    p.set_defaults(func=rename_lvol_bdev)

    def inflate_lvol_bdev(args):
        rpc.lvol.inflate_lvol_bdev(args.client,
                                   name=args.name)

    p = subparsers.add_parser('inflate_lvol_bdev', help='Make thin provisioned lvol a thick provisioned lvol')
    p.add_argument('name', help='lvol bdev name')
    p.set_defaults(func=inflate_lvol_bdev)

    def decouple_parent_lvol_bdev(args):
        rpc.lvol.decouple_parent_lvol_bdev(args.client,
                                           name=args.name)

    p = subparsers.add_parser('decouple_parent_lvol_bdev', help='Decouple parent of lvol')
    p.add_argument('name', help='lvol bdev name')
    p.set_defaults(func=decouple_parent_lvol_bdev)

    def resize_lvol_bdev(args):
        rpc.lvol.resize_lvol_bdev(args.client,
                                  name=args.name,
                                  size=args.size * 1024 * 1024)

    p = subparsers.add_parser('resize_lvol_bdev', help='Resize existing lvol bdev')
    p.add_argument('name', help='lvol bdev name')
    p.add_argument('size', help='new size in MiB for this bdev', type=int)
    p.set_defaults(func=resize_lvol_bdev)

    def set_read_only_lvol_bdev(args):
        rpc.lvol.set_read_only_lvol_bdev(args.client,
                                         name=args.name)

    p = subparsers.add_parser('set_read_only_lvol_bdev', help='Mark lvol bdev as read only')
    p.add_argument('name', help='lvol bdev name')
    p.set_defaults(func=set_read_only_lvol_bdev)

    def destroy_lvol_bdev(args):
        rpc.lvol.destroy_lvol_bdev(args.client,
                                   name=args.name)

    p = subparsers.add_parser('destroy_lvol_bdev', help='Destroy a logical volume')
    p.add_argument('name', help='lvol bdev name')
    p.set_defaults(func=destroy_lvol_bdev)

    def destroy_lvol_store(args):
        rpc.lvol.destroy_lvol_store(args.client,
                                    uuid=args.uuid,
                                    lvs_name=args.lvs_name)

    p = subparsers.add_parser('destroy_lvol_store', help='Destroy an logical volume store')
    p.add_argument('-u', '--uuid', help='lvol store UUID', required=False)
    p.add_argument('-l', '--lvs-name', help='lvol store name', required=False)
    p.set_defaults(func=destroy_lvol_store)

    def get_lvol_stores(args):
        print_dict(rpc.lvol.get_lvol_stores(args.client,
                                            uuid=args.uuid,
                                            lvs_name=args.lvs_name))

    p = subparsers.add_parser('get_lvol_stores', help='Display current logical volume store list')
    p.add_argument('-u', '--uuid', help='lvol store UUID', required=False)
    p.add_argument('-l', '--lvs-name', help='lvol store name', required=False)
    p.set_defaults(func=get_lvol_stores)

    def get_raid_bdevs(args):
        print_array(rpc.bdev.get_raid_bdevs(args.client,
                                            category=args.category))

    p = subparsers.add_parser('get_raid_bdevs', help="""This is used to list all the raid bdev names based on the input category
    requested. Category should be one of 'all', 'online', 'configuring' or 'offline'. 'all' means all the raid bdevs whether
    they are online or configuring or offline. 'online' is the raid bdev which is registered with bdev layer. 'configuring'
    is the raid bdev which does not have full configuration discovered yet. 'offline' is the raid bdev which is not registered
    with bdev as of now and it has encountered any error or user has requested to offline the raid bdev""")
    p.add_argument('category', help='all or online or configuring or offline')
    p.set_defaults(func=get_raid_bdevs)

    def construct_raid_bdev(args):
        base_bdevs = []
        for u in args.base_bdevs.strip().split(" "):
            base_bdevs.append(u)

        rpc.bdev.construct_raid_bdev(args.client,
                                     name=args.name,
                                     strip_size=args.strip_size,
                                     strip_size_kb=args.strip_size_kb,
                                     raid_level=args.raid_level,
                                     base_bdevs=base_bdevs)
    p = subparsers.add_parser('construct_raid_bdev', help='Construct new raid bdev')
    p.add_argument('-n', '--name', help='raid bdev name', required=True)
    p.add_argument('-s', '--strip-size', help='strip size in KB (deprecated)', type=int)
    p.add_argument('-z', '--strip-size_kb', help='strip size in KB', type=int)
    p.add_argument('-r', '--raid-level', help='raid level, only raid level 0 is supported', type=int, required=True)
    p.add_argument('-b', '--base-bdevs', help='base bdevs name, whitespace separated list in quotes', required=True)
    p.set_defaults(func=construct_raid_bdev)

    def destroy_raid_bdev(args):
        rpc.bdev.destroy_raid_bdev(args.client,
                                   name=args.name)
    p = subparsers.add_parser('destroy_raid_bdev', help='Destroy existing raid bdev')
    p.add_argument('name', help='raid bdev name')
    p.set_defaults(func=destroy_raid_bdev)

    # split
    def construct_split_vbdev(args):
        print_array(rpc.bdev.construct_split_vbdev(args.client,
                                                   base_bdev=args.base_bdev,
                                                   split_count=args.split_count,
                                                   split_size_mb=args.split_size_mb))

    p = subparsers.add_parser('construct_split_vbdev', help="""Add given disk name to split config. If bdev with base_name
    name exist the split bdevs will be created right away, if not split bdevs will be created when base bdev became
    available (during examination process).""")
    p.add_argument('base_bdev', help='base bdev name')
    p.add_argument('-s', '--split-size-mb', help='size in MiB for each bdev', type=int, default=0)
    p.add_argument('split_count', help="""Optional - number of split bdevs to create. Total size * split_count must not
    exceed the base bdev size.""", type=int)
    p.set_defaults(func=construct_split_vbdev)

    def destruct_split_vbdev(args):
        rpc.bdev.destruct_split_vbdev(args.client,
                                      base_bdev=args.base_bdev)

    p = subparsers.add_parser('destruct_split_vbdev', help="""Delete split config with all created splits.""")
    p.add_argument('base_bdev', help='base bdev name')
    p.set_defaults(func=destruct_split_vbdev)

    # ftl
    def construct_ftl_bdev(args):
        print_dict(rpc.bdev.construct_ftl_bdev(args.client,
                                               name=args.name,
                                               trtype=args.trtype,
                                               traddr=args.traddr,
                                               punits=args.punits,
                                               uuid=args.uuid,
                                               cache=args.cache,
                                               allow_open_bands=args.allow_open_bands))

    p = subparsers.add_parser('construct_ftl_bdev',
                              help='Add FTL bdev')
    p.add_argument('-b', '--name', help="Name of the bdev", required=True)
    p.add_argument('-t', '--trtype',
                   help='NVMe target trtype: e.g., pcie', default='pcie')
    p.add_argument('-a', '--traddr',
                   help='NVMe target address: e.g., an ip address or BDF', required=True)
    p.add_argument('-l', '--punits', help='Parallel unit range in the form of start-end: e.g. 4-8',
                   required=True)
    p.add_argument('-u', '--uuid', help='UUID of restored bdev (not applicable when creating new '
                   'instance): e.g. b286d19a-0059-4709-abcd-9f7732b1567d (optional)')
    p.add_argument('-c', '--cache', help='Name of the bdev to be used as a write buffer cache (optional)')
    p.add_argument('-o', '--allow_open_bands', help='Restoring after dirty shutdown without cache will'
                   ' result in partial data recovery, instead of error', action='store_true')
    p.set_defaults(func=construct_ftl_bdev)

    def delete_ftl_bdev(args):
        print_dict(rpc.bdev.delete_ftl_bdev(args.client, name=args.name))

    p = subparsers.add_parser('delete_ftl_bdev', help='Delete FTL bdev')
    p.add_argument('-b', '--name', help="Name of the bdev", required=True)
    p.set_defaults(func=delete_ftl_bdev)

    # nbd
    def start_nbd_disk(args):
        print(rpc.nbd.start_nbd_disk(args.client,
                                     bdev_name=args.bdev_name,
                                     nbd_device=args.nbd_device))

    p = subparsers.add_parser('start_nbd_disk', help='Export a bdev as a nbd disk')
    p.add_argument('bdev_name', help='Blockdev name to be exported. Example: Malloc0.')
    p.add_argument('nbd_device', help='Nbd device name to be assigned. Example: /dev/nbd0.', nargs='?')
    p.set_defaults(func=start_nbd_disk)

    def stop_nbd_disk(args):
        rpc.nbd.stop_nbd_disk(args.client,
                              nbd_device=args.nbd_device)

    p = subparsers.add_parser('stop_nbd_disk', help='Stop a nbd disk')
    p.add_argument('nbd_device', help='Nbd device name to be stopped. Example: /dev/nbd0.')
    p.set_defaults(func=stop_nbd_disk)

    def get_nbd_disks(args):
        print_dict(rpc.nbd.get_nbd_disks(args.client,
                                         nbd_device=args.nbd_device))

    p = subparsers.add_parser('get_nbd_disks', help='Display full or specified nbd device list')
    p.add_argument('-n', '--nbd-device', help="Path of the nbd device. Example: /dev/nbd0", required=False)
    p.set_defaults(func=get_nbd_disks)

    # net
    def add_ip_address(args):
        rpc.net.add_ip_address(args.client, ifc_index=args.ifc_index, ip_addr=args.ip_addr)

    p = subparsers.add_parser('add_ip_address', help='Add IP address')
    p.add_argument('ifc_index', help='ifc index of the nic device.', type=int)
    p.add_argument('ip_addr', help='ip address will be added.')
    p.set_defaults(func=add_ip_address)

    def delete_ip_address(args):
        rpc.net.delete_ip_address(args.client, ifc_index=args.ifc_index, ip_addr=args.ip_addr)

    p = subparsers.add_parser('delete_ip_address', help='Delete IP address')
    p.add_argument('ifc_index', help='ifc index of the nic device.', type=int)
    p.add_argument('ip_addr', help='ip address will be deleted.')
    p.set_defaults(func=delete_ip_address)

    def get_interfaces(args):
        print_dict(rpc.net.get_interfaces(args.client))

    p = subparsers.add_parser(
        'get_interfaces', help='Display current interface list')
    p.set_defaults(func=get_interfaces)

    # NVMe-oF
    def set_nvmf_target_max_subsystems(args):
        rpc.nvmf.set_nvmf_target_max_subsystems(args.client,
                                                max_subsystems=args.max_subsystems)

    p = subparsers.add_parser('set_nvmf_target_max_subsystems', help='Set the maximum number of NVMf target subsystems')
    p.add_argument('-x', '--max-subsystems', help='Max number of NVMf subsystems', type=int, required=True)
    p.set_defaults(func=set_nvmf_target_max_subsystems)

    def set_nvmf_target_config(args):
        rpc.nvmf.set_nvmf_target_config(args.client,
                                        acceptor_poll_rate=args.acceptor_poll_rate,
                                        conn_sched=args.conn_sched)

    p = subparsers.add_parser('set_nvmf_target_config', help='Set NVMf target config')
    p.add_argument('-r', '--acceptor-poll-rate', help='Polling interval of the acceptor for incoming connections (usec)', type=int)
    p.add_argument('-s', '--conn-sched', help="""'roundrobin' - Schedule the incoming connections from any host
    on the cores in a round robin manner (Default). 'hostip' - Schedule all the incoming connections from a
    specific host IP on to the same core. Connections from different IP will be assigned to cores in a round
    robin manner""")
    p.set_defaults(func=set_nvmf_target_config)

    def nvmf_create_transport(args):
        rpc.nvmf.nvmf_create_transport(args.client,
                                       trtype=args.trtype,
                                       max_queue_depth=args.max_queue_depth,
                                       max_qpairs_per_ctrlr=args.max_qpairs_per_ctrlr,
                                       in_capsule_data_size=args.in_capsule_data_size,
                                       max_io_size=args.max_io_size,
                                       io_unit_size=args.io_unit_size,
                                       max_aq_depth=args.max_aq_depth,
                                       num_shared_buffers=args.num_shared_buffers,
                                       buf_cache_size=args.buf_cache_size,
                                       max_srq_depth=args.max_srq_depth,
                                       no_srq=args.no_srq,
                                       c2h_success=args.c2h_success,
                                       dif_insert_or_strip=args.dif_insert_or_strip)

    p = subparsers.add_parser('nvmf_create_transport', help='Create NVMf transport')
    p.add_argument('-t', '--trtype', help='Transport type (ex. RDMA)', type=str, required=True)
    p.add_argument('-q', '--max-queue-depth', help='Max number of outstanding I/O per queue', type=int)
    p.add_argument('-p', '--max-qpairs-per-ctrlr', help='Max number of SQ and CQ per controller', type=int)
    p.add_argument('-c', '--in-capsule-data-size', help='Max number of in-capsule data size', type=int)
    p.add_argument('-i', '--max-io-size', help='Max I/O size (bytes)', type=int)
    p.add_argument('-u', '--io-unit-size', help='I/O unit size (bytes)', type=int)
    p.add_argument('-a', '--max-aq-depth', help='Max number of admin cmds per AQ', type=int)
    p.add_argument('-n', '--num-shared-buffers', help='The number of pooled data buffers available to the transport', type=int)
    p.add_argument('-b', '--buf-cache-size', help='The number of shared buffers to reserve for each poll group', type=int)
    p.add_argument('-s', '--max-srq-depth', help='Max number of outstanding I/O per SRQ. Relevant only for RDMA transport', type=int)
    p.add_argument('-r', '--no-srq', action='store_true', help='Disable per-thread shared receive queue. Relevant only for RDMA transport')
    p.add_argument('-o', '--c2h-success', help='Enable C2H success optimization. Relevant only for TCP transport', type=bool)
    p.add_argument('-f', '--dif-insert-or-strip', action='store_true', help='Enable DIF insert/strip. Relevant only for TCP transport')
    p.set_defaults(func=nvmf_create_transport)

    def get_nvmf_transports(args):
        print_dict(rpc.nvmf.get_nvmf_transports(args.client))

    p = subparsers.add_parser('get_nvmf_transports',
                              help='Display nvmf transports')
    p.set_defaults(func=get_nvmf_transports)

    def get_nvmf_subsystems(args):
        print_dict(rpc.nvmf.get_nvmf_subsystems(args.client))

    p = subparsers.add_parser('get_nvmf_subsystems',
                              help='Display nvmf subsystems')
    p.set_defaults(func=get_nvmf_subsystems)

    def nvmf_subsystem_create(args):
        rpc.nvmf.nvmf_subsystem_create(args.client,
                                       nqn=args.nqn,
                                       serial_number=args.serial_number,
                                       model_number=args.model_number,
                                       allow_any_host=args.allow_any_host,
                                       max_namespaces=args.max_namespaces)

    p = subparsers.add_parser('nvmf_subsystem_create', help='Create an NVMe-oF subsystem')
    p.add_argument('nqn', help='Subsystem NQN (ASCII)')
    p.add_argument("-s", "--serial-number", help="""
    Format:  'sn' etc
    Example: 'SPDK00000000000001'""", default='00000000000000000000')
    p.add_argument("-d", "--model-number", help="""
    Format:  'mn' etc
    Example: 'SPDK Controller'""", default='SPDK bdev Controller')
    p.add_argument("-a", "--allow-any-host", action='store_true', help="Allow any host to connect (don't enforce host NQN whitelist)")
    p.add_argument("-m", "--max-namespaces", help="Maximum number of namespaces allowed",
                   type=int, default=0)
    p.set_defaults(func=nvmf_subsystem_create)

    def delete_nvmf_subsystem(args):
        rpc.nvmf.delete_nvmf_subsystem(args.client,
                                       nqn=args.subsystem_nqn)

    p = subparsers.add_parser('delete_nvmf_subsystem',
                              help='Delete a nvmf subsystem')
    p.add_argument('subsystem_nqn',
                   help='subsystem nqn to be deleted. Example: nqn.2016-06.io.spdk:cnode1.')
    p.set_defaults(func=delete_nvmf_subsystem)

    def nvmf_subsystem_add_listener(args):
        rpc.nvmf.nvmf_subsystem_add_listener(args.client,
                                             nqn=args.nqn,
                                             trtype=args.trtype,
                                             traddr=args.traddr,
                                             adrfam=args.adrfam,
                                             trsvcid=args.trsvcid)

    p = subparsers.add_parser('nvmf_subsystem_add_listener', help='Add a listener to an NVMe-oF subsystem')
    p.add_argument('nqn', help='NVMe-oF subsystem NQN')
    p.add_argument('-t', '--trtype', help='NVMe-oF transport type: e.g., rdma', required=True)
    p.add_argument('-a', '--traddr', help='NVMe-oF transport address: e.g., an ip address', required=True)
    p.add_argument('-f', '--adrfam', help='NVMe-oF transport adrfam: e.g., ipv4, ipv6, ib, fc, intra_host')
    p.add_argument('-s', '--trsvcid', help='NVMe-oF transport service id: e.g., a port number')
    p.set_defaults(func=nvmf_subsystem_add_listener)

    def nvmf_subsystem_remove_listener(args):
        rpc.nvmf.nvmf_subsystem_remove_listener(args.client,
                                                nqn=args.nqn,
                                                trtype=args.trtype,
                                                traddr=args.traddr,
                                                adrfam=args.adrfam,
                                                trsvcid=args.trsvcid)

    p = subparsers.add_parser('nvmf_subsystem_remove_listener', help='Remove a listener from an NVMe-oF subsystem')
    p.add_argument('nqn', help='NVMe-oF subsystem NQN')
    p.add_argument('-t', '--trtype', help='NVMe-oF transport type: e.g., rdma', required=True)
    p.add_argument('-a', '--traddr', help='NVMe-oF transport address: e.g., an ip address', required=True)
    p.add_argument('-f', '--adrfam', help='NVMe-oF transport adrfam: e.g., ipv4, ipv6, ib, fc, intra_host')
    p.add_argument('-s', '--trsvcid', help='NVMe-oF transport service id: e.g., a port number')
    p.set_defaults(func=nvmf_subsystem_remove_listener)

    def nvmf_subsystem_add_ns(args):
        rpc.nvmf.nvmf_subsystem_add_ns(args.client,
                                       nqn=args.nqn,
                                       bdev_name=args.bdev_name,
                                       ptpl_file=args.ptpl_file,
                                       nsid=args.nsid,
                                       nguid=args.nguid,
                                       eui64=args.eui64,
                                       uuid=args.uuid)

    p = subparsers.add_parser('nvmf_subsystem_add_ns', help='Add a namespace to an NVMe-oF subsystem')
    p.add_argument('nqn', help='NVMe-oF subsystem NQN')
    p.add_argument('bdev_name', help='The name of the bdev that will back this namespace')
    p.add_argument('-p', '--ptpl-file', help='The persistent reservation storage location (optional)', type=str)
    p.add_argument('-n', '--nsid', help='The requested NSID (optional)', type=int)
    p.add_argument('-g', '--nguid', help='Namespace globally unique identifier (optional)')
    p.add_argument('-e', '--eui64', help='Namespace EUI-64 identifier (optional)')
    p.add_argument('-u', '--uuid', help='Namespace UUID (optional)')
    p.set_defaults(func=nvmf_subsystem_add_ns)

    def nvmf_subsystem_remove_ns(args):
        rpc.nvmf.nvmf_subsystem_remove_ns(args.client,
                                          nqn=args.nqn,
                                          nsid=args.nsid)

    p = subparsers.add_parser('nvmf_subsystem_remove_ns', help='Remove a namespace to an NVMe-oF subsystem')
    p.add_argument('nqn', help='NVMe-oF subsystem NQN')
    p.add_argument('nsid', help='The requested NSID', type=int)
    p.set_defaults(func=nvmf_subsystem_remove_ns)

    def nvmf_subsystem_add_host(args):
        rpc.nvmf.nvmf_subsystem_add_host(args.client,
                                         nqn=args.nqn,
                                         host=args.host)

    p = subparsers.add_parser('nvmf_subsystem_add_host', help='Add a host to an NVMe-oF subsystem')
    p.add_argument('nqn', help='NVMe-oF subsystem NQN')
    p.add_argument('host', help='Host NQN to allow')
    p.set_defaults(func=nvmf_subsystem_add_host)

    def nvmf_subsystem_remove_host(args):
        rpc.nvmf.nvmf_subsystem_remove_host(args.client,
                                            nqn=args.nqn,
                                            host=args.host)

    p = subparsers.add_parser('nvmf_subsystem_remove_host', help='Remove a host from an NVMe-oF subsystem')
    p.add_argument('nqn', help='NVMe-oF subsystem NQN')
    p.add_argument('host', help='Host NQN to remove')
    p.set_defaults(func=nvmf_subsystem_remove_host)

    def nvmf_subsystem_allow_any_host(args):
        rpc.nvmf.nvmf_subsystem_allow_any_host(args.client,
                                               nqn=args.nqn,
                                               disable=args.disable)

    p = subparsers.add_parser('nvmf_subsystem_allow_any_host', help='Allow any host to connect to the subsystem')
    p.add_argument('nqn', help='NVMe-oF subsystem NQN')
    p.add_argument('-e', '--enable', action='store_true', help='Enable allowing any host')
    p.add_argument('-d', '--disable', action='store_true', help='Disable allowing any host')
    p.set_defaults(func=nvmf_subsystem_allow_any_host)

    def nvmf_get_stats(args):
        print_dict(rpc.nvmf.nvmf_get_stats(args.client))

    p = subparsers.add_parser(
        'nvmf_get_stats', help='Display current statistics for NVMf subsystem')
    p.set_defaults(func=nvmf_get_stats)

    # pmem
    def create_pmem_pool(args):
        num_blocks = int((args.total_size * 1024 * 1024) / args.block_size)
        rpc.pmem.create_pmem_pool(args.client,
                                  pmem_file=args.pmem_file,
                                  num_blocks=num_blocks,
                                  block_size=args.block_size)

    p = subparsers.add_parser('create_pmem_pool', help='Create pmem pool')
    p.add_argument('pmem_file', help='Path to pmemblk pool file')
    p.add_argument('total_size', help='Size of malloc bdev in MB (int > 0)', type=int)
    p.add_argument('block_size', help='Block size for this pmem pool', type=int)
    p.set_defaults(func=create_pmem_pool)

    def pmem_pool_info(args):
        print_dict(rpc.pmem.pmem_pool_info(args.client,
                                           pmem_file=args.pmem_file))

    p = subparsers.add_parser('pmem_pool_info', help='Display pmem pool info and check consistency')
    p.add_argument('pmem_file', help='Path to pmemblk pool file')
    p.set_defaults(func=pmem_pool_info)

    def delete_pmem_pool(args):
        rpc.pmem.delete_pmem_pool(args.client,
                                  pmem_file=args.pmem_file)

    p = subparsers.add_parser('delete_pmem_pool', help='Delete pmem pool')
    p.add_argument('pmem_file', help='Path to pmemblk pool file')
    p.set_defaults(func=delete_pmem_pool)

    # subsystem
    def get_subsystems(args):
        print_dict(rpc.subsystem.get_subsystems(args.client))

    p = subparsers.add_parser('get_subsystems', help="""Print subsystems array in initialization order. Each subsystem
    entry contain (unsorted) array of subsystems it depends on.""")
    p.set_defaults(func=get_subsystems)

    def get_subsystem_config(args):
        print_dict(rpc.subsystem.get_subsystem_config(args.client, args.name))

    p = subparsers.add_parser('get_subsystem_config', help="""Print subsystem configuration""")
    p.add_argument('name', help='Name of subsystem to query')
    p.set_defaults(func=get_subsystem_config)

    # vhost
    def set_vhost_controller_coalescing(args):
        rpc.vhost.set_vhost_controller_coalescing(args.client,
                                                  ctrlr=args.ctrlr,
                                                  delay_base_us=args.delay_base_us,
                                                  iops_threshold=args.iops_threshold)

    p = subparsers.add_parser('set_vhost_controller_coalescing', help='Set vhost controller coalescing')
    p.add_argument('ctrlr', help='controller name')
    p.add_argument('delay_base_us', help='Base delay time', type=int)
    p.add_argument('iops_threshold', help='IOPS threshold when coalescing is enabled', type=int)
    p.set_defaults(func=set_vhost_controller_coalescing)

    def construct_vhost_scsi_controller(args):
        rpc.vhost.construct_vhost_scsi_controller(args.client,
                                                  ctrlr=args.ctrlr,
                                                  cpumask=args.cpumask)

    p = subparsers.add_parser(
        'construct_vhost_scsi_controller', help='Add new vhost controller')
    p.add_argument('ctrlr', help='controller name')
    p.add_argument('--cpumask', help='cpu mask for this controller')
    p.set_defaults(func=construct_vhost_scsi_controller)

    def add_vhost_scsi_lun(args):
        print_json(rpc.vhost.add_vhost_scsi_lun(args.client,
                                                ctrlr=args.ctrlr,
                                                scsi_target_num=args.scsi_target_num,
                                                bdev_name=args.bdev_name))

    p = subparsers.add_parser('add_vhost_scsi_lun',
                              help='Add lun to vhost controller')
    p.add_argument('ctrlr', help='conntroller name where add lun')
    p.add_argument('scsi_target_num', help='scsi_target_num', type=int)
    p.add_argument('bdev_name', help='bdev name')
    p.set_defaults(func=add_vhost_scsi_lun)

    def remove_vhost_scsi_target(args):
        rpc.vhost.remove_vhost_scsi_target(args.client,
                                           ctrlr=args.ctrlr,
                                           scsi_target_num=args.scsi_target_num)

    p = subparsers.add_parser('remove_vhost_scsi_target', help='Remove target from vhost controller')
    p.add_argument('ctrlr', help='controller name to remove target from')
    p.add_argument('scsi_target_num', help='scsi_target_num', type=int)
    p.set_defaults(func=remove_vhost_scsi_target)

    def construct_vhost_blk_controller(args):
        rpc.vhost.construct_vhost_blk_controller(args.client,
                                                 ctrlr=args.ctrlr,
                                                 dev_name=args.dev_name,
                                                 cpumask=args.cpumask,
                                                 readonly=args.readonly)

    p = subparsers.add_parser('construct_vhost_blk_controller', help='Add a new vhost block controller')
    p.add_argument('ctrlr', help='controller name')
    p.add_argument('dev_name', help='device name')
    p.add_argument('--cpumask', help='cpu mask for this controller')
    p.add_argument("-r", "--readonly", action='store_true', help='Set controller as read-only')
    p.set_defaults(func=construct_vhost_blk_controller)

    def construct_vhost_nvme_controller(args):
        rpc.vhost.construct_vhost_nvme_controller(args.client,
                                                  ctrlr=args.ctrlr,
                                                  io_queues=args.io_queues,
                                                  cpumask=args.cpumask)

    p = subparsers.add_parser('construct_vhost_nvme_controller', help='Add new vhost controller')
    p.add_argument('ctrlr', help='controller name')
    p.add_argument('io_queues', help='number of IO queues for the controller', type=int)
    p.add_argument('--cpumask', help='cpu mask for this controller')
    p.set_defaults(func=construct_vhost_nvme_controller)

    def add_vhost_nvme_ns(args):
        rpc.vhost.add_vhost_nvme_ns(args.client,
                                    ctrlr=args.ctrlr,
                                    bdev_name=args.bdev_name)

    p = subparsers.add_parser('add_vhost_nvme_ns', help='Add a Namespace to vhost controller')
    p.add_argument('ctrlr', help='conntroller name where add a Namespace')
    p.add_argument('bdev_name', help='block device name for a new Namespace')
    p.set_defaults(func=add_vhost_nvme_ns)

    def get_vhost_controllers(args):
        print_dict(rpc.vhost.get_vhost_controllers(args.client, args.name))

    p = subparsers.add_parser('get_vhost_controllers', help='List all or specific vhost controller(s)')
    p.add_argument('-n', '--name', help="Name of vhost controller", required=False)
    p.set_defaults(func=get_vhost_controllers)

    def remove_vhost_controller(args):
        rpc.vhost.remove_vhost_controller(args.client,
                                          ctrlr=args.ctrlr)

    p = subparsers.add_parser('remove_vhost_controller', help='Remove a vhost controller')
    p.add_argument('ctrlr', help='controller name')
    p.set_defaults(func=remove_vhost_controller)

    def construct_virtio_dev(args):
        print_array(rpc.vhost.construct_virtio_dev(args.client,
                                                   name=args.name,
                                                   trtype=args.trtype,
                                                   traddr=args.traddr,
                                                   dev_type=args.dev_type,
                                                   vq_count=args.vq_count,
                                                   vq_size=args.vq_size))

    p = subparsers.add_parser('construct_virtio_dev', help="""Construct new virtio device using provided
    transport type and device type. In case of SCSI device type this implies scan and add bdevs offered by
    remote side. Result is array of added bdevs.""")
    p.add_argument('name', help="Use this name as base for new created bdevs")
    p.add_argument('-t', '--trtype',
                   help='Virtio target transport type: pci or user', required=True)
    p.add_argument('-a', '--traddr',
                   help='Transport type specific target address: e.g. UNIX domain socket path or BDF', required=True)
    p.add_argument('-d', '--dev-type',
                   help='Device type: blk or scsi', required=True)
    p.add_argument('--vq-count', help='Number of virtual queues to be used.', type=int)
    p.add_argument('--vq-size', help='Size of each queue', type=int)
    p.set_defaults(func=construct_virtio_dev)

    def get_virtio_scsi_devs(args):
        print_dict(rpc.vhost.get_virtio_scsi_devs(args.client))

    p = subparsers.add_parser('get_virtio_scsi_devs', help='List all Virtio-SCSI devices.')
    p.set_defaults(func=get_virtio_scsi_devs)

    def remove_virtio_bdev(args):
        rpc.vhost.remove_virtio_bdev(args.client,
                                     name=args.name)

    p = subparsers.add_parser('remove_virtio_bdev', help="""Remove a Virtio device
    This will delete all bdevs exposed by this device""")
    p.add_argument('name', help='Virtio device name. E.g. VirtioUser0')
    p.set_defaults(func=remove_virtio_bdev)

    # ioat
    def scan_ioat_copy_engine(args):
        pci_whitelist = []
        if args.pci_whitelist:
            for w in args.pci_whitelist.strip().split(" "):
                pci_whitelist.append(w)
        rpc.ioat.scan_ioat_copy_engine(args.client, pci_whitelist)

    p = subparsers.add_parser('scan_ioat_copy_engine', help='Set scan and enable IOAT copy engine offload.')
    p.add_argument('-w', '--pci-whitelist', help="""Whitespace-separated list of PCI addresses in
    domain:bus:device.function format or domain.bus.device.function format""")
    p.set_defaults(func=scan_ioat_copy_engine)

    # send_nvme_cmd
    def send_nvme_cmd(args):
        print_dict(rpc.nvme.send_nvme_cmd(args.client,
                                          name=args.nvme_name,
                                          cmd_type=args.cmd_type,
                                          data_direction=args.data_direction,
                                          cmdbuf=args.cmdbuf,
                                          data=args.data,
                                          metadata=args.metadata,
                                          data_len=args.data_length,
                                          metadata_len=args.metadata_length,
                                          timeout_ms=args.timeout_ms))

    p = subparsers.add_parser('send_nvme_cmd', help='NVMe passthrough cmd.')
    p.add_argument('-n', '--nvme-name', help="""Name of the operating NVMe controller""")
    p.add_argument('-t', '--cmd-type', help="""Type of nvme cmd. Valid values are: admin, io""")
    p.add_argument('-r', '--data-direction', help="""Direction of data transfer. Valid values are: c2h, h2c""")
    p.add_argument('-c', '--cmdbuf', help="""NVMe command encoded by base64 urlsafe""")
    p.add_argument('-d', '--data', help="""Data transferring to controller from host, encoded by base64 urlsafe""")
    p.add_argument('-m', '--metadata', help="""Metadata transferring to controller from host, encoded by base64 urlsafe""")
    p.add_argument('-D', '--data-length', help="""Data length required to transfer from controller to host""", type=int)
    p.add_argument('-M', '--metadata-length', help="""Metadata length required to transfer from controller to host""", type=int)
    p.add_argument('-T', '--timeout-ms',
                   help="""Command execution timeout value, in milliseconds,  if 0, don't track timeout""", type=int, default=0)
    p.set_defaults(func=send_nvme_cmd)

    # Notifications
    def get_notification_types(args):
        print_dict(rpc.notify.get_notification_types(args.client))

    p = subparsers.add_parser('get_notification_types', help='List available notifications that user can subscribe to.')
    p.set_defaults(func=get_notification_types)

    def get_notifications(args):
        ret = rpc.notify.get_notifications(args.client,
                                           id=args.id,
                                           max=args.max)
        print_dict(ret)

    p = subparsers.add_parser('get_notifications', help='Get notifications')
    p.add_argument('-i', '--id', help="""First ID to start fetching from""", type=int)
    p.add_argument('-n', '--max', help="""Maximum number of notifications to return in response""", type=int)
    p.set_defaults(func=get_notifications)

    def thread_get_stats(args):
        print_dict(rpc.app.thread_get_stats(args.client))

    p = subparsers.add_parser(
        'thread_get_stats', help='Display current statistics of all the threads')
    p.set_defaults(func=thread_get_stats)

    def check_called_name(name):
        if name in deprecated_aliases:
            print("{} is deprecated, use {} instead.".format(name, deprecated_aliases[name]), file=sys.stderr)

    class dry_run_client:
        def call(self, method, params=None):
            print("Request:\n" + json.dumps({"method": method, "params": params}, indent=2))

    def null_print(arg):
        pass

    def call_rpc_func(args):
        args.func(args)
        check_called_name(args.called_rpc_name)

    def execute_script(parser, client, fd):
        executed_rpc = ""
        for rpc_call in map(str.rstrip, fd):
            if not rpc_call.strip():
                continue
            executed_rpc = "\n".join([executed_rpc, rpc_call])
            args = parser.parse_args(shlex.split(rpc_call))
            args.client = client
            try:
                call_rpc_func(args)
            except JSONRPCException as ex:
                print("Exception:")
                print(executed_rpc.strip() + " <<<")
                print(ex.message)
                exit(1)

    args = parser.parse_args()
    if args.dry_run:
        args.client = dry_run_client()
        print_dict = null_print
        print_json = null_print
        print_array = null_print
    else:
        args.client = rpc.client.JSONRPCClient(args.server_addr, args.port, args.timeout, log_level=getattr(logging, args.verbose.upper()))
    if hasattr(args, 'func'):
        try:
            call_rpc_func(args)
        except JSONRPCException as ex:
            print(ex)
            exit(1)
    elif sys.stdin.isatty():
        # No arguments and no data piped through stdin
        parser.print_help()
        exit(1)
    else:
        execute_script(parser, args.client, sys.stdin)
