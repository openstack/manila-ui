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


def data(TEST):

    # Add manila to the keystone data
    TEST.service_catalog.append(
        {"type": "share",
         "name": "Manila",
         "endpoints_links": [],
         "endpoints": [
             {"region": "RegionOne",
              "adminURL": "http://admin.manila.example.com:8786/v1",
              "internalURL": "http://int.manila.example.com:8786/v1",
              "publicURL": "http://public.manila.example.com:8786/v1"}]},
    )

projects = [
    type("%sProject" % v, (object, ),
         {'id': '%s_id' % v, 'name': '%s_name' % v})
    for v in ('foo', 'bar', 'quuz')
]
