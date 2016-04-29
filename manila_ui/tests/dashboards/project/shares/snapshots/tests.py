# Copyright 2014 NetApp, Inc.
#
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

from django.core.urlresolvers import reverse
import mock

from manila_ui.api import manila as api_manila
from manila_ui.tests.dashboards.project.shares import test_data
from manila_ui.tests import helpers as test

from openstack_dashboard.api import neutron

SHARE_INDEX_URL = reverse('horizon:project:shares:index')


class SnapshotSnapshotViewTests(test.TestCase):

    def test_create_snapshot(self):
        share = test_data.share
        url = reverse('horizon:project:shares:create_snapshot',
                      args=[share.id])
        formData = {
            'name': 'new_snapshot',
            'description': 'This is test snapshot',
            'method': 'CreateForm',
            'size': 1,
            'type': 'NFS',
            'share_id': share.id,
        }
        self.mock_object(api_manila, "share_snapshot_create")

        res = self.client.post(url, formData)

        api_manila.share_snapshot_create.assert_called_once_with(
            mock.ANY, share.id, formData['name'], formData['description'])
        self.assertRedirectsNoFollow(res, SHARE_INDEX_URL)

    def test_delete_snapshot(self):
        share = test_data.share
        snapshot = test_data.snapshot
        formData = {'action': 'snapshots__delete__%s' % snapshot.id}
        self.mock_object(api_manila, "share_snapshot_delete")
        self.mock_object(
            api_manila, "share_snapshot_list",
            mock.Mock(return_value=[snapshot]))
        self.mock_object(
            api_manila, "share_list", mock.Mock(return_value=[share]))
        url = reverse('horizon:project:shares:index')

        res = self.client.post(url, formData)

        api_manila.share_snapshot_delete.assert_called_once_with(
            mock.ANY, test_data.snapshot.id)
        api_manila.share_snapshot_list.assert_called_once_with(mock.ANY)
        api_manila.share_list.assert_called_once_with(mock.ANY)
        self.assertRedirectsNoFollow(res, SHARE_INDEX_URL)

    def test_detail_view(self):
        snapshot = test_data.snapshot
        share = test_data.share
        url = reverse('horizon:project:shares:snapshot-detail',
                      args=[snapshot.id])
        self.mock_object(
            api_manila, "share_snapshot_get", mock.Mock(return_value=snapshot))
        self.mock_object(
            api_manila, "share_get", mock.Mock(return_value=share))
        self.mock_object(
            neutron, "is_service_enabled", mock.Mock(return_value=[True]))

        res = self.client.get(url)

        self.assertContains(res, "<h1>Snapshot Details: %s</h1>"
                                 % snapshot.name,
                            1, 200)
        self.assertContains(res, "<dd>%s</dd>" % snapshot.name, 1, 200)
        self.assertContains(res, "<dd>%s</dd>" % snapshot.id, 1, 200)
        self.assertContains(res,
                            "<dd><a href=\"/admin/shares/%s/\">%s</a></dd>" %
                            (snapshot.share_id, share.name), 1, 200)
        self.assertContains(res, "<dd>%s GiB</dd>" % snapshot.size, 1, 200)
        self.assertNoMessages()
        api_manila.share_get.assert_called_once_with(mock.ANY, share.id)
        api_manila.share_snapshot_get.assert_called_once_with(
            mock.ANY, snapshot.id)
        self.assertEqual(3, neutron.is_service_enabled.call_count)

    def test_update_snapshot(self):
        snapshot = test_data.snapshot
        url = reverse('horizon:project:shares:edit_snapshot',
                      args=[snapshot.id])
        formData = {
            'method': 'UpdateForm',
            'name': snapshot.name,
            'description': snapshot.description,
        }
        self.mock_object(api_manila, "share_snapshot_update")
        self.mock_object(
            api_manila, "share_snapshot_get", mock.Mock(return_value=snapshot))

        res = self.client.post(url, formData)

        self.assertRedirectsNoFollow(
            res, SHARE_INDEX_URL + '?tab=share_tabs__snapshots_tab')
        api_manila.share_snapshot_get.assert_called_once_with(
            mock.ANY, snapshot.id)
        api_manila.share_snapshot_update.assert_called_once_with(
            mock.ANY, snapshot.id, name=formData['name'],
            description=formData['description'])
