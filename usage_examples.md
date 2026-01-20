
# Examples

#### Case 1: FMI weather forecast based PV system output
```python
import fmi_pv_forecaster as pvfc

"""
This example shows the minimal amount of needed code for forecasting PV output.
Panel angles are south facing with a tilt of 25 degrees, fairly typical for roof mounted panels.
Geolocation is within Helsinki.
Power rating set at 4kw.
"""

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
import fmi_pv_forecaster as pvfc

# This example shows how to estimate theoretical clears sky PV output in winter conditions using PVlib clearsky
# estimates.

pvfc.set_angles(90, 180)
pvfc.set_location(60, 25)
pvfc.set_nominal_power_kw(4)

pvfc.set_default_albedo(0.7) # ground reflectivity. Default is 0.25. Using 0.7 for snow.

# these 3 parameters are used for panel temperature estimation.
pvfc.set_module_elevation(3)
pvfc.set_default_air_temp(-10) # only needed for clearsky estimates
pvfc.set_default_wind_speed(0) # only needed for clearsky estimates

data = pvfc.get_default_clearsky_estimate()

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
import fmi_pv_forecaster as pvfc

# This example shows how to estimate theoretical clears sky PV output in winter conditions using PVlib clearsky
# estimates.

pvfc.set_angles(90, 180)
pvfc.set_location(60, 25)
pvfc.set_nominal_power_kw(4)

pvfc.set_default_albedo(0.7) # ground reflectivity. Default is 0.25. Using 0.7 for snow.

# these 3 parameters are used for panel temperature estimation.
pvfc.set_module_elevation(3)
pvfc.set_default_air_temp(-10) # only needed for clearsky estimates
pvfc.set_default_wind_speed(0) # only needed for clearsky estimates

data = pvfc.get_default_clearsky_estimate()

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