============================
So You Want to Contribute...
============================

For general information on contributing to OpenStack, please check out the
`contributor guide <https://docs.openstack.org/contributors/>`_ to get started.
It covers all the basics that are common to all OpenStack projects: the
accounts you need, the basics of interacting with our Gerrit review system,
how we communicate as a community, etc.

This project contains a plug-in to the OpenStack Dashboard (Horizon). It
adds functionality to the OpenStack Dashboard to interact with `Manila
<https://opendev.org/openstack/manila>`_, the OpenStack Shared File Systems
service. Refer to the `Contributor guide for Manila
<https://docs.openstack.org/manila/latest/contributor/contributing.html>`_
for information regarding the team's task trackers, communicating with other
project developers and contacting the core team.

See :doc:`development-environment` for details about how to bootstrap a
development environment and test manila-ui.

Bugs
~~~~

You found an issue and want to make sure we are aware of it? You can do so on
`Launchpad <https://bugs.launchpad.net/manila-ui>`_.

If you're looking to contribute, search for the `low-hanging-fruit`_ tag to
see issues that are easier to get started with.

.. _project-structure:


Project Structure
~~~~~~~~~~~~~~~~~

This project includes two dashboard components:

- `administrator dashboard`_
- `user dashboard`_

The administrator dashboard extends the OpenStack Dashboard's administrator
interface by adding ``Share`` (short for ``Shared File Systems``) functionality
to manage Share and Share Group Types, Share servers and other
`administrator-only` components of the Shared File System service. It also
extends the functionality of the Identity service to allow controlling
Shared File System service quotas.

The User dashboard provides all user facing functionality.

.. _low-hanging-fruit: https://bugs.launchpad.net/manila-ui/+bugs?field.tag=low-hanging-fruit
.. _administrator dashboard: https://opendev.org/openstack/manila-ui/src/branch/master/manila_ui/dashboards/admin
.. _user dashboard: https://opendev.org/openstack/manila-ui/src/branch/master/manila_ui/dashboards/project
