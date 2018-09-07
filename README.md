
# Using Google Home, Cloud Functions, Cloud Datastore, Maps Direction API, and Cloud KMS to get your kid ETA from school


## Create credentials

`gcloud kms keyrings create schoolbas --location global`
`gcloud kms keys create <child name> --location global --keyring schoolbas --purpose encryption`
`gcloud kms keys create maps-api --location global --keyring schoolbas --purpose encryption`
`pass=`echo -n <password> | base64``
`api=`echo -n <maps api key> | base64``

`curl -s -X POST "https://cloudkms.googleapis.com/v1/projects/[PROJECT_ID]/locations/global/keyRings/schoolbas/cryptoKeys/<yourchildname>:encrypt" \
-d "{\"plaintext\":\$pass}" \
  -H "Authorization:Bearer $(gcloud auth print-access-token)" \
  -H "Content-Type:application/json"`
  
   
`curl -s -X POST "https://cloudkms.googleapis.com/v1/projects/[PROJECT_ID]/locations/global/keyRings/schoolbas/cryptoKeys/maps-api:encrypt" \
-d "{\"plaintext\":\$api}" \
  -H "Authorization:Bearer $(gcloud auth print-access-token)" \
  -H "Content-Type:application/json"` 

##Deploy the cloud function
`gcloud functions deploy schoolbus --runtime python37 --trigger-http`

## DataStore 
Kind Config: maps_key - string
Kind  Cred: email,name,password  - string
Kind Home: address- string

## Actions

Create a zip form the Action directory and import it