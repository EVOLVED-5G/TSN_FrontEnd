# TSN Application Function

TSN front-end for Network Application developers.

## Endpoints

### [GET] `/profiles`

Returns a list of supported profiles, with the format:

```
{"profiles": ["<profile1>", "<profile2>", ..., "best_effort"]}
```

> Note that "best_effort" is always included.

### [GET] `/profiles?name=<profile_name>`

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