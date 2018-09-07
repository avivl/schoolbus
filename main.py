import datetime
import os
import base64

import googlemaps
from google.cloud import datastore
from pyicloud import PyiCloudService
import googleapiclient.discovery

def decrypt(project_id, location_id, key_ring_id, crypto_key_id,ciphertext):
    # Creates an API client for the KMS API.
    kms_client = googleapiclient.discovery.build('cloudkms', 'v1',cache=False, cache_discovery=False)

    # The resource name of the CryptoKey.
    name = 'projects/{}/locations/{}/keyRings/{}/cryptoKeys/{}'.format(
        project_id, location_id, key_ring_id, crypto_key_id)

    # Use the KMS API to decrypt the data.
    crypto_keys = kms_client.projects().locations().keyRings().cryptoKeys()
    request = crypto_keys.decrypt(
        name=name,
        body={'ciphertext': ciphertext})
    response = request.execute()
    plaintext = base64.b64decode(response['plaintext'].encode('ascii'))
    return plaintext

def schoolbus(request):
    """HTTP Cloud Function.
    """

    request_json = request.get_json()
    if request_json:
        Name = request_json['queryResult']['parameters']['name']
    else:
        body = '{"fulfillmentText":"%s"}' % "Can't find child name in request"
        return body
    datastore_client = datastore.Client()
    query = datastore_client.query(kind='Cred')
    cred = list(query.fetch())
    found = False
    if len(cred) > 0:
        for c in cred:
            if c['name'].lower() == Name.lower():
                user_mail = c['email']
                password = c['password']
                found = True
    if not found:
        body = '{"fulfillmentText":"%s"}' % "Can't find child name in database"
        return body
    project_id = os.environ['GCP_PROJECT']
    password = decrypt(project_id,'global','schoolbas',Name.lower(),password)
    query = datastore_client.query(kind='Home')
    home = list(query.fetch())
    query = datastore_client.query(kind='Config')
    config = list(query.fetch())
    api = PyiCloudService(user_mail, password.decode("utf-8") )
    location = api.iphone.location()

    if location['isOld']:
        fulfillment_text = "Can't get an accurate location for %s" % Name
        body = '{"fulfillmentText":"%s"}' % fulfillment_text
        return body

    key = decrypt(project_id, 'global', 'schoolbas', 'maps-api', config[0]['maps_key'])
    gmaps = googlemaps.Client(key = key.decode("utf-8") )
    reverse_geocode_result = gmaps.reverse_geocode(
        (location['latitude'], location['longitude']))
    now = datetime.datetime.now()
    directions_result = gmaps.directions(
        reverse_geocode_result[0]['formatted_address'],
        home[0]['address'],
        mode="driving",
        departure_time=now)
    fulfillment_text = Name + " will be home in %s" % \
                       directions_result[0]['legs'][0]['duration_in_traffic'][
                           'text']
    body = '{"fulfillmentText":"%s"}' % fulfillment_text
    return body

