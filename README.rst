roughrider.application
**********************

Base WSGI application using ``horseman`` nodes with routing capabilities.


Example
=======

Below is an example of an application, handling a GET request on '/'
and returning a JSON response.


.. code-block:: python

from horseman.response import Response
from roughrider.application import Application

app = Application()

@app.routes.register('/')
def json(request):
    return Response.to_json(body={'message': "Hello, world!"})
