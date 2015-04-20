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


import inspect

import openstack_dashboard.test.integration_tests.tests.decorators \
    as os_decorators


def skip_broken_test():
    """Decorator for skipping broken tests

    Usage:
    from manila_ui.test import decorators

    class TestDashboardHelp(helpers.TestCase):

        @decorators.skip_broken_test()
        def test_dashboard_help_redirection(self):
        .
        .
        .
    """

    def actual_decoration(obj):
        if inspect.isclass(obj):
            if not os_decorators._is_test_cls(obj):
                raise ValueError(os_decorators.NOT_TEST_OBJECT_ERROR_MSG)
            skip_method = os_decorators._mark_class_skipped
        else:
            if not os_decorators._is_test_method_name(obj.func_name):
                raise ValueError(os_decorators.NOT_TEST_OBJECT_ERROR_MSG)
            skip_method = os_decorators._mark_method_skipped

        obj = skip_method(obj, "Skipped broken test")
        return obj
    return actual_decoration
