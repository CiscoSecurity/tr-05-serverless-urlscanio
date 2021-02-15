[![Gitter Chat](https://img.shields.io/badge/gitter-join%20chat-brightgreen.svg)](https://gitter.im/CiscoSecurity/Threat-Response "Gitter Chat")

# urlscan.io. URL and website sandbox Relay

Concrete Relay implementation using
[urlscan.io. URL and website sandbox](https://urlscan.io/)
as a third-party Cyber Threat Intelligence service provider.

The Relay itself is just a simple application written in Python that can be
easily packaged and deployed as an AWS Lambda Function using
[Zappa](https://github.com/Miserlou/Zappa).

## Rationale

We need an application that will translate API requests from SecureX Threat Response
to the third-party integration, and vice versa. This application is provided
here in the GitHub repository, and we are going to install it in AWS Lambda
using Zappa.

## Requirements Installation

First of all, make sure that you already have Python 3 installed by typing
```
python3 --version
```
in your command-line shell.

The application has been implemented and tested using `Python 3.7`. You may try
to use any higher versions if you wish as they should be backward-compatible.

After that, you have to create a "virtual environment" to isolate the
application-specific requirements from the libraries globally installed to your
system. Here are the steps to follow:

1. Create a virtual environment named `venv`:

   `python3 -m venv venv`

2. Activate the virtual environment:
   - Linux/Mac: `source venv/bin/activate`
   - Windows: `venv\Scripts\activate.bat`

3. Upgrade PIP (optional):

   `pip install --upgrade pip`

**NOTE**. The virtual environment has to be created only once, you just have
to make sure to activate it each time you are working on or playing with the
application (modern IDEs can automatically do that for you). You can deactivate
a previously activated virtual environment by simply typing `deactivate` in
your command-line shell.

Finally, install the libraries required for the application to function from
the [requirements.txt](code/requirements.txt) file:

```
pip install --upgrade --requirement requirements.txt
```

## Testing (Optional)

If you want to test the application you have to install a couple of extra
dependencies from the [test-requirements.txt](code/test-requirements.txt) file:
```
pip install --upgrade --requirement test-requirements.txt
```

You can perform two kinds of testing:

- Run static code analysis checking for any semantic discrepancies and
[PEP 8](https://www.python.org/dev/peps/pep-0008/) compliance:

  `flake8 .`

- Run the suite of unit tests and measure the code coverage:

  `coverage run --source api/ -m pytest --verbose tests/unit/ && coverage report`

If you want to test the live Lambda you may use any HTTP client (e.g. Postman),
just make sure to send requests to your Lambda's `URL` with the `Authorization`
header set to `Bearer <JWT>`.

**NOTE.** If you need input data for testing purposes you can use data from the
[observables.json](code/observables.json) file.

### Building the Docker Container
In order to build the application, we need to use a `Dockerfile`.  

 1. Open a terminal.  Build the container image using the `docker build` command.

```
docker build -t tr-05-serverless-urlscanio .
```

 2. Once the container is built, and an image is successfully created, start your container using the `docker run` command and specify the name of the image we have just created.  By default, the container will listen for HTTP requests using port 9090.

```
docker run -dp 9090:9090 --name tr-05-serverless-urlscanio tr-05-serverless-urlscanio
```

 3. Watch the container logs to ensure it starts correctly.

```
docker logs tr-05-serverless-urlscanio
```

 4. Once the container has started correctly, open your web browser to http://localhost:9090.  You should see a response from the container.

```
curl http://localhost:9090
```

## Implementation Details

### Implemented Relay Endpoints

- `POST /health`
  - Verifies the Authorization Bearer JWT and decodes it to restore the
  original credentials.
  - Authenticates to the underlying external service to check that the provided
  credentials are valid and the service is available at the moment.

- `POST /observe/observables`
  - Accepts a list of observables and filters out unsupported ones.
  - Verifies the Authorization Bearer JWT and decodes it to restore the
  original credentials.
  - Makes a series of requests to the underlying external service to query for
  some cyber threat intelligence data on each supported observable.
  - Maps the fetched data into appropriate CTIM entities.
  - Returns a list per each of the following CTIM entities (if any extracted):
    - `Judgement`,
    - `Sighting`,
    - `Indicator`,
    - `Relationship`.
    
- `POST /refer/observables`
  - Accepts a list of observables and filters out unsupported ones.
  - Builds a search link per each supported observable to pivot back to 
  the underlying external service and look up the observable there.
  - Returns a list of those links.
  
- `POST /respond/observables`
  - Accepts a list of observables and filters out unsupported ones.
  - Makes action objects for each observable.
  - Returns a list of those actions.
  
- `POST /respond/trigger`
  - Accepts an observable and filters if it's unsupported.
  - Builds a scan link to make scan action with this observable on urlscan.io.
  - Make scan request to urlscan.io using the link.
  - Returns a message `status: ok` if the scan was success or error message if not.

- `POST /version`
  - Returns the current version of the application.
  
### Supported Types of Observables

- `ip`
- `ipv6`
- `domain`
- `url`

### Supported Environment Variables

- `CTR_ENTITIES_LIMIT`
  - Restricts the maximum number of CTIM entities of each type returned in a
  single response per each requested observable.
  - Applies to the following CTIM entities:
    - `Judgement`,
    - `Sighting`.
  - Must be a positive integer. Defaults to `100` (if unset or incorrect).

## CTIM Mapping Specifics

The application uses data from `search` and `result` endpoints responses.

Each response from the urlscan.io API for the supported observables generates
the following CTIM entities:

- `Judgement` is based on `result.verdicts.overall.malicious` and `result.task`
- `Sighting` is based on `search.results[]`
- `Indicator` is based on `result.verticts.overall.categories[]` and `result.task`
- `Relationship` has a relationship type `Indicates` which connects
 `Indicator` with its `Sighting` 
