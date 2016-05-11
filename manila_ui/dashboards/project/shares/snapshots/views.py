# Copyright 2012 Nebula, Inc.
#
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

from django.core.urlresolvers import reverse
from django.core.urlresolvers import reverse_lazy
from django.utils.http import urlencode
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import forms
from horizon import tabs
from horizon.utils import memoized

from manila_ui.api import manila
from manila_ui.dashboards.project.shares.snapshots import forms \
    as snapshot_forms
from manila_ui.dashboards.project.shares.snapshots\
    import tabs as snapshot_tabs
from openstack_dashboard.usage import quotas


class SnapshotDetailView(tabs.TabView):
    tab_group_class = snapshot_tabs.SnapshotDetailTabs
    template_name = 'project/shares/snapshots/snapshot_detail.html'
    redirect_url = reverse_lazy('horizon:project:shares:index')

    def get_context_data(self, **kwargs):
        context = super(SnapshotDetailView, self).get_context_data(**kwargs)
        snapshot = self.get_data()
        snapshot_display_name = snapshot.name or snapshot.id
        context["snapshot"] = snapshot
        context["snapshot_display_name"] = snapshot_display_name
        context["page_title"] = _("Snapshot Details: "
                                  "%(snapshot_display_name)s") % \
            {'snapshot_display_name': snapshot_display_name}
        return context

    @memoized.memoized_method
    def get_data(self):
        try:
            snapshot_id = self.kwargs['snapshot_id']
            snapshot = manila.share_snapshot_get(self.request, snapshot_id)
            share = manila.share_get(self.request, snapshot.share_id)
            snapshot.share_name_or_id = share.name or share.id
        except Exception:
            exceptions.handle(self.request,
                              _('Unable to retrieve snapshot details.'),
                              redirect=self.redirect_url)
        return snapshot

    def get_tabs(self, request, *args, **kwargs):
        snapshot = self.get_data()
        return self.tab_group_class(request, snapshot=snapshot, **kwargs)


class CreateSnapshotView(forms.ModalFormView):
    form_class = snapshot_forms.CreateSnapshotForm
    template_name = 'project/shares/snapshots/create_snapshot.html'
    success_url = reverse_lazy("horizon:project:shares:index")
    page_title = _('Create Share Snapshot')

    def get_context_data(self, **kwargs):
        context = super(CreateSnapshotView, self).get_context_data(**kwargs)
        context['share_id'] = self.kwargs['share_id']
        try:
            share = manila.share_get(self.request, context['share_id'])
            if (share.status == 'in-use'):
                context['attached'] = True
                context['form'].set_warning(_("This share is currently "
                                              "attached to an instance. "
                                              "In some cases, creating a "
                                              "snapshot from an attached "
                                              "share can result in a "
                                              "corrupted snapshot."))
            context['usages'] = quotas.tenant_limit_usages(self.request)
        except Exception:
            exceptions.handle(self.request,
                              _('Unable to retrieve share information.'))
        return context

    def get_initial(self):
        return {'share_id': self.kwargs["share_id"]}


class UpdateView(forms.ModalFormView):
    form_class = snapshot_forms.UpdateForm
    template_name = 'project/shares/snapshots/update.html'
    success_url = "horizon:project:shares:index"

    @memoized.memoized_method
    def get_object(self):
        if not hasattr(self, "_object"):
            snap_id = self.kwargs['snapshot_id']
            try:
                self._object = manila.share_snapshot_get(self.request, snap_id)
            except Exception:
                msg = _('Unable to retrieve snapshot.')
                url = reverse('horizon:project:shares:index')
                exceptions.handle(self.request, msg, redirect=url)
        return self._object

    def get_context_data(self, **kwargs):
        context = super(UpdateView, self).get_context_data(**kwargs)
        context['snapshot'] = self.get_object()
        return context

    def get_initial(self):
        snapshot = self.get_object()
        return {'snapshot_id': self.kwargs["snapshot_id"],
                'name': snapshot.name,
                'description': snapshot.description}

    def get_success_url(self):
        return "?".join([reverse(self.success_url),
                         urlencode({"tab": "share_tabs__snapshots_tab"})])
