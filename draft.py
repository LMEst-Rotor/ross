import numpy as np
import scipy
import toml

import ross as rs
from ross.defects import *
from ross.defects.misalignment import misalignment_flex_parallel_example

steel = rs.materials.steel
steel.rho = 7.85e3
steel.E = 2.17e11
#  Rotor with 6 DoFs, with internal damping, with 10 shaft elements, 2 disks and 2 bearings.
i_d = 0
o_d = 0.019
n = 33

# fmt: off
L = np.array(
        [0  ,  25,  64, 104, 124, 143, 175, 207, 239, 271,
         303, 335, 345, 355, 380, 408, 436, 466, 496, 526,
         556, 586, 614, 647, 657, 667, 702, 737, 772, 807,
         842, 862, 881, 914]
         )/ 1000
# fmt: on

L = [L[i] - L[i - 1] for i in range(1, len(L))]

shaft_elem = [
    rs.ShaftElement6DoF(
        material=steel,
        L=l,
        idl=i_d,
        odl=o_d,
        idr=i_d,
        odr=o_d,
        alpha=8.0501,
        beta=1.0e-5,
        rotary_inertia=True,
        shear_effects=True,
    )
    for l in L
]

Id = 0.003844540885417
Ip = 0.007513248437500

disk0 = rs.DiskElement6DoF(n=12, m=2.6375, Id=Id, Ip=Ip)
disk1 = rs.DiskElement6DoF(n=24, m=2.6375, Id=Id, Ip=Ip)

kxx1 = 4.40e5
kyy1 = 4.6114e5
kzz = 0
cxx1 = 27.4
cyy1 = 2.505
czz = 0
kxx2 = 9.50e5
kyy2 = 1.09e8
cxx2 = 50.4
cyy2 = 100.4553

bearing0 = rs.BearingElement6DoF(
    n=4, kxx=kxx1, kyy=kyy1, cxx=cxx1, cyy=cyy1, kzz=kzz, czz=czz
)
bearing1 = rs.BearingElement6DoF(
    n=31, kxx=kxx2, kyy=kyy2, cxx=cxx2, cyy=cyy2, kzz=kzz, czz=czz
)

rotor = rs.Rotor(shaft_elem, [disk0, disk1], [bearing0, bearing1])
# rotor.plot_rotor().show()

# misalignment = MisalignmentFlex(
#     dt=0.0001,
#     tI=0,
#     tF=50,
#     kd=40 * 10 ** (3),  # Rigidez radial do acoplamento flexivel
#     ks=38 * 10 ** (3),  # Rigidez de flexão do acoplamento flexivel
#     eCOUPx=2 * 10 ** (-4),  # Distancia de desalinhamento entre os eixos - direcao x
#     eCOUPy=2 * 10 ** (-4),  # Distancia de desalinhamento entre os eixos - direcao z
#     misalignment_angle=15 * np.pi / 180,  # Angulo do desalinhamento angular (rad)
#     TD=0,  # Torque antes do acoplamento
#     TL=0,  # Torque dopois do acoplamento
#     n1=0,
#     speed=1200,
#     mis_type="angular",
# )

## MISALIGNMENT
probe1 = (14, 0)
probe2 = (22, 0)
# response = rotor.run_misalignment(misalignment)
# response.plot_1d(probe=[probe1, probe2]).show()

misalignment = MisalignmentRigid(
    tI=0,
    tF=30,
    Kcoup_auxI=0.5,
    Kcoup_auxF=0.5,
    kCOUP=2e5,
    eCOUP=2e-4,
    TD=0,
    TL=0,
    n1=0,
    speed=1200,
)

# misalignmentrigid = rotor.run_misalignment(misalignmentrigid)
# misalignmentrigid.plot_time_response([probe1, probe2]).show()
# misalignmentrigid.plot_dfft([probe1, probe2], log=True).show()

misalignment = rotor.run_misalignment(misalignment)
misalignment.plot_time_response([probe1, probe2]).show()
misalignment.plot_dfft([probe1, probe2], log=True).show()
# # TIME RESPONSE

# node = 14
# t = np.linspace(0, 10, 1000)
# F = np.zeros((len(t), rotor.ndof))
# F[:, 6 * node] = 10 * np.cos(2 * t)
# F[:, 6 * node + 1] = 10 * np.sin(2 * t)

# response = rotor.run_time_response(speedI * np.pi / 30, F, t)

# response.plot_1d(probe=[probe1, probe2]).show()

# # UNBALANCE RESPONSE
#
# response = rotor.run_unbalance_response(
#     [12, 24],
#     [100e-06, 130e-06],
#     [-np.pi / 2, -np.pi / 2],
#     frequency=[1200*np.pi/30, 2400*np.pi/30],
# )
speed_range = np.arange(0, 1000, 100)
response = rotor.run_campbell(speed_range)
response.plot().show()

# # CAMPBELL

# speed_range = np.arange(0, 1000, 100)
# response = rotor.run_campbell(speed_range)
# response.plot().show()


crack = Crack(
    dt=0.0001,
    tI=0,
    tF=30,
    cd=0.5,
    n_crack=19,
    speed=1200,
    massunb=massunbt,
    phaseunb=phaseunbt,
    crack_type="Mayes"
    # torque=True,
)

rubbing = rotor.run_defect(crack)
rubbing.plot_time_response([probe1, probe2]).show()
rubbing.plot_dfft([probe1, probe2], log=True).show()
