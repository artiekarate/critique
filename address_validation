from requests.exceptions import ConnectionError, TooManyRedirects, Timeout, ReadTimeout
from requests import request
import json
import datetime
from traceback import format_exc
import logging


logger = logging.getLogger(__name__)


def ups_address_validation(city, state, zip_code, address1):
    """Returns a dictionay containing a UPS validated address, potential candidates for ambiguous matches 
    or a failure message."""

    if (
        not city or 
        not state or 
        not zip_code or 
        not address1):
        return {'success': False, 'messages': ["Not all data submitted"]}
    
    try:
        city = str(city)
        state = str(zip_code)
        zip_code = str(zip_code)
        address1 = str(address1)
    except Exception:
        return {'success': False, 'messages': ["Could not convert input to a string."]}
    
    payload = {
        "XAVRequest": {
            "AddressKeyFormat": {
                "AddressLine": [address1],
                "PoliticalDivision2": city,
                "PoliticalDivision1": state,
                "PostcodePrimaryLow": zip_code,
                "CountryCode": "US"
            }
        }
    }

    url = "https://onlinetools.ups.com/addressvalidation/v1/3?"

    headers = {
        'Content-Type': "application/json",
        'AccessLicenseNumber': "XXXXXXXXXX",
        "Username": "XXXXXXXXXX",
        "Password": "XXXXXXXXXX"
    }

    try:
        ups = request("POST", url, params=[('regionalrequestIndicator', 'true'), (
            'maximumcandidatelistsize', '1')], data=json.dumps(payload), headers=headers, timeout=2)
    except ConnectionError:
        return {'success': False, "messages": ["Could not establish a connection to UPS Address Validation, please try again."]}
    except ReadTimeout:
        return {'success': False, "messages": ["Connection to UPS Address Validation timedout, please try again."]}
    except Timeout:
        return {'success': False, "messages": ["Connection to UPS Address Validation timedout, please try again."]}

    # Parse response if a successfull API call is made.
    if ups.status_code == 200:
        ups = ups.json()
        
        # Return validated UPS Response.
        if 'ValidAddressIndicator' in ups['XAVResponse']:
            ups = ups['XAVResponse']['Candidate']['AddressKeyFormat']

            return {
                "success": True,
                'city': ups['PoliticalDivision2'],
                'state': ups['PoliticalDivision1'],
                'zip_code': ups['PostcodePrimaryLow'],
                'address1': ups["AddressLine"]
            }

        # Return ambiguous candidates list.
        if 'AmbiguousAddressIndicator' in ups['XAVResponse']:
            candidates = []
            if isinstance(ups['XAVResponse']['Candidate'], list):
                for candidate in ups['XAVResponse']['Candidate']:
                    candidates.append({
                        'city': candidate['AddressKeyFormat']['PoliticalDivision2'],
                        'state': candidate['AddressKeyFormat']['PoliticalDivision1'],
                        'zip_code': candidate['AddressKeyFormat']['PostcodePrimaryLow'],
                        'address1': candidate['AddressKeyFormat']["AddressLine"]
                    })
            else:
                candidate = ups['XAVResponse']['Candidate']
                candidates.append({
                    'city': candidate['AddressKeyFormat']['PoliticalDivision2'],
                    'state': candidate['AddressKeyFormat']['PoliticalDivision1'],
                    'zip_code': candidate['AddressKeyFormat']['PostcodePrimaryLow'],
                    'address1': candidate['AddressKeyFormat']["AddressLine"]
                })

            return {'success': "ambiguous", 'candidates': candidates}

        # Return False, No Candidates Found
        return {
            'success': False,
            'messages': [
                'UPS could not validate this address or offer a suggestion, please verify address and try again.'
            ]
        }

    # Return error message. Address cannot be validated, should call Customer Service.
    if ups.status_code == 400:
        ups = ups.json()
        if "response" in ups and 'errors' in ups['response']:
            return {'success': False, 'messages': ups['response']['errors']}
        else:
            return {'success': False, 'messages': ["UPS could not validate this shipping address"]}

    # Errors that are not the customers fault.
    if ups.status_code == 401:
        logger.critical(
            "UPS Validator authentication error. User bybased authentication for order and needs to be manually checked.")
        return {'success': "critical"}
    if ups.status_code == 404:
        logger.critical(
            "UPS Validator 404 error. URL not found. User bybased authentication for order and needs to be manually checked.")
        return {'success': "critical"}
    if ups.status_code == 405:
        logger.critical(
            "UPS Validator 405 error. Method not allowed. User bybased authentication for order and needs to be manually checked.")
        return {'success': "critical"}
    if ups.status_code == 500:
        logger.critical(
            "UPS Validator 500 error. UPS had an Internal Server Error. User bybased authentication for order and needs to be manually checked.")
        return {'success': "critical"}
    if ups.status_code == 503:
        logger.critical(
            "UPS Validator 503 error. Resource is down. User bybased authentication for order and needs to be manually checked.")
        return {'success': "critical"}

    logger.critical("Unknown Error")
    return {'success': "critical"}

if __name__ == "__main__":
    address = ups_address_validation(
        "Salt Lake City", "UT", "84108", "2600 Sunnyside Ave S")
    print(address)
