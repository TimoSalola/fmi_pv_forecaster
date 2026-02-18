# Package documentation

Functions accessible to the user can be split into two main categories. Input functions which are used to feed
system parameters to the PV model, and forecasting functions which run the PV model and generate a forecast.

There are also developmental functions, but these are listed more as a curiosity than something users should 
actively have to rely on or even be aware of.

<!-- TOC -->
* [Package documentation](#package-documentation)
* [1. Input functions](#1-input-functions)
  * [1.1. Required input functions](#11-required-input-functions)
  * [1.2. Optional input functions](#12-optional-input-functions)
  * [1.3. Conditional input functions](#13-conditional-input-functions)
* [2. Forecasting functions](#2-forecasting-functions)
  * [2.1. FMI forecasting functions](#21-fmi-forecasting-functions)
  * [2.2. Clear sky forecasting functions](#22-clear-sky-forecasting-functions)
  * [2.3 External data processing functions](#23-external-data-processing-functions)
* [3. Developmental functions](#3-developmental-functions)
<!-- TOC -->



---
# 1. Input functions
These functions set the parameters required by the PV model. Input functions can be split into 3 types:

* **Required:** The PV model will not work unless all of these functions are called with valid input values.
* **Optional:** The PV model will run even if these functions are not called, but calling these functions with valid
input values can increase model accuracy.
* **Conditional:** The PV model will run even if these functions are not called. The values set by these functions
will be ignored in some cases.

## 1.1. Required input functions

```python
pvfc.set_angles(tilt, azimuth)
pvfc.set_location(latitude, longitude)
```


* tilt: In degrees. Horisontal panel has tilt 0°. Vertical panel has 90°.
* azimuth: In degrees, [0°, 360°]. North facing panels have azimuth 0°, east 90° etc.
* latitude: In WGS84 coordinate format. [-90°, 90°]
* longitude : In WGS84 coordinate format. [-180°, 180°]

Coordinates can be retrieved from google maps. When browsing around, your url will contain the coordinates.

Tilt and azimuth should be set to an accuracy of 1 degree if possible. Deviations higher than 5 degrees can cause
noticeable modeling errors.

Geolocation does not have to be exact and 1km from actual location is good enough.


## 1.2. Optional input functions
```python
pvfc.set_module_elevation(elevation)
pvfc.set_nominal_power_kw(power_kw)
```


* elevation: Module distance from local ground level in meters. Panels on top of buildings have elevation of building
height + distance from roof. Has a default value of 7.
* power_kw: Combined nominal power of the PV panels in the system in kilowatts. Has a default value of 1.


## 1.3. Conditional input functions
```python
pvfc.set_default_air_temp(degrees_C) 
pvfc.set_default_albedo(albedo)
pvfc.set_default_wind_speed(wind_ms)
```


* degrees_C: Air temperature in Celsius. Overridden by "T" column in dataframe if column exists. Default is 20 degrees.
* albedo: Ground reflectivity in range [0,1]. Use 0.15 for dark ground, 0.6 for snow. Overridden by "albedo"
column in dataframe if column exists. Default is 0.25.
* wind_ms: Wind speed in meters per second. Overridden by "wind" column in dataframe if column exists.
Default value is 2.


---


# 2. Forecasting functions
Calling a single forecasting function is enough to generate a forecast. The forecasting functions can be split into 3
groups, FMI forecasts, clear sky forecasts and external data processing.



## 2.1. FMI forecasting functions

When any of these 3 functions is called, the package requests a full 66-hour forecast from FMI open data for the specified geolocation
given to the package by `pvfc.set_location(latitude, longitude)`.
This forecast will then be kept in memory for the next 60 seconds, and any following FMI -based forecast function
within this time window will
use the cached data instead.

This is done to decrease API calls and reduce network usage.


If geolocation is changed within the 60 second window, the system will clear the previous forecast from memory and 
a new forecast will be requested.

```python
pvfc.get_default_fmi_forecast()
pvfc.get_fmi_forecast_for_interval(interval_start, interval_end)
pvfc.get_fmi_forecast_at_interpolated_time(time)
```

The interval function takes two datetime objects, these can be used for slicing the forecast. This function is intended
for extracting time intervals for kWh calculations.

The interpolation function requires a datetime input which has to belong into the 66 hour forecasting interval.
The function will then return a single interpolated row from the PV forecast. This allows users to request forecasts for
times which do not align with times in the FMI default forecasts.







## 2.2. Clear sky forecasting functions


```python
pvfc.get_default_clearsky_estimate()
pvfc.get_clearsky_estimate_for_interval(interval_start, interval_end, timestep)
```


The default clear sky estimate aligns with the FMI open data forecasting interval. This is a convenient
way to generate a comparable clear sky forecast for plotting and comparison.

The clear sky interval function takes two datetime values as start and end points, and a timestep value which tells how
many minutes there should be between rows in the resulting PV output estimate. As the function is not restricted to any
time interval or geographic location, this can be used for calculating power output during different seasons or even 
over a whole year.


## 2.3 External data processing functions
```python
pvfc.process_radiation_df(radiation_df)
```

This function is actually the only PV model function in the program. When FMI or PVlib based forecasts are requested,
they generate radiation tables and then call this function with their radiation tables.

If you'd like to use your own data with the PV model, call this function with a dataframe. 
See [example 3](examples.md#example-3-processing-external-data-with-the-pv-model) for more details. 


# 3. Developmental functions
The following is a listing of functions included in the package but which are not typically useful to users.

* add_local_time_column()
* force_clear_fmi_cache()
* set_timezone
* set_cache
* set_clearsky_fc_time_offset
* set_clearsky_fc_timestep
* get_timezone
* set_extended_output

Cache functions can be used to clear the local fmi cache or set caching to never occur. This will increase API calls
to FMI servers so these should not be touched if at all possible.
