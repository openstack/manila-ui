# Copyright (c) 2014 NetApp, Inc.
# Copyright (c) 2015 Mirantis, Inc.
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
from openstack_dashboard.api import keystone as api_keystone
from openstack_dashboard.api import neutron as api_neutron

from manila_ui.api import manila as api_manila
from manila_ui.dashboards.admin import utils
from manila_ui.tests.dashboards.project import test_data
from manila_ui.tests import helpers as test
from manila_ui.tests.test_data import keystone_data

INDEX_URL = reverse('horizon:admin:shares:index')


@ddt.ddt
class SharesTests(test.BaseAdminViewTests):

    def setUp(self):
        super(self.__class__, self).setUp()
        self.mock_object(utils.timeutils, 'now', mock.Mock(return_value=1))
        self.mock_object(
            api_keystone, "tenant_list",
            mock.Mock(return_value=(keystone_data.projects, None)))
        # Reset taken list of projects to avoid test interference
        utils.PROJECTS = {}

    def test_index(self):
        snaps = [test_data.snapshot]
        shares = [test_data.share, test_data.nameless_share,
                  test_data.other_share]
        utils.timeutils.now.side_effect = [4] + [24 + i for i in range(4)]

        self.mock_object(
            api_manila, "share_list", mock.Mock(return_value=shares))
        self.mock_object(
            api_manila, "share_snapshot_list", mock.Mock(return_value=snaps))
        self.mock_object(
            api_neutron, "is_service_enabled", mock.Mock(return_value=[True]))

        res = self.client.get(INDEX_URL)

        self.assertTemplateUsed(res, 'admin/shares/index.html')
        self.assertEqual(res.status_code, 200)
        api_manila.share_list.assert_called_with(
            mock.ANY, search_opts={'all_tenants': True})
        api_manila.share_snapshot_list.assert_called_with(
            mock.ANY, detailed=True, search_opts={'all_tenants': True})
        api_keystone.tenant_list.assert_called_once_with(mock.ANY)

    def test_delete_share(self):
        url = reverse('horizon:admin:shares:index')
        share = test_data.share
        formData = {'action': 'shares__delete__%s' % share.id}
        self.mock_object(
            api_manila, "share_snapshot_list", mock.Mock(return_value=[]))
        self.mock_object(api_manila, "share_delete")
        self.mock_object(
            api_manila, "share_get", mock.Mock(return_value=share))
        self.mock_object(
            api_manila, "share_list", mock.Mock(return_value=[share]))

        res = self.client.post(url, formData)

        api_keystone.tenant_list.assert_called_once_with(mock.ANY)
        api_manila.share_delete.assert_called_once_with(
            mock.ANY, share.id, share_group_id=share.share_group_id)
        api_manila.share_list.assert_called_once_with(
            mock.ANY, search_opts={'all_tenants': True})
        api_manila.share_snapshot_list.assert_called_once_with(
            mock.ANY, detailed=True, search_opts={'all_tenants': True})
        self.assertRedirectsNoFollow(res, INDEX_URL)

    @ddt.data(None, Exception('fake'))
    def test_migration_start_post(self, exc):
        share = test_data.share
        url = reverse('horizon:admin:shares:migration_start',
                      args=[share.id])
        sn_choices = [test.FakeEntity('sn1_id', 'sn1_name'),
                      test.FakeEntity('sn2_id', 'sn2_name')]

        st_choices = [test.FakeEntity('st1_id', 'st1_name'),
                      test.FakeEntity('st2_id', 'st2_name')]

        dest_choices = [
            test.FakeEntity('ubuntu@beta#BETA', 'ubuntu@beta#BETA'),
            test.FakeEntity('ubuntu@alpha#ALPHA', 'ubuntu@alpha#ALPHA')
        ]

        formData = {
            'share_id': share.id,
            'name': share.name,
            'host': 'ubuntu@alpha#ALPHA',
            'writable': True,
            'preserve_metadata': True,
            'preserve_snapshots': True,
            'force_host_assisted_migration': True,
            'nondisruptive': True,
            'new_share_network': 'sn2_id',
            'new_share_type': 'st2_id',
        }
        self.mock_object(
            api_manila, "share_get", mock.Mock(return_value=share))
        self.mock_object(
            api_manila, "migration_start", mock.Mock(side_effect=exc))
        self.mock_object(
            api_manila, "share_network_list",
            mock.Mock(return_value=sn_choices))
        self.mock_object(
            api_manila, "share_type_list",
            mock.Mock(return_value=st_choices))
        self.mock_object(
            api_manila, "pool_list",
            mock.Mock(return_value=dest_choices))

        res = self.client.post(url, formData)

        api_manila.share_get.assert_called_once_with(mock.ANY, share.id)
        api_manila.migration_start.assert_called_once_with(
            mock.ANY, formData['share_id'],
            dest_host=formData['host'],
            force_host_assisted_migration=(
                formData['force_host_assisted_migration']),
            writable=formData['writable'],
            preserve_metadata=formData['preserve_metadata'],
            preserve_snapshots=formData['preserve_snapshots'],
            nondisruptive=formData['nondisruptive'],
            new_share_network_id=formData['new_share_network'],
            new_share_type_id=formData['new_share_type'])
        api_manila.share_network_list.assert_called_once_with(mock.ANY)
        api_manila.share_type_list.assert_called_once_with(mock.ANY)
        api_manila.pool_list.assert_called_once_with(mock.ANY)
        self.assertEqual(302, res.status_code)
        self.assertTemplateNotUsed(res, 'admin/shares/migration_start.html')
        self.assertRedirectsNoFollow(res, INDEX_URL)

    @ddt.data('migration_start', 'migration_cancel', 'migration_complete',
              'migration_get_progress')
    def test_migration_forms_open_form_successfully(self, method):
        share = test_data.share
        url = reverse('horizon:admin:shares:' + method, args=[share.id])

        self.mock_object(
            api_manila, "share_get", mock.Mock(return_value=share))
        self.mock_object(api_manila, method)

        if method == 'migration_start':
            self.mock_object(
                api_manila, "share_network_list",
                mock.Mock(
                    return_value=[test.FakeEntity('sn1_id', 'sn1_name'),
                                  test.FakeEntity('sn2_id', 'sn2_name')]))

            self.mock_object(
                api_manila, "share_type_list",
                mock.Mock(
                    return_value=[test.FakeEntity('st1_id', 'st1_name'),
                                  test.FakeEntity('st2_id', 'st2_name')]))

            self.mock_object(
                api_manila, "pool_list",
                mock.Mock(return_value=[test.FakeEntity('ubuntu@beta#BETA',
                                                        'ubuntu@beta#BETA'),
                                        test.FakeEntity('ubuntu@alpha#ALPHA',
                                                        'ubuntu@alpha#ALPHA')
                                        ]))

        res = self.client.get(url)

        api_manila.share_get.assert_called_once_with(mock.ANY, share.id)

        self.assertFalse(getattr(api_manila, method).called)

        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, 'admin/shares/' + method + '.html')

        if method == 'migration_start':
            api_manila.share_network_list.assert_called_once_with(mock.ANY)
            api_manila.share_type_list.assert_called_once_with(mock.ANY)
            api_manila.pool_list.assert_called_once_with(mock.ANY)

    @ddt.data('migration_start', 'migration_cancel', 'migration_complete',
              'migration_get_progress')
    def test_migration_start_get_share_exception(self, method):
        share = test_data.share
        url = reverse('horizon:admin:shares:' + method, args=[share.id])

        self.mock_object(
            api_manila, "share_get", mock.Mock(side_effect=Exception('fake')))
        self.mock_object(api_manila, method)

        res = self.client.get(url)

        api_manila.share_get.assert_called_once_with(mock.ANY, share.id)
        self.assertFalse(getattr(api_manila, method).called)

        self.assertEqual(res.status_code, 302)
        self.assertTemplateNotUsed(res, 'admin/shares/' + method + '.html')

    @ddt.data({'method': 'migration_complete', 'exc': None},
              {'method': 'migration_complete', 'exc': Exception('fake')},
              {'method': 'migration_cancel', 'exc': None},
              {'method': 'migration_cancel', 'exc': Exception('fake')},
              {'method': 'migration_get_progress',
               'exc': {'response': 200, 'total_progress': 25}},
              {'method': 'migration_get_progress', 'exc': Exception('fake')})
    @ddt.unpack
    def test_migration_forms_post(self, exc, method):
        share = test_data.share
        url = reverse('horizon:admin:shares:' + method,
                      args=[share.id])
        formData = {
            'share_id': share.id,
            'name': share.name,
        }

        self.mock_object(
            api_manila, "share_get", mock.Mock(return_value=share))
        self.mock_object(api_manila, method, mock.Mock(
            side_effect=exc))

        res = self.client.post(url, formData)

        api_manila.share_get.assert_called_once_with(mock.ANY, share.id)
        getattr(api_manila, method).assert_called_once_with(
            mock.ANY, formData['share_id'])

        status_code = 200 if exc else 302
        self.assertEqual(res.status_code, status_code)
        if not exc:
            self.assertTemplateNotUsed(
                res, 'admin/shares/' + method + '.html')
            self.assertRedirectsNoFollow(res, INDEX_URL)
        else:
            self.assertTemplateUsed(
                res, 'admin/shares/' + method + '.html')
