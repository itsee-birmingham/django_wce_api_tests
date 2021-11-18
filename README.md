# The API Tests App

These tests focus on the server side implementation of the API. There are no tests for the JavaScript code.

To run the tests in the main Django application run:

```python manage.py test api_tests```


## The Test Models

As the API app itself has no data models this app defines its own models for the specific purpose of testing the API.
This approach avoids introducing a dependency just for the sake of running tests.

The models are based on the scenario of a publishing firm (often a little contrived to generate the required testing
scenarios). They include models such as author, editor, work, review, decision and publication plan.
