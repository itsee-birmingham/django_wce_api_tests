# The API Tests App

These tests focus on the server side implementation of the API. There are no tests for the JavaScript code.

As this app is only used for testing it should not be listed in the installed apps for the general application.
Instead it should be installed only when the tests are being run.

One way to achieve this in the Django settings is as follows:

```python

import sys

if 'test' in sys.argv:
    TESTING = True
else:
    TESTING = False

INSTALLED_APPS = [
                # list of all regular apps to install
                ]

if TESTING:
    INSTALLED_APPS.append('api_tests.apps.ApitestsConfig')

```

To run the tests in the main Django application run:

```bash
python manage.py test api_tests
```

## The Test Models

As the API app itself has no data models this app defines its own models for the specific purpose of testing the API.
This approach avoids introducing a dependency just for the sake of running tests.

The models are based on the scenario of a publishing firm (often a little contrived to generate the required testing
scenarios). They include models such as author, editor, work, review, decision and publication plan.

## License

This app is licensed under the GNU General Public License v3.0.

## Acknowledgments

The software was created by Catherine Smith at the Institute for Textual Scholarship and Electronic Editing (ITSEE) in
the University of Birmingham. It is based on a suite of tools developed for and supported by the following research
projects:

- The Workspace for Collaborative Editing (AHRC/DFG collaborative project 2010-2013)
- COMPAUL (funded by the European Union 7th Framework Programme under grant agreement 283302, 2011-2016)
- MUYA (funded by the European Union Horizon 2020 Research and Innovation Programme under grant agreement 694612, 2016-2022)
- CATENA (funded by the European Union Horizon 2020 Research and Innovation Programme under grant agreement 770816, 2018-2023)
