# Copyright (c) 2015 Mirantis, Inc.
# All Rights Reserved.
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

from manila_ui.api import manila as api
from manila_ui.test import helpers as base


class ManilaApiTests(base.APITestCase):

    def setUp(self):
        super(self.__class__, self).setUp()
        self.id = "fake_id"

    def test_share_extend(self):
        new_size = "123"

        api.share_extend(self.request, self.id, new_size)

        self.manilaclient.shares.extend.assert_called_once_with(
            self.id, new_size
        )

    def test_share_type_set_extra_specs(self):
        data = {"foo": "bar"}

        api.share_type_set_extra_specs(self.request, self.id, data)

        share_types_get = self.manilaclient.share_types.get
        share_types_get.assert_called_once_with(self.id)
        share_types_get.return_value.set_keys.assert_called_once_with(data)

    def test_share_type_unset_extra_specs(self):
        keys = ["foo", "bar"]

        api.share_type_unset_extra_specs(self.request, self.id, keys)

        share_types_get = self.manilaclient.share_types.get
        share_types_get.assert_called_once_with(self.id)
        share_types_get.return_value.unset_keys.assert_called_once_with(keys)
