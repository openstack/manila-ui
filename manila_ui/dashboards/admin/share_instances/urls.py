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

from django.urls import re_path

from manila_ui.dashboards.admin.share_instances import views


urlpatterns = [
    re_path(
        r'^$',
        views.ShareInstancesView.as_view(),
        name='index'),
    re_path(
        r'^(?P<share_instance_id>[^/]+)$',
        views.ShareInstanceDetailView.as_view(),
        name='share_instance_detail'),
]
