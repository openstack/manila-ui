=============================================
Manila UI Selenium Integration Tests (pytest)
=============================================

Browser tests against a live Horizon dashboard with the Manila UI plugin.

-----------------------------
Running the integration tests
-----------------------------

#. Required: tox and a live OpenStack deployment with Horizon, Manila,
   and manila-ui enabled.
   Firefox and geckodriver are not needed on PATH.
   Selenium can download/cache them under ``~/.cache/selenium/``
   (first run may need network).

#. Config: Uncomment and set values in
   ``manila_ui/tests/selenium/horizon.conf``
   only when you must override the dashboard URL, the auth URL,
   or other parameters. Leave it commented for default/CI behavior.

#. Run (from the root repository): ::

      $ tox -e manila-ui-integration-pytest

   Run a subset: ::

      $ tox -e manila-ui-integration-pytest -- -k share_groups
