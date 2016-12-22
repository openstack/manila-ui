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
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import forms
from horizon import tables
from horizon import tabs
from horizon.utils import memoized

from manila_ui.api import manila
from manila_ui.dashboards.project.shares.snapshots import forms \
    as snapshot_forms
from manila_ui.dashboards.project.shares.snapshots \
    import tables as snapshot_tables
from manila_ui.dashboards.project.shares.snapshots \
    import tabs as snapshot_tabs
from manila_ui.dashboards import utils as ui_utils
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
                                  "%(snapshot_display_name)s") % (
            {'snapshot_display_name': snapshot_display_name})
        return context

    @memoized.memoized_method
    def get_data(self):
        try:
            snapshot_id = self.kwargs['snapshot_id']
            snapshot = manila.share_snapshot_get(self.request, snapshot_id)
            share = manila.share_get(self.request, snapshot.share_id)
            if share.mount_snapshot_support:
                snapshot.rules = manila.share_snapshot_rules_list(
                    self.request, snapshot_id)
                snapshot.export_locations = (
                    manila.share_snap_export_location_list(
                        self.request, snapshot))
                export_locations = [
                    exp['path'] for exp in snapshot.export_locations
                ]
                snapshot.el_size = ui_utils.calculate_longest_str_size(
                    export_locations)

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
    form_id = "create_share_snapshot"
    template_name = 'project/shares/snapshots/create_snapshot.html'
    modal_header = _("Create Share Snapshot")
    modal_id = "create_share_snapshot_modal"
    submit_label = _("Create Share Snapshot")
    submit_url = "horizon:project:shares:create_snapshot"
    success_url = reverse_lazy('horizon:project:shares:snapshots_tab')
    page_title = _('Create Share Snapshot')

    def get_context_data(self, **kwargs):
        context = super(CreateSnapshotView, self).get_context_data(**kwargs)
        context['share_id'] = self.kwargs['share_id']
        try:
            context['usages'] = quotas.tenant_limit_usages(self.request)
        except Exception:
            exceptions.handle(self.request, _('Unable to retrieve quotas.'))
        return context

    def get_initial(self):
        self.submit_url = reverse(self.submit_url, kwargs=self.kwargs)
        return {'share_id': self.kwargs["share_id"]}


class UpdateView(forms.ModalFormView):
    form_class = snapshot_forms.UpdateForm
    form_id = "update_snapshot"
    template_name = 'project/shares/snapshots/update.html'
    modal_header = _("Edit Snapshot")
    modal_id = "update_snapshot_modal"
    submit_label = _("Edit")
    submit_url = "horizon:project:shares:edit_snapshot"
    success_url = reverse_lazy('horizon:project:shares:snapshots_tab')
    page_title = _('Edit Snapshot')

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
        args = (self.get_object().id,)
        context['submit_url'] = reverse(self.submit_url, args=args)
        return context

    def get_initial(self):
        snapshot = self.get_object()
        return {'snapshot_id': self.kwargs["snapshot_id"],
                'name': snapshot.name,
                'description': snapshot.description}


class AddRuleView(forms.ModalFormView):
    form_class = snapshot_forms.AddRule
    form_id = "rule_add_snap"
    template_name = 'project/shares/snapshots/rule_add.html'
    modal_header = _("Add Rule")
    modal_id = "rule_add_snap_modal"
    submit_label = _("Add")
    submit_url = "horizon:project:shares:snapshot_rule_add"
    success_url = reverse_lazy("horizon:project:shares:index")
    page_title = _('Add Rule')

    def get_object(self):
        if not hasattr(self, "_object"):
            snapshot_id = self.kwargs['snapshot_id']
            try:
                self._object = manila.share_snapshot_get(
                    self.request, snapshot_id)
            except Exception:
                msg = _('Unable to retrieve snapshot.')
                url = reverse('horizon:project:shares:index')
                exceptions.handle(self.request, msg, redirect=url)
        return self._object

    def get_context_data(self, **kwargs):
        context = super(AddRuleView, self).get_context_data(**kwargs)
        args = (self.get_object().id,)
        context['submit_url'] = reverse(self.submit_url, args=args)
        return context

    def get_initial(self):
        snapshot = self.get_object()
        return {'snapshot_id': self.kwargs["snapshot_id"],
                'name': snapshot.name,
                'description': snapshot.description}

    def get_success_url(self):
        return reverse("horizon:project:shares:snapshot_manage_rules",
                       args=[self.kwargs['snapshot_id']])


class ManageRulesView(tables.DataTableView):
    table_class = snapshot_tables.RulesTable
    template_name = 'project/shares/snapshots/manage_rules.html'

    def get_context_data(self, **kwargs):
        context = super(ManageRulesView, self).get_context_data(**kwargs)
        snapshot = manila.share_snapshot_get(
            self.request, self.kwargs['snapshot_id'])
        context['snapshot_display_name'] = snapshot.name or snapshot.id
        context["snapshot"] = self.get_data()
        context["page_title"] = _("Snapshot Rules: "
                                  "%(snapshot_display_name)s") % {
            'snapshot_display_name': context['snapshot_display_name']}
        return context

    @memoized.memoized_method
    def get_data(self):
        try:
            snapshot_id = self.kwargs['snapshot_id']
            rules = manila.share_snapshot_rules_list(
                self.request, snapshot_id)
        except Exception:
            redirect = reverse('horizon:project:shares:index')
            exceptions.handle(self.request,
                              _('Unable to retrieve snapshot rules.'),
                              redirect=redirect)
        return rules
