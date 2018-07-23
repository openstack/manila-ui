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

from django.utils.translation import ugettext_lazy as _

from horizon import forms
from horizon import workflows

from openstack_dashboard.api import base
from openstack_dashboard.dashboards.identity.projects \
    import workflows as project_workflows

from manila_ui.api import manila as api_manila


class ShareQuotaAction(project_workflows.CommonQuotaAction):
    shares = forms.IntegerField(min_value=-1, label=_("Shares"))
    share_gigabytes = forms.IntegerField(
        min_value=-1, label=_("Share gigabytes"))
    share_snapshots = forms.IntegerField(
        min_value=-1, label=_("Share snapshots"))
    share_snapshot_gigabytes = forms.IntegerField(
        min_value=-1, label=_("Share snapshot gigabytes"))
    share_networks = forms.IntegerField(
        min_value=-1, label=_("Share Networks"))

    _quota_fields = api_manila.MANILA_QUOTA_FIELDS

    def _tenant_quota_update(self, request, project_id, data):
        api_manila.tenant_quota_update(request, project_id, **data)

    class Meta(object):
        name = _("Share")
        slug = 'update_share_quotas'
        help_text = _("Set maximum quotas for the project.")
        permissions = ('openstack.roles.admin', 'openstack.services.share')


class UpdateShareQuota(workflows.Step):
    action_class = ShareQuotaAction
    depends_on = ("project_id", "disabled_quotas")
    contributes = api_manila.MANILA_QUOTA_FIELDS

    def allowed(self, request):
        return base.is_service_enabled(request, 'share')
