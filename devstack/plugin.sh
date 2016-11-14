# plugin.sh - DevStack plugin.sh dispatch script manila-ui

function install_manila_ui {
    # NOTE(vponomaryov): workaround for devstack bug: 1540328
    # where devstack install 'test-requirements' but should not do it
    # for manila-ui project as it installs Horizon from url.
    # Remove following two 'mv' commands when mentioned bug is fixed.
    mv $MANILA_UI_DIR/test-requirements.txt $MANILA_UI_DIR/_test-requirements.txt

    setup_develop ${MANILA_UI_DIR}

    mv $MANILA_UI_DIR/_test-requirements.txt $MANILA_UI_DIR/test-requirements.txt
}

# check for service enabled
if is_service_enabled horizon && is_service_enabled manila && is_service_enabled manila-ui; then

    if [[ "$1" == "stack" && "$2" == "pre-install" ]]; then
        # Set up system services
        # no-op
        :
    elif [[ "$1" == "stack" && "$2" == "install" ]]; then
        # Perform installation of service source
        echo_summary "Installing Manila UI"
        install_manila_ui
    elif [[ "$1" == "stack" && "$2" == "post-config" ]]; then
        # Configure after the other layer 1 and 2 services have been configured
        echo_summary "Configuring Manila UI"
        cp -a ${MANILA_UI_DIR}/manila_ui/local/enabled/* ${DEST}/horizon/openstack_dashboard/local/enabled/
        cp -a ${MANILA_UI_DIR}/manila_ui/local/local_settings.d/* ${DEST}/horizon/openstack_dashboard/local/local_settings.d/
    elif [[ "$1" == "stack" && "$2" == "extra" ]]; then
        # no-op
        :
    fi

    if [[ "$1" == "unstack" ]]; then
        # no-op
        :
    fi

    if [[ "$1" == "clean" ]]; then
        # Remove state and transient data
        # Remember clean.sh first calls unstack.sh
        # no-op
        :
    fi
fi
