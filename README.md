# WiseRep API
API to access WiserRep data from command lines

[![repo](https://img.shields.io/badge/GitHub-temuller%2Fwiserep_api-blue.svg?style=flat)](https://github.com/temuller/wiserep_api)
[![license](http://img.shields.io/badge/license-MIT-blue.svg?style=flat)](https://github.com/temuller/wiserep_api/blob/master/LICENSE)
![Python Version](https://img.shields.io/badge/Python-3.9%2B-blue)
[![PyPI](https://img.shields.io/pypi/v/wiserep_api?label=PyPI&logo=pypi&logoColor=white)](https://pypi.org/project/wiserep_api/)
[![DOI](https://zenodo.org/badge/635179400.svg)](https://zenodo.org/badge/latestdoi/635179400)


## Installation

It is recommended to install ``wiserep_api`` from pip:

```python
pip install wiserep_api
```
or it can be installed from source in the usual way.

## Usage Example

Below are some basic examples of what the user can do with this package.

### Download a list of SNe

A list of targets can be downloaded for a given spectral type. The spectral types are as defined in Wiserep, which can be printed with ``print_spectral_types``:

```python
from wiserep_api.search import print_spectral_types, download_sn_list
print_spectral_types()
```
```python
{'Other': 0, 'SN': 1, 'SN I': 2, 'SN Ia': 3, 'SN Ib': 4, 'SN Ic': 5, 'SN Ib/c': 6, 'SN Ic-BL': 7, 'SN Ib - Ca-rich': 8, 'SN Ibn': 9, 'SN II': 10, 'SN IIP': 11, 'SN IIL': 12, 'SN IIn': 13, 'SN IIb': 14, 'SN I-faint': 15, 'SN I-rapid': 16, 'SLSN-I': 18, 'SLSN-II': 19, 'SLSN-R': 20, 'Afterglow': 23, 'LBV': 24, 'ILRT': 25, 'Nova': 26, 'CV': 27, 'Varstar': 28, 'AGN': 29, 'Galaxy': 30, 'QSO': 31, 'Std-spec': 50, 'Gap': 60, 'Gap I': 61, 'Gap II': 62, 'SN impostor': 99, 'SN Ia-pec': 100, 'SN Ia-SC': 102, 'SN Ia-91bg-like': 103, 'SN Ia-91T-like': 104, 'SN Ia-02cx-like': 105, 'SN Ia-CSM': 106, 'SN Ib-pec': 107, 'SN Ic-pec': 108, 'SN II-pec': 110, 'SN IIn-pec': 112, 'TDE': 120, 'WR': 200, 'WR-WN': 201, 'WR-WC': 202, 'WR-WO': 203, 'M dwarf': 210}
```
In this example, we can download 1991-T-like supernovae (SNe):

```python
download_sn_list("SN Ia-91T-like")
```
```python
390 "SN Ia-91T-like" objects found!
URL used: https://www.wiserep.org/search?&page=8&public=all&type[]=104
```

### Download spectra

The public available spectra can also be easily downloaded for a list of targets. These will be saved under the ``spectra`` directory, in a separate directory for each target:

```python
import numpy as np
from wiserep_api import download_target_spectra

sne_list = np.genfromtxt('SNIa-91T-like_wiserep.txt', dtype=str, delimiter='\n')

for sn in sne_list:
    try:
        download_target_spectra(sn, file_type='ascii', exclude=['SEDM'])
    except Exception as exc:
        print(f'{sn}: {exc}')
```

### Running SNID

Assuming that [SNID](https://people.lam.fr/blondin.stephane/software/snid/) is already istalled, it can be run with just a few lines of code:

```python
import os
from wiserep_api import snid

sne_list = np.genfromtxt('SNIa-91T-like_wiserep.txt', dtype=str, delimiter='\n')
snid_commmand = 'snid inter=0 plot=0 aband=0 usetype=Ia-91T'

for sn in sne_list:
    directory = os.path.join('spectra', sn)
    snid.run_snid(directory, command=snid_commmand)
```

### Getting object's properties  

The properties of a given object can be easily obtained:

```python
from wiserep_api import get_target_property

for prop in ['type', 'redshift', 'host', 'coords', 'coords_deg']:
    value = get_target_property('2004eo', prop)
    print(f'{prop}: {value}')
```   
```python
type: SN Ia
redshift: 0.015718
host: NGC6928
coords: 20:32:54.190 +09:55:42.71
coords_deg: 308.22579 +9.92853
```

Or you can get multiple properties at once:

```python
properties = ['type', 'redshift', 'host', 'coords', 'coords_deg']
values = get_target_property('2004eo', properties)
```

The spectral type of a given object can also be retrived with ``get_target_class``, which does a more "in-depth" search of the classification in case this is not found in the main properties:

```python
from wiserep_api import get_target_class

sn_type = get_target_class("2004eo")
print(sn_type)
```
```python
'SN Ia'
```


## Contributing

To contribute, either open an issue or send a pull request (prefered option). You can also contact me directly (check my profile: https://github.com/temuller).

## Citing WiseRep API

If you make use of this code, please cite it:

```code
@software{tomas_e_muller_bravo_2023_7896352,
  author       = {{M{\"u}ller-Bravo}, Tom{\'a}s E.},
  title        = {temuller/wiserep\_api: First Official Release!},
  month        = may,
  year         = 2023,
  publisher    = {Zenodo},
  version      = {v0.1.5},
  doi          = {10.5281/zenodo.7896352},
  url          = {https://doi.org/10.5281/zenodo.7896352}
}
```
