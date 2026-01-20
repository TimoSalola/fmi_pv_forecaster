# System parameters
from .pv_forecaster import set_angles
from .pv_forecaster import set_location
from .pv_forecaster import set_nominal_power_kw
from .pv_forecaster import set_timezone
from .pv_forecaster import get_timezone
from .pv_forecaster import set_clearsky_fc_timestep
from .pv_forecaster import set_clearsky_fc_time_offset

# optional system parameters
from .pv_forecaster import set_module_elevation

# clearsky system parameters
from .pv_forecaster import set_default_albedo
from .pv_forecaster import set_default_air_temp
from .pv_forecaster import set_default_wind_speed

# Forecast functions
from .pv_forecaster import get_default_fmi_forecast
from .pv_forecaster import get_default_clearsky_estimate
from .pv_forecaster import get_fmi_forecast_for_interval
from .pv_forecaster import get_clearsky_estimate_for_interval

from .pv_forecaster import get_fmi_forecast_at_interpolated_time

# toggles
from .pv_forecaster import set_extended_output
from .pv_forecaster import set_cache

# external usage
from .pv_forecaster import process_radiation_df

# debug
from .pv_forecaster import force_clear_fmi_cache

from .pv_forecaster import add_local_time_column



__all__ = [
    #system parameters
    "set_angles",
    "set_location",
    "set_nominal_power_kw",
    "set_timezone",
    "get_timezone",
    "set_clearsky_fc_timestep",
    "set_clearsky_fc_time_offset",


    "add_local_time_column",

    # optional system parameters
    "set_module_elevation",

    # clearsky system parameters
    "set_default_albedo",
    "set_default_wind_speed",
    "set_default_air_temp",

    # forecast functions
    "get_default_fmi_forecast",
    "get_default_clearsky_estimate",
    "get_clearsky_estimate_for_interval",
    "get_fmi_forecast_for_interval",
    "get_fmi_forecast_at_interpolated_time",

    # toggles
    "set_extended_output",
    "set_cache",

    # external usage
    "process_radiation_df",

    # debug
    "force_clear_fmi_cache"

    ]

__version__ = "0.1.0"