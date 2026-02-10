# PV model explained
This document explains the inner workings of the PV model in detail. Information shared here can be useful for debugging, implementation
or research purposes.

<!-- TOC -->
* [PV model explained](#pv-model-explained)
  * [Steps of the PV model](#steps-of-the-pv-model)
    * [1. Data input](#1-data-input)
    * [2. Irradiance transposition](#2-irradiance-transposition)
    * [3. Reflection estimation](#3-reflection-estimation)
    * [4. Absorbed radiation calculation](#4-absorbed-radiation-calculation)
    * [5. Panel temperature estimation](#5-panel-temperature-estimation)
    * [6. DC output estimation](#6-dc-output-estimation)
  * [Model input constants](#model-input-constants)
    * [Geolocation](#geolocation)
    * [Panel tilt and azimuth](#panel-tilt-and-azimuth)
    * [System size](#system-size)
    * [Module elevation](#module-elevation)
  * [Additional inputs](#additional-inputs)
    * [Wind speed](#wind-speed)
    * [Air temperature](#air-temperature)
    * [Albedo](#albedo)
  * [Tricks with inputs](#tricks-with-inputs)
* [Understanding data tables](#understanding-data-tables)
  * [CSV content example](#csv-content-example)
    * [Missing radiation components](#missing-radiation-components)
  * [CSV reading example](#csv-reading-example)
  * [Extended output tables](#extended-output-tables)
<!-- TOC -->

## Steps of the PV model
The model can be said to consist of 6 steps. These steps are hidden inside the package, and so they are not
exposed to the user. 

```python
pvfc.set_angles(25, 180)
pvfc.set_location(60.1576,24.8762)
pvfc.set_nominal_power_kw(4)
data = pvfc.get_default_fmi_forecast()
```
In the code sample above, the first 3 lines containing parameter inputs are parts of [Data input](#1.-data-input).
The 4th line requesting the default fmi forecast is a compound function which handles the remaining part of step 1
and starts steps 2, 3, 4, 5 and 6.

Internally the code looks a bit like this:


```python
# step 1. Loading data into the system
data = dummy_data_download_function_here()

# step 2. project irradiance components to plane of array:
data = irradiance_transpositions.irradiance_df_to_poa_df(data, site_latitude, site_longitude, panel_tilt,
                                                         panel_azimuth)

# step 3. simulate how much of irradiance components is absorbed:
data = reflection_estimator.add_reflection_corrected_poa_components_to_df(data, site_latitude, site_longitude,
                                                                          panel_tilt, panel_azimuth)

# step 4. compute sum of reflection-corrected components:
data = reflection_estimator.add_reflection_corrected_poa_to_df(data)

# step 5. estimate panel temperature based on wind speed, air temperature and absorbed radiation
data = panel_temperature_estimator.add_estimated_panel_temperature(data)

# step 6. estimate power output
data = output_estimator.add_output_to_df(data)
```



### 1. Data input
This step consists of feeding the system geolocation, panel angles, system size and other needed system
parameters. Feeding radiation tables into the system is also considered to belong to this step.

### 2. Irradiance transposition
Irradiance transposition is the process of calculating how much radiation reaches the panel surface from the three
radiation sources, direct sunlight, atmospheric scattering and ground reflection.

**DNI** is the direct sunlight component. And DNI transposition algorithm is just a simple geometric projection.
The algorithm used is from Sandia National Laboratories, the original author of PVlib, and it can be found
[here](https://pvpmc.sandia.gov/modeling-guide/1-weather-design-inputs/plane-of-array-poa-irradiance/calculating-poa-irradiance/poa-beam/).

**DHI** is the atmospheric scattering component, and it is calculated by using DHI radiation and Perez diffuse sky model
built into PVlib.

**GHI** is a sum of all radiation per square of ground, and it is used to estimate reflections from the ground.
The algorithm used is from Sandia National Laboratories, source 
[here](https://pvpmc.sandia.gov/modeling-guide/1-weather-design-inputs/plane-of-array-poa-irradiance/calculating-poa-irradiance/poa-ground-reflected/).

### 3. Reflection estimation

Once we have estimated how much radiation the panel surface receives from the three sources, we can estimate reflective
losses. Reflective losses have to be calculated separately as the direction of incoming light is different with
all three radiation sources.

The reflection algorithms are based on Martin & Ruiz 2001 _Calculation of the PV modules angular losses under
field conditions by means of an analytical model_. This paper is exceptionally good and I would 
recommend reading it if you are interested in PV modeling.


### 4. Absorbed radiation calculation
The absorbed radiation is calculated as the sum of the three transposed radiation values with reflective losses
removed. No complex math here.


### 5. Panel temperature estimation
Panel temperature is estimated with King 2004 from _Photovoltaic array
performance model_.

Inputs in this phase are absorbed radiation, air temperature and wind speed. 

### 6. DC output estimation

Finally, the DC output is estimated with the Huld 2010 model published in _Mapping the performance of PV modules, effects of 
module type and data averaging_.


---
## Model input constants
These constants are given to the PV model with `pvfc.set_variable_name(value)` -functions. They describe the
physical location and properties of the PV system.

### Geolocation

```python
pvfc.set_location(60.1576,24.8762)
```
- First latitude, then longitude. Both in WGS84 format.
- These can be easily retrieved from google maps. `www.google.com/maps/@60.1576,24.8762,481m`
- Location does not have to be exact, 3 to 4 decimals or about a kilometer from actual location is enough.

### Panel tilt and azimuth
```python
pvfc.set_angles(25, 180)
```
- First tilt, then azimuth.
- Unit is degrees.
- Tilt is 0 for a horizontal panel, eq. panel flat against the ground. 90 for a panel against the wall. 
- Azimuth tells the compass direction, range 0 to 360. 0 for north, 90 for east, 180 for south and so on.
- Accurate angle values are important and simulations with an azimuth deviation of just 5 degree can be
visibly distinct.
- Can be given as integers or decimals, integers are precise enough.

### System size
```python
pvfc.set_nominal_power_kw(4)
```

- Nominal power of the PV system in kilowatts.
- Use nominal_power*system_efficiency as input if you want to simulate inverter and electrical efficiency. 
For example: `.._kw(4 * 0.93)` for a 4kw system where expected combined inverter and cabling efficiency is 93%.


### Module elevation
```python
pvfc.set_module_elevation(8)
```

Module elevation is used for estimating the wind speed at the panels. The wind speed reported in weather forecasts
is typically wind at 2 meters, but if the panels are at 10m, (maybe on top of a building?) the panels likely experience a higher wind speed.
The equation used is as follows:

```python
wind_speed = (module_elevation / 10) ** 0.1429 * wind # 0.1429 is terrain surface roughness 
```


- Unit is meters. Measured from local ground level. 
- Module elevation is used to estimate the wind speed at panel altitude.



---

## Additional inputs
These values are only used if the given weather data does not contain the values as columns. Values are:

- Albedo
- Wind speed
- Air temperature

Setting these values does not do anything if using `pvfc.get_default_fmi_forecast()` or any other fmi -function as
the FMI forecasts contain albedo, wind speed and air temperature.


### Wind speed
```python
pvfc.set_default_wind_speed(3)
```

- In meters per second, measured at 10m elevation.
- Default value is 2m/s.

### Air temperature
```python
pvfc.set_default_air_temp(-5)
```
- In Celsius.
- Default value 20C.
- Panel temperature is always air temperature + some extra.
- Correct air temperature becomes more important at 15C and higher as temperature induced losses start becoming
higher.

### Albedo
```python
pvfc.set_default_albedo(0.6)
```
- Ground reflectivity.
- Varies depending on the season as snow, grass and so on influence albedo.
- Albedo values matter more when tilt of panels increase.
- Albedo of the ground in front of the panels is the actual albedo that matters.
- Actual relevant area varies depending on panel elevation and terrain.
- 0 for completely black ground which does not reflect any light at all. 1 for 
a perfect reflector.
- Values between 0.15 and 0.8 are fairly reasonable.
- Wikipedia has a list of albedo values for differing materials at https://en.wikipedia.org/wiki/Albedo.



---

## Tricks with inputs

**Wind speed**, **air temperature** and **module elevation** do not have to be accurate, and using false values can even be
beneficial in some situations.

- With FMI-based forecasts, air temperature and wind speed are not adjustable. However, if
the panels are located on a beach or on an open plain, it may make sense to use a higher than actual module elevation
to compensate for the exposed location. 

- Roof mounted panels which are flat against the roof may experience lower wind speeds and thus using a lower
than actual module elevation can make sense.

- If module elevation is set to 10 meters, the wind speed equation reduces nicely:

    `wind_speed = (module_elevation / 10) ** 0.1429 * wind`
    
    `= (10 / 10) ** 0.1429 * wind` 
    
    `= 1 ** 0.1429 * wind` 
    
    `= 1 * wind` 
    
    `= wind` 

    This means that if you have a dataset with wind speed measured next to the panels, you can set module elevation
    to 10m and the exact given wind speed will be used for panel temperature estimation.


---

# Understanding data tables
The PV model uses pandas dataframes in order to store pass on radiation and weather data. These
data frames have to contain specific columns and the columns have to be of specific types in order for the
model to be able to process them. This section explains them.


## CSV content example
This is what a full .csv containing all the possible inputs can look like. The lowest amount of input variables
the system can take would contain variables **time**, **dni**, **dhi**, **ghi**.


```commandline
time,dni,dhi,ghi,T,wind,albedo
2024-05-31 23:30:00+00:00,0.000,0.000,0.000,21.539,2.794,0.130
2024-06-01 00:30:00+00:00,0.000,0.000,0.000,21.723,2.958,0.130
2024-06-01 01:30:00+00:00,0.000,8.871,8.871,21.244,3.396,0.097
2024-06-01 02:30:00+00:00,95.500,54.205,65.636,21.223,3.238,0.096
2024-06-01 03:30:00+00:00,458.266,66.915,173.244,21.469,3.639,0.096
```

### Missing radiation components
If the data available only contains two of the radiation components, the third can be calculated
based on the two first values. This requires some geometric trickery and the method varies
on the two known values.

## CSV reading example
A such .csv file can be loaded into the system with the following lines(borrowing from [example 3](examples.md)):
````python
# reading external radiation data csv and creating a dataframe
radiation_data = pd.read_csv("external_radiation_data.csv", index_col="time", parse_dates=["time"])

print("Radiation dataframe")
print_full(radiation_data)

print("Index type:")
print(type(radiation_data.index))
print("Index value type:")
print(type(radiation_data.index[0]))
print(radiation_data.index[0].tz)
````

Resulting print:
```commandline
Radiation dataframe
                                 dni        dhi        ghi          T       wind     albedo
time                                                                                       
2024-05-31 23:30:00+00:00       0.00       0.00       0.00      21.54       2.79       0.13
2024-06-01 00:30:00+00:00       0.00       0.00       0.00      21.72       2.96       0.13
2024-06-01 01:30:00+00:00       0.00       8.87       8.87      21.24       3.40       0.10
2024-06-01 02:30:00+00:00      95.50      54.20      65.64      21.22       3.24       0.10
2024-06-01 03:30:00+00:00     458.27      66.92     173.24      21.47       3.64       0.10
2024-06-01 04:30:00+00:00     590.50      84.46     292.00      21.91       3.97       0.10
...


Index type:
<class 'pandas.DatetimeIndex'>
Index value type:
<class 'pandas.Timestamp'>
UTC
```
**Notes:**
- The time values can also be of type python.datetime and this should still work without issues. Other
time formats like numpy.datetime64 are likely to cause issues. 
- Time inputs should always be in UTC time. Outputs will also always be in UTC time.




## Extended output tables
The system has functionality built in for keeping 


```commandline
                                 dni        dhi        ghi          T       wind     albedo  cloud_cover    dni_poa    dhi_poa    ghi_poa        poa     dni_rc     dhi_rc     ghi_rc  poa_ref_cor  module_temp     output
time                                                                                                                                                                                                                      
2024-05-31 23:30:00+00:00       0.00       0.00       0.00      21.54       2.79       0.13            0       0.00       0.00       0.00       0.00       0.00       0.00       0.00         0.00        21.54       0.00
2024-06-01 00:30:00+00:00       0.00       0.00       0.00      21.72       2.96       0.13            0       0.00       0.00       0.00       0.00       0.00       0.00       0.00         0.00        21.72       0.00
2024-06-01 01:30:00+00:00       0.00       8.87       8.87      21.24       3.40       0.10            0       0.00       8.52       0.01       8.54       0.00       8.13       0.01         8.14        21.45      85.43
2024-06-01 02:30:00+00:00      95.50      54.20      65.64      21.22       3.24       0.10            0      17.06      56.12       0.11      73.28      11.53      53.51       0.06        65.11        22.91   1,031.24
2024-06-01 03:30:00+00:00     458.27      66.92     173.24      21.47       3.64       0.10            0     152.15      77.94       0.28     230.37     133.54      74.32       0.16       208.02        26.74   4,018.16
2024-06-01 04:30:00+00:00     590.50      84.46     292.00      21.91       3.97       0.10            0     285.22     101.12       0.48     386.81     272.05      96.42       0.28       368.75        31.08   7,347.98
```

- **time:** pandas.Timestamp or python datetime. In UTC
- **dni:** Direct normal irradiance. This describes the amount of direct sunlight on a plane which tracks the
movement of the Sun without atmosphere scattered light. Unit: W/m²

- **dhi:** Diffuse horizontal irradiance. This is the amount of atmosphere scattered light on a horizontal plane
with direct sunlight being blocked. Unit: W/m²
- **ghi:** Global horizontal irradiance. This is the total amount of light on a horizontal surface, sum of direct and
atmosphere scattered light. Unit: W/m²
- **T:** Air temperature in Celsius.
- **wind:** Wind speed at 10m in meters per second. 
- **albedo:** Ground reflectivity. Range 0 to 1.
- **cloud_cover:** Value in range 0 to 100, 100 means a fully cloudy weather, 0 is perfectly clear.
- **dni_poa:** DNI radiation transposed to the panel surface. Unit: W/m²
- **dhi_poa:** DHI radiation transposed to the panel surface. Unit: W/m²
- **ghi_poa:** GHI radiation transposed to the panel surface. Unit: W/m²
- **poa:** Sum of **dni_poa**, **dhi_poa**, **ghi_poa**, not actually used for anything. This describes the amount of
radiation reaching the surface of the PV panels but this specific value should not be used. Unit: W/m²
- **dni_rc:** DNI radiation absorbed by the PV panels. Comes from feeding **DNI_poa**(direct sunlight component of
radiation on panel surface) to a function which estimates how much light is lost due to panel surface reflectivity. Unit: W/m²

- **dhi_rc:** DHI radiation absorbed by the PV panels. Comes from feeding **DHI_poa**(atmosphere scattered component of
radiation on panel surface) to a function which estimates how much light is lost due to panel surface reflectivity. Unit: W/m²
- **ghi_rc:** GHI radiation absorbed by the PV panels. Comes from feeding **GHI_poa**(ground reflected component of
radiation on panel surface) to a function which estimates how much light is lost due to panel surface reflectivity. Unit: W/m²
- **poa_ref_cor:** Amount of light absorbed by the PV panels. Unit: W/m²
- **module_temp:** Modeled module temperature, based on air temperature(**T**), wind speed(**wind**) and absorbed
radiation **(poa_ref_cor**).
- **output:** Modeled system output. Calculated based on module temperature, absorbed radiation and system size.

