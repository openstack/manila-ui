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

    def test_share_extend(self):
        fake_share_id = "fake_id"
        new_size = "123"

        api.share_extend(self.request, fake_share_id, new_size)

        self.manilaclient.shares.extend.assert_called_once_with(
            fake_share_id, new_size
        )
