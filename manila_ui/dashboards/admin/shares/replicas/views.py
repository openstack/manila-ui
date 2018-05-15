# Copyright (c) 2016 Mirantis, Inc.
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

from manila_ui.api import manila
from manila_ui.dashboards.admin.shares.replicas import (
    tables as replicas_tables)
from manila_ui.dashboards.admin.shares.replicas import forms as replicas_forms
from manila_ui.dashboards.admin.shares.replicas import tabs as replicas_tabs
from manila_ui.dashboards.project.shares.replicas import (
    views as project_replica_views)


class ManageReplicasView(project_replica_views.ManageReplicasView):
    table_class = replicas_tables.ReplicasTable
    template_name = 'admin/shares/replicas/manage_replicas.html'
    _redirect_url = 'horizon:admin:shares:index'


class DetailReplicaView(project_replica_views.DetailReplicaView):
    tab_group_class = replicas_tabs.ReplicaDetailTabs
    template_name = 'admin/shares/replicas/detail.html'
    _redirect_url = 'horizon:admin:shares:index'


class ResyncReplicaView(forms.ModalFormView):
    form_class = replicas_forms.ResyncReplicaForm
    form_id = "resync_replica"
    template_name = 'admin/shares/replicas/resync_replica.html'
    modal_header = _("Resync Replica")
    modal_id = "resync_replica_modal"
    submit_label = _("Resync")
    submit_url = "horizon:admin:shares:resync_replica"
    success_url = 'horizon:admin:shares:manage_replicas'
    page_title = _("Resync Replica")

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
                url = reverse('horizon:admin:shares:index')
                exceptions.handle(self.request, msg, redirect=url)
        return self._object

    def get_context_data(self, **kwargs):
        context = super(self.__class__, self).get_context_data(**kwargs)
        context['replica_id'] = self.kwargs['replica_id']
        args = (context['replica_id'],)
        context['submit_url'] = reverse(self.submit_url, args=args)
        return context

    def get_initial(self):
        return {'replica_id': self.kwargs["replica_id"]}


class ResetReplicaStatusView(forms.ModalFormView):
    form_class = replicas_forms.ResetReplicaStatusForm
    form_id = "reset_replica_status"
    template_name = 'admin/shares/replicas/reset_replica_status.html'
    modal_header = _("Reset Replica Status")
    modal_id = "reset_replica_status_modal"
    submit_label = _("Reset status")
    submit_url = "horizon:admin:shares:reset_replica_status"
    success_url = 'horizon:admin:shares:manage_replicas'
    page_title = _("Reset Replica Status")

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
                url = reverse('horizon:admin:shares:index')
                exceptions.handle(self.request, msg, redirect=url)
        return self._object

    def get_context_data(self, **kwargs):
        context = super(self.__class__, self).get_context_data(**kwargs)
        context['replica_id'] = self.kwargs['replica_id']
        args = (context['replica_id'],)
        context['submit_url'] = reverse(self.submit_url, args=args)
        return context

    def get_initial(self):
        return {'replica_id': self.kwargs["replica_id"]}


class ResetReplicaStateView(forms.ModalFormView):
    form_class = replicas_forms.ResetReplicaStateForm
    form_id = "reset_replica_state"
    template_name = 'admin/shares/replicas/reset_replica_state.html'
    modal_header = _("Reset Replica State")
    modal_id = "reset_replica_state_modal"
    submit_label = _("Reset state")
    submit_url = "horizon:admin:shares:reset_replica_state"
    success_url = 'horizon:admin:shares:manage_replicas'
    page_title = _("Reset Replica State")

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
                url = reverse('horizon:admin:shares:index')
                exceptions.handle(self.request, msg, redirect=url)
        return self._object

    def get_context_data(self, **kwargs):
        context = super(self.__class__, self).get_context_data(**kwargs)
        context['replica_id'] = self.kwargs['replica_id']
        args = (context['replica_id'],)
        context['submit_url'] = reverse(self.submit_url, args=args)
        return context

    def get_initial(self):
        return {'replica_id': self.kwargs["replica_id"]}
