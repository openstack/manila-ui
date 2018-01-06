============
New Features
============

When implementing a new feature, you may think about making it optional,
so it could be enabled or disabled in different deployments.

How to use it:

.. code-block:: python

    from django.conf import settings
    manila_config = getattr(settings, 'OPENSTACK_MANILA_FEATURES', {})
    manila_config.get('your_new_config_option', 'value_of_config_option')

See :doc:`/configuration/index` section for more configuration details.

It is also expected that each addition of new logic to Manila UI is covered by
unit tests.

Test modules should be located under "manila_ui/tests", satisfying
the following template when tests are written for a specific module:

.. code-block:: none

   manila_ui[/tests]/path/to/[test_]modulename.py

However, when testing the flow between different modules (using test app),
the tests can be added to a test module that can satisfy
the following template:

.. code-block:: none

   manila_ui[/tests]/path/to/directory/tests.py

Manila UI tests use the mock library for testing.
