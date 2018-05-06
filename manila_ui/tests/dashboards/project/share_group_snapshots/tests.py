# Copyright (c) 2017 Mirantis, Inc.
# All rights reserved.
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

import ddt
from django.urls import reverse
import mock

from manila_ui.api import manila as api_manila
from manila_ui.tests.dashboards.project import test_data
from manila_ui.tests import helpers as test

INDEX_URL = reverse('horizon:project:share_group_snapshots:index')


@ddt.ddt
class ShareGroupSnapshotTests(test.TestCase):

    def setUp(self):
        super(self.__class__, self).setUp()
        self.sg = test_data.share_group
        self.sg_nl = test_data.share_group_nameless
        self.sg_dhss_true = test_data.share_group_dhss_true
        self.sgs = test_data.share_group_snapshot
        self.sgs_nl = test_data.share_group_snapshot_nameless

    def test_share_group_snapshots_list_get(self):
        share_groups = [self.sg, self.sg_nl, self.sg_dhss_true]
        sgss = [self.sgs, self.sgs_nl]
        self.mock_object(
            api_manila, 'share_group_snapshot_list',
            mock.Mock(return_value=sgss))
        self.mock_object(
            api_manila, 'share_group_list',
            mock.Mock(return_value=share_groups))

        res = self.client.get(INDEX_URL)

        self.assertStatusCode(res, 200)
        self.assertMessageCount(error=0)
        self.assertNoMessages()
        api_manila.share_group_snapshot_list.assert_called_once_with(
            mock.ANY, search_opts={'all_tenants': True})
        api_manila.share_group_list.assert_called_once_with(mock.ANY)
        self.assertTemplateUsed(
            res, 'project/share_group_snapshots/index.html')
        self.assertContains(res, "<h1>Share Group Snapshots</h1>")
        self.assertContains(
            res, 'Delete Share Group Snapshot</button>', len(sgss))
        self.assertContains(res, 'Delete Share Group Snapshots</button>', 1)
        for sgs in sgss:
            self.assertContains(
                res, 'value="share_group_snapshots__delete__%s' % sgs.id, 1)
        self.assertContains(
            res,
            '<a href="/project/share_group_snapshots/%(id)s/" >%(name)s</a' % {
                'id': self.sgs.id, 'name': self.sgs.name}, 1)
        self.assertContains(
            res,
            '<a href="/project/share_group_snapshots/%s/" '
            '>-</a>' % self.sgs_nl.id, 1)

    def test_share_group_snapshots_list_error_get(self):
        self.mock_object(
            api_manila, 'share_group_snapshot_list',
            mock.Mock(side_effect=type('CustomExc', (Exception, ), {})))

        res = self.client.get(INDEX_URL)

        self.assertStatusCode(res, 200)
        self.assertTemplateUsed(
            res, 'project/share_group_snapshots/index.html')
        self.assertContains(res, "<h1>Share Group Snapshots</h1>")
        self.assertContains(res, 'Delete Share Group Snapshot</button>', 0)
        self.assertContains(res, 'Delete Share Group Snapshots</button>', 0)
        self.assertNoMessages()

    @ddt.data(
        test_data.share_group_snapshot,
        test_data.share_group_snapshot_nameless,
    )
    def test_share_group_snapshot_detailed_page_get(self, sgs):
        sg = test_data.share_group_nameless
        url = reverse(
            'horizon:project:share_group_snapshots:detail', args=[sgs.id])
        self.mock_object(
            api_manila, 'share_group_snapshot_get',
            mock.Mock(return_value=sgs))
        self.mock_object(
            api_manila, 'share_group_get', mock.Mock(return_value=sg))

        res = self.client.get(url)

        self.assertTemplateUsed(
            res, 'project/share_group_snapshots/detail.html')
        self.assertStatusCode(res, 200)
        api_manila.share_group_snapshot_get.assert_called_once_with(
            mock.ANY, sgs.id)
        api_manila.share_group_get.assert_called_once_with(
            mock.ANY, sgs.share_group_id)

    def test_share_group_snapshot_detailed_page_error_get(self):
        url = reverse(
            'horizon:project:share_group_snapshots:detail', args=[self.sgs.id])
        self.mock_object(
            api_manila, 'share_group_snapshot_get',
            mock.Mock(side_effect=type('CustomExc', (Exception, ), {})))

        res = self.client.get(url)

        self.assertTemplateNotUsed(
            res, 'admin/share_group_snapshots/detail.html')
        self.assertStatusCode(res, 302)
        self.assertMessageCount(error=1)
        self.assertMessageCount(success=0)

    @ddt.data(
        lambda *args, **kwargs: test_data.share_group,
        type('CustomExc', (Exception, ), {}),
    )
    def test_share_group_snapshot_create_get(self, sg_get_side_effect):
        url = reverse(
            'horizon:project:share_group_snapshots:create', args=[self.sg.id])
        self.mock_object(
            api_manila, 'share_group_get',
            mock.Mock(side_effect=sg_get_side_effect))

        res = self.client.get(url)

        self.assertTemplateUsed(
            res, 'project/share_group_snapshots/create.html')
        self.assertStatusCode(res, 200)
        self.assertNoMessages()
        api_manila.share_group_get.assert_called_once_with(
            mock.ANY, self.sg.id)
        self.assertMessageCount(error=0)

    def test_share_group_snapshot_create_post(self):
        url = reverse(
            'horizon:project:share_group_snapshots:create', args=[self.sg.id])
        form_data = {
            'method': 'CreateShareGroupSnapshotForm',
            'name': 'fake_SG_snapshot_name',
            'description': 'fake SG snapshot description',
            'share_group_id': self.sg.id,
        }
        self.mock_object(
            api_manila, "share_group_snapshot_create",
            mock.Mock(return_value=self.sgs))

        res = self.client.post(url, form_data)

        self.assertTemplateNotUsed(
            res, 'project/share_group_snapshots/create.html')
        self.assertStatusCode(res, 302)
        self.assertRedirectsNoFollow(res, INDEX_URL)
        self.assertMessageCount(error=0)
        self.assertMessageCount(success=1)
        api_manila.share_group_snapshot_create.assert_called_once_with(
            mock.ANY, self.sg.id, form_data['name'], form_data['description'])

    def test_share_group_snapshot_create_error_post(self):
        url = reverse(
            'horizon:project:share_group_snapshots:create', args=[self.sg.id])
        form_data = {
            'method': 'CreateShareGroupSnapshotForm',
            'name': 'fake_SG_snapshot_name',
            'description': 'fake SG snapshot description',
            'share_group_id': self.sg.id,
        }
        self.mock_object(
            api_manila, "share_group_snapshot_create",
            mock.Mock(side_effect=type('CustomExc', (Exception, ), {})))

        res = self.client.post(url, form_data)

        self.assertTemplateNotUsed(
            res, 'project/share_group_snapshots/create.html')
        self.assertStatusCode(res, 302)
        self.assertRedirectsNoFollow(res, INDEX_URL)
        self.assertMessageCount(error=1)
        self.assertMessageCount(success=0)
        api_manila.share_group_snapshot_create.assert_called_once_with(
            mock.ANY, self.sg.id, form_data['name'], form_data['description'])

    def test_share_group_snapshot_update_get(self):
        url = reverse(
            'horizon:project:share_group_snapshots:update', args=[self.sgs.id])
        self.mock_object(
            api_manila, 'share_group_snapshot_get',
            mock.Mock(return_value=self.sgs))

        res = self.client.get(url)

        self.assertTemplateUsed(
            res, 'project/share_group_snapshots/update.html')
        self.assertStatusCode(res, 200)
        self.assertNoMessages()
        api_manila.share_group_snapshot_get.assert_called_once_with(
            mock.ANY, self.sgs.id)

    def test_share_group_snapshot_update_error_get(self):
        url = reverse(
            'horizon:project:share_group_snapshots:update', args=[self.sgs.id])
        self.mock_object(
            api_manila, 'share_group_snapshot_get',
            mock.Mock(side_effect=type('CustomExc', (Exception, ), {})))

        res = self.client.get(url)

        self.assertTemplateNotUsed(
            res, 'project/share_group_snapshots/update.html')
        self.assertStatusCode(res, 302)
        self.assertRedirectsNoFollow(res, INDEX_URL)
        self.assertMessageCount(error=1)
        api_manila.share_group_snapshot_get.assert_called_once_with(
            mock.ANY, self.sgs.id)

    def test_share_group_snapshot_update_post(self):
        self.mock_object(api_manila, "share_group_snapshot_update")
        self.mock_object(
            api_manila, 'share_group_snapshot_get',
            mock.Mock(return_value=self.sgs))
        form_data = {
            'method': 'UpdateShareGroupSnapshotForm',
            'name': self.sgs.name,
            'description': self.sgs.description,
        }
        url = reverse(
            'horizon:project:share_group_snapshots:update', args=[self.sgs.id])

        res = self.client.post(url, form_data)

        self.assertStatusCode(res, 302)
        self.assertRedirectsNoFollow(res, INDEX_URL)
        api_manila.share_group_snapshot_update.assert_called_once_with(
            mock.ANY, self.sgs.id, form_data['name'], form_data['description'])
        api_manila.share_group_snapshot_get.assert_called_once_with(
            mock.ANY, self.sgs.id)
        self.assertMessageCount(error=0)
        self.assertMessageCount(success=1)

    def test_share_group_snapshot_update_error_post(self):
        self.mock_object(
            api_manila, "share_group_snapshot_update",
            mock.Mock(side_effect=type('CustomExc', (Exception, ), {})))
        self.mock_object(
            api_manila, 'share_group_snapshot_get',
            mock.Mock(return_value=self.sgs))
        form_data = {
            'method': 'UpdateShareGroupSnapshotForm',
            'name': self.sgs.name,
            'description': self.sgs.description,
        }
        url = reverse(
            'horizon:project:share_group_snapshots:update', args=[self.sgs.id])

        res = self.client.post(url, form_data)

        self.assertStatusCode(res, 302)
        self.assertRedirectsNoFollow(res, INDEX_URL)
        api_manila.share_group_snapshot_update.assert_called_once_with(
            mock.ANY, self.sgs.id, form_data['name'], form_data['description'])
        api_manila.share_group_snapshot_get.assert_called_once_with(
            mock.ANY, self.sgs.id)
        self.assertMessageCount(error=1)
        self.assertMessageCount(success=0)

    def test_share_group_snapshot_delete_post(self):
        data = {'action': 'share_group_snapshots__delete__%s' % self.sgs.id}
        self.mock_object(api_manila, "share_group_snapshot_delete")
        self.mock_object(
            api_manila, "share_group_snapshot_list",
            mock.Mock(return_value=[self.sgs]))

        res = self.client.post(INDEX_URL, data)

        self.assertStatusCode(res, 302)
        self.assertMessageCount(success=1)
        api_manila.share_group_snapshot_delete.assert_called_once_with(
            mock.ANY, self.sgs.id)
        api_manila.share_group_snapshot_list.assert_called_once_with(
            mock.ANY, search_opts={'all_tenants': True})
        self.assertRedirectsNoFollow(res, INDEX_URL)
