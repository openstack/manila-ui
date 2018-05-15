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

INDEX_URL = reverse('horizon:admin:share_groups:index')


@ddt.ddt
class ShareGroupTests(test.BaseAdminViewTests):

    def setUp(self):
        super(self.__class__, self).setUp()
        self.sg = test_data.share_group
        self.sg_nl = test_data.share_group_nameless
        self.sg_dhss_true = test_data.share_group_dhss_true

    def test_share_groups_list_get(self):
        sgs = [self.sg, self.sg_nl, self.sg_dhss_true]
        self.mock_object(
            api_manila, 'share_group_list', mock.Mock(return_value=sgs))

        res = self.client.get(INDEX_URL)

        self.assertStatusCode(res, 200)
        api_manila.share_group_list.assert_called_once_with(
            mock.ANY, detailed=True)
        self.assertTemplateUsed(res, 'admin/share_groups/index.html')
        self.assertContains(res, "<h1>Share Groups</h1>")
        self.assertContains(res, 'Delete Share Group</button>', len(sgs))
        self.assertContains(res, 'Delete Share Groups</button>', 1)
        for sg in sgs:
            self.assertContains(
                res,
                'href="/admin/share_groups/%s/reset_status"> '
                'Reset status</a>' % sg.id, 1)
            self.assertContains(
                res, 'value="share_groups__delete__%s' % sg.id, 1)
        self.assertContains(
            res,
            '<a href="/admin/share_networks/%s"' % (
                self.sg_dhss_true.share_network_id), 1)
        self.assertContains(
            res,
            '<a href="/admin/share_servers/%s"' % (
                self.sg_dhss_true.share_server_id), 1)
        for sg in (self.sg, self.sg_dhss_true):
            self.assertContains(
                res,
                '<a href="/admin/share_groups/%(id)s/" >%(name)s</a>' % {
                    'id': sg.id, 'name': sg.name}, 1)
        self.assertContains(
            res,
            '<a href="/admin/share_groups/%s/" >-</a>' % self.sg_nl.id, 1)
        self.assertNoMessages()

    def test_share_group_list_error_get(self):
        self.mock_object(
            api_manila, 'share_group_list',
            mock.Mock(side_effect=type('CustomExc', (Exception, ), {})))

        res = self.client.get(INDEX_URL)

        self.assertStatusCode(res, 200)
        self.assertTemplateUsed(res, 'admin/share_groups/index.html')
        self.assertContains(res, "<h1>Share Groups</h1>")
        self.assertContains(res, 'Delete Share Group</button>', 0)
        self.assertContains(res, 'Delete Share Groups</button>', 0)
        self.assertNoMessages()

    @ddt.data(
        test_data.share_group_nameless,
        test_data.share_group_dhss_true,
    )
    def test_share_group_detailed_page_get(self, sg):
        url = reverse('horizon:admin:share_groups:detail', args=[sg.id])
        shares = [test_data.share, test_data.nameless_share]
        self.mock_object(
            api_manila, 'share_group_get', mock.Mock(return_value=sg))
        self.mock_object(
            api_manila, 'share_list', mock.Mock(return_value=shares))
        self.mock_object(
            api_manila, 'share_type_list', mock.Mock(return_value=[
                test_data.share_type, test_data.share_type_dhss_true]))

        res = self.client.get(url)

        self.assertTemplateUsed(res, 'admin/share_groups/detail.html')
        self.assertStatusCode(res, 200)
        for share in shares:
            data = {'id': share.id, 'name': share.name or share.id}
            self.assertContains(
                res, '<a href="/admin/shares/%(id)s/">%(name)s</a>' % data)

    def test_share_group_detailed_page_error_get(self):
        sg = test_data.share_group_dhss_true
        url = reverse('horizon:admin:share_groups:detail', args=[sg.id])
        self.mock_object(
            api_manila, 'share_group_get', mock.Mock(side_effect=type(
                'CustomExc', (Exception, ), {})))

        res = self.client.get(url)

        self.assertTemplateNotUsed(res, 'admin/share_groups/detail.html')
        self.assertStatusCode(res, 302)
        self.assertMessageCount(error=1)
        self.assertMessageCount(success=0)

    def test_share_group_reset_status_get(self):
        sg = test_data.share_group_dhss_true
        url = reverse('horizon:admin:share_groups:reset_status', args=[sg.id])
        self.mock_object(
            api_manila, 'share_group_get', mock.Mock(return_value=sg))

        res = self.client.get(url)

        self.assertTemplateUsed(res, 'admin/share_groups/reset_status.html')
        self.assertStatusCode(res, 200)
        self.assertMessageCount(error=0)
        api_manila.share_group_get.assert_called_once_with(mock.ANY, sg.id)

    def test_share_group_reset_status_error_get(self):
        sg = test_data.share_group_dhss_true
        url = reverse('horizon:admin:share_groups:reset_status', args=[sg.id])
        self.mock_object(
            api_manila, 'share_group_get',
            mock.Mock(side_effect=type('CustomExc', (Exception, ), {})))

        res = self.client.get(url)

        self.assertTemplateNotUsed(res, 'admin/share_groups/reset_status.html')
        self.assertStatusCode(res, 302)
        self.assertMessageCount(error=1)
        api_manila.share_group_get.assert_called_once_with(mock.ANY, sg.id)

    def test_share_group_reset_status_post(self):
        sg = test_data.share_group_dhss_true
        url = reverse('horizon:admin:share_groups:reset_status', args=[sg.id])
        self.mock_object(
            api_manila, 'share_group_get', mock.Mock(return_value=sg))
        self.mock_object(api_manila, 'share_group_reset_state')
        form_data = {'status': 'error'}

        res = self.client.post(url, form_data)

        self.assertTemplateNotUsed(res, 'admin/share_groups/reset_status.html')
        self.assertStatusCode(res, 302)
        self.assertMessageCount(error=0)
        api_manila.share_group_get.assert_called_once_with(mock.ANY, sg.id)
        api_manila.share_group_reset_state.assert_called_once_with(
            mock.ANY, sg.id, form_data['status'])
        self.assertRedirectsNoFollow(res, INDEX_URL)

    def test_share_group_delete_post(self):
        sg = test_data.share_group_dhss_true
        data = {'action': 'share_groups__delete__%s' % sg.id}
        self.mock_object(api_manila, "share_group_delete")
        self.mock_object(
            api_manila, "share_group_list", mock.Mock(return_value=[sg]))

        res = self.client.post(INDEX_URL, data)

        self.assertStatusCode(res, 302)
        self.assertMessageCount(success=1)
        api_manila.share_group_delete.assert_called_once_with(mock.ANY, sg.id)
        api_manila.share_group_list.assert_called_once_with(
            mock.ANY, detailed=True)
        self.assertRedirectsNoFollow(res, INDEX_URL)
