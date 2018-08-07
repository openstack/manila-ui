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

import ddt
from django.core.handlers import wsgi
import mock

from manila_ui.api import manila as api_manila
from manila_ui.dashboards.project.share_snapshots import tables
from manila_ui.tests.dashboards.project import test_data
from manila_ui.tests import helpers as base


@ddt.ddt
class CreateSnapshotTests(base.APITestCase):

    def setUp(self):
        super(self.__class__, self).setUp()
        FAKE_ENVIRON = {'REQUEST_METHOD': 'GET', 'wsgi.input': 'fake_input'}
        self.request = wsgi.WSGIRequest(FAKE_ENVIRON)
        self.create_snapshot = tables.CreateShareSnapshot()

    def _get_fake_share(self, **kwargs):
        if 'status' not in kwargs.keys():
            kwargs.update({'status': 'available'})
        return type("Share", (object, ), kwargs)()

    @ddt.data(True, False)
    def test_allowed_with_snapshot_support_attr(self, snapshot_support):
        self.mock_object(
            api_manila, "tenant_absolute_limits",
            mock.Mock(return_value=test_data.limits))

        share = self._get_fake_share(snapshot_support=snapshot_support)

        result = self.create_snapshot.allowed(self.request, share)

        self.assertEqual(snapshot_support, result)

    def test_allowed_no_snapshot_support_attr(self):
        self.mock_object(
            api_manila, "tenant_absolute_limits",
            mock.Mock(return_value=test_data.limits))
        share = self._get_fake_share()

        result = self.create_snapshot.allowed(self.request, share)

        self.assertNotIn('disabled', self.create_snapshot.classes)

        self.assertTrue(result)

    def test_allowed_no_snapshot_support_attr_no_quota(self):
        self.mock_object(
            api_manila, "tenant_absolute_limits",
            mock.Mock(return_value=test_data.limits_negative))

        share = self._get_fake_share()

        result = self.create_snapshot.allowed(self.request, share)

        self.assertIn('disabled', self.create_snapshot.classes)

        self.assertTrue(result)
