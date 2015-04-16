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

import os

from django.utils import unittest

from manila_ui.test.test_data import utils
from openstack_dashboard.test import helpers


def create_stubs(stubs_to_create={}):
    return helpers.create_stubs(stubs_to_create)


class ManilaTestsMixin(object):
    def _setup_test_data(self):
        super(ManilaTestsMixin, self)._setup_test_data()
        utils.load_test_data(self)


@unittest.skipIf(os.environ.get('SKIP_UNITTESTS', False),
                 "The SKIP_UNITTESTS env variable is set.")
class TestCase(ManilaTestsMixin, helpers.TestCase):
    pass


class BaseAdminViewTests(ManilaTestsMixin, helpers.BaseAdminViewTests):
    pass


class APITestCase(ManilaTestsMixin, helpers.APITestCase):
    pass
