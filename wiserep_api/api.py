import requests


def get_response(url):
    """Obtains the response from a given Wiserep URL.

    Parameters
    ----------
    url: str
        Wiserep URL.

    Returns
    -------
    response: requests.Response
        Response object.
    """
    # ID of your Bot:
    YOUR_BOT_ID = 1234
    # name of your Bot:
    YOUR_BOT_NAME = "My_Bot1"
    # API key of your Bot:
    api_key = "604d60d302f86eb38fd1407abe41d05b438043bd"

    headers = {
        "User-Agent": 'tns_marker{"tns_id":' + str(YOUR_BOT_ID) + ', "type":"bot",'
        ' "name":"' + YOUR_BOT_NAME + '"}'
    }

    http_errors = {
        304: "Error 304: Not Modified: There was no new data to return.",
        400: "Error 400: Bad Request: The request was invalid. "
        "An accompanying error message will explain why.",
        403: "Error 403: Forbidden: The request is understood, but it has "
        "been refused. An accompanying error message will explain why.",
        404: "Error 404: Not Found: The URI requested is invalid or the "
        "resource requested, such as a category, does not exists.",
        500: "Error 500: Internal Server Error: Something is broken.",
        503: "Error 503: Service Unavailable.",
    }

    ###############################################################
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response
    else:
        print('Response error:', http_errors[response.status_code])
        print(url)
        return None


def get_object_id(iau_name, verbose=False):
    """Obtains the objects's Wiserep ID.

    Parameters
    ----------
    iau_name: str
        IAU name of the target (e.g. 2020xne).
    verbose: bool, default 'False'
        If True, print some of the intermediate information

    Returns
    -------
    obj_id: str
        The object's Wiserep ID. Returns 'Unknown' if not found
        or None if there is a problem of some other kind.
    """
    # look for the target ID in the search webpage
    wiserep_search_url = "https://www.wiserep.org/search?"
    search_name = iau_name.replace('+', '%2B')  # is this an html thing?
    target_search_url = wiserep_search_url + f'name={search_name}&name_like=1'
    response = get_response(target_search_url)
    if response is None:
        print(f'Could not load the webpage of {iau_name}')
        return None

    obj_id = None
    split_text = response.text.split('="Click to Object page">')
    for st in split_text:
        if f'{iau_name}<' in st:
            if 'href="/object/' in st:
                obj_id = st.split('href="/object/')[1].split('"')[0]
                break
            
    if verbose:
        print("Object ID (Wiserep):", obj_id)

    if obj_id is None:
        print(f"No target with this name found on Wiserep: {iau_name}")
    
    return obj_id
