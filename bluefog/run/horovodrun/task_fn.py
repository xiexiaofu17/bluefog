# Copyright 2019 Uber Technologies, Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

import sys

from bluefog.run.horovodrun.common.util import codec, host_hash
from bluefog.run.horovodrun.driver import driver_service
from bluefog.run.horovodrun.task import task_service


def _task_fn(index, driver_addresses, num_hosts, tmout, key):
    task = task_service.HorovodRunTaskService(index, key)
    try:
        driver = driver_service.HorovodRunDriverClient(
            driver_addresses, key)
        driver.register_task(index,
                             task.addresses(),
                             host_hash.host_hash())
        task.wait_for_initial_registration(tmout)
        # Tasks ping each other in a circular fashion to determine interfaces
        # reachable within the cluster.
        next_task_index = (index + 1) % num_hosts
        next_task_addresses = driver.all_task_addresses(next_task_index)
        # We request interface matching to weed out all the NAT'ed interfaces.
        next_task = task_service.HorovodRunTaskClient(
            next_task_index,
            next_task_addresses,
            key,
            match_intf=True,
            retries=10)
        driver.register_task_to_task_addresses(next_task_index,
                                               next_task.addresses())
        # Notify the next task that the address checks are completed.
        next_task.task_to_task_address_check_completed()
        # Wait to get a notification from previous task that its address checks
        # are completed as well.
        task.wait_for_task_to_task_address_check_finish_signal(tmout)

    finally:
        task.shutdown()


if __name__ == '__main__':
    if len(sys.argv) != 6:
        print(
            'Usage: %s <index> <service addresses> <num_hosts> <tmout> <key>' %
            sys.argv[0])
        sys.exit(1)

    index = codec.loads_base64(sys.argv[1])
    driver_addresses = codec.loads_base64(sys.argv[2])
    num_hosts = codec.loads_base64(sys.argv[3])
    tmout = codec.loads_base64(sys.argv[4])
    key = codec.loads_base64(sys.argv[5])

    _task_fn(index, driver_addresses, num_hosts, tmout, key)
