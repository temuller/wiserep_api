from wiserep_api.api import get_response, get_target_response

def get_target_property(iau_name, property_name, verbose=False):
    """Obtains the target's properties from Wiserep.

    Properties: ``type``, ``redshift``, ``host``, ``coords``
    and ``coords_deg``.

    Parameters
    ----------
    iau_name: str
        IAU name of the target (e.g. 2020xne).
    property_name : str or list
        Name of the target's property or multiple properties.
    verbose: bool, default 'False'
        If True, print some of the intermediate information

    Returns
    -------
    target_properties: str, float or list
        The values of the target's properties.
    """
    # target's webpage
    response = get_target_response(iau_name, verbose)
    if response is None:
        return None

    properties_dict = {'type':'Type',
                       'redshift':'Redshift',
                       'host':'Host Name',
                       'coords':'RA/DEC (J2000)',
                       'coords_deg':'RA/DEC (J2000)',
                       } 
    
    if isinstance(property_name, str):
        properties_list = [property_name]
    else:
        properties_list = property_name

    target_properties = []
    for property in properties_list:
        assert property in properties_dict.keys(), f"Not a valid property: '{property}'"
        prop_str = properties_dict[property]

        # search for the property
        if property=='coords':
            if prop_str not in response.text:
                prop_str = prop_str.replace('J2000', '')  # relatively new targets do not have coordinates epoch
            split_text = response.text.split(f'{prop_str}</span><b><div class="value">')
        elif property=='coords_deg':
            if prop_str not in response.text:
                prop_str = prop_str.replace('J2000', '')
            split_text = response.text.split(f'{prop_str}</span><b><div class="value">')
            if len(split_text)>1:
                split_text = split_text[1].split('div class="alter-value">')
        else:
            split_text = response.text.split(f'{prop_str}</span><div class="value"><b>')

        if len(split_text) > 1:
            target_property = split_text[1].split("<")[0]
        else:
            target_property = ''
            
        if property=='redshift' and len(target_property)>0:
            target_property = float(target_property)

        target_properties.append(target_property)

    if len(target_properties)==1:
        target_properties = target_properties[0]

    return target_properties

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
    # target's webpage
    response = get_target_response(iau_name, verbose)

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
