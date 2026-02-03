# FMI open pv forecast package


The main functionality of this package is the PV forecasting tool which is a combination of the FMI PV model and
weather forecasts from FMI open data. The resulting PV forecasting tool generates hourly weather aware PV forecasts for 
a 66-hour period. These forecasts take panel orientation, panel surface reflections, panel temperature and other factors
into account, resulting in generally accurate modeling of PV output when weather forecasts align with actual experienced
weather.

The forecasting package has in-built functionality for using clear sky radiation estimates from PVlib. These clear sky
forecasts can be used for testing purposes, system monitoring or in cases when internet access is not available.

The PV model can also be used with external data sources by feeding it dataframes with the required radiation components.
See example on using external data from usage_examples.md.


---
## FMI PV forecasts

### Forecast updating frequency and time window
The FMI open data forecasts are available for a 66-hour window. This window extends into the past due to the
simulations being started at T0 and being finished and available at around T0 + 3 hours. Available forecasts update
once every 3 hours with exact timing having some variance.


### Geographic boundaries

The available forecasting region depends on the radiation and weather forecasts. FMI open forecasting region 
covers Finland, Scandinavia and the baltic countries with some additional margin. 

See https://en.ilmatieteenlaitos.fi/numerical-weather-prediction for the full available forecast area.

The geographic area is split into a 2.5km by 2.5km grid. When data for a location is retrieved from the FMI servers,
forecast for the closest available grid point is used.

### Forecast accuracy

The PV model has been tested with on-site measurements and with these measurements as inputs, the simulated
PV output is nearly identical to measured PV output in various weather conditions even at 1-minute time resolution.


Forecasts and measured PV output also align well together, but the accuracy of PV forecasts is largely determined 
by the accuracy of cloud forecasts. Especially partly cloudy days are challenging to forecast accurately.

---

## Clearsky forecasts

This package also contains functions for simulating clear sky PV output using simulated radiation values from
PVlib. These forecasts do not have geographical restrictions, and they can be computed for any time interval with any
time resolution. Another benefit is that computing them does not require internet access.

The downsides of clear sky forecasts are the complete lack of weather-awareness. The PV model requires air temperature
and wind speed values which must be manually fed to the system for clear sky forecasts to be computable. A good 
air temperature would be equal to the expected air temperature during peak production hours for the interval. Given wind 
value depends on the PV site and experienced weather. 2m/s is a fairly good default value, but values higher
or lower can be used if panels are sheltered or exposed or if the location is particularly windy.

---

# Usage of external data instead of FMI open data
The PV model was programmed in a way which makes usage of external radiation data as easy as possible. If you have
access to DNI, DHI and GHI radiation tables from historical forecasts or forecasting service, you can feed *"standard"* format
dataframes into the PV model. This way you can use the same PV model for your own forecasts or even research purposes
without having to implement the PV model yourself.

Similarly to the clearsky forecasts, using your own radiation and weather data as inputs does not come with the 
time interval or temporal resolution restrictions of FMI open data. Nor are there any geographical restrictions.

External data should have radiation values DNI, DHI and GHI + datetime included. Additionally, air temperature
 and wind speed values will increase the accuracy of the model, but constants in their place can also be given.

See [usage examples](usage_examples.md) for an example on using data from a .csv file as input.


---

# Usage example
This example shows how to use the forecasting tool by computing a forecast for a 4kw system.
Additional examples with commentary are available at [usage examples](usage_examples.md).


```python
import fmi_pv_forecaster as pvfc

pvfc.set_angles(25, 180)
pvfc.set_location(60.1576,24.8762)
pvfc.set_nominal_power_kw(4)

data = pvfc.get_default_fmi_forecast()

print("Forecast:")
print(data)
```


Resulting print:
```commandline
Forecast:
                        T  wind  module_temp     output
Time                                                   
2026-01-20 10:30:00  -0.8  0.79    -0.800000   0.000000
2026-01-20 11:30:00  -0.6  1.33    -0.048916  38.589095
2026-01-20 12:30:00  -0.5  1.78    -0.136189  25.854990
2026-01-20 13:30:00  -0.7  2.30    -0.627352   5.316707
2026-01-20 14:30:00  -1.0  2.37    -0.999996   0.000000
...                   ...   ...          ...        ...
2026-01-23 01:30:00 -15.2  0.73   -15.200000   0.000000
2026-01-23 02:30:00 -15.6  0.73   -15.600000   0.000000
2026-01-23 03:30:00   NaN   NaN          NaN   0.000000
2026-01-23 04:30:00   NaN   NaN          NaN   0.000000
2026-01-23 05:30:00   NaN   NaN          NaN   0.000000
```




---


#### Authors and acknowledgements
Timo Salola.

Additional help from: Viivi Kallio, William Wandji, Anders Lindfors, Juha Karhu.

This project uses PVlib.

<img src="readme_images/pvlib_logo.webp" height="100"/>
