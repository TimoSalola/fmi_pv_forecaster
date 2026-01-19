from datetime import datetime, timedelta

from fmi_pv_forecaster import meps_loader
from fmi_pv_forecaster.meps_loader import get_solar_azimuth_zenit_fast
import pandas


def test_get_solar_azimuth_zenit_fast():

    print("\n----------")
    print("Testing Sun angle estimation function")
    dt = datetime(2025, 6, 21, 12, 0)  # noon on summer solstice
    lat = 59.3293    # Stockholm latitude
    lon = 18.0686    # Stockholm longitude

    azimuth, zenith = get_solar_azimuth_zenit_fast(dt, lat, lon)

    # Test return types
    assert isinstance(azimuth, pandas.Series)
    assert isinstance(zenith, pandas.Series)

    # that index consists of timestamps
    assert isinstance(azimuth.index[0], pandas.Timestamp)
    assert isinstance(zenith.index[0], pandas.Timestamp)

    print("Sun angle testing complete.")
    print("----------")


def test_fmi_opendata_data_retrieval():
    print("\n----------")
    print("Testing fmi open data retrieval for this moment in time")


    lat = 60.2044
    lon = 24.9625


    today = datetime.now()
    date_start = datetime(today.year, today.month, today.day)


    date_end = date_start + timedelta(days=4, minutes=-1)

    print("Time requested for interval: " + str(date_start)+ " to " + str(date_end))


    meps_data = meps_loader.collect_fmi_opendata(lat, lon, date_start, date_end)



    if isinstance(meps_data, str):
        assert meps_data == "No observations found"

    #print("index values")
    #print(meps_data.index[0])
    #print(meps_data.index[-1])

    data_len_in_hours_with_nans = (meps_data.index[-1] - meps_data.index[0]).total_seconds() / 3600

    print("Got data for " + str(data_len_in_hours_with_nans) + " hours.")

    meps_data = meps_data.dropna()

    #print("index values")
    #print(meps_data.index[0])
    #print(meps_data.index[-1])

    data_len_in_hours_with_no_nans = (meps_data.index[-1]- meps_data.index[0]).total_seconds() / 3600

    print("Out of which " + str(data_len_in_hours_with_no_nans) + " hours remain after removing nans.")


    assert data_len_in_hours_with_no_nans >= 64.0 , "Got less than 64 hours of forecast data from FMI forecast service."

    print("FMI open data retrieval for this moment complete")
    print("----------")





def test_clearsky_estimator():
    print("\n----------")
    print("Testing pvlib clearsky estimation. This should always work with no issues.")


    lat = 60
    lon = 24

    date_start = datetime.now()
    date_end = date_start + timedelta(days=3, minutes=-1)

    clearsky = meps_loader.__get_irradiance_pvlib(lat, lon, date_start, date_end)

    print(clearsky)

    print("PVlib clearsky testing done.")
    print("----------")





