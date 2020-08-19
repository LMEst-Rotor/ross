import numpy as np

import ross as rs
from ross.defects import (
    MisalignmentFlexAngular,
    MisalignmentFlexCombined,
    MisalignmentFlexParallel,
    MisalignmentRigid,
)

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
        alpha=2.0501,
        beta=1.4e-8,
        rotary_inertia=True,
        shear_effects=True,
    )
    for l in L
]

Id = 0.003844540885417
Ip = 2 * Id

disk0 = rs.DiskElement6DoF(n=12, m=2.6375, Id=Id, Ip=Ip)
disk1 = rs.DiskElement6DoF(n=24, m=2.6375, Id=Id, Ip=Ip)

kxx1 = 6.7072e5
kyy1 = 7.8114e5
kzz = 0
cxx1 = 10.4
cyy1 = 7.505
czz = 0
kxx2 = 2.010e6
kyy2 = 1.1235e8
cxx2 = 13.4
cyy2 = 8.4553

bearing0 = rs.BearingElement6DoF(
    n=4, kxx=kxx1, kyy=kyy1, cxx=cxx1, cyy=cyy1, kzz=kzz, czz=czz
)
bearing1 = rs.BearingElement6DoF(
    n=31, kxx=kxx2, kyy=kyy2, cxx=cxx2, cyy=cyy2, kzz=kzz, czz=czz
)

rotor = rs.Rotor(shaft_elem, [disk0, disk1], [bearing0, bearing1])
# rotor.plot_rotor().show()

misalignment = MisalignmentFlexCombined(
    dt=0.0001,
    tI=0,
    tF=30,
    kd=40 * 10 ** (3),  # Rigidez radial do acoplamento flexivel
    ks=38 * 10 ** (3),  # Rigidez de flexão do acoplamento flexivel
    eCOUPx=2 * 10 ** (-4),  # Distancia de desalinhamento entre os eixos - direcao x
    eCOUPy=2 * 10 ** (-4),  # Distancia de desalinhamento entre os eixos - direcao z
    misalignment_angle=5 * np.pi / 180,  # Angulo do desalinhamento angular (rad)
    TD=0,  # Torque antes do acoplamento
    TL=0,  # Torque dopois do acoplamento
    n1=0,
    speed=1200,
)

## MISALIGNMENT

probe1 = (14, 0)
probe2 = (22, 0)
# response = rotor.run_misalignment(misalignment)
# response.plot_1d(probe=[probe1, probe2]).show()

misalignmentrigid = MisalignmentRigid(
    dt=1e-4,
    tI=0,
    tF=1,
    Kcoup_auxI=0.5,
    Kcoup_auxF=0.5,
    kCOUP=2e5,
    eCOUP=2e-4,
    TD=0,
    TL=0,
    n1=0,
    speed=1200 * np.pi / 30,
)

rotor.run_misalignment_rigid(misalignmentrigid)
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
