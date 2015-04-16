# Copyright (c) 2015 Mirantis, Inc.
# All Rights Reserved.
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

from openstack_dashboard.api import base
from openstack_dashboard.api import network
from openstack_dashboard.api import neutron
from openstack_dashboard.api import nova


def _nova_network_list(request):
    nets = nova.novaclient(request).networks.list()
    for net in nets:
        net.name_or_id = net.to_dict().get('label', net.to_dict().get('id'))
    return nets


def _nova_network_get(request, nova_net_id):
    net = nova.novaclient(request).networks.get(nova_net_id)
    net.name_or_id = net.to_dict().get('label', net.to_dict().get('id'))
    return net


class NetworkClient(network.NetworkClient):
    def __init__(self, request):
        super(NetworkClient, self).__init__(request)
        if base.is_service_enabled(request, 'network'):
            self.network_list = neutron.network_list
            self.network_get = neutron.network_get
        else:
            self.network_list = _nova_network_list
            self.network_get = _nova_network_get


def network_list(request):
    return NetworkClient(request).network_list(request)


def network_get(request, net_id):
    return NetworkClient(request).network_get(request, net_id)
