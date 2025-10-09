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

import openstack.exceptions as openstack_exception
from openstack_dashboard.test.selenium import widgets
import pytest


def wait_for_steady_state_of_share_snapshot(openstack_client,
                                            share_snapshot_id):
    for attempt in range(120):
        if (openstack_client.shared_file_system.get_share_snapshot(
                share_snapshot_id).status in ["available", "error"]):
            break
        else:
            time.sleep(3)


def wait_for_share_snapshot_is_deleted(openstack_client, share_snapshot_id):
    for attempt in range(120):
        try:
            openstack_client.shared_file_system.get_share_snapshot(
                share_snapshot_id)
            time.sleep(3)
        except openstack_exception.NotFoundException:
            break


@pytest.mark.parametrize(
    "new_share, openstack_client, user_type, clear_share_snapshot",
    [
        ("openstack_demo", "openstack_demo", "user", "openstack_demo"),
        ("openstack_admin", "openstack_admin", "admin", "openstack_admin"),
    ], indirect=["new_share", "openstack_client", "clear_share_snapshot"])
def test_create_share_snapshot(login, driver, config, new_share, user_type,
                               openstack_client, share_snapshot_name,
                               clear_share_snapshot):
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
    widgets.select_from_dropdown(actions_column, "Create Share Snapshot")
    share_snapshot_form = driver.find_element_by_css_selector(
        ".modal-content form")
    share_snapshot_form.find_element_by_id("id_name").send_keys(
        share_snapshot_name)
    share_snapshot_form.find_element_by_css_selector(
        ".btn-primary[value='Create Share Snapshot']").click()
    messages = widgets.get_and_dismiss_messages(driver, config)
    assert (f'Success: Creating share snapshot "{share_snapshot_name}".'
            in messages)
    assert any(snapshot.name == share_snapshot_name for snapshot in
               openstack_client.shared_file_system.share_snapshots())


@pytest.mark.parametrize(
    "new_share, new_share_snapshot, openstack_client, user_type",
    [
        ("openstack_demo", "openstack_demo", "openstack_demo", "user"),
        ("openstack_admin", "openstack_admin", "openstack_admin", "admin"),
    ], indirect=["new_share", "new_share_snapshot", "openstack_client"])
def test_delete_share_snapshot(login, driver, config, new_share_snapshot,
                               user_type, openstack_client,
                               share_snapshot_name):
    login(user_type)
    url = '/'.join((
        config.dashboard.dashboard_url,
        'project',
        'share_snapshots',
    ))
    driver.get(url)
    rows = driver.find_elements_by_css_selector(
        f"table#share_snapshots tr[data-display='{new_share_snapshot.name}']")
    assert len(rows) == 1
    actions_column = rows[0].find_element_by_css_selector("td.actions_column")
    widgets.select_from_dropdown(actions_column, "Delete Share Snapshot")
    widgets.confirm_modal(driver)
    messages = widgets.get_and_dismiss_messages(driver, config)
    assert (f"Success: Deleted Share Snapshot: {share_snapshot_name}"
            in messages)
    wait_for_share_snapshot_is_deleted(openstack_client, new_share_snapshot.id)
    assert not any(snapshot.name == share_snapshot_name for snapshot in
                   openstack_client.shared_file_system.share_snapshots())


@pytest.mark.parametrize(
    ("new_share, new_share_snapshot, openstack_client, "
     "user_type, clear_share_from_snapshot"),
    [
        ("openstack_demo", "openstack_demo", "openstack_demo",
         "user", "openstack_demo"),
        ("openstack_admin", "openstack_admin", "openstack_admin",
         "admin", "openstack_admin"),
    ], indirect=["new_share", "new_share_snapshot", "openstack_client",
                 "clear_share_from_snapshot"])
def test_create_share_from_snapshot(login, driver, config, new_share_snapshot,
                                    user_type, share_from_snapshot_name,
                                    share_snapshot_name, openstack_client,
                                    clear_share_from_snapshot):
    login(user_type)
    url = '/'.join((
        config.dashboard.dashboard_url,
        'project',
        'share_snapshots',
    ))
    driver.get(url)
    rows = driver.find_elements_by_css_selector(
        f"table#share_snapshots tr[data-display='{new_share_snapshot.name}']")
    assert len(rows) == 1
    actions_column = rows[0].find_element_by_css_selector("td.actions_column")
    widgets.select_from_dropdown(actions_column, "Create Share")
    share_snapshot_form = driver.find_element_by_css_selector(
        ".modal-content form")
    share_snapshot_form.find_element_by_id("id_name").clear()
    share_snapshot_form.find_element_by_id("id_name").send_keys(
        share_from_snapshot_name)
    share_snapshot_form.find_element_by_css_selector(
        ".btn-primary[value='Create']").click()
    messages = widgets.get_and_dismiss_messages(driver, config)
    assert f'Success: Creating share "{share_from_snapshot_name}"' in messages
    assert openstack_client.shared_file_system.find_share(
        share_from_snapshot_name) is not None
