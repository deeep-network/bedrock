#!/bin/bash
set -euo pipefail

# Function to check if a pool exists
check_pool_exists() {
    if zpool list default >/dev/null 2>&1; then
        echo "ERROR: Pool 'default' already exists"
        exit 1
    fi
}

# Function to check if a disk has partitions
check_disk_partitions() {
    local disk=$1
    if lsblk -r "$disk" | grep -q "part"; then
        return 1
    fi
    return 0
}

# Get the root device and handle NVMe partitioning scheme
ROOT_DEVICE=$(findmnt -n -o SOURCE /)
ROOT_DEVICE=$(echo $ROOT_DEVICE | sed 's/p[0-9]*$//')
ROOT_DEVICE=$(readlink -f ${ROOT_DEVICE%[0-9]})

# Check if default pool exists
check_pool_exists

# Find available disks, excluding the root device and its partitions
AVAILABLE_DISKS=($(lsblk -ndp -o NAME | grep -v -e "^${ROOT_DEVICE}" -e "^${ROOT_DEVICE}p[0-9]" -e "loop" -e "sr0" | sort))
DISK_COUNT=${#AVAILABLE_DISKS[@]}

if [ $DISK_COUNT -eq 0 ]; then
    echo "ERROR: No available disks found for ZFS pool"
    exit 1
fi

# Check for partitions on all disks
CLEAN_DISKS=()
for disk in "${AVAILABLE_DISKS[@]}"; do
    if check_disk_partitions "$disk"; then
        CLEAN_DISKS+=("$disk")
    else
        echo "WARNING: Skipping $disk as it contains partitions"
    fi
done

# Update available disks to only include clean disks
AVAILABLE_DISKS=("${CLEAN_DISKS[@]}")
DISK_COUNT=${#AVAILABLE_DISKS[@]}

if [ $DISK_COUNT -eq 0 ]; then
    echo "ERROR: No eligible disks found (all disks have partitions)"
    exit 1
fi

# Verify disk sizes if multiple disks
if [ $DISK_COUNT -gt 1 ]; then
    # Find the largest disk size
    LARGEST_SIZE=0
    for disk in "${AVAILABLE_DISKS[@]}"; do
        CURRENT_SIZE=$(lsblk -bdno SIZE "$disk")
        if [ "$CURRENT_SIZE" -gt "$LARGEST_SIZE" ]; then
            LARGEST_SIZE=$CURRENT_SIZE
        fi
    done

    VALID_DISKS=()
    for disk in "${AVAILABLE_DISKS[@]}"; do
        CURRENT_SIZE=$(lsblk -bdno SIZE "$disk")
        if [ "$CURRENT_SIZE" -ge "$LARGEST_SIZE" ]; then
            VALID_DISKS+=("$disk")
        else
            echo "WARNING: Skipping $disk due to size mismatch"
        fi
    done

    # Update available disks to only include matching sizes
    AVAILABLE_DISKS=("${VALID_DISKS[@]}")
    DISK_COUNT=${#AVAILABLE_DISKS[@]}

    if [ $DISK_COUNT -eq 0 ]; then
        echo "ERROR: No valid disks found after size verification"
        exit 1
    fi
fi

# Create disk string for zpool create command
if [ $DISK_COUNT -ge 2 ]; then
    POOL_CONFIG="raidz1 ${AVAILABLE_DISKS[*]}"
else
    POOL_CONFIG="${AVAILABLE_DISKS[*]}"
fi

# Create the pool
zpool create -f default $POOL_CONFIG
zpool set autotrim=on default

# Set basic pool properties
zfs set compression=lz4 default
zfs set atime=off default

# Create basic datasets
zfs create default/lxd
echo "ZFS pool 'default' created successfully"
