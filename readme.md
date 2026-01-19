# FMI open pv forecast packge

This repository contains a packaged version of the FMI PV forecasting and modeling code available at:
https://github.com/fmidev/fmi-open-pv-forecast.

This packaged version exists so that others can utilize the PV forecasting tool for their own purposes without having to
copy the whole project.


---
# Examples

#### Case 1: FMI weather forecast based PV system output
```python
import fmi_pv_forecast

fmi_pv_forecast.set_angles(25, 135) # panel tilt, panel azimuth
fmi_pv_forecast.set_location(60, 25) # wgs84 coordinates, latitude, longitude
fmi_pv_forecast.set_nominal_power_kw(21) # kwp rating of the system. Default is 1kw

data = fmi_pv_forecast.get_default_fmi_forecast()

print(data)
```


Resulting print:
```commandline
                       T   wind  cloud_cover  module_temp       output
Time                                                                  
2026-01-12 09:30:00 -3.9   9.49            0    -3.900000     0.000000
2026-01-12 10:30:00 -3.8   8.82            0    -2.678103  1039.646162
2026-01-12 11:30:00 -3.7   8.54            0    -2.903494   649.622513
2026-01-12 12:30:00 -3.6   8.33            0    -3.247530   190.337779
2026-01-12 13:30:00 -3.5   8.32            0    -3.460868    21.119638
```


#### Output parameters explained:
- **Time** Datetime index, times are in UTC time.
- **T** Air temperature at 2m from ground.
- **wind** Wind speed in m/s at 2m from ground.
- **cloud_cover** Value in range [0,100]. 0 indicates clear sky, 100 for full cloud cover.
- **module_temp** Modeled module temperature in Celsius. 
- **output** Power output in watts.

---
#### Case 2: theoretical clear sky forecast example for vertical panels in cold and calm weather

```python
import fmi_pv_forecast

# This example shows how to estimate theoretical clears sky PV output in winter conditions using PVlib clearsky
# estimates.

fmi_pv_forecast.set_angles(90, 180)
fmi_pv_forecast.set_location(60, 25)
fmi_pv_forecast.set_nominal_power_kw(4)

fmi_pv_forecast.set_default_albedo(0.7) # ground reflectivity. Default is 0.25. Using 0.7 for snow.

# these 3 parameters are used for panel temperature estimation.
fmi_pv_forecast.set_module_elevation(3)
fmi_pv_forecast.set_default_air_temp(-10) # only needed for clearsky estimates
fmi_pv_forecast.set_default_wind_speed(0) # only needed for clearsky estimates

data = fmi_pv_forecast.get_default_clearsky_estimate()

print(data)
```


Resulting print:

```commandline
                            T  wind  cloud_cover  module_temp       output
2026-01-12 11:00:00+00:00 -10     0            0     4.364507  2009.364195
2026-01-12 12:00:00+00:00 -10     0            0     0.633579  1487.380702
2026-01-12 13:00:00+00:00 -10     0            0    -6.791568   399.175174
2026-01-12 14:00:00+00:00 -10     0            0   -10.000000     0.000000
2026-01-12 15:00:00+00:00 -10     0            0   -10.000000     0.000000
...                        ..   ...          ...          ...          ...
```

---
#### Case 2: theoretical clear sky forecast example for vertical panels in cold and calm weather

```python
import fmi_pv_forecast

# This example shows how to estimate theoretical clears sky PV output in winter conditions using PVlib clearsky
# estimates.

fmi_pv_forecast.set_angles(90, 180)
fmi_pv_forecast.set_location(60, 25)
fmi_pv_forecast.set_nominal_power_kw(4)

fmi_pv_forecast.set_default_albedo(0.7) # ground reflectivity. Default is 0.25. Using 0.7 for snow.

# these 3 parameters are used for panel temperature estimation.
fmi_pv_forecast.set_module_elevation(3)
fmi_pv_forecast.set_default_air_temp(-10) # only needed for clearsky estimates
fmi_pv_forecast.set_default_wind_speed(0) # only needed for clearsky estimates

data = fmi_pv_forecast.get_default_clearsky_estimate()

print(data)
```


Resulting print:

```commandline
                            T  wind  cloud_cover  module_temp       output
2026-01-12 11:00:00+00:00 -10     0            0     4.364507  2009.364195
2026-01-12 12:00:00+00:00 -10     0            0     0.633579  1487.380702
2026-01-12 13:00:00+00:00 -10     0            0    -6.791568   399.175174
2026-01-12 14:00:00+00:00 -10     0            0   -10.000000     0.000000
2026-01-12 15:00:00+00:00 -10     0            0   -10.000000     0.000000
...                        ..   ...          ...          ...          ...
```

### Advanced usage

