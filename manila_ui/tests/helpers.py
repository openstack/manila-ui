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

import mock
import os
import unittest

from manila_ui import api
from manila_ui.tests.test_data import utils
from openstack_dashboard.test import helpers


class ManilaTestsMixin(object):
    def _setup_test_data(self):
        super(ManilaTestsMixin, self)._setup_test_data()
        utils.load_test_data(self)

    def mock_object(self, obj, attr_name, new_attr=None, **kwargs):
        """Use python mock to mock an object attribute
        Mocks the specified objects attribute with the given value.
        Automatically performs 'addCleanup' for the mock.
        """
        if not new_attr:
            new_attr = mock.Mock()
        patcher = mock.patch.object(obj, attr_name, new_attr, **kwargs)
        patcher.start()
        # NOTE(vponomaryov): 'self.addCleanup(patcher.stop)' is not called
        # here, because it is inherited from Horizon project's test class.
        return new_attr


@unittest.skipIf(os.environ.get('SKIP_UNITTESTS', False),
                 "The SKIP_UNITTESTS env variable is set.")
class TestCase(ManilaTestsMixin, helpers.TestCase):
    pass


class BaseAdminViewTests(ManilaTestsMixin, helpers.BaseAdminViewTests):
    pass


class APITestCase(ManilaTestsMixin, helpers.APITestCase):

    def setUp(self):
        super(APITestCase, self).setUp()
        self._manilaclient = self.mock_object(api.manila, "manilaclient")
        self.manilaclient = self._manilaclient.return_value


class FakeEntity(object):
    def __init__(self, id, name):
        self.id = id
        self.name = name
