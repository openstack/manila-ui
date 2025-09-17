#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from oslo_utils import uuidutils

import pytest

from manila_ui.tests.selenium.integration import test_share_snapshots
from manila_ui.tests.selenium.integration import test_shares


# Shares fixtures:
@pytest.fixture
def share_name():
    return 'horizon_share_%s' % uuidutils.generate_uuid(dashed=False)


@pytest.fixture
def new_share(request, share_name):
    client_fixture_name = request.param
    openstack_client = request.getfixturevalue(client_fixture_name)
    share = openstack_client.shared_file_system.create_share(
        name=share_name,
        size=1,
        share_protocol="NFS",
        wait=True,
    )
    test_shares.wait_for_steady_state_of_share(openstack_client, share_name)
    yield share
    openstack_client.shared_file_system.delete_share(share)


@pytest.fixture
def clear_share(request, share_name):
    client_fixture_name = request.param
    openstack_client = request.getfixturevalue(client_fixture_name)
    yield None
    test_shares.wait_for_steady_state_of_share(openstack_client, share_name)
    openstack_client.shared_file_system.delete_share(
        openstack_client.shared_file_system.find_share(share_name).id)


# Share Snapshots fixtures:
@pytest.fixture
def share_snapshot_name():
    return 'horizon_share_snapshot_%s' % uuidutils.generate_uuid(dashed=False)


@pytest.fixture
def share_from_snapshot_name():
    return 'horizon_share_from_snapshot_%s' % uuidutils.generate_uuid(
        dashed=False)


@pytest.fixture
def new_share_snapshot(new_share, share_snapshot_name,
                       openstack_client):
    share_snapshot = openstack_client.shared_file_system.create_share_snapshot(
        share_id=new_share.id,
        display_name=share_snapshot_name,
    )
    yield share_snapshot
    openstack_client.shared_file_system.delete_share_snapshot(
        snapshot_id=share_snapshot.id)
    test_share_snapshots.wait_for_share_snapshot_is_deleted(
        openstack_client, share_snapshot.id)


@pytest.fixture
def clear_share_snapshot(request, share_snapshot_name, new_share):
    client_fixture_name = request.param
    openstack_client = request.getfixturevalue(client_fixture_name)
    yield None
    snapshot_id = None
    snapshots_sdk = openstack_client.shared_file_system.share_snapshots()
    for snapshot in snapshots_sdk:
        if snapshot['name'] == share_snapshot_name:
            snapshot_id = snapshot['id']
            break
    test_share_snapshots.wait_for_steady_state_of_share_snapshot(
        openstack_client, snapshot_id)
    openstack_client.shared_file_system.delete_share_snapshot(snapshot_id)
    test_share_snapshots.wait_for_share_snapshot_is_deleted(
        openstack_client, snapshot_id)


@pytest.fixture
def clear_share_from_snapshot(request, share_from_snapshot_name,
                              new_share_snapshot):
    client_fixture_name = request.param
    openstack_client = request.getfixturevalue(client_fixture_name)
    yield None
    test_shares.wait_for_steady_state_of_share(
        openstack_client, share_from_snapshot_name)
    openstack_client.shared_file_system.delete_share(
        openstack_client.shared_file_system.find_share(
            share_from_snapshot_name).id)
