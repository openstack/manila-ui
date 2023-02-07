# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from manila_ui.dashboards.utils import transform_dashed_name as tdn
from manila_ui.tests import helpers as test


class UtilsTests(test.TestCase):

    def test_no_transform(self):
        inputs = ['foo',
                  'bar01',
                  'baz_01']
        res = [tdn(x) for x in inputs]
        self.assertEqual(inputs, res)

    def test_transform(self):
        inputs = ['Foo',
                  'Bar01',
                  'baz-01']
        exp_res = ['izxw6___',
                   'ijqxembr',
                   'mjqxuljqge______']
        res = [tdn(x) for x in inputs]
        self.assertEqual(res, exp_res)

    def test_undo_transform(self):
        inputs = ['izxw6___',
                  'ijqxembr',
                  'mjqxuljqge______']
        exp_res = ['Foo',
                   'Bar01',
                   'baz-01']
        res = [tdn(x) for x in inputs]
        self.assertEqual(res, exp_res)
