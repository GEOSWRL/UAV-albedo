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

## Workflow

![image](file://workflow.jpg)

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