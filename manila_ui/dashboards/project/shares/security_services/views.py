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
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import forms
from horizon import tabs

from openstack_dashboard.api import manila
from openstack_dashboard.dashboards.project.shares.security_services import\
    forms as sec_services_forms
from openstack_dashboard.dashboards.project.shares.security_services \
    import tabs as security_services_tabs
from openstack_dashboard.dashboards.project.shares.share_networks import forms\
    as share_net_forms


class UpdateView(forms.ModalFormView):
    template_name = "project/shares/security_services/update.html"
    form_class = sec_services_forms.Update
    success_url = 'horizon:project:shares:index'

    def get_success_url(self):
        return reverse(self.success_url)

    def get_object(self):
        if not hasattr(self, "_object"):
            sec_service_id = self.kwargs['sec_service_id']
            try:
                self._object = manila.security_service_get(
                    self.request, sec_service_id)
            except Exception:
                msg = _('Unable to retrieve security_service.')
                url = reverse('horizon:project:shares:index')
                exceptions.handle(self.request, msg, redirect=url)
        return self._object

    def get_context_data(self, **kwargs):
        context = super(UpdateView, self).get_context_data(**kwargs)
        context['sec_service'] = self.get_object()
        return context

    def get_initial(self):
        sec_service = self.get_object()
        return {'sec_service_id': self.kwargs["sec_service_id"],
                'name': sec_service.name,
                'description': sec_service.description}


class CreateView(forms.ModalFormView):
    form_class = sec_services_forms.Create
    template_name = ('project/shares/security_services'
                     '/create_security_service.html')
    success_url = 'horizon:project:shares:index'

    def get_success_url(self):
        return reverse(self.success_url)


class AddSecurityServiceView(forms.ModalFormView):
    form_class = share_net_forms.AddSecurityServiceForm
    template_name = ('project/shares/security_services'
                     '/add_security_service.html')
    success_url = 'horizon:project:shares:index'

    def get_object(self):
        if not hasattr(self, "_object"):
            share_id = self.kwargs['share_network_id']
            try:
                self._object = manila.share_network_get(self.request, share_id)
            except Exception:
                msg = _('Unable to retrieve share network.')
                url = reverse('horizon:project:shares:index')
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
    tab_group_class = security_services_tabs.SecurityServiceDetailTabs
    template_name = 'project/shares/security_services/detail.html'

    def get_context_data(self, **kwargs):
        context = super(Detail, self).get_context_data(**kwargs)
        sec_service = self.get_data()
        context["sec_service"] = sec_service
        sec_service_display_name = sec_service.name or sec_service.id
        context["sec_service_display_name"] = sec_service_display_name
        return context

    def get_data(self):
        try:
            sec_service_id = self.kwargs['sec_service_id']
            sec_service = manila.security_service_get(
                self.request, sec_service_id)
        except Exception:
            redirect = reverse('horizon:project:shares:index')
            exceptions.handle(
                self.request,
                _('Unable to retrieve security service details.'),
                redirect=redirect)
        return sec_service

    def get_tabs(self, request, *args, **kwargs):
        sec_service = self.get_data()
        return self.tab_group_class(request, sec_service=sec_service, **kwargs)
