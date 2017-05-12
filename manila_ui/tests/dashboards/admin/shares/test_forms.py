# Copyright (c) 2015 Mirantis, Inc.
# All rights reserved.

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

from django.core.handlers import wsgi
import mock

from manila_ui.api import manila as api
from manila_ui.dashboards.admin.shares import forms
from manila_ui.tests import helpers as base


class ManilaDashboardsAdminMigrationFormTests(base.APITestCase):

    def setUp(self):
        super(self.__class__, self).setUp()
        FAKE_ENVIRON = {'REQUEST_METHOD': 'GET', 'wsgi.input': 'fake_input'}
        self.request = wsgi.WSGIRequest(FAKE_ENVIRON)

    def _get_initial(self):
        initial = {'name': 'fake_name', 'share_id': 'fake_id'}
        kwargs = {
            'prefix': None,
            'initial': initial,
        }
        return kwargs

    @mock.patch('horizon.messages.success')
    def test_migration_start(self, mock_horizon_messages_success):

        self.mock_object(
            api, "share_network_list",
            mock.Mock(return_value=[base.FakeEntity('sn1_id', 'sn1_name'),
                                    base.FakeEntity('sn2_id', 'sn2_name')]))

        self.mock_object(
            api, "share_type_list",
            mock.Mock(return_value=[base.FakeEntity('st1_id', 'st1_name'),
                                    base.FakeEntity('st2_id', 'st2_name')]))

        self.mock_object(
            api, "pool_list",
            mock.Mock(return_value=[base.FakeEntity('ubuntu@beta#BETA',
                                                    'ubuntu@beta#BETA'),
                                    base.FakeEntity('ubuntu@alpha#ALPHA',
                                                    'ubuntu@alpha#ALPHA')]))

        form = forms.MigrationStart(self.request, **self._get_initial())

        data = {
            'force_host_assisted_migration': False,
            'writable': True,
            'preserve_metadata': True,
            'preserve_snapshots': True,
            'nondisruptive': True,
            'new_share_network': 'fake_net_id',
            'new_share_type': 'fake_type_id',
            'host': 'fake_host',
        }

        result = form.handle(self.request, data)
        self.assertTrue(result)
        mock_horizon_messages_success.assert_called_once_with(
            self.request, mock.ANY)

        api.share_network_list.assert_called_once_with(mock.ANY)
        api.share_type_list.assert_called_once_with(mock.ANY)
        api.pool_list.assert_called_once_with(mock.ANY)

    @mock.patch('horizon.messages.success')
    def test_migration_complete(self, mock_horizon_messages_success):

        form = forms.MigrationComplete(self.request, **self._get_initial())
        result = form.handle(self.request, {})
        self.assertTrue(result)
        mock_horizon_messages_success.assert_called_once_with(
            self.request, mock.ANY)

    @mock.patch('horizon.messages.success')
    def test_migration_cancel(self, mock_horizon_messages_success):
        form = forms.MigrationCancel(self.request, **self._get_initial())
        result = form.handle(self.request, {})
        self.assertTrue(result)
        mock_horizon_messages_success.assert_called_once_with(
            self.request, mock.ANY)

    @mock.patch('horizon.messages.success')
    def test_migration_get_progress(self, mock_horizon_messages_success):

        result = ({'Response': 200}, {'total_progress': 25})
        self.mock_object(api, 'migration_get_progress',
                         mock.Mock(return_value=result))
        form = forms.MigrationGetProgress(self.request, **self._get_initial())
        result = form.handle(self.request, {})
        self.assertTrue(result)
        mock_horizon_messages_success.assert_called_once_with(
            self.request, mock.ANY)
