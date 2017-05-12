# Copyright (c) 2015 Mirantis, Inc.
# All rights reserved.

# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import ddt
from django.core.handlers import wsgi
from django import forms as django_forms
from horizon import forms as horizon_forms
import mock

from manila_ui.dashboards.admin.share_types import forms
from manila_ui.tests import helpers as base


@ddt.ddt
class ManilaDashboardsAdminSharesUpdateShareTypeFormTests(base.APITestCase):

    def setUp(self):
        super(self.__class__, self).setUp()
        FAKE_ENVIRON = {'REQUEST_METHOD': 'GET', 'wsgi.input': 'fake_input'}
        self.request = wsgi.WSGIRequest(FAKE_ENVIRON)

    def _get_form(self, initial):
        kwargs = {
            'prefix': None,
            'initial': initial,
        }
        return forms.UpdateShareType(self.request, **kwargs)

    @ddt.data(
        ({}, []),
        ({'foo': 'bar', 'quuz': 'zaab'}, ["foo=bar\r\n", "quuz=zaab\r\n"]),
    )
    @ddt.unpack
    def test___init__(self, extra_specs_dict_input, extra_specs_str_output):
        form = self._get_form({'extra_specs': extra_specs_dict_input})

        for expected_extra_spec in extra_specs_str_output:
            self.assertIn(expected_extra_spec, form.initial['extra_specs'])
        self.assertIn('extra_specs', list(form.fields.keys()))
        self.assertTrue(
            isinstance(form.fields['extra_specs'], horizon_forms.CharField))

    @mock.patch('horizon.messages.success')
    def test_handle_success_no_changes(self, mock_horizon_messages_success):
        initial = {'id': 'fake_id', 'name': 'fake_name', 'extra_specs': {}}
        form = self._get_form(initial)
        data = {'extra_specs': ''}

        result = form.handle(self.request, data)

        self.assertTrue(result)
        mock_horizon_messages_success.assert_called_once_with(
            mock.ANY, mock.ANY)

    @mock.patch('horizon.messages.success')
    def test_handle_success_only_set(self, mock_horizon_messages_success):
        initial = {
            'id': 'fake_id',
            'name': 'fake_name',
            'extra_specs': {'foo': 'bar'}
        }
        form = self._get_form(initial)
        data = {'extra_specs': 'foo=bar\r\n'}

        result = form.handle(self.request, data)

        self.assertTrue(result)
        mock_horizon_messages_success.assert_called_once_with(
            mock.ANY, mock.ANY)
        self.manilaclient.share_types.get.assert_called_once_with(
            initial['id'])
        self.manilaclient.share_types.get.return_value.set_keys.\
            assert_called_once_with({'foo': 'bar'})
        self.assertFalse(
            self.manilaclient.share_types.get.return_value.unset_keys.called)

    @mock.patch('horizon.messages.success')
    def test_handle_success_only_unset(self, mock_horizon_messages_success):
        initial = {
            'id': 'fake_id',
            'name': 'fake_name',
            'extra_specs': {'foo': 'bar'}
        }
        form = self._get_form(initial)
        data = {'extra_specs': 'foo\r\n'}
        share_types_get = self.manilaclient.share_types.get
        share_types_get.return_value.get_keys.return_value = {
            'foo': 'bar', 'quuz': 'zaab'}

        result = form.handle(self.request, data)

        self.assertTrue(result)
        mock_horizon_messages_success.assert_called_once_with(
            mock.ANY, mock.ANY)
        self.manilaclient.share_types.get.assert_has_calls([
            mock.call(initial['id'])])
        share_types_get.return_value.get_keys.assert_called_once_with()
        self.assertFalse(share_types_get.return_value.set_keys.called)
        share_types_get.return_value.unset_keys.assert_called_once_with(
            {'foo'})

    @mock.patch('horizon.messages.success')
    def test_handle_success_set_and_unset(self, mock_horizon_messages_success):
        initial = {
            'id': 'fake_id',
            'name': 'fake_name',
            'extra_specs': {'foo': 'bar'}
        }
        form = self._get_form(initial)
        data = {'extra_specs': 'foo\r\nquuz=zaab'}
        share_types_get = self.manilaclient.share_types.get
        share_types_get.return_value.get_keys.return_value = {'foo': 'bar'}

        result = form.handle(self.request, data)

        self.assertTrue(result)
        mock_horizon_messages_success.assert_called_once_with(
            mock.ANY, mock.ANY)
        self.manilaclient.share_types.get.assert_has_calls([
            mock.call(initial['id'])])
        share_types_get.return_value.get_keys.assert_called_once_with()
        share_types_get.return_value.set_keys.assert_called_once_with(
            {'quuz': 'zaab'})
        share_types_get.return_value.unset_keys.assert_called_once_with(
            {'foo'})

    def test_handle_validation_error(self):
        initial = {'id': 'fake_id', 'name': 'fake_name', 'extra_specs': {}}
        form = self._get_form(initial)
        form.api_error = mock.Mock()
        data = {'extra_specs': 'a b'}

        result = form.handle(self.request, data)

        self.assertFalse(result)
        form.api_error.assert_called_once_with(mock.ANY)

    @mock.patch('horizon.exceptions.handle')
    def test_handle_other_exception(self, mock_horizon_exceptions_handle):
        django_forms.ValidationError
        initial = {'id': 'fake_id', 'name': 'fake_name', 'extra_specs': {}}
        form = self._get_form(initial)
        data = {'extra_specs': None}

        result = form.handle(self.request, data)

        self.assertFalse(result)
        mock_horizon_exceptions_handle.assert_called_once_with(
            self.request, mock.ANY)


@ddt.ddt
class ManilaDashboardsAdminSharesCreateShareTypeFormTests(base.APITestCase):

    def setUp(self):
        super(self.__class__, self).setUp()
        FAKE_ENVIRON = {'REQUEST_METHOD': 'GET', 'wsgi.input': 'fake_input'}
        self.request = wsgi.WSGIRequest(FAKE_ENVIRON)

    def _get_form(self, **kwargs):
        return forms.CreateShareType(self.request, **kwargs)

    @mock.patch('horizon.messages.success')
    def test_create_share_type(self, mock_horizon_messages_success):
        form = self._get_form()
        data = {
            'extra_specs': '',
            'is_public': False,
            'spec_driver_handles_share_servers': 'True',
            'name': 'share',
        }

        result = form.handle(self.request, data)

        self.assertTrue(result)
        self.manilaclient.share_types.create.assert_called_once_with(
            name=data['name'],
            spec_driver_handles_share_servers='true',
            spec_snapshot_support=True,
            is_public=data["is_public"])
        mock_horizon_messages_success.assert_called_once_with(
            self.request, mock.ANY)

    @mock.patch('horizon.messages.success')
    def test_create_share_type_with_extra_specs(self,
                                                mock_horizon_messages_success):
        form = self._get_form()
        data = {'extra_specs': 'a=b \n c=d',
                'is_public': False,
                'spec_driver_handles_share_servers': 'True',
                'name': 'share'}

        result = form.handle(self.request, data)

        self.assertTrue(result)

        set_keys = self.manilaclient.share_types.get.return_value.set_keys
        set_keys.assert_called_once_with(
            {'a': 'b', 'c': 'd'})
        self.manilaclient.share_types.create.assert_called_once_with(
            name=data['name'],
            spec_driver_handles_share_servers='true',
            spec_snapshot_support=True,
            is_public=data["is_public"])
        mock_horizon_messages_success.assert_called_once_with(
            self.request, mock.ANY)

    @ddt.data(True, False)
    @mock.patch('horizon.messages.success')
    def test_public_share_type_creation(self,
                                        enable_public_share_type_creation,
                                        mock_horizon_messages_success):
        with self.settings(OPENSTACK_MANILA_FEATURES={
                'enable_public_share_type_creation':
                enable_public_share_type_creation}):
            form = self._get_form()

            data = {
                'extra_specs': '',
                'is_public': enable_public_share_type_creation,
                'spec_driver_handles_share_servers': 'True',
                'name': 'share',
            }

            result = form.handle(self.request, data)

            self.assertTrue(result)
            self.assertEqual(
                enable_public_share_type_creation,
                form.enable_public_share_type_creation)
            if enable_public_share_type_creation:
                self.assertIn("is_public", form.fields)
                self.assertTrue(form.fields["is_public"])
            else:
                self.assertNotIn("is_public", form.fields)
            self.manilaclient.share_types.create.assert_called_once_with(
                name=data['name'],
                spec_driver_handles_share_servers='true',
                spec_snapshot_support=True,
                is_public=enable_public_share_type_creation)
            mock_horizon_messages_success.assert_called_once_with(
                self.request, mock.ANY)
