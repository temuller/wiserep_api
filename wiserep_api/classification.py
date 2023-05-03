from wiserep_api.api import get_response, get_object_id


def get_target_class(iau_name, verbose=False):
    """Obtains the target's classification (type) from Wiserep.

    Parameters
    ----------
    iau_name: str
        IAU name of the target (e.g. 2020xne).
    verbose: bool, default 'False'
        If True, print some of the intermediate information

    Returns
    -------
    target_class: str
        The target's classification. Returns 'Unknown' if not found.
    """
    # look for the target ID in the search webpage
    obj_id = get_object_id(iau_name, verbose)
    if (obj_id is None) or (obj_id == "Unknown"):
        return obj_id

    # target's webpage
    target_url = f"https://www.wiserep.org/object/{obj_id}"
    response = get_response(target_url)
    if response is None:
        return None

    # search for classification
    split_text = response.text.split('Type</span><div class="value"><b>')
    if len(split_text) > 1:
        # look for classification under "Type" parameter
        target_class = split_text[1].split("<")[0]
        if target_class != "SN":
            return target_class

    # look for classifications in TNS reports at the bottom of the webpage
    table = response.text.split("\n <thead><tr>")[-1]
    simply_a_SN = False
    for row in table.split('<td class="cell-objtype_name">'):
        target_class = row.split("<")[0]
        if len(target_class) > 0 and target_class != "SN":
            return target_class

        if target_class == "SN":
            simply_a_SN = True

    if simply_a_SN is True:
        # Some objects just have the classification as "SN"
        return "SN"
    else:
        print(f"Target classification not found: {iau_name}")
        return "Unknown"
