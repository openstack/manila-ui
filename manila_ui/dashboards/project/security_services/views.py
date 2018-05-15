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

from django.urls import reverse
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from horizon import exceptions
from horizon import forms
from horizon import tables
from horizon import tabs
from horizon.utils import memoized

from manila_ui.api import manila
from manila_ui.dashboards.project.security_services import forms as ss_forms
from manila_ui.dashboards.project.security_services import tables as ss_tables
from manila_ui.dashboards.project.security_services import tabs as ss_tabs
from manila_ui.dashboards.project.share_networks import forms as sn_forms
from manila_ui.dashboards import utils


class SecurityServicesView(tables.MultiTableView):
    table_classes = (
        ss_tables.SecurityServicesTable,
    )
    template_name = "project/security_services/index.html"
    page_title = _("Security Services")

    @memoized.memoized_method
    def get_security_services_data(self):
        try:
            security_services = manila.security_service_list(self.request)
        except Exception:
            security_services = []
            exceptions.handle(
                self.request, _("Unable to retrieve security services"))

        return security_services


class UpdateView(forms.ModalFormView):
    template_name = "project/security_services/update.html"
    form_class = ss_forms.Update
    form_id = "update_security_service"
    modal_header = _("Edit Security Service")
    modal_id = "update_security_service_modal"
    submit_label = _("Edit")
    submit_url = "horizon:project:security_services:security_service_update"
    success_url = reverse_lazy("horizon:project:security_services:index")
    page_title = _('Edit Security Service')

    def get_object(self):
        if not hasattr(self, "_object"):
            sec_service_id = self.kwargs['sec_service_id']
            try:
                self._object = manila.security_service_get(
                    self.request, sec_service_id)
            except Exception:
                msg = _('Unable to retrieve security_service.')
                url = reverse('horizon:project:security_services:index')
                exceptions.handle(self.request, msg, redirect=url)
        return self._object

    def get_context_data(self, **kwargs):
        context = super(UpdateView, self).get_context_data(**kwargs)
        return context

    def get_initial(self):
        self.submit_url = reverse(self.submit_url, kwargs=self.kwargs)
        sec_service = self.get_object()
        return {'sec_service_id': self.kwargs["sec_service_id"],
                'name': sec_service.name,
                'description': sec_service.description}


class CreateView(forms.ModalFormView):
    form_class = ss_forms.Create
    form_id = "create_security_service"
    template_name = 'project/security_services/create.html'
    modal_header = _("Create Security Service")
    modal_id = "create_security_service_modal"
    submit_label = _("Create")
    submit_url = reverse_lazy(
        "horizon:project:security_services:security_service_create")
    success_url = reverse_lazy("horizon:project:security_services:index")
    page_title = _('Create Security Service')


class AddSecurityServiceView(forms.ModalFormView):
    form_class = sn_forms.AddSecurityServiceForm
    template_name = 'project/security_services/add.html'
    success_url = 'horizon:project:security_services:index'
    page_title = _('Add Security Service')

    def get_object(self):
        if not hasattr(self, "_object"):
            share_id = self.kwargs['share_network_id']
            try:
                self._object = manila.share_network_get(self.request, share_id)
            except Exception:
                msg = _('Unable to retrieve share network.')
                url = reverse('horizon:project:security_services:index')
                exceptions.handle(self.request, msg, redirect=url)
        return self._object

    def get_context_data(self, **kwargs):
        context = super(AddSecurityServiceView,
                        self).get_context_data(**kwargs)
        context['share_network'] = self.get_object()
        return context

    def get_initial(self):
        share_net = self.get_object()
        return {'share_net_id': self.kwargs["share_network_id"],
                'name': share_net.name,
                'description': share_net.description}


class Detail(tabs.TabView):
    tab_group_class = ss_tabs.SecurityServiceDetailTabs
    template_name = 'project/security_services/detail.html'
    redirect_url = reverse_lazy('horizon:project:security_services:index')

    def get_context_data(self, **kwargs):
        context = super(Detail, self).get_context_data(**kwargs)
        sec_service = self.get_data()
        context["sec_service"] = sec_service
        sec_service_display_name = sec_service.name or sec_service.id
        context["sec_service_display_name"] = sec_service_display_name
        context["page_title"] = _("Security Service Details: "
                                  "%(service_display_name)s") % \
            {'service_display_name': sec_service_display_name}
        return context

    @memoized.memoized_method
    def get_data(self):
        try:
            sec_service_id = self.kwargs['sec_service_id']
            sec_service = manila.security_service_get(
                self.request, sec_service_id)
            sec_service.type = utils.get_nice_security_service_type(
                sec_service)
        except Exception:
            message = _("Unable to retrieve security service "
                        "'%s' details.") % sec_service_id
            exceptions.handle(
                self.request, message, redirect=self.redirect_url)
        return sec_service

    def get_tabs(self, request, *args, **kwargs):
        sec_service = self.get_data()
        return self.tab_group_class(request, sec_service=sec_service, **kwargs)
