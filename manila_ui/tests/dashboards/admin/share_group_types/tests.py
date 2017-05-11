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

import copy

from django.core.urlresolvers import reverse
import mock

from manila_ui.api import manila as api_manila
from manila_ui.tests.dashboards.project import test_data
from manila_ui.tests import helpers as test

INDEX_URL = reverse('horizon:admin:share_group_types:index')


class ShareGroupTypeTests(test.BaseAdminViewTests):

    def setUp(self):
        super(self.__class__, self).setUp()
        self.sgt = copy.copy(test_data.share_group_type)
        self.sgt_p = copy.copy(test_data.share_group_type_private)
        self.url = reverse(
            'horizon:admin:share_group_types:update', args=[self.sgt.id])
        self.mock_object(
            api_manila, "share_group_type_get",
            mock.Mock(return_value=self.sgt))

    def test_list_share_group_types_get(self):
        sgts = [self.sgt, self.sgt_p]
        self.mock_object(
            api_manila, "share_group_type_list", mock.Mock(return_value=sgts))
        self.mock_object(
            api_manila, "share_type_list",
            mock.Mock(return_value=[
                test_data.share_type, test_data.share_type_private]))
        self.mock_object(
            api_manila, "share_group_type_get",
            mock.Mock(side_effect=lambda req, sgt_id: (
                self.sgt
                if sgt_id in (self.sgt, self.sgt.id, self.sgt.name) else
                self.sgt_p)))

        res = self.client.get(INDEX_URL)

        api_manila.share_group_type_list.assert_called_once_with(mock.ANY)
        api_manila.share_type_list.assert_called_once_with(mock.ANY)
        self.assertEqual(len(sgts), api_manila.share_group_type_get.call_count)
        self.assertContains(res, "<h1>Share Group Types</h1>")
        self.assertContains(res, 'href="/admin/share_group_types/create"')
        self.assertContains(res, 'Delete Share Group Type</button>', len(sgts))
        self.assertContains(res, 'Delete Share Group Types</button>', 1)
        for sgt in (self.sgt, self.sgt_p):
            for s in (
                    'href="/admin/share_group_types/%s/update">' % sgt.id,
                    'value="share_group_types__delete__%s"' % sgt.id):
                self.assertContains(res, s, 1, 200)
            self.assertContains(
                res,
                'href="/admin/share_group_types/%s/manage_access"' % sgt.id,
                0 if sgt.is_public else 1)

    def test_create_share_group_type_post(self):
        url = reverse('horizon:admin:share_group_types:create')
        data = {
            'method': u'CreateShareGroupTypeForm',
            'is_public': True,
            'name': 'my_share_group_type',
            'share_types': ['foo'],
            'group_specs': 'key=value',
        }
        self.mock_object(
            api_manila, "share_group_type_create",
            mock.Mock(return_value=type(
                'SGT', (object, ), {'id': 'sgt_id', 'name': 'sgt_name'})))
        self.mock_object(api_manila, "share_group_type_set_specs")
        self.mock_object(
            api_manila, "share_type_list",
            mock.Mock(return_value=[
                type('ST', (object, ), {'id': s_id, 'name': s_id + '_name'})
                for s_id in ('foo', 'bar')
            ]))

        res = self.client.post(url, data)

        api_manila.share_group_type_create.assert_called_once_with(
            mock.ANY,
            data['name'],
            is_public=data['is_public'],
            share_types=['foo'])
        api_manila.share_type_list.assert_called_once_with(mock.ANY)
        api_manila.share_group_type_set_specs.assert_called_once_with(
            mock.ANY, 'sgt_id', {'key': 'value'})
        self.assertRedirectsNoFollow(res, INDEX_URL)

    def test_update_share_group_type_get(self):
        res = self.client.get(self.url)

        api_manila.share_group_type_get.assert_called_once_with(
            mock.ANY, self.sgt.id)
        self.assertNoMessages()
        self.assertTemplateUsed(res, 'admin/share_group_types/update.html')

    def test_update_share_group_type_post(self):
        form_data = {'group_specs': 'foo=bar'}
        data = {'group_specs': {'foo': 'bar'}}
        self.mock_object(api_manila, "share_group_type_set_specs")

        res = self.client.post(self.url, form_data)

        api_manila.share_group_type_set_specs.assert_called_once_with(
            mock.ANY, self.sgt.id, data['group_specs'])
        self.assertRedirectsNoFollow(res, INDEX_URL)

    def test_delete_share_group_type(self):
        data = {'action': 'share_group_types__delete__%s' % self.sgt.id}
        self.mock_object(api_manila, "share_group_type_delete")
        self.mock_object(
            api_manila, "share_group_type_list",
            mock.Mock(return_value=[self.sgt]))
        self.mock_object(
            api_manila, "share_type_list",
            mock.Mock(return_value=[test_data.share_type]))

        res = self.client.post(INDEX_URL, data)

        api_manila.share_group_type_delete.assert_called_once_with(
            mock.ANY, self.sgt.id)
        api_manila.share_group_type_list.assert_called_once_with(
            mock.ANY)
        self.assertRedirectsNoFollow(res, INDEX_URL)
