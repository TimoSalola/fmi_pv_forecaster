from matplotlib import pyplot as plt
import fmi_pv_forecaster as pvfc

# setting parameters:
pvfc.set_location(65, 25)
pvfc.set_angles(90, 270)
pvfc.set_extended_output(True)

# checking the radiation parameters that forecasts normally receive:
#rad_data = pvfc.get_fmi_radiation_forecast()
# ['dni', 'dhi', 'ghi', 'albedo', 'T', 'wind', 'cloud_cover']

# generating a normal clearsky forecast, so we can extract radiation parameters from it
clearsky_forecast = pvfc.get_default_clearsky_forecast(timestep=10)

# required params for forecasting from clearsky model
clearsky_rad = clearsky_forecast[["ghi", "dni", "dhi", "T", "wind"]].copy()


# generating forecast 1
forecast1 = pvfc.process_radiation_df(clearsky_rad)

# adding dni and dhi shading multipliers to radiation data
clearsky_rad["dni_shading"] = 0.1
clearsky_rad["dhi_shading"] = 0.3

# generating forecast 2
forecast2 = pvfc.process_radiation_df(clearsky_rad)

# figure base:
fig, ax = plt.subplots(figsize=(12, 6))

ax.grid(True)
ax.legend(loc="upper right")
ax.set_xlabel("time")
ax.set_ylabel("output power")
plt.title("shading test")

# plotting shaded and unshaded results:
ax.plot(forecast1.index,forecast1["output"], label="Unshaded output")
ax.plot(forecast2.index,forecast2["output"], label="Shaded output")

# showing plot
plt.legend(loc="upper right")
plt.tight_layout()
plt.show()


