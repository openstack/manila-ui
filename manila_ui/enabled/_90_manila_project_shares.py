PANEL_DASHBOARD = 'project'
PANEL_GROUP = 'compute'
PANEL = 'shares'
ADD_PANEL = 'manila_ui.dashboards.project.shares.panel.Shares'
# ADD_INSTALLED_APPS enables using html templates from within the plugin
ADD_INSTALLED_APPS = ['manila_ui.dashboards.project']
UPDATE_HORIZON_CONFIG = {
    'customization_module': 'manila_ui.overrides',
}
