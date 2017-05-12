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

from django.conf import urls

from manila_ui.dashboards.admin.share_types import views


urlpatterns = [
    urls.url(
        r'^$',
        views.ShareTypesView.as_view(),
        name='index'),
    urls.url(
        r'^create_type$',
        views.CreateShareTypeView.as_view(),
        name='create_type'),
    urls.url(
        r'^update_type/(?P<share_type_id>[^/]+)/extra_specs$',
        views.UpdateShareTypeView.as_view(),
        name='update_type'),
    urls.url(
        r'^manage_share_type_access/(?P<share_type_id>[^/]+)$',
        views.ManageShareTypeAccessView.as_view(),
        name='manage_share_type_access'),
]
