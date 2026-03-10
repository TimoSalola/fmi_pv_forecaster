import datetime

import numpy
import numpy as np

import fmi_pv_forecaster.helpers.output_estimator as output_estimator
import fmi_pv_forecaster.helpers.irradiance_transpositions as irradiance_transpositions
import fmi_pv_forecaster.helpers.astronomical_calculations as astronomical_calculations
import random

def test_power_output_estimation_function():
    """
    This function tests if the power output estimation function is outputting reasonable values.
    """

    random.seed(1)

    for i in range(0, 100):
        kwh_rating1 = random.randint(1,100)
        kwh_rating2 = random.randint(1, 100)
        panel_temp = random.randint(-40, 100)

        absorbed_radiation = random.random()*1000
        output_estimator.rated_power = kwh_rating1
        estimated_output1 = output_estimator.__estimate_output(absorbed_radiation, panel_temp)
        output_estimator.rated_power = kwh_rating2
        estimated_output2 = output_estimator.__estimate_output(absorbed_radiation, panel_temp)

        #print("Nominal power 1: " +str(kwh_rating1))
        #print("Nominal power 2: " +str(kwh_rating2))
        #print("absorbed radiation: " + str(absorbed_radiation))
        #print("Power 1: " +str(estimated_output1))
        #print("Power 2: " + str(estimated_output2))
        #print("Upper limit1: " + str(absorbed_radiation*kwh_rating1))
        #print("Upper limit2: " + str(absorbed_radiation * kwh_rating2))
        #print("Power ratio: " + str(rating_ratio))
        #print("panel temp: " + str(panel_temp))

        assert np.issubdtype(type(estimated_output1), np.floating), (
            # np.floating is a group in which all numpy.float -types belong to. Type seems to be float64 but
            # being careful here, perhaps on some systems the package returns a float32 or some other.
            print("Output type was not numpy float, type was instead: " + str(type(estimated_output1)))
        )

        assert estimated_output1 >= 0, (
            "Estimated power output was negative, this should never happen."
        )
        assert estimated_output1 < absorbed_radiation*kwh_rating1*1.01, (
            # including a 1% margin due to floating point errors.
            "Estimated power was greater than absorbed radiation, this should never happen.",
            str(estimated_output1) + " < " + str(absorbed_radiation*kwh_rating1)
        )

        # power rating values should be just simple multipliers, this bit tests if both estimated power values are
        # within a 2% range when scaling is reversed
        assert estimated_output1/kwh_rating1  >= (estimated_output2/kwh_rating2) * 0.98, (
            "Nominal system power scaling does not appear to be linear."
        )

        assert estimated_output1/kwh_rating1 <= (estimated_output2/kwh_rating2) * 1.02, (
            "Nominal system power scaling does not appear to be linear."
        )


    print("Power output function is returning values which seem physically possible and reasonable.")


"""
IRRADIANCE TRANSPOSITION MINI FUNCTION TESTS
"""


def test_ghi_transposition():

    for i in range(0, 100):
        ghi = random.random()*1000
        tilt = random.randint(0,90)
        albedo = random.random()

        transposed_irradiance = irradiance_transpositions.__project_ghi_to_panel_surface(ghi, tilt, albedo)

        print(transposed_irradiance)

        assert transposed_irradiance >= 0, (
            "Transposed ghi was negative, this should never happen."
        )

        assert transposed_irradiance <= ghi, (
            "Transposed ghi was greater than ghi, this should never happen."
        )

    print("Tested 100 random ghi transpositions, no obvious faults found.")

def test_dhi_transposition_tilt0():
    """
    This function tests dhi transpositions, proper testing is unfortunately difficult so this just checks physical
    impossibilities.

    This set of tests focuses on tilt 0 cases as these tend to be easier to check.

    Only the isotropic model is easy to understand, it will always equal to dhi when tilt is 0.
    Both perez and perez_driesse models start to decrease when AOI is 85+
    This might be unwanted since if DHI is 100W/m² and panel tilt is 0, panels should receive 100w of dhi radiation
    no matter where the sun is positioned.

    """

    for i in range(0, 300):

        time = datetime.datetime.now()

        dhi = round(random.random()*300, 2)
        dni = round(random.random()*1000, 2)
        latitude = round(random.random()*90, 2)
        longitude = round(180-random.random()*360, 2)

        tilt = 0 #random.randint(0,90)
        azimuth = random.randint(0, 360)

        aoi = round(
            astronomical_calculations.get_solar_angle_of_incidence_fast(time, latitude, longitude, tilt, azimuth), 2)


        irradiance_driesse = round(irradiance_transpositions.__project_dhi_to_panel_surface_perez_fast(time, dhi, dni,
                                latitude, longitude, tilt, azimuth), 2)

        irradiance_perez = round(
            irradiance_transpositions.__project_dhi_to_panel_surface_perez_fast(time, dhi, dni,
                                       latitude, longitude, tilt, azimuth, driesse=False), 2)

        irradiance_isotropic = irradiance_transpositions.__project_dhi_to_panel_surface(dhi, tilt)

        """
        print("=====")
        print("dni: " + str(dni)+"w")
        print("dhi: " + str(dhi)+"w")
        print("tilt: " + str(tilt)+"deg")
        print("azimuth: " + str(azimuth)+"deg")
        print("aoi: " + str(aoi)+"deg")
        print("Transposed irradiances:")
        print("Driesse: " + str(irradiance_driesse) +"w")
        print("Perez: " + str(irradiance_perez) + "w")
        print("Isotropic:: " + str(irradiance_isotropic) + "w")
        print("=====")
        """

        # negative tests
        assert irradiance_driesse >= 0, (
            "Driesse transposed dhi was negative, this should never happen." + str(irradiance_driesse)
        )

        assert irradiance_perez >= 0, (
                "Perez transposed dhi was negative, this should never happen." + str(irradiance_perez)
        )

        assert irradiance_isotropic >= 0, (
                "Isotropic transposed dhi was negative, this should never happen." + str(irradiance_isotropic)
        )

        # higher than dhi tests
        assert irradiance_driesse <= dhi, (
            "Driesse transposed dhi was greater than dhi, this should never happen."
        )
        assert irradiance_perez <= dhi, (
            "Perez transposed dhi was greater than dhi, this should never happen."
        )
        assert irradiance_isotropic <= dhi, (
            "Transposed dhi was greater than dhi, this should never happen."
        )



        # isotropic tests
        assert irradiance_isotropic == dhi, (
            "Isotropic projection model should result in dhi projection values equal to dhi when panel tilt is 0."
        )

        assert irradiance_isotropic >= irradiance_perez, (
            "Perez model should not result in values higher than isotropic."
        )
        assert irradiance_isotropic >= irradiance_perez, (
            "Perez-driesse model should not result in values higher than isotropic."
        )

    print("Tested 300 random dhi transpositions at tilt = 0 using otherwise random inputs. No faults found.")


def test_dhi_transposition_random_panel_angles():
    """
    This function tests dhi transpositions, proper testing is unfortunately difficult so this just checks physical
    impossibilities.

    This tests random panel angles. Results are more random and fewer restrictions are in place.
    """

    for i in range(0, 300):
        time = datetime.datetime.now()

        dhi = round(random.random() * 300, 2)
        dni = round(random.random() * 1000, 2)
        latitude = round(random.random() * 90, 2)
        longitude = round(180 - random.random() * 360, 2)

        tilt = random.randint(0,90)
        azimuth = random.randint(0, 360)

        aoi = round(
            astronomical_calculations.get_solar_angle_of_incidence_fast(time, latitude, longitude, tilt, azimuth), 2)

        irradiance_driesse = round(irradiance_transpositions.__project_dhi_to_panel_surface_perez_fast(time, dhi, dni,
                                                                                                       latitude,
                                                                                                       longitude, tilt,
                                                                                                       azimuth), 2)

        irradiance_perez = round(
            irradiance_transpositions.__project_dhi_to_panel_surface_perez_fast(time, dhi, dni,
                                                                                latitude, longitude, tilt, azimuth,
                                                                                driesse=False), 2)

        irradiance_isotropic = irradiance_transpositions.__project_dhi_to_panel_surface(dhi, tilt)

        # negative tests
        assert irradiance_driesse >= 0, (
                "Driesse transposed dhi was negative, this should never happen." + str(irradiance_driesse)
        )

        assert irradiance_perez >= 0, (
                "Perez transposed dhi was negative, this should never happen." + str(irradiance_perez)
        )

        assert irradiance_isotropic >= 0, (
                "Isotropic transposed dhi was negative, this should never happen." + str(irradiance_isotropic)
        )

        # higher than dhi tests
        assert irradiance_isotropic <= dhi, (
            "Transposed dhi was greater than dhi, this should never happen."
        )

    print("Tested 300 random dhi transpositions with all random inputs. No faults found.")
