import datetime
import random
import time
from datetime import timedelta

import numpy
import pandas as pd
import pandas
import pytest


import fmi_pv_forecaster
from fmi_pv_forecaster import pv_forecaster as pv_forecast



def random_int(a, b):
    # helper, generates ints for some functions
    return random.randint(a, b)

def random_float(a, b):
    # helper, generates floats for some functions. 6 decimal values can do geolocation at 1m accuracy so 6 should be
    # enough for testing purposes. Also keeps prints neater.
    return round(random.uniform(a, b),6)


def print_full(x: pandas.DataFrame):
    """
    Prints a dataframe without leaving any columns or rows out. Useful for debugging.
    """

    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 1400)
    pd.set_option('display.float_format', '{:10,.2f}'.format)
    pd.set_option('display.max_colwidth', None)
    print(x)
    pd.reset_option('display.max_rows')
    pd.reset_option('display.max_columns')
    pd.reset_option('display.width')
    pd.reset_option('display.float_format')
    pd.reset_option('display.max_colwidth')

def clearsky_test_with_random_parameters(test_number = None):
    print("====================================================")
    print("==== Testing clearsky estimation for custom interval with random parameters")
    print("====================================================")


    tilt = random_float(0, 90)
    azimuth = random_float(0, 360)

    latitude = random_float(-90, 90)
    longitude = random_float(-180, 180)

    timestep = random_int(1,60)

    time_start = datetime.datetime(random_int(2000, 2050), random_int(1, 12), random_int(1,28), random_int(0, 23))
    time_end = time_start + timedelta(days=random_int(1,10))


    pv_forecast.set_location(latitude, longitude)
    pv_forecast.set_angles(tilt, azimuth)


    clearsky_data = pv_forecast.__get_clearsky_radiation_for_interval(time_start, time_end, timestep)

    assert clearsky_data is not None, "Clearsky data was none, something has to be wrong with the clearsky estimation function." + str(clearsky_data)


    # checking measurement count from df.

    expected_values_per_hour = 60.0/timestep

    interval_length_in_hours = (time_end-time_start).total_seconds()/3600

    expected_measurement_count = round(interval_length_in_hours*expected_values_per_hour)

    measurement_count = len(clearsky_data)

    #print(expected_measurement_count)
    #print(measurement_count) # this is usually the same or 1 higher than expected measurement count

    assert measurement_count >= expected_measurement_count, "Got fewer than expected measurements from clearsky estimation. There were " + str(measurement_count) +" measurements when " + str(expected_measurement_count) +"(+1) were expected."
    assert measurement_count-1 <= expected_measurement_count, "Got more measurements than expected from clearsky estimation. There were " + str(measurement_count) +" measurements when " + str(expected_measurement_count) +"(+1) were expected."

    prt_string = "Clearsky test " + str(test_number) +" successful." + "Lat: " + str(latitude) + " Lon:" + str(longitude) + " tilt: " + str(tilt) + " azimuth:" + str(azimuth)+ " date: " + str(time_start)

    print(prt_string)

    print("====================================================")
    print("==== Clearsky random parameter estimation complete")
    print("====================================================")




def test_clearsky_radiation_estimation():
    print("====================================================")
    print("==== Testing clearsky radiation estimation")
    print("====================================================")


    for i in range(10):
        clearsky_test_with_random_parameters(test_number=i)
        print("= Clearsky radiation test " + str(i) + " done.")



    print("====================================================")
    print("==== Testing clearsky radiation done")
    print("====================================================")


def test_clearsky_power1():
    print("====================================================")
    print("==== Testing clearsky power estimation")
    print("====================================================")
    tilt = random_float(0, 90)
    azimuth = random_float(0, 360)

    latitude = random_float(-90, 90)
    longitude = random_float(-180, 180)

    timestep = random_int(1, 60)

    time_start = datetime.datetime(random_int(2000, 2050), random_int(1, 12), random_int(1, 28), random_int(0, 23))
    time_end = time_start + timedelta(days=random_int(1, 10))

    pv_forecast.set_location(latitude, longitude)
    pv_forecast.set_angles(tilt, azimuth)


    powerdata = pv_forecast.get_clearsky_estimate_for_interval(time_start, time_end, timestep)

    print_full(powerdata)

    print("====================================================")
    print("==== Testing clearsky power estimation done")
    print("====================================================")



def test_forecast_power1():
    print("====================================================")
    print("==== Testing clearsky power estimation")
    print("====================================================")

    print("testing retrieval of pv forecast parts")
    tilt = random_float(0, 90)
    azimuth = random_float(0, 360)

    latitude = 60.0
    longitude = 25.0

    time_start = datetime.datetime.now()

    time_end = time_start + timedelta(days=3)
    pv_forecast.set_location(latitude, longitude)
    pv_forecast.set_angles(tilt, azimuth)

    #print(pv_forecast.site_latitude)
    #print(pv_forecast.site_longitude)


    powerdata = pv_forecast.get_fmi_forecast_for_interval(time_start, time_end)
    #print("printing full result")
    #print_full(powerdata)

    print("====================================================")
    print("==== Clearsky power estimation done")
    print("====================================================")






def test_set_default_parameters():
    print("\n")
    print("====================================================")
    print("==== Testing if set wind speed, air temp and elevation actually work")
    print("====================================================")

    tilt = random_float(0, 90)
    azimuth = random_float(0, 360)

    latitude = 50
    longitude = 25.0

    test_air_temp = random_int(-20, 30)
    test_wind_speed = random_int(0, 20)

    pv_forecast.set_default_air_temp(test_air_temp)
    pv_forecast.set_default_wind_speed(test_wind_speed)

    pv_forecast.set_location(latitude, longitude)
    pv_forecast.set_angles(tilt, azimuth)

    powerdata = pv_forecast.get_default_clearsky_estimate()

    air_temp_values = powerdata["T"].values

    for air_temp in air_temp_values:
        assert air_temp == test_air_temp, "Air temperature was set at " + str(test_air_temp) + "C but output df had " + str(air_temp) +"C."

    module_temp_values = powerdata["module_temp"].values

    for module_temp in module_temp_values:
        assert  module_temp >= test_air_temp, ("Module temperature was lower than air temperature. This should not be"
                                               "possible because module temperature is calculated as air temperature + radiation")

    wind_speed_values = powerdata["wind"].values

    for wind in wind_speed_values:
        assert  wind == test_wind_speed, "Wind speed for clearsky was not the same as given constant. Something is going wrong."

    print("====================================================")
    print("==== Value setting test complete!")
    print("====================================================")




def disabled_test_outside_area_getter():

    print("\n")
    print("====================================================")
    print("==== Testing how code handles retrieval of data outside allowed area")
    print("====================================================")



    tilt = random_float(0, 90)
    azimuth = random_float(0, 360)

    latitude = 50
    longitude = 25.0

    pv_forecast.set_location(latitude, longitude)
    pv_forecast.set_angles(tilt, azimuth)

    powerdata = pv_forecast.get_fmi_forecast_today()

    print_full(powerdata)

    print("\n")
    print("====================================================")
    print("==== Testing of how code handles retrieval of data outside allowed area complete")
    print("====================================================")




## Testing alternative forecast functions


def test_default_fmi_forecast():
    print("====================================================")
    print("==== Testing default time interval for FMI PV forecast")
    print("====================================================")

    tilt = random_float(0, 90)
    azimuth = random_float(0, 360)

    latitude = 60.0
    longitude = 25.0

    pv_forecast.set_location(latitude, longitude)
    pv_forecast.set_angles(tilt, azimuth)

    powerdata = pv_forecast.get_default_fmi_forecast()

    print_full(powerdata)

    print("====================================================")
    print("==== FMI default interval forecast test done")
    print("====================================================")



def test_fmi_forecast_today():

    print("\n")
    print("====================================================")
    print("==== Testing fmi forecast for today")
    print("====================================================")



    tilt = random_float(0, 90)
    azimuth = random_float(0, 360)

    latitude = 60
    longitude = 25.0

    pv_forecast.set_location(latitude, longitude)
    pv_forecast.set_angles(tilt, azimuth)

    powerdata = pv_forecast.get_fmi_forecast_today()

    print_full(powerdata)

    print("\n")
    print("====================================================")
    print("==== FMI forecast test for today complete")
    print("====================================================")



def test_clearsky_forecast_default_range():
    print("====================================================")
    print("==== Testing default clearsky interval complete")
    print("====================================================")

    tilt = random_float(0, 90)
    azimuth = random_float(0, 360)

    latitude = 60
    longitude = 25.0

    pv_forecast.set_location(latitude, longitude)
    pv_forecast.set_angles(tilt, azimuth)

    powerdata = pv_forecast.get_default_clearsky_estimate()

    print_full(powerdata)

    print("====================================================")
    print("==== Clearsky default interval test complete")
    print("====================================================")



def test_fmi_open_data_cache():
    tilt = random_float(0, 90)
    azimuth = random_float(0, 360)

    latitude = 60
    longitude = 25.0

    pv_forecast.set_location(latitude, longitude)
    pv_forecast.set_angles(tilt, azimuth)

    print("getting forecast 1")

    powerdata = pv_forecast.get_default_fmi_forecast()

    print_full(powerdata)

    #time.sleep(10)

    print("getting forecast 2")

    powerdata = pv_forecast.get_default_fmi_forecast()

    print_full(powerdata)


def test_fmi_get_power_now():
    tilt = random_float(0, 90)
    azimuth = random_float(0, 360)

    latitude = 60
    longitude = 25.0

    pv_forecast.set_location(latitude, longitude)
    pv_forecast.set_angles(tilt, azimuth)

    print("getting powerdata for now")
    powerdata = pv_forecast.get_fmi_forecast_now()

    assert powerdata is not None, "Powerdata for this moment in time is None, this should not happen"


def test_set_get_timezone():

    print("Reading current timezone")
    print(pv_forecast.get_timezone())

    print("Testing invalid timezone")
    with pytest.raises(ValueError) as excinfo:
        pv_forecast.set_timezone("kissa")
    assert excinfo.type is ValueError


    print("Setting and reading timezone")
    pv_forecast.set_timezone("Indian/Maldives")
    assert pv_forecast.get_timezone() == "Indian/Maldives"


def test_add_localtime():

    print("Testing local time column adding to fmi forecast")
    fmi_pv_forecaster.set_timezone("Indian/Maldives")
    forecast = fmi_pv_forecaster.get_default_fmi_forecast()
    forecast = fmi_pv_forecaster.add_local_time_column(forecast)

    print("resulting df: ")
    print(forecast)

    # check that none of the local times were NotATime, NaT's are a common failure mode here
    assert numpy.datetime64('NaT') not in forecast["local_time"]

    print("testing local time column adding to clearsky forecast")
    clearsky_forecast = fmi_pv_forecaster.get_default_clearsky_estimate()
    clearsky_forecast = fmi_pv_forecaster.add_local_time_column(clearsky_forecast)

    print("resulting df: ")
    print(clearsky_forecast)

    # check that none of the local times were NotATime, NaT's are a common failure mode here
    assert numpy.datetime64('NaT') not in clearsky_forecast["local_time"], "Clearsky local_time adding resulted in NaT-values"



def test_interpolation_multiple_times():

    """
    This test function checks interpolation several times in a row. A previous interpolation function had an issue where
    repeating the function call caused errors.
    :return:
    """

    print("Testing interpolation multiple times")

    time_now = datetime.datetime.now(datetime.timezone.utc)
    time_now = datetime.datetime(year=time_now.year, month=time_now.month, day=time_now.day, hour=time_now.hour)

    for i in range(0,20):
        time_point = time_now + timedelta(minutes=90*i)
        datapoint = fmi_pv_forecaster.get_fmi_forecast_at_interpolated_time(time_point)
        assert datapoint["output"] >= 0, "Interpolation resulted in a negative power value."



def test_interpolation_outside_forecast_time():

    """
    system should always return None if attempting to ask for forecast outside [now, now+66-ish hours]
    """

    datapoint = fmi_pv_forecaster.get_fmi_forecast_at_interpolated_time(datetime.datetime(2012, 6 , 10))

    print("datapoint")
    print(datapoint)

    assert datapoint is None, "Interpolation for a timepoint in the past returned something else than None"






