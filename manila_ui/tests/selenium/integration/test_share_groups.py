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


from openstack_dashboard.test.selenium import widgets
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select


@pytest.mark.parametrize(
    "openstack_client, user_type, clear_share_group",
    [
        ("openstack_demo", "user", "openstack_demo"),
        ("openstack_admin", "admin", "openstack_admin"),
    ], indirect=["openstack_client", "clear_share_group"])
def test_create_share_group(login, driver, config, user_type,
                            openstack_client, share_group_name,
                            clear_share_group):
    login(user_type)
    url = '/'.join((
        config.dashboard.dashboard_url,
        'project',
        'share_groups',
    ))
    driver.get(url)
    driver.find_element(By.LINK_TEXT, "Create Share Group").click()
    share_group_form = driver.find_element(
        By.CSS_SELECTOR, ".modal-content form")
    share_group_form.find_element(By.ID, "id_name").send_keys(
        share_group_name)
    select_sgt_element = share_group_form.find_element(By.ID, "id_sgt")
    Select(select_sgt_element).select_by_visible_text('default')
    select_sst_element = share_group_form.find_element(
        By.CSS_SELECTOR, "[id^='id_share-type']")
    Select(select_sst_element).select_by_visible_text('default')
    share_group_form.find_element(
        By.CSS_SELECTOR, ".btn-primary[value='Create']").click()
    messages = widgets.get_and_dismiss_messages(driver, config)
    assert f'Success: Creating share group "{share_group_name}"' in messages
    assert openstack_client.shared_file_system.find_share_group(
        share_group_name) is not None


@pytest.mark.parametrize(
    "openstack_client, user_type, new_share_group",
    [
        ("openstack_demo", "user", "openstack_demo"),
        ("openstack_admin", "admin", "openstack_admin"),
    ], indirect=["openstack_client", "new_share_group"])
def test_delete_share_group(login, driver, config, user_type,
                            openstack_client, new_share_group):
    login(user_type)
    url = '/'.join((
        config.dashboard.dashboard_url,
        'project',
        'share_groups',
    ))
    driver.get(url)
    rows = driver.find_elements(
        By.CSS_SELECTOR,
        f"table#share_groups tr[data-display='{new_share_group.id}']")
    assert len(rows) == 1
    actions_column = rows[0].find_element(By.CSS_SELECTOR, "td.actions_column")
    widgets.select_from_dropdown(actions_column, "Delete Share Group")
    widgets.confirm_modal(driver)
    messages = widgets.get_and_dismiss_messages(driver, config)
    assert f"Success: Deleted Share Group: {new_share_group.id}" in messages
    assert openstack_client.shared_file_system.find_share_group(
        new_share_group.name) is None
