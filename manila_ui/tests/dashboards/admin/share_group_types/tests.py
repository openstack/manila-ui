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
from django.urls import reverse
import mock

from manila_ui.api import manila as api_manila
from manila_ui.tests.dashboards.project import test_data
from manila_ui.tests import helpers as test

INDEX_URL = reverse('horizon:admin:share_group_types:index')


class ShareGroupTypeTests(test.BaseAdminViewTests):

    def setUp(self):
        super(self.__class__, self).setUp()
        self.share_group_type = test_data.share_group_type
        self.share_group_type_alt = test_data.share_group_type_alt
        self.share_group_type_p = test_data.share_group_type_private
        self.url = reverse('horizon:admin:share_group_types:update',
                           args=[self.share_group_type.id])
        self.mock_object(api_manila, "share_group_type_get",
                         mock.Mock(return_value=self.share_group_type))

    def test_create_share_group_type(self):
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
                'ShareGroupType',
                (object, ),
                {'id': 'sgt_id', 'name': 'sgt_name'})))
        self.mock_object(api_manila, "share_group_type_set_specs")
        self.mock_object(
            api_manila, "share_type_list",
            mock.Mock(return_value=[type(
                'ShareType',
                (object, ),
                {'id': s_id, 'name': s_id + '_name'})
                for s_id in ('foo', 'bar')
            ]))

        res = self.client.post(url, data)

        api_manila.share_group_type_create.assert_called_once_with(
            mock.ANY, data['name'],
            is_public=data['is_public'],
            share_types=['foo'])
        api_manila.share_type_list.assert_called_once_with(mock.ANY)
        api_manila.share_group_type_set_specs.assert_called_once_with(
            mock.ANY, 'sgt_id', {'key': 'value'})
        self.assertRedirectsNoFollow(res, INDEX_URL)

    def test_update_share_group_type_get(self):
        res = self.client.get(self.url)

        api_manila.share_group_type_get.assert_called_once_with(
            mock.ANY, self.share_group_type.id)
        self.assertNoMessages()
        self.assertTemplateUsed(res, 'admin/share_group_types/update.html')

    def test_update_share_group_type_post(self):
        data = {'group_specs': 'foo=bar'}
        form_data = {'group_specs': {'foo': 'bar'}}
        self.mock_object(api_manila, "share_group_type_set_specs")

        res = self.client.post(self.url, data)

        api_manila.share_group_type_set_specs.assert_called_once_with(
            mock.ANY, self.share_group_type.id, form_data['group_specs'])
        self.assertRedirectsNoFollow(res, INDEX_URL)

    def test_delete_share_group_type(self):
        data = {'action': 'share_group_types__delete__%s' %
                self.share_group_type_alt.id}
        self.mock_object(api_manila, "share_group_type_delete")
        self.mock_object(
            api_manila, "share_group_type_list",
            mock.Mock(return_value=[self.share_group_type_alt]))
        self.mock_object(
            api_manila, "share_type_list",
            mock.Mock(return_value=[test_data.share_type_alt]))

        res = self.client.post(INDEX_URL, data)

        api_manila.share_group_type_delete.assert_called_once_with(
            mock.ANY, self.share_group_type_alt.id)
        api_manila.share_group_type_list.assert_called_once_with(
            mock.ANY)
        self.assertRedirectsNoFollow(res, INDEX_URL)
