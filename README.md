# TSN FrontEnd

**TSN front-end for Network Application developers.**

The TSN FrontEnd allows the configuration of certain parameters in the underlying TSN infrastructure
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

The TSN FrontEnd can work without a real TSN backend. This is the default configuration (no value specified for `BackEnd` in
`config.json`), however, in this case the TSN FrontEnd will only accept best-effort requests. This is, the following payload:

```
{"identifier": <identifier>, "profile": "best_effort", "overrides": {}}
```

Any other request will result in a 400 error with the following detail message: `"Requested profile or overrides are
not supported"`. To enable a backend, specify the URL where the TSN backend is listening on `config.json`.

### CAPIF integration

The TSN FrontEnd can optionally work with CAPIF, both for publishing the API and for securing access to the endpoints. This
behavior is controlled by the `Enabled` and `SecurityEnabled` entries in the `CAPIF` section of `config.json`. These
two settings are set to `true` by default.

> By default, this configuration points to the `capifcore` domain, which is also the default for CAPIF deployments.
> Unless the CAPIF domain can be resolved by external DNS, this value should be configured on the `hosts` file of the
> machine:
> 
> ```capifcore    <CAPIF IP address>```

Upon a successful publishing process, the following file will be created `capif_data/publisherDetails.txt`. This
file contains the username and password used during the registration (randomly generated) and the host and port
configured for the FrontEnd. In the case of a Docker deployment, this file can be checked using the following command
in the host machine:

```
docker exec TSN_FrontEnd bash -c "cat ./capif_data/publisherDetails.txt"
```

If the publishing process was unsuccessful this command will return a `No such file or directory` error.

When `SecurityEnabled` is set to `true`, every request sent to the API endpoints must include a valid `Authentication`
header, with the Bearer provided by CAPIF.

> If this setting is enabled, but for some reason the TSN FrontEnd was not able to register the API through CAPIF, or to
> retrieve the CAPIF public key, the server will immediately abort the execution.

## Deployment

### Docker container

This repository contains 3 files (`Dockerfile`, `build.sh`, `run.sh`) prepared for supporting the deployment of the
TSF FrontEnd as a Docker container. The deployment procedure is as follows:

1. Clone this repository. The environment must already have an installation of Docker (tested on version 20.10.7).
2. Include any necessary profile information in the `Profiles` sub-folder. `Profiles/sample` can be used as a guide.
Profiles must have the `yml` extension to be read by the TSN FrontEnd.
3. Edit the contents of `config.json` if necessary. By default:
     - The TSN FrontEnd works on backend-less mode.
     - The frontend is configured localhost:8899
     - CAPIF is configured in the `capifcore` domain, with ports 8080 (HTTP) and 443 (HTTPS)
4. Execute `build.sh`. This file will prepare a Docker image (tagged `tsn_frontend`).
5. Execute `run.sh`. This will create a new container (named `TSN_FrontEnd`) based on the previously generated image.

> Note that the build process will create a copy of the files in the `Profiles` sub-folder and `config.json`. If these
> files are edited after the creation of the image, this process (starting from step 4) must be executed again.
> To ensure that the changes are reflected, remove the existing container before the build
> (`docker stop TSN_FrontEnd && docker rm TSN_FrontEnd`)

### Local deployment

The TSN FrontEnd can be deployed directly in a host machine. The procedure is as follows.

1. Clone this repository and navigate to the containing folder. The environment must already be able to run Python
(3.10) code.
2. Follow steps (2) and (3) of the Docker deployment guide in order to configure the TSN FrontEnd.
3. Create a separate virtual environment: `python -m venv ./venv`
4. Activate the virtual environment: `source ./venv/bin/activate`
5. Install the required libraries: `pip install -r requirements.txt`
6. Start the server: `flask run --host <HOST>> --port <PORT>`. When exposing the frontend through CAPIF, make sure
that the values for `<HOST>` and `<PORT>` match those configured in `config.json`

> Changes made to the `Profiles` folder and `config.json` will be reflected in the TSN FrontEnd after restarting the server.
>
> In order to force a new CAPIF publishing process, manually delete the `capif_data/publisherDetails.txt` file
> previously generated.

## Endpoints

### [GET] `/tsn/api/v1/profile`

Returns a list of supported profiles, with the format:

```
{"profiles": ["<profile1>", "<profile2>", ..., "best_effort"]}
```

> Note that "best_effort" is always included.

### [GET] `/tsn/api/v1/profile?name=<profile_name>`

Returns the default configuration values for `profile_name`, with the format:

```
{"<profile_name>": {"<parameter1>": <value1>, "<parameter2>": <value2>, ...}}
```

### [POST] `/tsn/api/v1/apply`

Applies the specified configuration to the selected traffic identifier. The endpoint expects to receive a payload with
the format:

```
{"identifier": <identifier>, "profile": <profile>, "overrides": <overrides>}
```

Where:

- `identifier`: A unique identifier for the configuration.
- `profile`: Name of the profile to use. The values in this profile will be used as default, when not overriden.
- `overrides`: A dictionary of values that will be overriden from the used profile. May be empty.

If any of these values is missing from the payload, the endpoint reply will detail the missing values.

In case of success, the TSN FrontEnd will create and apply a configuration for the selected `identifier`, by merging the
values in the profile and `overrides`. Then, will reply with the following payload (status 200):

```
{"message": "Success", "token": "<token>"}
```

Where `token` is a randomly generated value that is used to secure the usage of the `/clear` endpoint.

In case of failure, the TSN FrontEnd will reply with the following payload (status 400):

```
{"message": ["Bad Request"|"Request Failed"], "detail": "<detailed_error_explanation>"}
```

### [POST] `/tsn/api/v1/clear`

Disables the configuration applied by a previous usage of `/apply`, for the selected `identifier`. The endpoint
expects to receive a payload with the format:

```
{"identifier": <identifier>, "token": <token>}
```

Where:

- `identifier`: Identifier of the configuration.
- `token`: Random value returned by the `/apply` call used to configure `identifier`. Used to avoid misuse of `/clear`
by unrelated parties.

In case of success, the endpoint will return the following payload (status 200):

```
{"message": "Configuration '<identifier>' successfully removed"}
```

In case of failure, the TSN FrontEnd will reply with the following payload (status 400):

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