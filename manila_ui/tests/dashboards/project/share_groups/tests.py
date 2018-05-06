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

INDEX_URL = reverse('horizon:project:share_groups:index')


@ddt.ddt
class ShareGroupTests(test.TestCase):

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
        self.assertTemplateUsed(res, 'project/share_groups/index.html')
        self.assertContains(res, "<h1>Share Groups</h1>")
        self.assertContains(res, 'Delete Share Group</button>', len(sgs))
        self.assertContains(res, 'Delete Share Groups</button>', 1)
        for sg in sgs:
            self.assertContains(
                res, 'value="share_groups__delete__%s' % sg.id, 1)
        self.assertContains(
            res,
            '<a href="/project/share_networks/%s"' % (
                self.sg_dhss_true.share_network_id), 1)
        for sg in (self.sg, self.sg_dhss_true):
            self.assertContains(
                res,
                '<a href="/project/share_groups/%(id)s/" >%(name)s</a>' % {
                    'id': sg.id, 'name': sg.name}, 1)
        self.assertContains(
            res,
            '<a href="/project/share_groups/%s/" >-</a>' % self.sg_nl.id, 1)
        self.assertNoMessages()

    def test_share_group_list_error_get(self):
        self.mock_object(
            api_manila, 'share_group_list',
            mock.Mock(side_effect=type('CustomExc', (Exception, ), {})))

        res = self.client.get(INDEX_URL)

        self.assertStatusCode(res, 200)
        self.assertTemplateUsed(res, 'project/share_groups/index.html')
        self.assertContains(res, "<h1>Share Groups</h1>")
        self.assertContains(res, 'Delete Share Group</button>', 0)
        self.assertContains(res, 'Delete Share Groups</button>', 0)
        self.assertNoMessages()

    @ddt.data(
        test_data.share_group_nameless,
        test_data.share_group_dhss_true,
    )
    def test_share_group_detailed_page_get(self, sg):
        url = reverse('horizon:project:share_groups:detail', args=[sg.id])
        shares = [test_data.share, test_data.nameless_share]
        self.mock_object(
            api_manila, 'share_group_get', mock.Mock(return_value=sg))
        self.mock_object(
            api_manila, 'share_list', mock.Mock(return_value=shares))
        self.mock_object(
            api_manila, 'share_type_list', mock.Mock(return_value=[
                test_data.share_type, test_data.share_type_dhss_true]))

        res = self.client.get(url)

        self.assertTemplateUsed(res, 'project/share_groups/detail.html')
        self.assertStatusCode(res, 200)
        for share in shares:
            data = {'id': share.id, 'name': share.name or share.id}
            self.assertContains(
                res, '<a href="/project/shares/%(id)s/">%(name)s</a>' % data)

    def test_share_group_detailed_page_error_get(self):
        url = reverse('horizon:project:share_groups:detail', args=[self.sg.id])
        self.mock_object(
            api_manila, 'share_group_get',
            mock.Mock(side_effect=type('CustomExc', (Exception, ), {})))

        res = self.client.get(url)

        self.assertTemplateNotUsed(res, 'project/share_groups/detail.html')
        self.assertStatusCode(res, 302)
        self.assertMessageCount(error=1)
        self.assertMessageCount(success=0)

    def test_share_group_update_get(self):
        url = reverse('horizon:project:share_groups:update', args=[self.sg.id])
        self.mock_object(
            api_manila, 'share_group_get', mock.Mock(return_value=self.sg))

        res = self.client.get(url)

        self.assertTemplateUsed(res, 'project/share_groups/update.html')
        self.assertStatusCode(res, 200)
        self.assertNoMessages()
        api_manila.share_group_get.assert_called_once_with(
            mock.ANY, self.sg.id)

    def test_share_group_update_error_get(self):
        url = reverse('horizon:project:share_groups:update', args=[self.sg.id])
        self.mock_object(
            api_manila, 'share_group_get',
            mock.Mock(side_effect=type('CustomExc', (Exception, ), {})))

        res = self.client.get(url)

        self.assertTemplateNotUsed(res, 'project/share_groups/update.html')
        self.assertStatusCode(res, 302)
        self.assertRedirectsNoFollow(res, INDEX_URL)
        self.assertMessageCount(error=1)
        api_manila.share_group_get.assert_called_once_with(
            mock.ANY, self.sg.id)

    def test_share_group_update_post(self):
        self.mock_object(api_manila, "share_group_update")
        self.mock_object(
            api_manila, 'share_group_get', mock.Mock(return_value=self.sg))
        form_data = {
            'method': 'UpdateShareGroupForm',
            'name': self.sg.name,
            'description': self.sg.description,
        }
        url = reverse('horizon:project:share_groups:update', args=[self.sg.id])

        res = self.client.post(url, form_data)

        self.assertStatusCode(res, 302)
        self.assertRedirectsNoFollow(res, INDEX_URL)
        api_manila.share_group_update.assert_called_once_with(
            mock.ANY, self.sg.id, form_data['name'], form_data['description'])
        api_manila.share_group_get.assert_called_once_with(
            mock.ANY, self.sg.id)
        self.assertMessageCount(error=0)
        self.assertMessageCount(success=1)

    def test_share_group_update_error_post(self):
        self.mock_object(
            api_manila, 'share_group_update',
            mock.Mock(side_effect=type('CustomExc', (Exception, ), {})))
        self.mock_object(
            api_manila, 'share_group_get', mock.Mock(return_value=self.sg))
        form_data = {
            'method': 'UpdateShareGroupForm',
            'name': self.sg.name,
            'description': self.sg.description,
        }
        url = reverse('horizon:project:share_groups:update', args=[self.sg.id])

        res = self.client.post(url, form_data)

        self.assertStatusCode(res, 302)
        self.assertRedirectsNoFollow(res, INDEX_URL)
        api_manila.share_group_update.assert_called_once_with(
            mock.ANY, self.sg.id, form_data['name'], form_data['description'])
        api_manila.share_group_get.assert_called_once_with(
            mock.ANY, self.sg.id)
        self.assertMessageCount(error=1)
        self.assertMessageCount(success=0)

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

    def test_share_group_create_get(self):
        url = reverse('horizon:project:share_groups:create')
        self.mock_object(
            api_manila, 'share_group_type_list',
            mock.Mock(return_value=[
                test_data.share_group_type,
                test_data.share_group_type_private,
                test_data.share_group_type_dhss_true,
            ]))
        self.mock_object(
            api_manila, 'share_group_snapshot_list',
            mock.Mock(return_value=[
                test_data.share_group_snapshot,
                test_data.share_group_snapshot_nameless,
            ]))
        self.mock_object(
            api_manila, 'share_network_list',
            mock.Mock(return_value=[
                test_data.inactive_share_network,
                test_data.active_share_network,
            ]))
        self.mock_object(
            api_manila, 'share_type_list',
            mock.Mock(return_value=[
                test_data.share_type,
                test_data.share_type_private,
                test_data.share_type_dhss_true,
            ]))
        self.mock_object(
            api_manila, 'availability_zone_list',
            mock.Mock(return_value=[]))

        res = self.client.get(url)

        self.assertTemplateUsed(res, 'project/share_groups/create.html')
        self.assertStatusCode(res, 200)
        self.assertNoMessages()
        self.assertMessageCount(error=0)
        api_manila.share_group_type_list.assert_called_once_with(mock.ANY)
        api_manila.share_group_snapshot_list.assert_called_once_with(mock.ANY)
        api_manila.share_network_list.assert_called_once_with(mock.ANY)
        api_manila.share_type_list.assert_called_once_with(mock.ANY)
        api_manila.availability_zone_list.assert_called_once_with(mock.ANY)

    def test_share_group_create_post(self):
        url = reverse('horizon:project:share_groups:create')
        form_data = {
            'method': 'CreateShareGroupForm',
            'name': 'fake_sg_name',
            'description': 'fake SG description',
            'sgt': test_data.share_group_type.id,
            'share-type-choices-%s' % test_data.share_group_type.id: (
                test_data.share_group_type.share_types[0]),
            'availability_zone': '',
            'share_network': test_data.inactive_share_network.id,
            'snapshot': '',
        }
        self.mock_object(
            api_manila, "share_group_create", mock.Mock(return_value=self.sg))
        self.mock_object(
            api_manila, 'share_group_type_list',
            mock.Mock(return_value=[
                test_data.share_group_type,
                test_data.share_group_type_private,
                test_data.share_group_type_dhss_true,
            ]))
        self.mock_object(
            api_manila, 'share_group_snapshot_list',
            mock.Mock(return_value=[
                test_data.share_group_snapshot,
                test_data.share_group_snapshot_nameless,
            ]))
        self.mock_object(
            api_manila, 'share_network_list',
            mock.Mock(return_value=[
                test_data.inactive_share_network,
                test_data.active_share_network,
            ]))
        self.mock_object(
            api_manila, 'share_type_list',
            mock.Mock(return_value=[
                test_data.share_type,
                test_data.share_type_private,
                test_data.share_type_dhss_true,
            ]))
        self.mock_object(
            api_manila, 'availability_zone_list',
            mock.Mock(return_value=[]))

        res = self.client.post(url, form_data)

        self.assertTemplateNotUsed(res, 'project/share_groups/create.html')
        self.assertStatusCode(res, 302)
        self.assertRedirectsNoFollow(res, INDEX_URL)
        api_manila.share_group_type_list.assert_called_once_with(mock.ANY)
        api_manila.share_group_snapshot_list.assert_called_once_with(mock.ANY)
        api_manila.share_network_list.assert_called_once_with(mock.ANY)
        api_manila.share_type_list.assert_called_once_with(mock.ANY)
        api_manila.availability_zone_list.assert_called_once_with(mock.ANY)
        api_manila.share_group_create.assert_called_once_with(
            mock.ANY,
            name=form_data['name'],
            description=form_data['description'],
            share_group_type=test_data.share_group_type.id,
            share_types=[test_data.share_type.id],
            share_network=form_data['share_network'],
            source_share_group_snapshot=None,
            availability_zone=form_data['availability_zone'])

    def test_share_group_create_from_snapshot_post(self):
        url = reverse('horizon:project:share_groups:create')
        form_data = {
            'method': 'CreateShareGroupForm',
            'name': 'fake_sg_name',
            'description': 'fake SG description',
            'sgt': '',
            'snapshot': test_data.share_group_snapshot.id,
        }
        self.mock_object(
            api_manila, "share_group_snapshot_get",
            mock.Mock(return_value=test_data.share_group_snapshot))
        self.mock_object(
            api_manila, "share_group_get", mock.Mock(return_value=self.sg_nl))
        self.mock_object(
            api_manila, "share_group_create", mock.Mock(return_value=self.sg))
        self.mock_object(
            api_manila, 'share_group_type_list',
            mock.Mock(return_value=[
                test_data.share_group_type,
                test_data.share_group_type_private,
                test_data.share_group_type_dhss_true,
            ]))
        self.mock_object(
            api_manila, 'share_group_snapshot_list',
            mock.Mock(return_value=[
                test_data.share_group_snapshot,
                test_data.share_group_snapshot_nameless,
            ]))
        self.mock_object(
            api_manila, 'share_network_list',
            mock.Mock(return_value=[
                test_data.inactive_share_network,
                test_data.active_share_network,
            ]))
        self.mock_object(
            api_manila, 'share_type_list',
            mock.Mock(return_value=[
                test_data.share_type,
                test_data.share_type_private,
                test_data.share_type_dhss_true,
            ]))
        self.mock_object(
            api_manila, 'availability_zone_list',
            mock.Mock(return_value=[]))

        res = self.client.post(url, form_data)

        self.assertTemplateNotUsed(res, 'project/share_groups/create.html')
        self.assertStatusCode(res, 302)
        self.assertRedirectsNoFollow(res, INDEX_URL)
        api_manila.share_group_snapshot_list.assert_not_called()
        api_manila.share_group_type_list.assert_not_called()
        api_manila.share_network_list.assert_not_called()
        api_manila.share_type_list.assert_not_called()
        api_manila.availability_zone_list.assert_not_called()
        api_manila.share_group_snapshot_get.assert_called_once_with(
            mock.ANY, test_data.share_group_snapshot.id)
        api_manila.share_group_create.assert_called_once_with(
            mock.ANY,
            name=form_data['name'],
            description=form_data['description'],
            share_group_type=test_data.share_group_type.id,
            share_types=None,
            share_network=None,
            source_share_group_snapshot=test_data.share_group_snapshot.id,
            availability_zone=None)
