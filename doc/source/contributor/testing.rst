=======
Testing
=======

Starting the app
----------------

If everything has gone according to plan, you should be able to run:

.. code-block:: console

   ./run_tests.sh --runserver 0.0.0.0:8080

and have the application start on port 8080. The horizon dashboard will
be located at http://localhost:8080/

Running unit tests
------------------

The unit tests can be executed directly from within this Manila UI plugin
project directory by using::

    $ cd ../manila-ui
    $ tox

This is made possible by the dependency in test-requirements.txt upon the
horizon source, which pulls down all of the horizon and openstack_dashboard
modules that the plugin uses.

To run only py27 unit tests, use following command::

    $ tox -e py27

To run only py34 unit tests, use following command::

    $ tox -e py34

To run unit tests using specific Django version use the following::

    $ tox -e py27dj17
    $ tox -e py27dj18
    $ tox -e py27dj19
    $ tox -e py27dj110
