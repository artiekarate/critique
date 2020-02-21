from requests.exceptions import ConnectionError, TooManyRedirects, Timeout, ReadTimeout
from requests import request
from logging import getLogger
from json import loads, dumps

logger = getLogger(__name__)


def ups_address_validation(city, state, zip_code, address1):
    """Returns 
    {'success': True, "canidates": [
        "city": city,
        "state": state,
        "zip_code": zip_code,
        "address1": "address1,
    ]} for successfull UPS queries 
    or
    {"success": False, "messages" []} with error message for unsucessful attempts.
    """

    # Check for no input values.
    if not city or not state or not zip_code or not address1:
        return {"success": False, "messages": ["Not all data submitted"]}

    # Convert data to string.
    try:
        city = str(city)
        state = str(zip_code)
        zip_code = str(zip_code)
        address1 = str(address1)
    except Exception:
        return {"success": False, "messages": ["Could not convert input to a string."]}

    payload = {
        "XAVRequest": {
            "AddressKeyFormat": {
                "AddressLine": [address1],
                "PoliticalDivision2": city,
                "PoliticalDivision1": state,
                "PostcodePrimaryLow": zip_code,
                "CountryCode": "US",
            }
        }
    }

    url = "https://onlinetools.ups.com/addressvalidation/v1/1?"

    headers = {
        "Content-Type": "application/json",
        "AccessLicenseNumber": "XXXXXXXXX",
        "Username": "XXXXXXXXX",
        "Password": "XXXXXXXXX",
    }

    try:
        ups = request(
            "POST",
            url,
            params=[
                ("regionalrequestIndicator", "true"),
                ("maximumcandidatelistsize", "5"),
            ],
            data=dumps(payload),
            headers=headers,
            timeout=2,
        )
    except ConnectionError:
        return {
            "success": False,
            "messages": [
                "Could not establish a connection to UPS Address Validation, please try again."
            ],
        }
    except ReadTimeout:
        return {
            "success": False,
            "messages": [
                "Connection to UPS Address Validation timedout, please try again."
            ],
        }
    except Timeout:
        return {
            "success": False,
            "messages": [
                "Connection to UPS Address Validation timedout, please try again."
            ],
        }

    # Parse response if a successfull API call is made.
    if ups.status_code == 200:
        try:
            ups = loads(ups.text)
        except ValueError:
            logger.exception(
                "Could not decode JSON response from successfull API attempt.",
                exc_info=True,
            )
            return {
                "success": True,
                "candidates": [],
            }

        # Return validated UPS Response.
        if "ValidAddressIndicator" in ups["XAVResponse"]:
            ups = ups["XAVResponse"]["Candidate"]["AddressKeyFormat"]

            return {
                "success": True,
                "candidates": [
                    {
                        "city": ups["PoliticalDivision2"],
                        "state": ups["PoliticalDivision1"],
                        "zip_code": ups["PostcodePrimaryLow"],
                        "address1": ups["AddressLine"],
                    }
                ],
            }

        # Return ambiguous candidates list.
        if "AmbiguousAddressIndicator" in ups["XAVResponse"]:
            candidates = []
            if isinstance(ups["XAVResponse"]["Candidate"], list):
                for candidate in ups["XAVResponse"]["Candidate"]:
                    candidates.append(
                        {
                            "city": candidate["AddressKeyFormat"]["PoliticalDivision2"],
                            "state": candidate["AddressKeyFormat"][
                                "PoliticalDivision1"
                            ],
                            "zip_code": candidate["AddressKeyFormat"][
                                "PostcodePrimaryLow"
                            ],
                            "address1": candidate["AddressKeyFormat"]["AddressLine"],
                        }
                    )
            else:
                candidate = ups["XAVResponse"]["Candidate"]["AddressKeyFormat"]
                candidates.append(
                    {
                        "city": candidate["PoliticalDivision2"],
                        "state": candidate["PoliticalDivision1"],
                        "zip_code": candidate["PostcodePrimaryLow"],
                        "address1": candidate["AddressLine"],
                    }
                )

            return {"success": True, "candidates": candidates}

        # Return validated UPS Response.
        if "NoCandidatesIndicator" in ups["XAVResponse"]:
            return {
                "success": True,
                "candidates": [],
            }

        # Return False, did not succesfully parse UPS response.
        logger.critical("Internal code, could not parse UPS response.")
        return {
            "success": False,
            "messages": ["Error parsing UPS response."],
        }

    # Return error message. Address cannot be validated, should call Customer Service.
    if ups.status_code == 400:
        ups = ups.json()
        if "response" in ups and "errors" in ups["response"]:
            return {"success": False, "messages": ups["response"]["errors"]}
        else:
            return {
                "success": False,
                "messages": ["Unknown"],
            }

    # Errors that are not the customers fault.
    error_codes = (
        (401, "Authentication error"),
        (404, "URL not found"),
        (405, "Method Not allowed"),
        (500, "Internatl Server Error"),
        (503, "Resource is Down"),
    )
    for error in error_codes:
        if error[0] == ups.status_code:
            logger.critical("{}, {}".format(error[0], error[1]))
            return {"success": False, "messages": [error[1]]}

    logger.critical("Unknown Error")
    return {"success": False, "messages": ["Unknown error"]}


if __name__ == "__main__":
    address = ups_address_validation(
        "Salt Lake City", "UT", "84108", "2600 Sunnyside Ave S"
    )
    print(address)
