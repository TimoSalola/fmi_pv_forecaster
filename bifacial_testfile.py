from matplotlib import pyplot as plt

import fmi_pv_forecaster as pvfc




latitude = 64
longitude = 25
tilt1 = 90
azimuth1 = 200

tilt2 = None
azimuth2 = None

azimuth2 = azimuth1
tilt2 = tilt1 + 180


pvfc.set_location(latitude, longitude)
pvfc.set_angles(tilt1, azimuth1)

pvfc.set_extended_output(True)

data1 = pvfc.get_default_clearsky_forecast(10)

pvfc.set_angles(tilt1 + 180, azimuth1)
data2 = pvfc.get_default_clearsky_forecast(10)

print(data1.columns)


fig, ax = plt.subplots(4,3)

ax1 = ax[0,0]
ax2 = ax[1,0]
ax3 = ax[2,0]
ax4 = ax[3,0]

ax5 = ax[0,1]
ax6 = ax[1,1]
ax7 = ax[2,1]
ax8 = ax[3,1]


ax9 = ax[0,2]
ax10 = ax[1,2]
ax11 = ax[2,2]
ax12 = ax[3,2]

### col 1
ax1.set_title('DNI')
ax1.plot(data1.index, data1["dni_poa"], label="panel 1 dni_poa")
ax1.plot(data2.index, data2["dni_poa"], label="panel 2 dni_poa")
ax1.legend()

ax2.set_title('DHI')
ax2.plot(data1.index, data1["dhi_poa"], label="panel 1 dhi_poa")
ax2.plot(data2.index, data2["dhi_poa"], label="panel 2 dhi_poa")
ax2.legend()

ax3.set_title('GHI')
ax3.plot(data1.index, data1["ghi_poa"], label="panel 1 ghi_poa")
ax3.plot(data2.index, data2["ghi_poa"], label="panel 2 ghi_poa")
ax3.legend()

ax4.set_title('Outputs')
ax4.plot(data1.index, data1["output"], label="Angles 1, a: " + str(azimuth1)+ " t: " + str(tilt1))
ax4.plot(data2.index, data2["output"], label="Angles 2, a: " + str(azimuth1)+ " t: " + str(tilt1+180))
ax4.legend()


## col 2

ax5.set_title('Panel set 1 radiation values')
ax5.plot(data1.index, data1["dni"], label="dni")
ax5.plot(data1.index, data1["dni_poa"], label="panel 1 dni_poa")
ax5.plot(data1.index, data1["dni_rc"], label="panel 1 dni_rc")
ax5.legend()


ax6.plot(data1.index, data1["dhi"], label="dhi")
ax6.plot(data1.index, data1["dhi_poa"], label="panel 1 dhi_poa")
ax6.plot(data1.index, data1["dhi_rc"], label="panel 1 dhi_rc")
ax6.legend()

ax7.plot(data1.index, data1["ghi"], label="ghi")
ax7.plot(data1.index, data1["ghi_poa"], label="panel 1 ghi_poa")
ax7.plot(data1.index, data1["ghi_rc"], label="panel 1 ghi_rc")
ax7.legend()

#### col 3

ax9.set_title('Panel set 2 radiation values')
ax9.plot(data2.index, data2["dni"], label="dni")
ax9.plot(data2.index, data2["dni_poa"], label="panel 2 dni_poa")
ax9.plot(data2.index, data2["dni_rc"], label="panel 2 dni_rc")
ax9.legend()


ax10.plot(data2.index, data2["dhi"], label="dhi")
ax10.plot(data2.index, data2["dhi_poa"], label="panel 2 dhi_poa")
ax10.plot(data2.index, data2["dhi_rc"], label="panel 2 dhi_rc")
ax10.legend()

ax11.plot(data2.index, data2["ghi"], label="ghi")
ax11.plot(data2.index, data2["ghi_poa"], label="panel 2 ghi_poa")
ax11.plot(data2.index, data2["ghi_rc"], label="panel 2 ghi_rc")
ax11.legend()




plt.show()




