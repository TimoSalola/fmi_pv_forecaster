import datetime

import pandas
import pandas as pd
import pytz

import fmi_pv_forecaster.helpers.default_parameters
from fmi_pv_forecaster import meps_loader
from fmi_pv_forecaster.helpers import irradiance_transpositions, output_estimator
from fmi_pv_forecaster.helpers import reflection_estimator
from fmi_pv_forecaster.helpers import panel_temperature_estimator


# These variables must be set before pv forecast is called
site_latitude = None
site_longitude = None
panel_tilt = None
panel_azimuth = None

# These variables can be changed if desired
extended_output = False # set to true and the radiation parameters and intermediate steps of the pv output calculation
# will be included in the output

power_rating = 1 # power in kw

timezone = "UTC"



def print_info():
    print("System location(WGS84): " + str(site_latitude) + ", " + str(site_longitude)+".")
    print("Panel angles: " + str(panel_tilt) + ", " + str(panel_azimuth) + ".")
    print("System power: " + str(power_rating))
    print("Timezone: " + str(timezone))
    print("Extended output: " + str(extended_output))



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



"""
Parameter setting functions begin here, some mandatory, some optional.
"""

def set_location(latitude, longitude):
    """
    Call this function to set the PV site latitude and longitude. Values outside metcoop forecast region will cause
    issues with FMI forecast retrieval.
    :param latitude: WGS84 as float. Valid values are -90 to 90.
    :param longitude: WGS84 in float format. eq 60.4312. Valid values are -180 to 180.
    """

    global site_latitude
    global site_longitude

    if site_latitude != latitude or site_longitude != longitude:
        # at least one of the geolocation components was different
        # clearing cache, new location so data from old one can't be used anymore
        meps_loader.clear_cache()

    site_latitude = latitude
    site_longitude = longitude
    #print("Geolocation set at: " + str(site_latitude) + "°, " + str(site_longitude)+"°")

def force_clear_fmi_cache():
    """
    This function will force clearing of FMI open data cache. Cache clearing should normally happen automatically when
    geolocation has been changed or when cache is old and so this function should be useless. Leaving it in for
    debugging.
    """

    meps_loader.clear_cache()

def set_angles(p_tilt, p_azimuth):
    """
    Call this function to set the panel angles for the PV system. Tilt 0 is for a
    :param p_tilt: 0 to 90. 0 for panel flat on the ground, 90 for vertical panel where center normal points to horizon.
    :param p_azimuth: 0 to 360. 0 for north, 90 for east, 180 south and so on. Accepts floats and integers.
    """

    global panel_tilt
    global panel_azimuth

    panel_tilt = p_tilt
    panel_azimuth = p_azimuth
    #print("Panel angles set at tilt: " + str(panel_tilt)+ "°  Azimuth: " + str(panel_azimuth)+"°")


def set_extended_output(extended: bool):
    """
    Use this function to enable or disable additional variables in the PV forecasts. Most of these variables are irrelevant
    to users and thus extended output is disabled as default.
    :param extended: True -> additional variables will be given, False -> additional variables will be hidden.
    :return:
    """
    global extended_output
    extended_output = extended

def set_nominal_power_kw(nominal_power: float):
    """
    This function sets the power rating of the PV system.
    :param nominal_power: Advertised power output of the PV system in standard conditions(perfect weather, direct sunlight)
    :return: None
    """
    global power_rating
    power_rating = nominal_power
    output_estimator.rated_power = nominal_power


def set_default_air_temp(air_temp_c: float):
    """
    This function will set the air temperature(in Celsius) which will be used by clearsky PV forecasts.
    FMI forecasts do not use the default value as air temperature is given by the forecast API.
    Air temperature influences panel temperature which in turn changes panel efficiency.
    """
    fmi_pv_forecaster.helpers.default_parameters.air_temperature = air_temp_c
    #print("Air temperature for clearsky simulations set at: " + str(fmi_pv_forecast.helpers.default_parameters.air_temperature)+ "°C")

def set_default_wind_speed(wind_speed_ms: float):
    """
    This function will set the wind speed(in meters per second at 2m above ground) used by clearsky PV forecasts.
    FMI forecasts do not use the default value as wind speed at 2m is given by the forecast API.
    Wind transfers heat away from PV panels and decreases the difference between air temperature and panel temperature.
    """
    fmi_pv_forecaster.helpers.default_parameters.wind_speed = wind_speed_ms
    #print("Wind speed for clearsky simulations set at: " + str(fmi_pv_forecast.helpers.default_parameters.wind_speed)+ "ms")

def set_module_elevation(module_elevation_m: float):
    """
    This function will set the physical module elevation(measured from ground, not sea level). Module elevation and
    wind speed at 2m are used together to estimate the wind at panel elevation.

    Higher than actual elevation can be used to compensate for exposed panels and lower than actual for sheltered panels.

    If you are processing external data with wind measured at panel elevation, use measured wind as wind value and
    set module elevation as 2m. This way exact wind speed measurements will be used.
    """

    fmi_pv_forecaster.helpers.default_parameters.panel_elevation = module_elevation_m
    #print("Module elevation set at: " + str(fmi_pv_forecast.helpers.default_parameters.panel_elevation) + "m")


def set_default_albedo(albedo: float):
    """
    Albedo here means ground reflectivity around the PV panel. Range is [0,1] with 0.12 being similar to grey old
    asphalt and 0.8 similar to snow.
    """

    fmi_pv_forecaster.helpers.default_parameters.albedo = albedo



def set_cache(cache_on):
    """
    Cache is on by default and this package was built with the intention of having cache always on.

    Disabling cache will cause every function with FMI in its name to make a new server query to
    FMI servers. This will result in unnecessary server calls.

    Having cache on will only make new server calls if data isn't cached yet, caching was done
    over a minute ago, geolocation was changed or cache was manually purged.
    """
    meps_loader.cache_enabled = cache_on


def set_timezone(timezone_string):


    global timezone

    all_viable_timezones = pytz.all_timezones_set

    if timezone_string not in all_viable_timezones:
        raise ValueError("Given timezone \""+ str(timezone_string) + "\" is not in pytz.all_timezones. Timezone should"
              " be similar to \"Europe/Helsinki\", List of valid timezones can be found at https://en.wikipedia.org/wiki/List_of_tz_database_time_zones")

    timezone = timezone_string


def get_timezone():
    return timezone
"""
Parameter setting functions end here.
Internal helper functions begin here. These are not exposed outside the package
"""


def __get_clearsky_radiation_for_interval(interval_start, interval_end, timestep):

    """
    Helper function, this will return a dataframe with clearsky radiation values dni, dhi and ghi
    """

    if site_latitude is None or site_longitude is None:
        raise ValueError(
            "Latitude and longitude must be defined before calling"
            " get_clearsky_radiation_for_interval(). Call pv_forecast.set_location(latitude, longitude) first with"
            " valid WGS84 coordinates."
        )

    clearsky_estimate = meps_loader.__get_irradiance_pvlib(site_latitude, site_longitude, interval_start, interval_end, timestep)

    return clearsky_estimate

def __get_fmi_forecast_for_interval(interval_start, interval_end):

    """
    Main function for getting FMI open data -radiation values.
    :param interval_start:
    :param interval_end:
    :return:
    """

    if site_latitude is None or site_longitude is None:
        raise ValueError(
            "Latitude and longitude must be defined before calling forecast -functions."
            " Call pv_forecast.set_location(latitude, longitude) first with valid WGS84 coordinates."
        )

    data = meps_loader.collect_fmi_opendata(site_latitude, site_longitude, interval_start, interval_end)

    return data





"""
Internal helper functions  end here.
! Public functions begin
Starting with radiation table processing.
"""

def process_radiation_df(data):
    """
    This function processes a radiation dataframe and estimates the output of a pv system.

    The input df must have columns:
    'time', 'dni', 'dhi', 'ghi'
    additional columns "T", "wind" and "albedo" are also useful

    time column is the mathematical point for which each row in the data is simulated for.
    Since weather at 18:00 represents weather between 17:00 and 18:00, the time column is often index-30min
    """

    if "cloud_cover" not in data.index:
        # If using pvlib clearsky data, there will not be a cloud cover column. Added here for compatibility.
        data["cloud_cover"] = 0

    #print(data)
    #print(data.columns)

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

    if not extended_output:
        # if extended output not in use, return only some columns
        return data[["T", "wind", "cloud_cover", "module_temp", "output"]]

    return data


"""
Flexible forecast functions with custom intervals:
"""

def get_clearsky_estimate_for_interval(interval_start, interval_end, timestep=60):

    if site_latitude is None or site_longitude is None:
        raise ValueError(
            "Latitude and longitude must be defined before PV output is estimated."
            "Call pv_forecast.set_location(latitude, longitude) first with"
            " valid WGS84 coordinates."
        )

    if panel_tilt is None or panel_azimuth is None:
        raise ValueError(
            "Tilt and azimuth must be defined before PV output is estimated."
            " Call pv_forecast.set_angles(tilt, azimuth) first with"
            " valid 0-90, 0-360 degree panel angles."
        )

    # timeshifting

    interval_start.minute = fmi_pv_forecaster.helpers.default_parameters.clearsky_fc_time_offset

    # step 1. getting clearsky radiation
    data = __get_clearsky_radiation_for_interval(interval_start, interval_end, timestep)

    # processing data with our pv model
    data = process_radiation_df(data)

    return data


def get_fmi_forecast_for_interval(interval_start, interval_end):
    """
    Loads the complete fmi forecast and returns a subsection.

    Uses cache so if this or any other fmi function has been recently called, no additional server calls will be made.

    :param interval_start: Start time for subsection
    :param interval_end:  End time for subsection
    :return:
    """
    default_fmi_forecast = get_default_fmi_forecast()
    return  default_fmi_forecast.loc[interval_start:interval_end]


"""
Fixed interval forecast functions begin here
"""

def get_default_fmi_forecast():
    """
    This function returns the whole 66~ish hour FMI forecast available at this moment in time.
    :return:
    """

    interval_start = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None) - datetime.timedelta(hours=3)
    # the line above creates a timezone naive utc timestamp. If timezone is included, server will return errors.
    # if time is local time, starting values will be wrong
    # looking 4 hours into the past just for some historical data to be included.

    interval_end = interval_start + datetime.timedelta(hours=68)

    if site_latitude is None or site_longitude is None:
        raise ValueError(
            "Latitude and longitude must be defined before PV output is estimated."
            "Call pv_forecast.set_location(latitude, longitude) first with"
            " valid WGS84 coordinates."
        )

    if panel_tilt is None or panel_azimuth is None:
        raise ValueError(
            "Tilt and azimuth must be defined before PV output is estimated."
            " Call pv_forecast.set_angles(tilt, azimuth) first with"
            " valid 0-90, 0-360 degree panel angles."
        )


    data = __get_fmi_forecast_for_interval(interval_start, interval_end)

    # processing data with our pv model
    data = process_radiation_df(data)

    return data


def set_clearsky_fc_timestep(new_timestep):
    """
    This function will set timestep in minutes used by clearsky forecasts.
    Default value is 60 in order to match FMI forecasts, but any integer value can be used.

    Values such as 15 or 5 will result in smooth plots and as the PV model is fast, even using 1 will not slow the
    clearsky function significantly.

    With 60-minute timesteps forecasts will be timed 12:00, 13:00, 14:00 ...
    With 30-minute timesteps forecasts will be timed 12:00, 12:30, 13:00 ...

    See set_clearsky_fc_time_offset() for adjusting forecast offsets.

    :param new_timestep: Timestep in minutes.
    """
    fmi_pv_forecaster.helpers.default_parameters.clearsky_fc_timestep = new_timestep

def set_clearsky_fc_time_offset(new_offset):
    """
    This function will set offset in minutes used by clearsky forecasts.
    Normally forecasts are done hourly with 0 offsets, meaning 12:00, 13:00, 14:00 ...

    With default 0-minute offsets forecasts will be timed 12:00, 13:00, 14:00 ...
    With 30-minute offsets forecasts will be timed 12:30, 13:30, 14:30 ...

    See set_clearsky_fc_timestep() for adjusting time between measurements.

    :param new_offset: Forecast timestamp offset.
    """
    fmi_pv_forecaster.helpers.default_parameters.clearsky_fc_time_offset = new_offset


def get_default_clearsky_estimate():
    """
    This function returns an approximation for the clearsky PV output during a time window which should cover the
    FMI forecast based PV output from "get_default_fmi_forecast()"

    Forecast will have 60 minute time resolution, 70 hours of measurements and first measurement will be at xx:00 where
    xx is current hour.
    """

    time_start = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)- datetime.timedelta(hours=3)
    time_start = datetime.datetime(time_start.year, time_start.month, time_start.day, time_start.hour)
    time_end = time_start + datetime.timedelta(hours=68)

    data = get_clearsky_estimate_for_interval(time_start, time_end, fmi_pv_forecaster.helpers.default_parameters.clearsky_fc_timestep)

    return data


### Custom hour/day functions from this moment to the future.

def get_fmi_forecast_today():


    time_start = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
    time_end = datetime.datetime(time_start.year, time_start.month, time_start.day, 23)
    data = get_fmi_forecast_for_interval(time_start, time_end)

    return data

def get_fmi_forecast_now():
    """
    Returns interpolated likely forecast values including output for this specific moment in time.
    :return:
    """
    fmi_power_forecast = get_default_fmi_forecast()
    # getting nearest hour:
    time_now = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
    return __interpolate_nearest_power_to_time_value(fmi_power_forecast, time_now)

def get_fmi_forecast_at_interpolated_time(given_time):

    fmi_power_forecast = get_default_fmi_forecast()
    return __interpolate_nearest_power_to_time_value(fmi_power_forecast, given_time)


def __extract_nearest_row_from_power_df(power_df, time_value):
    """
    :param power_df: Dataframe with datetime index containing hourly time values with 30minute offsets. 12:30, 13:30 and
    so on. Will cause errors or crashes if
    :param time_value: Datetime timestamp,dateT12:45:21 for example. This would round to 12:30 which is then read from
    power_df.
    :return:
    """

    time_index = datetime.datetime(time_value.year, time_value.month, time_value.day, time_value.hour, 30)
    nearest_row = power_df.loc[str(time_index)]
    return nearest_row


def __interpolate_nearest_power_to_time_value(power_df, time_value):
    """
    This column interpolates 2 nearest rows with linear interpolation and returns a single row which is the linear
    inbetween of the 2 nearest rows. This function expects index to be hh:30 and hourly. eq. 13:30, 14:30 and so on.
    :param power_df:
    :param time_value:
    :return:
    """

    minute = time_value.minute

    timestamp1 = None
    timestamp2 = None

    if minute < 30:
        timestamp1 = datetime.datetime(time_value.year, time_value.month, time_value.day, time_value.hour, 30) - datetime.timedelta(minutes=60)
        timestamp2 = datetime.datetime(time_value.year, time_value.month, time_value.day, time_value.hour,30)

    elif minute >= 30:
        timestamp1 = datetime.datetime(time_value.year, time_value.month, time_value.day, time_value.hour,
                                       30)
        timestamp2 = datetime.datetime(time_value.year, time_value.month, time_value.day, time_value.hour, 30)+datetime.timedelta(minutes=60)

    # distances between given time value and surrounding values

    if timestamp1 not in power_df.index or timestamp2 not in power_df.index:
        return None

    #print("timevalue:" + str(time_value))
    #print("timestamp1:" + str(timestamp1))
    #print("timestamp2:" + str(timestamp2))
    time_from1 = time_value - timestamp1 # a = X_pos - A_pos
    time_from2 = timestamp2-time_value # b = B_pos- X_pos
    total_time = time_from1 + time_from2  # C = a+b

    # A                         B
    # o------X------------------o
    # |--a---|-------b----------|
    # |------------C------------|

    # X = A*(1- a/C) + B*(1 - b/C)
    # C = 1
    # a = 0.1, b = 0.9
    # X = A*(0.9) + B*(0.1)


    # multipliers, fractional inverses, (1-a/c)
    fractional_distance_from1 = 1-time_from1/total_time # 1-a/C
    fractional_distance_from2 = 1-time_from2/total_time # 1-b/C

    # rows between which to interpolate
    row1 = power_df.loc[str(timestamp1)].copy()
    row2 = power_df.loc[str(timestamp2)].copy()

    # interpolated row
    interpolated_row = row1*fractional_distance_from1 + row2*fractional_distance_from2

    # returning interpolated value
    return interpolated_row


def add_local_time_column(df):

    """
    This function adds a column "local_time" to given dataframe. Local time is calculated based on timezone given with
    set_timezone() and the index of the dataframe which should be naive or timezone aware UTC timestamp.

    :return Original DF with new "local_time" - column.
    """
    # reading given timezone
    tz = get_timezone()

    # extracting index, index can be timezone aware or naive
    idx = df.index

    if idx.tz is None: # handling aware and naive situations with separate functions
        idx = idx.tz_localize("UTC")
    else:
        idx = idx.tz_convert("UTC")

    # this avoids setting with copy warning.
    df = df.copy()
    df["local_time"] = idx.tz_convert(tz)

    return df







