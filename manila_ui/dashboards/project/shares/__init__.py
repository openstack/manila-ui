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

import functools
import sys

from django.utils.translation import ugettext_lazy as _

import horizon

from manila_ui.api import manila

from openstack_dashboard.api import base
from openstack_dashboard.dashboards.admin.defaults import tables as quota_tbl
from openstack_dashboard.dashboards.admin.defaults import views \
    as default_views
from openstack_dashboard.dashboards.admin.defaults import workflows \
    as default_workflows
from openstack_dashboard.dashboards.identity.projects import views \
    as project_views
from openstack_dashboard.dashboards.identity.projects import workflows \
    as project_workflows
from openstack_dashboard.dashboards.project.overview import views \
    as overview_views
from openstack_dashboard.usage import base as usage_base
from openstack_dashboard.usage import quotas


def wrap(orig_func):
    """decorator to wrap an existing function
       Modified post from http://downgra.de/2009/05/16/python-monkey-patching/
       to work with functions
       e.g.

       @wrap(quotas.tenant_limit_usages)
       def tenant_limit_usages(orig, self):
           limits = orig(request)
           limits['disksUsed'] = 100
           return limits

       the first parameter of the new function is the the original,
       overwritten function ('orig').
    """

    def outer(new_func):
        @functools.wraps(orig_func)
        def wrapper(*args, **kwargs):
            return new_func(orig_func, *args, **kwargs)
        # Replace the original function in the module with the wrapper
        orig_module = sys.modules[orig_func.__module__]
        setattr(orig_module, orig_func.__name__, wrapper)
        return wrapper
    return outer


# All public methods in openstack_dashboard.usage.quotas are hardcoded to
# only look at a fixed set of services (nova, cinder, etc.).  In order to
# incorporate manila quotas and usage, all public functions must be
# monkey-patched to add that information in.

MANILA_QUOTA_FIELDS = (
    "shares",
    "snapshots",
    "gigabytes",
    "share_networks",
)
MANILA_QUOTA_NAMES = {
    'shares': _('Shares'),
    'share_networks': _('Shares Networks'),
}

quotas.QUOTA_FIELDS = quotas.QUOTA_FIELDS + MANILA_QUOTA_FIELDS


def _get_manila_disabled_quotas(request):
    disabled_quotas = []
    if not base.is_service_enabled(request, 'share'):
        disabled_quotas.extend(MANILA_QUOTA_FIELDS)

    return disabled_quotas


def _get_manila_quota_data(request, method_name, disabled_quotas=None,
                           tenant_id=None):
    if not tenant_id:
        tenant_id = request.user.tenant_id
    if disabled_quotas is None:
        disabled_quotas = _get_manila_disabled_quotas(request)
    if 'shares' not in disabled_quotas:
        return getattr(manila, method_name)(request, tenant_id)
    else:
        return None


@wrap(quotas.get_default_quota_data)
def get_default_quota_data(f, request, disabled_quotas=None, tenant_id=None):
    qs = f(request, disabled_quotas, tenant_id)
    manila_quota = _get_manila_quota_data(request, "default_quota_get",
                                          disabled_quotas=disabled_quotas,
                                          tenant_id=tenant_id)
    if manila_quota:
        qs.add(manila_quota)
    return qs


@wrap(quotas.get_tenant_quota_data)
def get_tenant_quota_data(f, request, disabled_quotas=None, tenant_id=None):
    qs = f(request, disabled_quotas, tenant_id)
    manila_quota = _get_manila_quota_data(request, "tenant_quota_get",
                                          disabled_quotas=disabled_quotas,
                                          tenant_id=tenant_id)
    if manila_quota:
        qs.add(manila_quota)
    return qs


@wrap(quotas.get_disabled_quotas)
def get_disabled_quotas(f, request):
    disabled_quotas = f(request)
    disabled_quotas.extend(_get_manila_disabled_quotas(request))
    return disabled_quotas


@wrap(quotas.tenant_quota_usages)
def tenant_quota_usages(f, request, tenant_id=None):

    usages = f(request, tenant_id)

    if 'shares' not in _get_manila_disabled_quotas(request):
        shares = manila.share_list(request)
        snapshots = manila.share_snapshot_list(request)
        sn_l = manila.share_network_list(request)
        gig_s = sum([int(v.size) for v in shares])
        gig_ss = sum([int(v.size) for v in snapshots])
        usages.tally('gigabytes', gig_s + gig_ss)
        usages.tally('shares', len(shares))
        usages.tally('snapshots', len(snapshots))
        usages.tally('share_networks', len(sn_l))

    return usages


@wrap(quotas.tenant_limit_usages)
def tenant_limit_usages(f, request):

    limits = f(request)

    if base.is_service_enabled(request, 'share'):
        try:
            limits.update(manila.tenant_absolute_limits(request))
            shares = manila.share_list(request)
            snapshots = manila.share_snapshot_list(request)
            total_s_size = sum([getattr(share, 'size', 0) for share in shares])
            total_ss_size = sum([getattr(ss, 'size', 0) for ss in snapshots])
            limits['totalGigabytesUsed'] = total_s_size + total_ss_size
            limits['totalSharesUsed'] = len(shares)
            limits['totalSnapshotsUsed'] = len(snapshots)
        except Exception:
            msg = _("Unable to retrieve share limit information.")
            horizon.exceptions.handle(request, msg)

    return limits


@wrap(quota_tbl.get_quota_name)
def get_quota_name(f, quota):
    if quota.name in MANILA_QUOTA_NAMES:
        return MANILA_QUOTA_NAMES.get(quota.name)
    else:
        return f(quota)


#
# Add manila fields to Admin/Defaults/Update Defaults
#


class ManilaUpdateDefaultQuotaAction(
        default_workflows.UpdateDefaultQuotasAction):
    shares = horizon.forms.IntegerField(min_value=-1, label=_("Shares"))
    share_networks = horizon.forms.IntegerField(min_value=-1,
                                                label=_("Share Networks"))

    class Meta(object):
        name = _("Default Quota")
        slug = 'update_default_quotas'
        help_text = _("From here you can update the default quotas "
                      "(max limits).")


class ManilaUpdateDefaultQuotasStep(default_workflows.UpdateDefaultQuotasStep):
    action_class = ManilaUpdateDefaultQuotaAction
    contributes = quotas.QUOTA_FIELDS


class ManilaUpdateDefaultQuotas(default_workflows.UpdateDefaultQuotas):
    default_steps = (ManilaUpdateDefaultQuotasStep,)

    def handle(self, request, data):
        try:
            super(ManilaUpdateDefaultQuotas, self).handle(request, data)

            if base.is_service_enabled(request, 'share'):
                manila_data = dict([(key, data[key]) for key in
                                    MANILA_QUOTA_FIELDS])
                manila.default_quota_update(request, **manila_data)

        except Exception:
            horizon.exceptions.handle(request,
                                      _('Unable to update default quotas.'))

        return True


default_views.UpdateDefaultQuotasView.workflow_class = \
    ManilaUpdateDefaultQuotas

#
# Add manila fields to Identity/Projects/Modify Quotas
#


class ManilaUpdateProjectQuotaAction(
        project_workflows.UpdateProjectQuotaAction):
    shares = horizon.forms.IntegerField(min_value=-1, label=_("Shares"))
    share_networks = horizon.forms.IntegerField(min_value=-1,
                                                label=_("Share Networks"))

    class Meta(object):
        name = _("Quota")
        slug = 'update_quotas'
        help_text = _("Set maximum quotas for the project.")

project_workflows.UpdateProjectQuota.action_class = \
    ManilaUpdateProjectQuotaAction
project_workflows.UpdateProjectQuota.contributes = quotas.QUOTA_FIELDS


class ManilaUpdateProject(project_workflows.UpdateProject):
    def handle(self, request, data):
        try:
            super(ManilaUpdateProject, self).handle(request, data)

            if base.is_service_enabled(request, 'share'):
                manila_data = dict([(key, data[key]) for key in
                                    MANILA_QUOTA_FIELDS])
                manila.tenant_quota_update(request,
                                           data['project_id'],
                                           **manila_data)

        except Exception:
            horizon.exceptions.handle(request,
                                      _('Modified project information and '
                                        'members, but unable to modify '
                                        'project quotas.'))
        return True

project_views.UpdateProjectView.workflow_class = ManilaUpdateProject

#
# Add manila fields to Identity/Projects/Create Project
#


class ManilaCreateProjectQuotaAction(
        project_workflows.CreateProjectQuotaAction):
    shares = horizon.forms.IntegerField(min_value=-1, label=_("Shares"))
    share_networks = horizon.forms.IntegerField(min_value=-1,
                                                label=_("Share Networks"))

    class Meta(object):
        name = _("Quota")
        slug = 'create_quotas'
        help_text = _("Set maximum quotas for the project.")

project_workflows.CreateProjectQuota.action_class = \
    ManilaCreateProjectQuotaAction
project_workflows.CreateProjectQuota.contributes = quotas.QUOTA_FIELDS


class ManilaCreateProject(project_workflows.CreateProject):
    def handle(self, request, data):
        try:
            super(ManilaCreateProject, self).handle(request, data)

            if base.is_service_enabled(request, 'share'):
                manila_data = dict([(key, data[key]) for key in
                                    MANILA_QUOTA_FIELDS])
                manila.tenant_quota_update(request,
                                           self.object.id,
                                           **manila_data)

        except Exception:
            horizon.exceptions.handle(request,
                                      _('Unable to set project quotas.'))
        return True

project_views.CreateProjectView.workflow_class = ManilaCreateProject

#
# Add extra pie charts to Project/Compute Overview
#


class ManilaUsage(usage_base.ProjectUsage):

    def get_manila_limits(self):
        """Get share limits if manila is enabled."""
        if not base.is_service_enabled(self.request, 'share'):
            return
        try:
            self.limits.update(manila.tenant_absolute_limits(self.request))
        except Exception:
            msg = _("Unable to retrieve share limit information.")
            horizon.exceptions.handle(self.request, msg)
        return

    def get_limits(self):
        super(self.__class__, self).get_limits()
        self.get_manila_limits()


def get_context_data(self, **kwargs):
    context = super(self.__class__, self).get_context_data(**kwargs)
    types = (
        ("totalSharesUsed", "maxTotalShares", _("Shares")),
        ("totalShareGigabytesUsed", "maxTotalShareGigabytes",
         _("Share Storage")),
        ("totalShareSnapshotsUsed", "maxTotalShareSnapshots",
         _("Share Snapshots")),
        ("totalSnapshotGigabytesUsed", "maxTotalSnapshotGigabytes",
         _("Share Snapshots Storage")),
        ("totalShareNetworksUsed", "maxTotalShareNetworks",
         _("Share Networks")),
    )
    for t in types:
        if t[0] in self.usage.limits and t[1] in self.usage.limits:
            context['charts'].append({
                'name': t[2],
                'used': self.usage.limits[t[0]],
                'max': self.usage.limits[t[1]],
                'text': False,
            })
    return context


overview_views.ProjectOverview.get_context_data = get_context_data
overview_views.ProjectOverview.usage_class = ManilaUsage
