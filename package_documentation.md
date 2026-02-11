# Package functions


---
## Input functions
These functions set the parameters required by the PV model. Input functions can be split into 3 types:

* Required: The PV model will not work unless all of these functions are called with valid input values.
* Optional: The PV model will run even if these functions are not called, but calling these functions with valid
input values can increase model accuracy.
* Conditional: The PV model will run even if these functions are not called. The values set by these functions
will be ignored in some cases.


### Required input functions 
```python
pvfc.set_angles(tilt, azimuth)
pvfc.set_location(latitude, longitude)
```


* tilt: In degrees. Horisontal panel has tilt 0. Vertical panel has 90.
* azimuth: In degrees, [0, 360]. North facing panels have azimuth 0, east 90 etc.
* latitude: In WGS84 coordinate format. [-90, 90]
* longitude : In WGS84 coordinate format. [-180, 180]


### Optional input functions
```python
pvfc.set_module_elevation(elevation)
pvfc.set_nominal_power_kw(power_kw)
```


* elevation: Module distance from local ground level. Panels on top of buildings have elevation of building
height + distance from roof. Used for estimating wind speed at 
* power_kw: Combined nominal power of the PV panels in the system.


### Conditional input functions
```python
pvfc.set_default_air_temp(degrees_C) 
pvfc.set_default_albedo(albedo)
pvfc.set_default_wind_speed(wind_ms)
```


* degrees_C: Air temperature in Celsius. Overridden by "T" column in dataframe if column exists.
* albedo: Ground reflectivity in range [0,1]. 0.15 for dark ground, 0.6 for snow. Overridden by "albedo"
column in dataframe if column exists.
* wind_ms: Wind speed in meters per second. Overridden my "wind" column in dataframe if column exists.


---


## Forecasting functions
Calling a single forecasting function is enough to generate a forecast. The forecasting functions can be split into 3
groups, FMI forecasts, clear sky forecasts and external data processing.




### FMI forecasting functions

```python
pvfc.get_default_fmi_forecast()
pvfc.get_fmi_forecast_for_interval()
pvfc.get_fmi_forecast_at_interpolated_time()
```

`get_default_fmi_forecast()`


will return a dataframe with the available 66-hour forecast using data from FMI.



`get_fmi_forecast_at_interpolated_time(time)` will return a single dataframe row at interpolated time. 




### Clear sky forecasting functions


```python
pvfc.get_default_clearsky_estimate()
pvfc.get_clearsky_estimate_for_interval()
```


### External data processing functions
```python
pvfc.process_radiation_df(radiation_df)
```

## Developmental functions
* add_local_time_column()
* force_clear_fmi_cache()
* set_timezone
* set_cache
* set_clearsky_fc_time_offset
* set_clearsky_fc_timestep
* get_timezone
* set_extended_output
