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

from horizon import exceptions
from horizon import forms
from horizon import workflows

from openstack_dashboard.api import base

from manila_ui.api import manila as api_manila


class UpdateDefaultShareQuotasAction(workflows.Action):
    shares = forms.IntegerField(min_value=-1, label=_("Shares"))
    share_gigabytes = forms.IntegerField(
        min_value=-1, label=_("Share gigabytes"))
    share_snapshots = forms.IntegerField(
        min_value=-1, label=_("Share snapshots"))
    share_snapshot_gigabytes = forms.IntegerField(
        min_value=-1, label=_("Share snapshot gigabytes"))
    share_networks = forms.IntegerField(
        min_value=-1, label=_("Share Networks"))

    def __init__(self, request, context, *args, **kwargs):
        super(UpdateDefaultShareQuotasAction, self).__init__(
            request, context, *args, **kwargs)
        disabled_quotas = context['disabled_quotas']
        for field in disabled_quotas:
            if field in self.fields:
                self.fields[field].required = False
                self.fields[field].widget = forms.HiddenInput()

    def handle(self, request, data):
        try:
            if base.is_service_enabled(request, 'share'):
                manila_data = dict([(key, data[key]) for key in
                                    api_manila.MANILA_QUOTA_FIELDS])
                api_manila.default_quota_update(request, **manila_data)
                return True
        except Exception:
            exceptions.handle(request,
                              _('Unable to update default quotas.'))
            return False

    class Meta(object):
        name = _("Share")
        slug = 'update_default_share_quotas'
        help_text = _("From here you can update the default share quotas "
                      "(max limits).")


class UpdateDefaultShareQuotasStep(workflows.Step):
    action_class = UpdateDefaultShareQuotasAction
    contributes = api_manila.MANILA_QUOTA_FIELDS
    depends_on = ('disabled_quotas',)

    def prepare_action_context(self, request, context):
        try:
            quota_defaults = api_manila.default_quota_get(
                request, request.user.tenant_id)
            for field in api_manila.MANILA_QUOTA_FIELDS:
                context[field] = quota_defaults.get(field).limit
        except Exception:
            exceptions.handle(request,
                              _('Unable to retrieve default share quotas.'))
        return context

    def allowed(self, request):
        return base.is_service_enabled(request, 'share')
