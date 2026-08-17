import datetime

import pandas
import pandas as pd
import pytz

import fmi_pv_forecaster.helpers.default_parameters
from fmi_pv_forecaster import meps_loader
from fmi_pv_forecaster.helpers import irradiance_transpositions, output_estimator
from fmi_pv_forecaster.helpers import panel_temperature_estimator
from fmi_pv_forecaster.helpers import reflection_estimator

# These variables must be set before pv forecast is called
site_latitude = None
site_longitude = None
panel_tilt = None
panel_azimuth = None

# These variables can be changed if desired
extended_output = False  # set to true and the radiation parameters and intermediate steps of the pv output calculation
# will be included in the output

bifacial = False
backside_efficiency = 1.0

snow_slide_modeling = False

power_rating = 1  # power in kw

timezone = "UTC"


def print_info():
    print("System location(WGS84): " + str(site_latitude) + ", " + str(site_longitude) + ".")
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
    issues with FMI forecast retrieval, but they will work with your own data and clearsky forecasts.
    :param latitude: WGS84 latitude as float. Valid values are -90 to 90.
    :param longitude: WGS84 longitude in float format. eq 60.4312. Valid values are -180 to 180.
    """

    global site_latitude
    global site_longitude

    if site_latitude != latitude or site_longitude != longitude:
        # at least one of the geolocation components was different
        # clearing cache, new location so data from old one can't be used anymore
        meps_loader.clear_cache()

    site_latitude = latitude
    site_longitude = longitude
    # print("Geolocation set at: " + str(site_latitude) + "°, " + str(site_longitude)+"°")


def force_clear_fmi_cache():
    """
    This package keeps a single FMI weather forecasts in memory in order to limit the amount of server calls.
    This function removes the forecast from memory. Calling any of the .get_fmi_XXX functions after clearing
    cache will request a new forecast and store it in cache.

    Cache will also be cleared if geolocation of the installation is changed. This is done because forecasts retrieved
    from FMI are only for a single point.

    This function was originally made to test if caching works, but I'm leaving it in for experimentation.
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
    # print("Panel angles set at tilt: " + str(panel_tilt)+ "°  Azimuth: " + str(panel_azimuth)+"°")


def set_extended_output(extended: bool):
    """
    Use this function to enable or disable additional variables in the PV forecasts.
    Most of these variables are irrelevant to users and thus extended output is disabled as default.
    :param extended: True -> additional variables will be given, False -> additional variables will be hidden.
    :return:
    """
    global extended_output
    extended_output = extended


def set_nominal_power_kw(nominal_power: float):
    """
    This function sets the power rating of the PV system. Value can be int/float, and it will be used to scale the simulated
    system output. Use a value that matches the power rating of the PV installation.

    :param nominal_power: Advertised power output of the PV system in standard conditions (perfect weather, direct sunlight)
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
    # print("Air temperature for clearsky simulations set at: " +
    # str(fmi_pv_forecast.helpers.default_parameters.air_temperature)+ "°C")


def set_default_wind_speed(wind_speed_ms: float):
    """
    This function will set the wind speed(in meters per second at 10m above ground) used by clearsky PV forecasts.
    FMI forecasts do not use the default value as wind speed at 10m is given by the forecast API.
    Wind transfers heat away from PV panels and decreases the difference between air temperature and panel temperature.
    """
    fmi_pv_forecaster.helpers.default_parameters.wind_speed = wind_speed_ms
    # print("Wind speed for clearsky simulations set at: " +
    # str(fmi_pv_forecast.helpers.default_parameters.wind_speed)+ "ms")


def set_module_elevation(module_elevation_m: float):
    """
    This function will set the physical module elevation(measured from ground, not sea level). Module elevation and
    wind speed at 10m are used together to estimate the wind at panel elevation.

    Higher than actual elevation can be used to compensate for really windy locations and exposed panels. Lower for
    sheltered panels.

    If you are processing external data with wind measured at panel elevation, use measured wind as wind value and
    set module elevation as 10m. This way exact wind speed measurements will be used.
    """

    fmi_pv_forecaster.helpers.default_parameters.panel_elevation = module_elevation_m



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
    FMI servers. This will result in unnecessary server calls and server may even refuse calls if load from your IP
    is too high.

    Having cache on will only make new server calls if data isn't cached yet, caching was done
    over a minute ago, geolocation was changed or cache was manually purged.
    """

    meps_loader.cache_enabled = cache_on

def set_bifacial(bifacial_on):
    """
    Bifaciality toggle, turning this on will estimate the PV output for a bifacial panel where front surface
    orientation matches the given panel angles.

    Current model is fairly simple, temperatures and efficiency might be off. Set a custom backside efficiency with
    .set_relative_bifacial_backside_efficiency()

    :param bifacial_on: Boolean value, True for on, False for off
    :return:
    """
    global bifacial
    bifacial = bifacial_on

def set_relative_bifacial_backside_efficiency(bs_efficiency):
    """
    Bifacial panels have wirings/logic on the backaside and thus backside is often a couple of percents worse at
    generating power than frontside. This varies between panels. This function can be used to set custom multipliers.


    :param bs_efficiency: Float in range of [0.7, 0.9] would be typical. 1.0 can be used for testing purposes.
    :return:
    """

    global relative_bifacial_backside_efficiency
    relative_bifacial_backside_efficiency = bs_efficiency

def set_snow_sliding(snow_on):
    """
    Turning snow sliding on will add column "snow sliding" into the model. This column represents the snow temperature.



    This is a toggle for turning snow sliding modeling on and off. Calculations are based on the Marion model
    and research on how well this works is currently ongoing.

    When on, this adds column "snow sliding" to output dataframe. Value in column is in celcius.
    If value is positive, snow sliding is likely to occur due to melting snow. If negative, snow sliding is unlikely.

    The further the value is from zero, the stronger the effect is.

    Each positive degree in the snow sliding column means that air is one degree warmer than it would have to be for
    snow to melt.
    """
    global snow_slide_modeling
    snow_slide_modeling = snow_on



def set_timezone(timezone_string):
    global timezone

    all_viable_timezones = pytz.all_timezones_set

    if timezone_string not in all_viable_timezones:
        raise ValueError("Given timezone \"" + str(timezone_string) + "\" is not in pytz.all_timezones. Timezone should"
                                                                      " be similar to \"Europe/Helsinki\", List of valid timezones can be found at "
                                                                      "https://en.wikipedia.org/wiki/List_of_tz_database_time_zones")

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

    clearsky_estimate = meps_loader.__get_irradiance_pvlib(site_latitude, site_longitude,
                                                           interval_start, interval_end, timestep)

    return clearsky_estimate



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
    additional columns "T", "wind" and "albedo" are also useful. Those contain the ambient air temperature, wind speed
    and ground reflectivity. If not included in the dataframe, defaults from the package are used. Those defaults can
    be adjusted with .set_default_xxx -functions.

    time column is the exact mathematical point for which each row in the data is simulated for. So if this is wrong,
    sun position will be wrong, and you will get wrong results.

    Since weather at 18:00 can represent the exact weather at 18:00, or the average of 17:00 to 18:00. You need to
    figure out how times are indexed in your dataset.

    With FMI radiation data, timestamp 18:00 represent time interval of 17:00 to 18:00, which is why a 30-minute time
    shift is needed.
    """

    #print("bifacial check")
    if bifacial:
        #print("was bifacial, using bifacial processing instead")
        return process_radiation_df_bifacial(data)

    #print("was not bifacial, using common processing instead")

    if panel_tilt is None or panel_azimuth is None:
        raise ValueError(
            "Tilt and azimuth must be defined before PV output is estimated."
            " Call pv_forecast.set_angles(tilt, azimuth) first with"
            " valid 0-90, 0-360 degree panel angles."
        )

    if "cloud_cover" not in data.columns:
        # If using pvlib clearsky data, there will not be a cloud cover column. Added here for compatibility.
        data["cloud_cover"] = 0

    # print(data)
    # print(data.columns)

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

    if snow_slide_modeling:
        #print("Snow slide modeling is on")
        # uses a modified marion model, has to be after step 5 due to T requirement, which is only added to the data in
        # step 5 if it is missing.
        """
        Marion model:
        T_ambient > Gpoa/-80
        """
        data["degrees above snowsliding"] = data["T"]+data["poa"]/80

    # step 6. estimate power output
    data = output_estimator.add_output_to_df(data)

    if not extended_output:
        # if extended output not in use, return only some columns
        if snow_slide_modeling:
            return data[["T", "wind", "module_temp","degrees above snowsliding", "output"]]
        else:
            return data[["T", "wind", "module_temp", "output"]]

    return data

def process_radiation_df_bifacial(data_in):
    """
    This function processes a radiation dataframe and estimates the output of a pv system.

    The input df must have columns:
    'time', 'dni', 'dhi', 'ghi'
    additional columns "T", "wind" and "albedo" are also useful

    time column is the mathematical point for which each row in the data is simulated for.
    Since weather at 18:00 represents weather between 17:00 and 18:00, the time column is often index-30min
    """

    if "cloud_cover" not in data_in.columns:
        # If using pvlib clearsky data, there will not be a cloud cover column. Added here for compatibility.
        data_in["cloud_cover"] = 0

    # panel main surface:
    data_a = data_in.copy()
    # panel back surface:
    data_b = data_in.copy()

    if panel_tilt is None or panel_azimuth is None:
        raise ValueError(
            "Tilt and azimuth must be defined before PV output is estimated."
            " Call pv_forecast.set_angles(tilt, azimuth) first with"
            " valid 0-90, 0-360 degree panel angles."
        )



    #print("########### phase 1:")
    #print("data a:")
    #print_full(data_b)
    #print("data b:")
    #print_full(data_b)

    # step 2. project irradiance components to plane of array:
    # panel front surface, same as always
    data_a = irradiance_transpositions.irradiance_df_to_poa_df(data_a, site_latitude, site_longitude, panel_tilt,
                                                             panel_azimuth)





    # panel back surface, requires recomputation of panel angles
    azimuth_b = (panel_azimuth + 180) % 360
    tilt_b = 180-panel_tilt

    #print("azimuth_b: " + str(azimuth_b))
    #print("tilt_b: " + str(tilt_b))
    data_b = irradiance_transpositions.irradiance_df_to_poa_df(data_b, site_latitude, site_longitude, tilt_b,
                                                             azimuth_b)

    #print("########### phase 2:")
    #print("tilt_a: " + str(panel_tilt))
    #print("azimuth_a: " + str(panel_azimuth))
    #print("data a:")
    #print_full(data_b)
    #print("azimuth_b: " + str(azimuth_b))
    #print("tilt_b: " + str(tilt_b))
    #print("data b:")
    #print_full(data_b)

    # step 3. simulate how much of irradiance components is absorbed:
    data_a = reflection_estimator.add_reflection_corrected_poa_components_to_df(data_a, site_latitude, site_longitude,
                                                                              panel_tilt, panel_azimuth)

    data_b = reflection_estimator.add_reflection_corrected_poa_components_to_df(data_b, site_latitude, site_longitude,
                                                                              tilt_b, azimuth_b)





    # step 4. compute sum of reflection-corrected components:
    #print("Phase 4")
    data_a = reflection_estimator.add_reflection_corrected_poa_to_df(data_a)

    data_b = reflection_estimator.add_reflection_corrected_poa_to_df(data_b)

    #print(data_a)
    #print(data_a.columns)
    #print(data_b)
    #print(data_b.columns)

    output = data_a.copy()

    # 'time', 'ghi', 'dni', 'dhi', 'cloud_cover', 'dni_poa', 'dhi_poa',
    #        'ghi_poa', 'poa', 'dni_rc', 'dhi_rc', 'ghi_rc', 'poa_ref_cor'

    output["dni_poa_back"] = data_b["dni_poa"]
    output["dhi_poa_back"] = data_b["dhi_poa"]
    output["ghi_poa_back"] = data_b["ghi_poa"]

    output["dni_rc_back"] = data_b["dni_rc"]
    output["dhi_rc_back"] = data_b["dhi_rc"]
    output["ghi_rc_back"] = data_b["ghi_rc"]

    # adding absorbed radiation values for front, back and both sides.
    output["poa_ref_cor_front"] = data_a["poa_ref_cor"]
    output["poa_ref_cor_back"] = data_b["poa_ref_cor"]

    # adding both here at 100% for temperature calculations
    output["poa_ref_cor"] = output["poa_ref_cor_front"] + output["poa_ref_cor_back"]

    #print("phase 5")

    # step 5. estimate panel temperature based on wind speed, air temperature and absorbed radiation
    output = panel_temperature_estimator.add_estimated_panel_temperature(output)

    # Rewriting the total absorbed radiation using backsíde efficiency as a backside multiplier.
    # This may appear odd, but I'm making the assumption that backside efficiency doesn't matter when it comes to
    # temperatures, but it does matter for output estimation.
    output["poa_ref_cor"] = output["poa_ref_cor_front"] + output["poa_ref_cor_back"]*backside_efficiency

    # step 6. estimate power output
    output = output_estimator.add_output_to_df(output)

    if not extended_output:
        # if extended output not in use, return only some columns
        #print("output not extended, returning minimal set of values")
        return output[["T", "wind", "module_temp", "output"]]

    #print("output was extended, returning all values")
    return output

"""
Flexible forecast functions with custom intervals:
"""


def get_clearsky_forecast_for_interval(interval_start, interval_end, timestep=60):
    """
    Returns an optimistic weather-unaware PV production for selected time interval using selected timestep.
    This clearsky forecast uses constant or given air temp, wind speed and albedo values. Set them with
    .set_default_air_temp, .set_default_albedo, .set_default_wind_speed

    :param interval_start: Datetime with year, month, day, hour. Minute and second will be ignored and set to zero.
    :param interval_end:  Datetime with year, month, day, hour. Minute and second will be ignored and set to zero.
    :param timestep: Minutes between rows in forecast. Only tested with integers.
    :return: DF with columns: datetime index, T, wind, module_temp, output. T is ambient air temperature in C. wind is
    wind speed in m/s.

    Example: interval_start = datetime(2026-08-17 13:20), interval_end = datetime(2026-08-17 13:20), timestep = 10
    Output:
                                T  wind  module_temp       output
    2026-08-17 13:00:00+00:00  20     2    39.187484  2581.720278
    2026-08-17 13:10:00+00:00  20     2    38.527107  2499.579738
    2026-08-17 13:20:00+00:00  20     2    37.833034  2412.422395
    2026-08-17 13:30:00+00:00  20     2    37.106726  2320.309278
    ...
    2026-08-18 12:50:00+00:00  20     2    39.691894  2643.946165
    2026-08-18 13:00:00+00:00  20     2    39.064610  2566.494637

    """



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


    interval_start = datetime.datetime(year=interval_start.year, month=interval_start.month, day=interval_start.day,
                                       hour=interval_start.hour, minute=0)

    interval_end = datetime.datetime(year=interval_end.year, month=interval_end.month, day=interval_end.day,
                                       hour=interval_end.hour, minute=0)

    # step 1. getting clearsky radiation
    data = __get_clearsky_radiation_for_interval(interval_start, interval_end, timestep)

    # processing data with our pv model
    data = process_radiation_df(data)

    return data


def get_fmi_forecast_for_interval(interval_start, interval_end):
    """
    Loads the complete fmi forecast and returns a subsection.

    Uses cache so if this or any other fmi function has been recently called, no additional server calls will be made.

    :param interval_start: Datetime, Start time for subsection
    :param interval_end: Datetime, End time for subsection
    :return:
    """
    default_fmi_forecast = get_default_fmi_forecast()
    return default_fmi_forecast.loc[interval_start:interval_end]


"""
Fixed interval forecast functions begin here
"""


def __get_fmi_forecast_rad_data():
    """
    This is a helper function for getting radiation data from FMI.
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

    data = get_fmi_forecast_for_interval(interval_start, interval_end)

    return data


def get_default_fmi_forecast(interpolate=False):
    """
    This function returns the whole 66~ish hour FMI forecast available at this moment in time.
    Timestamps in the forecast are every 60 minutes with a 30min offset. 12:30, 13:30 and so on, using UTC time.
    :param interpolate: Default false will skip interpolation. Interpolate = "15min" will result in interpolated
    forecasts where power values are at 12:00, 12:15, 12:30...

    Interpolation works nicely with values which divide 60 into integers.
    30, 20, 15, 12, 10, 6, 5, 4, 3, 2, 1.

    :return:
    """

    # getting the hourly 66-hour forecast
    data = __get_fmi_forecast_rad_data()

    # if interpolation is left False, interpolation will not be done
    if interpolate is not False:
        # resampling to given time resolution, "15min" perhaps?
        data = data.resample(interpolate).asfreq()

        # interpolating nans from resampling
        data = data.interpolate(method="linear")
        # Note, this function supports other interpolation methods. Got a bunch of errors with them, but in theory
        # some interpolation functions could result in nicer output.

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


def get_default_clearsky_forecast(timestep=60):
    """
    This function returns an approximation for the clearsky PV output during a time window which should cover the
    FMI forecast based PV output from "get_default_fmi_forecast()"

    Forecast will have 60 minute time resolution, 70 hours of measurements and first measurement will be at xx:00 where
    xx is current hour.

    This clearsky forecast relies on default wind speed, air temperature and albedo built into the package. Adjust them
    with functions .set_default_air_temp, .set_default_albedo, .set_default_wind_speed

    :param timestep: Timestep in minutes between rows of the forecast. Default is 60.
    """

    time_start = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None) - datetime.timedelta(hours=3)
    time_start = datetime.datetime(time_start.year, time_start.month, time_start.day, time_start.hour)
    time_end = time_start + datetime.timedelta(hours=68)

    data = get_clearsky_forecast_for_interval(
        time_start,
        time_end,
        timestep)

    return data


# Custom hour/day functions below this line

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
    """
    This is a somewhat odd function. It will return the FMI weather forecast based PV forecast at the given time as
    long as the time is within the forecast window.

    So if you want to get the PV power today at this very second(12:43:33 for example), then this is the function to use.
    As the package uses cached FMI forecasts, you could call this function in a loop a thousand times if you really
    wanted to, without that resulting in any additional network traffic.

    Note that since this uses linear interpolation, outputs are just approximations of likely current output.


    :param given_time: datetime with seconds. Has to be within the approximate interval of [now, now+60hours]
    :return:
    """


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
        timestamp1 = (datetime.datetime(time_value.year, time_value.month, time_value.day, time_value.hour, 30)
                      - datetime.timedelta(minutes=60))
        timestamp2 = datetime.datetime(time_value.year, time_value.month, time_value.day, time_value.hour, 30)

    elif minute >= 30:
        timestamp1 = datetime.datetime(time_value.year, time_value.month, time_value.day, time_value.hour,
                                       30)
        timestamp2 = (datetime.datetime(time_value.year, time_value.month, time_value.day, time_value.hour, 30)
                      + datetime.timedelta(minutes=60))

    # distances between given time value and surrounding values

    if timestamp1 not in power_df.index or timestamp2 not in power_df.index:
        return None

    # print("timevalue:" + str(time_value))
    # print("timestamp1:" + str(timestamp1))
    # print("timestamp2:" + str(timestamp2))
    time_from1 = time_value - timestamp1  # a = X_pos - A_pos
    time_from2 = timestamp2 - time_value  # b = B_pos- X_pos
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
    fractional_distance_from1 = 1 - time_from1 / total_time  # 1-a/C
    fractional_distance_from2 = 1 - time_from2 / total_time  # 1-b/C

    # rows between which to interpolate
    row1 = power_df.loc[str(timestamp1)].copy()
    row2 = power_df.loc[str(timestamp2)].copy()

    # interpolated row
    interpolated_row = row1 * fractional_distance_from1 + row2 * fractional_distance_from2

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

    if idx.tz is None:  # handling aware and naive situations with separate functions
        idx = idx.tz_localize("UTC")
    else:
        idx = idx.tz_convert("UTC")

    # this avoids setting with copy warning.
    df = df.copy()
    df["local_time"] = idx.tz_convert(tz)

    return df


def get_fmi_radiation_forecast():
    """
    This function doesn't return a PV forecast, but rather the radiation and weather forecast that the PV forecast
    is based on.

    If you want to examine radiation forecasts or modify them in some way, you could call this function and
    .process_radiation_df(df) with the output of this function as an input.
    :return:
    """
    interval_start = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None) - datetime.timedelta(hours=6)
    # the line above creates a timezone naive utc timestamp. If timezone is included, server will return errors.
    # if time is local time, starting values will be wrong
    # looking 4 hours into the past just for some historical data to be included.

    interval_end = interval_start + datetime.timedelta(hours=70)

    if site_latitude is None or site_longitude is None:
        raise ValueError(
            "Latitude and longitude must be defined before PV output is estimated."
            "Call pv_forecast.set_location(latitude, longitude) first with"
            " valid WGS84 coordinates."
        )


    data = get_fmi_forecast_for_interval(interval_start, interval_end)

    return data