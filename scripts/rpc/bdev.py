def set_bdev_options(client, bdev_io_pool_size=None, bdev_io_cache_size=None):
    """Set parameters for the bdev subsystem.

    Args:
        bdev_io_pool_size: number of bdev_io structures in shared buffer pool (optional)
        bdev_io_cache_size: maximum number of bdev_io structures cached per thread (optional)
    """
    params = {}

    if bdev_io_pool_size:
        params['bdev_io_pool_size'] = bdev_io_pool_size
    if bdev_io_cache_size:
        params['bdev_io_cache_size'] = bdev_io_cache_size

    return client.call('set_bdev_options', params)


def construct_compress_bdev(client, base_bdev_name, pm_path):
    """Construct a compress virtual block device.

    Args:
        base_bdev_name: name of the underlying base bdev
        pm_path: path to persistent memory

    Returns:
        Name of created virtual block device.
    """
    params = {'base_bdev_name': base_bdev_name, 'pm_path': pm_path}

    return client.call('construct_compress_bdev', params)


def delete_compress_bdev(client, name):
    """Delete compress virtual block device.

    Args:
        name: name of compress vbdev to delete
    """
    params = {'name': name}
    return client.call('delete_compress_bdev', params)


def set_compress_pmd(client, pmd):
    """Set pmd options for the bdev compress.

    Args:
        pmd: 0 = auto-select, 1 = QAT, 2 = ISAL
    """
    params = {'pmd': pmd}

    return client.call('set_compress_pmd', params)


def construct_crypto_bdev(client, base_bdev_name, name, crypto_pmd, key):
    """Construct a crypto virtual block device.

    Args:
        base_bdev_name: name of the underlying base bdev
        name: name for the crypto vbdev
        crypto_pmd: name of of the DPDK crypto driver to use
        key: key

    Returns:
        Name of created virtual block device.
    """
    params = {'base_bdev_name': base_bdev_name, 'name': name, 'crypto_pmd': crypto_pmd, 'key': key}

    return client.call('construct_crypto_bdev', params)


def delete_crypto_bdev(client, name):
    """Delete crypto virtual block device.

    Args:
        name: name of crypto vbdev to delete
    """
    params = {'name': name}
    return client.call('delete_crypto_bdev', params)


def construct_ocf_bdev(client, name, mode, cache_bdev_name, core_bdev_name):
    """Add an OCF block device

    Args:
        name: name of constructed OCF bdev
        mode: OCF cache mode: {'wb', 'wt', 'pt'}
        cache_bdev_name: name of underlying cache bdev
        core_bdev_name: name of underlying core bdev

    Returns:
        Name of created block device
    """
    params = {'name': name, 'mode': mode, 'cache_bdev_name': cache_bdev_name, 'core_bdev_name': core_bdev_name}

    return client.call('construct_ocf_bdev', params)


def delete_ocf_bdev(client, name):
    """Delete an OCF device

    Args:
        name: name of OCF bdev

    """
    params = {'name': name}

    return client.call('delete_ocf_bdev', params)


def get_ocf_stats(client, name):
    """Get statistics of chosen OCF block device

    Args:
        name: name of OCF bdev

    Returns:
        Statistics as json object
    """
    params = {'name': name}

    return client.call('get_ocf_stats', params)


def get_ocf_bdevs(client, name=None):
    """Get list of OCF devices including unregistered ones

    Args:
        name: name of OCF vbdev or name of cache device or name of core device (optional)

    Returns:
        Array of OCF devices with their current status
    """
    params = None
    if name:
        params = {'name': name}
    return client.call('get_ocf_bdevs', params)


def construct_malloc_bdev(client, num_blocks, block_size, name=None, uuid=None):
    """Construct a malloc block device.

    Args:
        num_blocks: size of block device in blocks
        block_size: block size of device; must be a power of 2 and at least 512
        name: name of block device (optional)
        uuid: UUID of block device (optional)

    Returns:
        Name of created block device.
    """
    params = {'num_blocks': num_blocks, 'block_size': block_size}
    if name:
        params['name'] = name
    if uuid:
        params['uuid'] = uuid
    return client.call('construct_malloc_bdev', params)


def delete_malloc_bdev(client, name):
    """Delete malloc block device.

    Args:
        bdev_name: name of malloc bdev to delete
    """
    params = {'name': name}
    return client.call('delete_malloc_bdev', params)


def construct_null_bdev(client, num_blocks, block_size, name, uuid=None):
    """Construct a null block device.

    Args:
        num_blocks: size of block device in blocks
        block_size: block size of device; must be a power of 2 and at least 512
        name: name of block device
        uuid: UUID of block device (optional)

    Returns:
        Name of created block device.
    """
    params = {'name': name, 'num_blocks': num_blocks,
              'block_size': block_size}
    if uuid:
        params['uuid'] = uuid
    return client.call('construct_null_bdev', params)


def delete_null_bdev(client, name):
    """Remove null bdev from the system.

    Args:
        name: name of null bdev to delete
    """
    params = {'name': name}
    return client.call('delete_null_bdev', params)


def get_raid_bdevs(client, category):
    """Get list of raid bdevs based on category

    Args:
        category: any one of all or online or configuring or offline

    Returns:
        List of raid bdev names
    """
    params = {'category': category}
    return client.call('get_raid_bdevs', params)


def construct_raid_bdev(client, name, raid_level, base_bdevs, strip_size=None, strip_size_kb=None):
    """Construct raid bdev. Either strip size arg will work but one is required.

    Args:
        name: user defined raid bdev name
        strip_size (deprecated): strip size of raid bdev in KB, supported values like 8, 16, 32, 64, 128, 256, etc
        strip_size_kb: strip size of raid bdev in KB, supported values like 8, 16, 32, 64, 128, 256, etc
        raid_level: raid level of raid bdev, supported values 0
        base_bdevs: Space separated names of Nvme bdevs in double quotes, like "Nvme0n1 Nvme1n1 Nvme2n1"

    Returns:
        None
    """
    params = {'name': name, 'raid_level': raid_level, 'base_bdevs': base_bdevs}

    if strip_size:
        params['strip_size'] = strip_size

    if strip_size_kb:
        params['strip_size_kb'] = strip_size_kb

    return client.call('construct_raid_bdev', params)


def destroy_raid_bdev(client, name):
    """Destroy raid bdev

    Args:
        name: raid bdev name

    Returns:
        None
    """
    params = {'name': name}
    return client.call('destroy_raid_bdev', params)


def construct_aio_bdev(client, filename, name, block_size=None):
    """Construct a Linux AIO block device.

    Args:
        filename: path to device or file (ex: /dev/sda)
        name: name of block device
        block_size: block size of device (optional; autodetected if omitted)

    Returns:
        Name of created block device.
    """
    params = {'name': name,
              'filename': filename}

    if block_size:
        params['block_size'] = block_size

    return client.call('construct_aio_bdev', params)


def delete_aio_bdev(client, name):
    """Remove aio bdev from the system.

    Args:
        bdev_name: name of aio bdev to delete
    """
    params = {'name': name}
    return client.call('delete_aio_bdev', params)


def set_bdev_nvme_options(client, action_on_timeout=None, timeout_us=None, retry_count=None,
                          nvme_adminq_poll_period_us=None, nvme_ioq_poll_period_us=None):
    """Set options for the bdev nvme. This is startup command.

    Args:
        action_on_timeout:  action to take on command time out. Valid values are: none, reset, abort (optional)
        timeout_us: Timeout for each command, in microseconds. If 0, don't track timeouts (optional)
        retry_count: The number of attempts per I/O when an I/O fails (optional)
        nvme_adminq_poll_period_us: How often the admin queue is polled for asynchronous events in microseconds (optional)
        nvme_ioq_poll_period_us: How often to poll I/O queues for completions in microseconds (optional)
    """
    params = {}

    if action_on_timeout:
        params['action_on_timeout'] = action_on_timeout

    if timeout_us:
        params['timeout_us'] = timeout_us

    if retry_count:
        params['retry_count'] = retry_count

    if nvme_adminq_poll_period_us:
        params['nvme_adminq_poll_period_us'] = nvme_adminq_poll_period_us

    if nvme_ioq_poll_period_us:
        params['nvme_ioq_poll_period_us'] = nvme_ioq_poll_period_us

    return client.call('set_bdev_nvme_options', params)


def set_bdev_nvme_hotplug(client, enable, period_us=None):
    """Set options for the bdev nvme. This is startup command.

    Args:
       enable: True to enable hotplug, False to disable.
       period_us: how often the hotplug is processed for insert and remove events. Set 0 to reset to default. (optional)
    """
    params = {'enable': enable}

    if period_us:
        params['period_us'] = period_us

    return client.call('set_bdev_nvme_hotplug', params)


def construct_nvme_bdev(client, name, trtype, traddr, adrfam=None, trsvcid=None,
                        subnqn=None, hostnqn=None, hostaddr=None, hostsvcid=None,
                        prchk_reftag=None, prchk_guard=None):
    """Construct NVMe namespace block devices.

    Args:
        name: bdev name prefix; "n" + namespace ID will be appended to create unique names
        trtype: transport type ("PCIe", "RDMA")
        traddr: transport address (PCI BDF or IP address)
        adrfam: address family ("IPv4", "IPv6", "IB", or "FC") (optional for PCIe)
        trsvcid: transport service ID (port number for IP-based addresses; optional for PCIe)
        subnqn: subsystem NQN to connect to (optional)
        hostnqn: NQN to connect from (optional)
        hostaddr: host transport address (IP address for IP-based transports, NULL for PCIe or FC; optional)
        hostsvcid: host transport service ID (port number for IP-based transports, NULL for PCIe or FC; optional)
        prchk_reftag: Enable checking of PI reference tag for I/O processing (optional)
        prchk_guard: Enable checking of PI guard for I/O processing (optional)

    Returns:
        Names of created block devices.
    """
    params = {'name': name,
              'trtype': trtype,
              'traddr': traddr}

    if hostnqn:
        params['hostnqn'] = hostnqn

    if hostaddr:
        params['hostaddr'] = hostaddr

    if hostsvcid:
        params['hostsvcid'] = hostsvcid

    if adrfam:
        params['adrfam'] = adrfam

    if trsvcid:
        params['trsvcid'] = trsvcid

    if subnqn:
        params['subnqn'] = subnqn

    if prchk_reftag:
        params['prchk_reftag'] = prchk_reftag

    if prchk_guard:
        params['prchk_guard'] = prchk_guard

    return client.call('construct_nvme_bdev', params)


def delete_nvme_controller(client, name):
    """Remove NVMe controller from the system.

    Args:
        name: controller name
    """

    params = {'name': name}
    return client.call('delete_nvme_controller', params)


def construct_rbd_bdev(client, pool_name, rbd_name, block_size, name=None, user=None, config=None):
    """Construct a Ceph RBD block device.

    Args:
        pool_name: Ceph RBD pool name
        rbd_name: Ceph RBD image name
        block_size: block size of RBD volume
        name: name of block device (optional)
        user: Ceph user name (optional)
        config: map of config keys to values (optional)

    Returns:
        Name of created block device.
    """
    params = {
        'pool_name': pool_name,
        'rbd_name': rbd_name,
        'block_size': block_size,
    }

    if name:
        params['name'] = name
    if user is not None:
        params['user_id'] = user
    if config is not None:
        params['config'] = config

    return client.call('construct_rbd_bdev', params)


def delete_rbd_bdev(client, name):
    """Remove rbd bdev from the system.

    Args:
        name: name of rbd bdev to delete
    """
    params = {'name': name}
    return client.call('delete_rbd_bdev', params)


def construct_error_bdev(client, base_name):
    """Construct an error injection block device.

    Args:
        base_name: base bdev name
    """
    params = {'base_name': base_name}
    return client.call('construct_error_bdev', params)


def bdev_delay_create(client, base_bdev_name, name, avg_read_latency, p99_read_latency, avg_write_latency, p99_write_latency):
    """Construct a delay block device.

    Args:
        base_bdev_name: name of the existing bdev
        name: name of block device
        avg_read_latency: complete 99% of read ops with this delay
        p99_read_latency: complete 1% of read ops with this delay
        avg_write_latency: complete 99% of write ops with this delay
        p99_write_latency: complete 1% of write ops with this delay

    Returns:
        Name of created block device.
    """
    params = {
        'base_bdev_name': base_bdev_name,
        'name': name,
        'avg_read_latency': avg_read_latency,
        'p99_read_latency': p99_read_latency,
        'avg_write_latency': avg_write_latency,
        'p99_write_latency': p99_write_latency,
    }
    return client.call('bdev_delay_create', params)


def bdev_delay_delete(client, name):
    """Remove delay bdev from the system.

    Args:
        name: name of delay bdev to delete
    """
    params = {'name': name}
    return client.call('bdev_delay_delete', params)


def delete_error_bdev(client, name):
    """Remove error bdev from the system.

    Args:
        bdev_name: name of error bdev to delete
    """
    params = {'name': name}
    return client.call('delete_error_bdev', params)


def construct_iscsi_bdev(client, name, url, initiator_iqn):
    """Construct a iSCSI block device.

    Args:
        name: name of block device
        url: iSCSI URL
        initiator_iqn: IQN name to be used by initiator

    Returns:
        Name of created block device.
    """
    params = {
        'name': name,
        'url': url,
        'initiator_iqn': initiator_iqn,
    }
    return client.call('construct_iscsi_bdev', params)


def delete_iscsi_bdev(client, name):
    """Remove iSCSI bdev from the system.

    Args:
        bdev_name: name of iSCSI bdev to delete
    """
    params = {'name': name}
    return client.call('delete_iscsi_bdev', params)


def construct_pmem_bdev(client, pmem_file, name):
    """Construct a libpmemblk block device.

    Args:
        pmem_file: path to pmemblk pool file
        name: name of block device

    Returns:
        Name of created block device.
    """
    params = {
        'pmem_file': pmem_file,
        'name': name
    }
    return client.call('construct_pmem_bdev', params)


def delete_pmem_bdev(client, name):
    """Remove pmem bdev from the system.

    Args:
        name: name of pmem bdev to delete
    """
    params = {'name': name}
    return client.call('delete_pmem_bdev', params)


def construct_passthru_bdev(client, base_bdev_name, name):
    """Construct a pass-through block device.

    Args:
        base_bdev_name: name of the existing bdev
        name: name of block device

    Returns:
        Name of created block device.
    """
    params = {
        'base_bdev_name': base_bdev_name,
        'name': name,
    }
    return client.call('construct_passthru_bdev', params)


def delete_passthru_bdev(client, name):
    """Remove pass through bdev from the system.

    Args:
        name: name of pass through bdev to delete
    """
    params = {'name': name}
    return client.call('delete_passthru_bdev', params)


def construct_split_vbdev(client, base_bdev, split_count, split_size_mb=None):
    """Construct split block devices from a base bdev.

    Args:
        base_bdev: name of bdev to split
        split_count: number of split bdevs to create
        split_size_mb: size of each split volume in MiB (optional)

    Returns:
        List of created block devices.
    """
    params = {
        'base_bdev': base_bdev,
        'split_count': split_count,
    }
    if split_size_mb:
        params['split_size_mb'] = split_size_mb

    return client.call('construct_split_vbdev', params)


def destruct_split_vbdev(client, base_bdev):
    """Destroy split block devices.

    Args:
        base_bdev: name of previously split bdev
    """
    params = {
        'base_bdev': base_bdev,
    }

    return client.call('destruct_split_vbdev', params)


def construct_ftl_bdev(client, name, trtype, traddr, punits, allow_open_bands=None, uuid=None, cache=None):
    """Construct FTL bdev

    Args:
        name: name of the bdev
        trtype: transport type
        traddr: transport address
        punit: parallel unit range
        uuid: UUID of the device
        cache: name of the write buffer bdev
        allow_open_bands: allow for partial restore after dirty shutdown
    """
    params = {'name': name,
              'trtype': trtype,
              'traddr': traddr,
              'punits': punits}
    if uuid:
        params['uuid'] = uuid
    if cache:
        params['cache'] = cache
    if allow_open_bands:
        params['allow_open_bands'] = allow_open_bands

    return client.call('construct_ftl_bdev', params)


def delete_ftl_bdev(client, name):
    """Delete FTL bdev

    Args:
        name: name of the bdev
    """
    params = {'name': name}

    return client.call('delete_ftl_bdev', params)


def get_bdevs(client, name=None):
    """Get information about block devices.

    Args:
        name: bdev name to query (optional; if omitted, query all bdevs)

    Returns:
        List of bdev information objects.
    """
    params = {}
    if name:
        params['name'] = name
    return client.call('get_bdevs', params)


def get_bdevs_iostat(client, name=None):
    """Get I/O statistics for block devices.

    Args:
        name: bdev name to query (optional; if omitted, query all bdevs)

    Returns:
        I/O statistics for the requested block devices.
    """
    params = {}
    if name:
        params['name'] = name
    return client.call('get_bdevs_iostat', params)


def enable_bdev_histogram(client, name, enable):
    """Control whether histogram is enabled for specified bdev.

    Args:
        bdev_name: name of bdev
    """
    params = {'name': name, "enable": enable}
    return client.call('enable_bdev_histogram', params)


def get_bdev_histogram(client, name):
    """Get histogram for specified bdev.

    Args:
        bdev_name: name of bdev
    """
    params = {'name': name}
    return client.call('get_bdev_histogram', params)


def bdev_inject_error(client, name, io_type, error_type, num=1):
    """Inject an error via an error bdev.

    Args:
        name: name of error bdev
        io_type: one of "clear", "read", "write", "unmap", "flush", or "all"
        error_type: one of "failure" or "pending"
        num: number of commands to fail
    """
    params = {
        'name': name,
        'io_type': io_type,
        'error_type': error_type,
        'num': num,
    }

    return client.call('bdev_inject_error', params)


def set_bdev_qd_sampling_period(client, name, period):
    """Enable queue depth tracking on a specified bdev.

    Args:
        name: name of a bdev on which to track queue depth.
        period: period (in microseconds) at which to update the queue depth reading. If set to 0, polling will be disabled.
    """

    params = {}
    params['name'] = name
    params['period'] = period
    return client.call('set_bdev_qd_sampling_period', params)


def set_bdev_qos_limit(
        client,
        name,
        rw_ios_per_sec=None,
        rw_mbytes_per_sec=None,
        r_mbytes_per_sec=None,
        w_mbytes_per_sec=None):
    """Set QoS rate limit on a block device.

    Args:
        name: name of block device
        rw_ios_per_sec: R/W IOs per second limit (>=10000, example: 20000). 0 means unlimited.
        rw_mbytes_per_sec: R/W megabytes per second limit (>=10, example: 100). 0 means unlimited.
        r_mbytes_per_sec: Read megabytes per second limit (>=10, example: 100). 0 means unlimited.
        w_mbytes_per_sec: Write megabytes per second limit (>=10, example: 100). 0 means unlimited.
    """
    params = {}
    params['name'] = name
    if rw_ios_per_sec is not None:
        params['rw_ios_per_sec'] = rw_ios_per_sec
    if rw_mbytes_per_sec is not None:
        params['rw_mbytes_per_sec'] = rw_mbytes_per_sec
    if r_mbytes_per_sec is not None:
        params['r_mbytes_per_sec'] = r_mbytes_per_sec
    if w_mbytes_per_sec is not None:
        params['w_mbytes_per_sec'] = w_mbytes_per_sec
    return client.call('set_bdev_qos_limit', params)


def apply_firmware(client, bdev_name, filename):
    """Download and commit firmware to NVMe device.

    Args:
        bdev_name: name of NVMe block device
        filename: filename of the firmware to download
    """
    params = {
        'filename': filename,
        'bdev_name': bdev_name,
    }
    return client.call('apply_nvme_firmware', params)
