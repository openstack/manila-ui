# Copyright 2016 Red Hat Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

# The OPENSTACK_MANILA_FEATURES settings can be used to enable or disable
# the UI for the various services provided by Manila.
OPENSTACK_MANILA_FEATURES = {
    'enable_share_groups': True,
    'enable_replication': True,
    'enable_migration': True,
    'enable_public_share_type_creation': True,
    'enable_public_share_group_type_creation': True,
    'enable_public_shares': True,
    'enabled_share_protocols': ['NFS', 'CIFS', 'GlusterFS', 'HDFS', 'CephFS',
                                'MapRFS'],
}
