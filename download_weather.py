#!/usr/bin/env python
"""
Weather API Python sample code

Copyright 2019 Oath Inc. Licensed under the terms of the zLib license see https://opensource.org/licenses/Zlib for terms.

$ python --version
Python 2.7.10

"""
import json
import os
import time, uuid, urllib, urllib2
import hmac, hashlib
from base64 import b64encode


def download_to_json_file():
    """
    Basic info
    """
    url = 'https://weather-ydn-yql.media.yahoo.com/forecastrss'
    method = 'GET'
    app_id = os.environ.get('YAHOO_APP_ID')
    consumer_key = os.environ.get('YAHOO_CLIENT_ID')
    consumer_secret = os.environ.get('YAHOO_CLIENT_SECRET')
    concat = '&'
    query = {'location': 'madison,wi', 'format': 'json'}
    oauth = {
        'oauth_consumer_key': consumer_key,
        'oauth_nonce': uuid.uuid4().hex,
        'oauth_signature_method': 'HMAC-SHA1',
        'oauth_timestamp': str(int(time.time())),
        'oauth_version': '1.0'
    }

    """
    Prepare signature string (merge all params and SORT them)
    """
    merged_params = query.copy()
    merged_params.update(oauth)
    try:
        sorted_params = [k + '=' + urllib.quote(merged_params[k], safe='') for k in sorted(merged_params.keys())]
        signature_base_str =  method + concat + urllib.quote(url, safe='') + concat + urllib.quote(concat.join(sorted_params), safe='')
    except:
        print(json.dumps(merged_params, indent=2))
#        print(json.dumps(sorted_params, indent=2))
        raise

    """
    Generate signature
    """
    composite_key = urllib.quote(consumer_secret, safe='') + concat
    oauth_signature = b64encode(hmac.new(composite_key, signature_base_str, hashlib.sha1).digest())

    """
    Prepare Authorization header
    """
    oauth['oauth_signature'] = oauth_signature
    auth_header = 'OAuth ' + ', '.join(['{}="{}"'.format(k,v) for k,v in oauth.iteritems()])

    """
    Send request
    """
    url = url + '?' + urllib.urlencode(query)
    request = urllib2.Request(url)
    request.add_header('Authorization', auth_header)
    request.add_header('Yahoo-App-Id', app_id)
    response = urllib2.urlopen(request).read()
    with open("/home/ed/.cache/weather.json", "w") as weather_file:
        json.dump(json.loads(response), weather_file, indent=2)


if __name__ == "__main__":
    download_to_json_file()
    

