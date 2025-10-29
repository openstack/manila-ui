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

import pytest
from selenium.webdriver.support.ui import Select

from openstack_dashboard.test.selenium import widgets


def wait_for_steady_state_of_share(openstack, share_name):
    for attempt in range(120):
        if (openstack.shared_file_system.get_share(
            openstack.shared_file_system.find_share(
                share_name).id).status in
                ["available", "error"]):
            break
        else:
            time.sleep(3)


def wait_for_share_is_deleted(openstack, share_name):
    for attempt in range(120):
        if openstack.shared_file_system.find_share(share_name) is None:
            break
        else:
            time.sleep(3)


@pytest.mark.parametrize(
    "clear_share, openstack_client, user_type",
    [
        ("openstack_demo", "openstack_demo", "user"),
        ("openstack_admin", "openstack_admin", "admin"),
    ], indirect=["clear_share", "openstack_client"])
def test_create_share(login, driver, share_name, openstack_client,
                      config, clear_share, user_type):
    login(user_type)
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
# select share_type required only for UI based on 2023.1 and previous.
# in newer versions there is set initial non-empty choice.
    select_element = share_form.find_element_by_id("id_share_type")
    Select(select_element).select_by_value('default')
    share_form.find_element_by_css_selector(
        ".btn-primary[value='Create']").click()
    messages = widgets.get_and_dismiss_messages(driver, config)
    assert f'Success: Creating share "{share_name}"' in messages
    assert openstack_client.shared_file_system.find_share(
        share_name) is not None


@pytest.mark.parametrize(
    "new_share, openstack_client, user_type",
    [
        ("openstack_demo", "openstack_demo", "user"),
        ("openstack_admin", "openstack_admin", "admin"),
    ], indirect=["new_share", "openstack_client"])
def test_delete_share(login, driver, config, new_share,
                      openstack_client, user_type):
    login(user_type)
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
    wait_for_share_is_deleted(openstack_client, new_share.name)
    assert openstack_client.shared_file_system.find_share(
        new_share.name) is None


@pytest.mark.parametrize(
    "new_share, openstack_client, user_type",
    [
        ("openstack_demo", "openstack_demo", "user"),
        ("openstack_admin", "openstack_admin", "admin"),
    ], indirect=["new_share", "openstack_client"])
def test_edit_share_description(login, driver, openstack_client,
                                config, new_share, user_type):
    login(user_type)
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
    assert (openstack_client.shared_file_system.get_share(
        new_share.id).description ==
        f"EDITED_Description for: {new_share.name}")


@pytest.mark.parametrize(
    "new_share, openstack_client, user_type",
    [
        ("openstack_demo", "openstack_demo", "user"),
        ("openstack_admin", "openstack_admin", "admin"),
    ], indirect=["new_share", "openstack_client"])
def test_resize_share_demo(login, driver, openstack_client,
                           config, new_share, user_type):
    login(user_type)
    url = '/'.join((
        config.dashboard.dashboard_url,
        'project',
        'shares',
    ))
    driver.get(url)
    rows = driver.find_elements_by_css_selector(
        f"table#shares tr[data-display='{new_share.name}']")
    assert len(rows) == 1
    assert (openstack_client.shared_file_system.get_share(
        new_share.id).size == 1)
    actions_column = rows[0].find_element_by_css_selector("td.actions_column")
    widgets.select_from_dropdown(actions_column, "Resize Share")
    share_form = driver.find_element_by_css_selector(".modal-content form")
    share_form.find_element_by_id("id_new_size").clear()
    share_form.find_element_by_id("id_new_size").send_keys("2")
    share_form.find_element_by_css_selector(
        ".btn-primary[value='Resize']").click()
    messages = widgets.get_and_dismiss_messages(driver, config)
    assert f'Success: Resized share "{new_share.name}"' in messages
    assert (openstack_client.shared_file_system.get_share(
        new_share.id).size == 2)


@pytest.mark.parametrize(
    "new_share, openstack_client, user_type",
    [
        ("openstack_demo", "openstack_demo", "user"),
        ("openstack_admin", "openstack_admin", "admin"),
    ], indirect=["new_share", "openstack_client"])
def test_edit_share_metadata(login, driver, openstack_client,
                             config, new_share, user_type):
    login(user_type)
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
    widgets.select_from_dropdown(actions_column, "Edit Share Metadata")
    share_form = driver.find_element_by_css_selector(".modal-content form")
    share_form.find_element_by_id("id_metadata").clear()
    share_form.find_element_by_id("id_metadata").send_keys(
        "test_value=integration_tests")
    share_form.find_element_by_css_selector(
        ".btn-primary[value='Save Changes']").click()
    messages = widgets.get_and_dismiss_messages(driver, config)
    assert (f'Success: Updating share metadata "{new_share.name}"'
            in messages)
    assert (openstack_client.shared_file_system.get_share(
        new_share.id).metadata == {'test_value': 'integration_tests'})
