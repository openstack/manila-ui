# Copyright (c) 2015 Mirantis, Inc.
# All rights reserved.
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

from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import forms
from horizon import tables
from horizon import tabs
from horizon.utils import memoized

from manila_ui.api import manila
from manila_ui.dashboards.project.shares.replicas import (
    forms as replicas_forms)
from manila_ui.dashboards.project.shares.replicas import (
    tables as replicas_tables)
from manila_ui.dashboards.project.shares.replicas import tabs as replicas_tabs
from manila_ui.dashboards import utils as ui_utils


class ManageReplicasView(tables.DataTableView):
    table_class = replicas_tables.ReplicasTable
    template_name = 'project/shares/replicas/manage_replicas.html'
    _redirect_url = 'horizon:project:shares:index'

    def get_context_data(self, **kwargs):
        context = super(ManageReplicasView, self).get_context_data(**kwargs)
        try:
            share = manila.share_get(self.request, self.kwargs["share_id"])
        except Exception:
            redirect = reverse(self._redirect_url)
            exceptions.handle(
                self.request,
                _('Unable to retrieve share. %s') % self.kwargs["share_id"],
                redirect=redirect)
        context["share_display_name"] = share.name or share.id
        context["share"] = self.get_data()
        context["page_title"] = _(
            "Share Replicas: %(share_display_name)s") % {
                "share_display_name": context["share_display_name"]}
        return context

    @memoized.memoized_method
    def get_data(self):
        try:
            share_id = self.kwargs['share_id']
            return manila.share_replica_list(self.request, share_id)
        except Exception:
            redirect = reverse(self._redirect_url)
            exceptions.handle(
                self.request,
                _('Unable to retrieve share replicas.'),
                redirect=redirect)


class DetailReplicaView(tabs.TabView):
    tab_group_class = replicas_tabs.ReplicaDetailTabs
    template_name = 'project/shares/replicas/detail.html'
    _redirect_url = 'horizon:project:shares:index'

    def get_context_data(self, **kwargs):
        context = super(DetailReplicaView, self).get_context_data(**kwargs)
        replica = self.get_data()
        replica_display_name = replica.id
        context["replica"] = replica
        context["replica_display_name"] = replica_display_name
        context["page_title"] = _(
            "Replica Details: %(replica_display_name)s") % {
                "replica_display_name": replica_display_name}
        return context

    @memoized.memoized_method
    def get_data(self):
        try:
            replica_id = self.kwargs['replica_id']
            replica = manila.share_replica_get(self.request, replica_id)
            try:
                # The default policy for this API does not allow
                # non-admins to retrieve export locations.
                replica.export_locations = (
                    manila.share_instance_export_location_list(
                        self.request, replica_id))
                export_locations = [
                    exp['path'] for exp in replica.export_locations
                ]
                replica.el_size = ui_utils.calculate_longest_str_size(
                    export_locations)
            except Exception:
                replica.export_locations = []
        except Exception:
            redirect = reverse(self._redirect_url)
            exceptions.handle(
                self.request,
                _('Unable to retrieve details of replica %s') %
                self.kwargs['replica_id'], redirect=redirect)
        return replica

    def get_tabs(self, request, *args, **kwargs):
        replica = self.get_data()
        return self.tab_group_class(request, replica=replica, **kwargs)


class CreateReplicaView(forms.ModalFormView):
    form_class = replicas_forms.CreateReplicaForm
    form_id = "create_replica"
    template_name = 'project/shares/replicas/create_replica.html'
    modal_header = _("Create Replica")
    modal_id = "create_replica_modal"
    submit_label = _("Create")
    submit_url = "horizon:project:shares:create_replica"
    success_url = 'horizon:project:shares:manage_replicas'
    page_title = _("Create Replica")

    def get_context_data(self, **kwargs):
        context = super(CreateReplicaView, self).get_context_data(**kwargs)
        context['share_id'] = self.kwargs['share_id']
        args = (context['share_id'],)
        context['submit_url'] = reverse(self.submit_url, args=args)
        return context

    def get_initial(self):
        return {'share_id': self.kwargs["share_id"]}

    def get_success_url(self):
        return reverse(self.success_url, args=[self.kwargs['share_id']])


class SetReplicaAsActiveView(forms.ModalFormView):
    form_class = replicas_forms.SetReplicaAsActiveForm
    form_id = "set_replica_as_active"
    template_name = "project/shares/replicas/set_replica_as_active.html"
    modal_header = _("Set Replica as Active")
    modal_id = "set_replica_as_active_modal"
    submit_label = _("Set as Active")
    submit_url = "horizon:project:shares:set_replica_as_active"
    success_url = "horizon:project:shares:manage_replicas"
    page_title = _("Set Replica as Active")

    def get_success_url(self):
        return reverse(self.success_url, args=[self.get_object().share_id])

    def get_object(self):
        if not hasattr(self, "_object"):
            replica_id = self.kwargs["replica_id"]
            try:
                self._object = manila.share_replica_get(
                    self.request, replica_id)
            except Exception:
                msg = _("Unable to retrieve replica '%s'.") % replica_id
                url = reverse("horizon:project:shares:index")
                exceptions.handle(self.request, msg, redirect=url)
        return self._object

    def get_context_data(self, **kwargs):
        context = super(SetReplicaAsActiveView, self).get_context_data(
            **kwargs)
        context["replica_id"] = self.kwargs["replica_id"]
        args = (context["replica_id"],)
        context["submit_url"] = reverse(self.submit_url, args=args)
        return context

    def get_initial(self):
        return {"replica_id": self.kwargs["replica_id"]}
