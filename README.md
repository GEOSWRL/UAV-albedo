# UAV-Albedo

UAV-Albedo is a Python library for processing albedo data collected from an upward and downward-facing pyranometer. The project also contains code to compare pyranometer measurements with a rasterized albedo product, which in this case is Landsat 8-derived albedo.

## Requirements
* Datalog containing the following fields from the UAV
	* date and time
	* pitch
	* roll
	* yaw
	* latitude
	* longitude
	* altitude (above mean sea level)
* Datalog containing the following fields from the pyranometers
	* date and time
	* Incoming irradiance (W/m^2)
	* reflected irradiance (W/m^2)
* Terrain models 
	* elevation
	* slope
	* aspect
	* note: all terrain models must have the same geographical extent and pixel size
* External gridded albedo product
	* note: must have the same geographical extent and pixel size as terrain models

# Program Structure
There are 6 python programs that make up the core of the data processing

## Class process_UAV
This class contains the code required to process UAV albedo data and convert it into a .csv file that contains all required fields for the topographic correction and comparison to external gridded albedo data.

## Class process_ground_data
This class is similar to process_UAV in that it preprocesses the albedo/carrying platform data for ingestion into the topographic correction and comparison processes. This class is tailored to the research outlined in Mullen et al., 2021 to merge and preprocess ground validation data.

## Class process_surface_data
This class is used in the creation of a Surface_Data object containing all required surface raster data (elevation, slope, aspect, gridded albedo product for comparison (in this case LS8)) for topographic correction and comparison to the external product.

## Class process_topographic_correction
This class is used in the creation of a topographic correction object. The topographic correction object contains calculated surface parameters, uncorrected albedo, corrected albedo, and the albedo value derived from the external product used for comparison. Creation of an instance of this object requires a surface data object and a series (single line from dataframe) or dictionary corresponding to a single albedo measurement.

## process_main
This python script handles all processing of the UAV data from a higher level. All data paths and user-defined parameters are set in this file. This file allows for UAV data pre-processing, topographic correction, as well as footprint sensitivity analyses.

## process_util
This python script contains methods used in multiple other scripts within the project.

## Workflow

![image](workflow.jpg)

## Usage

```python
import foobar

# returns 'words'
foobar.pluralize('word')

# returns 'geese'
foobar.pluralize('goose')

# returns 'phenomenon'
foobar.singularize('phenomena')
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

```bash
pip install foobar
```

## License
[MIT](https://choosealicense.com/licenses/mit/)