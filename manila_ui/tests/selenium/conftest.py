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

import pytest

from openstack_dashboard.test.selenium.conftest import config  # noqa: F401
from openstack_dashboard.test.selenium.conftest import driver  # noqa: F401
from openstack_dashboard.test.selenium.conftest import login  # noqa: F401
from openstack_dashboard.test.selenium.conftest import xdisplay  # noqa: F401
from openstack_dashboard.test.selenium.integration.conftest import \
    openstack_admin  # noqa: F401
from openstack_dashboard.test.selenium.integration.conftest import \
    openstack_demo  # noqa: F401


@pytest.fixture
def openstack_client(request):
    return request.getfixturevalue(request.param)
