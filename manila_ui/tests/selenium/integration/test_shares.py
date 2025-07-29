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

import time

from oslo_utils import uuidutils
import pytest

from openstack_dashboard.test.selenium import widgets


@pytest.fixture
def share_name():
    return 'horizon_share_%s' % uuidutils.generate_uuid(dashed=False)


@pytest.fixture
def new_share(share_name, openstack_demo):
    share = openstack_demo.shared_file_system.create_share(
        name=share_name,
        size=1,
        share_protocol="NFS",
        wait=True,
    )
    wait_for_steady_state_of_share(openstack_demo, share_name)
    yield share
    openstack_demo.shared_file_system.delete_share(share)


@pytest.fixture
def clear_share(share_name, openstack_demo):
    yield None
    wait_for_steady_state_of_share(openstack_demo, share_name)
    openstack_demo.shared_file_system.delete_share(
        openstack_demo.shared_file_system.find_share(share_name).id)


def wait_for_steady_state_of_share(openstack, share_name):
    for attempt in range(120):
        if (openstack.shared_file_system.get_share(
            openstack.shared_file_system.find_share(
                share_name).id).status in
                ["available", "error", "inactive"]):
            break
        else:
            time.sleep(3)


def wait_for_share_is_deleted(openstack, share_name):
    for attempt in range(120):
        if openstack.shared_file_system.find_share(share_name) is None:
            break
        else:
            time.sleep(3)


def test_create_share_demo(login, driver, share_name,
                           openstack_demo,
                           config, clear_share):
    login('user')
    url = '/'.join((
        config.dashboard.dashboard_url,
        'project',
        'shares',
    ))
    driver.get(url)
    driver.find_element_by_link_text("Create Share").click()
    share_form = driver.find_element_by_css_selector(".modal-content form")
    share_form.find_element_by_id("id_name").send_keys(share_name)
    share_form.find_element_by_id("id_size").send_keys("1")
    share_form.find_element_by_css_selector(
        ".btn-primary[value='Create']").click()
    messages = widgets.get_and_dismiss_messages(driver, config)
    assert f'Success: Creating share "{share_name}"' in messages
    assert openstack_demo.shared_file_system.find_share(share_name) is not None


def test_delete_share_demo(login, driver, openstack_demo,
                           config, new_share):
    login('user')
    url = '/'.join((
        config.dashboard.dashboard_url,
        'project',
        'shares',
    ))
    driver.get(url)
    rows = driver.find_elements_by_css_selector(
        f"table#shares tr[data-display='{new_share.name}']")
    assert len(rows) == 1
    actions_column = rows[0].find_element_by_css_selector("td.actions_column")
    widgets.select_from_dropdown(actions_column, "Delete Share")
    widgets.confirm_modal(driver)
    messages = widgets.get_and_dismiss_messages(driver, config)
    assert f"Success: Deleted Share: {new_share.name}" in messages
    wait_for_share_is_deleted(openstack_demo, new_share.name)
    assert openstack_demo.shared_file_system.find_share(new_share.name) is None


def test_edit_share_demo(login, driver, openstack_demo,
                         config, new_share):
    login('user')
    url = '/'.join((
        config.dashboard.dashboard_url,
        'project',
        'shares',
    ))
    driver.get(url)
    rows = driver.find_elements_by_css_selector(
        f"table#shares tr[data-display='{new_share.name}']")
    assert len(rows) == 1
    rows[0].find_element_by_css_selector(".data-table-action").click()
    share_form = driver.find_element_by_css_selector(".modal-content form")
    share_form.find_element_by_id("id_description").send_keys(
        f"EDITED_Description for: {new_share.name}")
    share_form.find_element_by_css_selector(
        ".btn-primary[value='Edit']").click()
    messages = widgets.get_and_dismiss_messages(driver, config)
    assert f'Success: Updating share "{new_share.name}"' in messages
    assert (openstack_demo.shared_file_system.get_share(
        openstack_demo.shared_file_system.find_share(
            new_share.name).id).description ==
            f"EDITED_Description for: {new_share.name}")
