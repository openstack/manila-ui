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

from openstack_dashboard.api import base
from openstack_dashboard.usage import base as usage

from manila_ui.api import manila

#
# Add extra pie charts to project/compute overview
#


class ManilaUsage(usage.ProjectUsage):

    def get_manila_limits(self):
        """Get share limits if manila is enabled."""
        if not base.is_service_enabled(self.request, 'share'):
            return
        try:
            self.limits.update(manila.tenant_absolute_limits(self.request))
        except Exception:
            msg = _("Unable to retrieve share limit information.")
            exceptions.handle(self.request, msg)
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
                'type': t[0],
                'name': t[2],
                'used': self.usage.limits[t[0]],
                'max': self.usage.limits[t[1]],
                'text': False,
            })
    return context
