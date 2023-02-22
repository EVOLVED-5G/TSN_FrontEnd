# TSN Application Function

**TSN front-end for Network Application developers.**

The TSN Application Function allows the configuration of certain parameters in the underlying TSN infrastructure
of the testbed. These parameters indicate the expected QoS of the communication. The following parameters can
be configured, either as part of a Profile, or as values in the `overrides` dictionaries:

The following values specify the expected (SLA) KPIs:
  - `delay`: float (ms). Maximum value
  - `jitter`: float (ms). Maximum value
  - `throughput`: float (Mbps). Minimum value
  - `packet_loss`: float (percent). Maximum value

The following values specify the traffic type:
  - `periodicity`: 'periodic' or 'sporadic'
  - `period`: float (ms)
  - `data_size`: integer (bytes)
  - `critical`: boolean

The following table can be used as reference for the `period` and `periodicity` values, depending on the kind of
traffic:

| Traffic type                        | Periodic/Sporadic | Typical period         |
|-------------------------------------|-------------------|------------------------|
| Isochronous                         | periodic          | 0.1ms ~ 2ms            |
| Cyclic - Synchronous                | periodic          | 0.5ms ~ 1ms            |
| Cyclic - Asynchronous               | periodic          | 2ms ~ 20ms             |
| Events: Control                     | sporadic          | 10ms ~ 50 ms           |
| Events: alarm and operator commands | sporadic          | 2s                     |
| Events: Network control             | periodic          | 50ms ~ 1s              |
| Configuration and diagnostics       | sporadic          | n.a.                   |
| Video/Audio/Voice                   | periodic          | Frame Rate/Sample Rate |
| Best Effort                         | sporadic          | n.a.                   |

### TSN backend

The TSN AF can work without a real TSN backend. This is the default configuration (no value specified for `BackEnd` in
`config.yml`), however, in this case the TSN AF will only accept best-effort requests. This is, the following payload:

```
{"identifier": <identifier>, "profile": "best_effort", "overrides": {}}
```

Any other request will result in a 400 error with the following detail message: `"Requested profile or overrides are
not supported"`. To enable a backend, specify the URL where the TSN backend is listening on `config.yml`.

### CAPIF integration

The TSN AF can work without CAPIF, however, it will try to publish the API on every start-up. The TSN AF looks for
CAPIF on the `capifcore` domain, so this value should be configured on the `hosts` file of the machine:

```capifcore    <CAPIF IP address>```

Upon a successful publishing process, the following file will be created `capif_data/publisherDetails.txt`. This
file contains the user name and password used during the registration (randomly generated). In the case of a Docker
deployment, this file can be check using the following command:

```
docker exec TSN_AF bash -c "cat ./capif_data/publisherDetails.txt"
```

If the publishing process was unsuccessful this command will return a `No such file or directory` error

## Deployment

### Docker container

This repository contains 3 files (`Dockerfile`, `build.sh`, `run.sh`) prepared for supporting the deployment of the
TSF AF as a Docker container. The deployment procedure is as follows:

1. Clone this repository. The environment must already have an installation of Docker (tested on version 20.10.7).
2. Include any necessary profile information in the `Profiles` sub-folder. `Profiles/sample` can be used as a guide.
3. Edit the contents of `config.yml` if necessary. By default, the TSN_AF works on backend-less mode.
4. Execute `build.sh`. This file will prepare a Docker image (tagged `tsn_af`).
5. Execute `run.sh`. This will create a new container (named `TSN_AF`) based on the previously generated image. By
default, the TSN AF will listen on port 8899.

> Note that the build process will create a copy of the files in the `Profiles` sub-folder and `config.yml`. If these
> files are edited after the creation of the image, this process (starting from step 4) must be executed again.
> To ensure that the changes are reflected, remove the existing container before the build
> (`docker stop TSN_AF && docker rm TSN_AF`)

### Local deployment

The TSN AF can be deployed directly in a host machine. The procedure is as follows.

1. Clone this repository and navigate to the containing folder. The environment must already be able to run Python
(3.10) code.
2. Create a separate virtual environment: `python -m venv ./venv`
3. Activate the virtual environment: `source ./venv/bin/activate`
4. Install the required libraries: `pip install -r requirements.txt`
5. Start the server: `flask run --host 0.0.0.0 --port 8899`. Other parameters can be set, but when using CAPIF these
are the interface details.

> Changes made to the `Profiles` folder and `config.yml` will be reflected in the TSN AF after restarting the server

## Endpoints

### [GET] `/profile`

Returns a list of supported profiles, with the format:

```
{"profiles": ["<profile1>", "<profile2>", ..., "best_effort"]}
```

> Note that "best_effort" is always included.

### [GET] `/profile?name=<profile_name>`

Returns the default configuration values for `profile_name`, with the format:

```
{"<profile_name>": {"<parameter1>": <value1>, "<parameter2>": <value2>, ...}}
```

### [POST] `/apply`

Applies the specified configuration to the selected traffic identifier. The endpoint expects to receive a payload with
the format:

```
{"identifier": <identifier>, "profile": <profile>, "overrides": <overrides>}
```

Where:

- `identifier`: Identifier of the packets that will be configured.
- `profile`: Name of the profile to use. The values in this profile will be used as default, when not overriden.
- `overrides`: A dictionary of values that will be overriden from the used profile. May be empty.

If any of these values is missing from the payload, the endpoint reply will detail the missing values.

In case of success, the TSN AF will create and apply a configuration for the selected `identifier`, by merging the
values in the profile and `overrides`. Then, will reply with the following payload (status 200):

```
{"message": "Success", "token": "<token>"}
```

Where `token` is a randomly generated value that is used to secure the usage of the `/clear` endpoint.

In case of failure, the TSN AF will reply with the following payload (status 400):

```
{"message": ["Bad Request"|"Request Failed"], "detail": "<detailed_error_explanation>"}
```

### [POST] `/clear`

Disables the configuration applied by a previous usage of `/apply`, for the selected traffic `identifier`. The endpoint
expects to receive a payload with the format:

```
{"identifier": <identifier>, "token": <token>}
```

Where:

- `identifier`: Identifier of the packets that will be configured.
- `token`: Random value returned by the `/apply` call used to configure `identifier`. Used to avoid misuse of `/clear`
by unrelated parties.

In case of success, the endpoint will return the following payload (status 200):

```
{"message": "Configuration '<identifier>' successfully removed"}
```

In case of failure, the TSN AF will reply with the following payload (status 400):

```
{"message": ["Bad Request"|"Request Failed"], "detail": "<detailed_error_explanation>"}
```


## Authors

* **[Bruno Garcia Garcia](https://github.com/NaniteBased)**

## License

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   > <http://www.apache.org/licenses/LICENSE-2.0>

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.