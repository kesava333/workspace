#!/bin/bash

size=$(df -k /dev/mapper/default_vg-root | tail -1 | awk '{print $4}')
dt=$(date '+%d%m%Y');
echo "$dt"
if (($size < 30000000)); then
 find /apt-cacher-ng/updates.clearpathrobotics.com/v1/releases/aws-bundles-2.28/pool/main/clearpath-2.28 -name "clearpath-2.28-rosbridge_2.28.0~$dt" -delete
fi

### Delete old deb's ---- we are keeping lated debs i.e. 3 days debs
