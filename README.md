# Redwing Vector Sandbox Installation
To obtain a software license please visit https://redwing.ai/plans

Once license is emailed to you alongside customer id, add these as environment variables.

# Set env vars

```
export LICENSE_KEY=[your_license_key]
export CUSTOMER_ID=[your_customer_id]
```

Pull and compose the Vector docker image, this will start up the server up to the number of cores that are enabled in your software license.

```
docker pull helloredwing/vector && docker-compose up
```

For help or questions please reach out to hello [at] redwing.ai

