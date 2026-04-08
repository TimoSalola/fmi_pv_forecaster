


import fmi_pv_forecaster as pvfc

pvfc.set_location(64, 25)
pvfc.set_angles(35, 200)
pvfc.set_default_albedo(0.7)

pvfc.set_bifacial(True)

data = pvfc.get_default_clearsky_forecast(120)


print("n")

print(data)


