# Box API

## Overview

We use the Stanford Medicine Box to store Protected Health Information (PHI).
To access this data, you will need the appropriate credentials. Ask Jonathan.
Once you have credentials, you can use the Box API to query data via the
`BoxClient`.

## Box API Access

Use a `stanford.edu` email address to access the Box
![Developer Console](https://stanfordmedicine.app.box.com/developers/console/).

Use the Console interface to create a new app (e.g. `HealthRex`) and set the
authentication method to Standard OAuth 2.0.

To access Box via the API, you will need:
1. Client ID (in the console under Configuration > OAuth 2.0 Credentials)
2. Client Secret (in the console under Configuration > OAuth 2.0 Credentials)
3. Access Token (in the console under Configuration > Developer Token)
4. Box STRIDE Folder ID (48947257871)

Copy these values into `LocalEnv.py`.
