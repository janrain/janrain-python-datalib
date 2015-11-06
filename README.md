Janrain Capture Data Library
============================

A library for working with Janrain Capture applications.


Overview
--------

The objects in this package reflect the components in a Capture application.
App is the top-level object and contains the `apicall` method for speaking to
Capture. Other objects should be fetched via the App object - they each will
have a reference to the parent App object.


Docs
----

Friendly api docs can be generated with Sphinx.

Install Sphinx if it is not installed yet:

    pip install sphinx --user

Build the docs:

    cd docs; make html

The docs will be in `docs/_build/html`


Tests
-----

To run the tests:

    setup.py test


Examples
--------

Make an App object:

    import janrain_datalib
    app = janrain_datalib.get_app(app_uri, client_id, client_secret)

Add a client setting:

    client = app.get_client(client_id)
    updated = client.settings.set(setting_key, setting_value)

Create a new schema:

    schema = app.get_schema(new_schema_name)
    schema.create(attr_defs_list)

Retrieve all records in a schema:

    for record in schema.records.iterator(batch_size=1000):
        uuid = record['uuid']

Update a specific record:

    record = schema.records.get_record(uuid)
    record.update({'email':'test@test.test'})
