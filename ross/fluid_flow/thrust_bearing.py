import numpy as np
from numpy.linalg import pinv
from scipy.linalg import solve
from decimal import Decimal


class Thrust:
    def __init__(
        r1,
        r2,
        rp,
        teta0,
        tetap,
        TC,
        Tin,
        T0,
        rho,
        cp,
        kt,
        k1,
        k2,
        k3,
        mi0,
        fz,
        Npad,
        NTETA,
        NR,
        war,
        R1,
        R2,
        TETA1,
        TETA2,
        Rp,
        TETAp,
        dR,
        dTETA,
        Ti,
        x0,
    ):
        self.r1 = r1
        self.r2 = r2
        self.rp = rp
        self.teta0 = teta0
        self.tetap = tetap
        self.TC = TC
        self.Tin = Tin
        self.T0 = T0
        self.rho = rho
        self.cp = cp
        self.kt = kt
        self.k1 = k1
        self.k2 = k2
        self.k3 = k3
        self.mi0 = (1e-3)*k1*np.exp(k2/(T0-k3))
        self.fz = fz
        self.Npad = Npad
        self.NTETA = NTETA
        self.NR = NR
        # self.war = war
        self.war = wa * (np.pi / 30)
        self.R1 = R1
        self.R2 = R2
        self.TETA1 = TETA1
        self.TETA2 = TETA2
        self.Rp = Rp
        self.TETAp = TETAp
        self.dR = dR
        self.dTETA = dTETA
        self.Ti = Ti
        self.x0 = x0

        # -------------------------------------------------------------------
        # PRE PROCESSING - Preparing auxilary variables and declarations

        # vector aux_dR dimensionless
        aux_dR = np.zeros([nK + 2])
        aux_dR[0 : nK + 1] = np.arange(
            self.R1 + 0.5 * self.dR, self.R2 - 0.5 * self.dR, self.dR
        )

        # vector aux_dTETA dimensionless
        aux_dTETA = np.zeros([nK + 2])
        aux_dTETA[0 : nK + 1] = np.arange(
            self.TETA1 + 0.5 * self.dTETA, self.TETA2 - 0.5 * self.dTETA, self.dTETA
        )

        # -------------------------------------------------------------------------
        # ENTRY VARIABLES FROM ANOTHER CODE, STILL TO BE INTEGRATED HERE
        # Pitch angles alpha_r and alpha_p and oil filme thickness at pivot h0
        a_r = x[0]  # [rad]
        a_s = x[1]  # [rad]
        h0 = x[2]  # [m]

        for ii in range(0, self.NR):
            for jj in range(0, self.NTETA):
                MI[jj, ii] = self.mi0 / self.mi0  # dimensionless

        # Dimensioneless Parameters
        Ar = a_r * self.r1 / h0
        As = a_s * self.r1 / h0
        H0 = h0 / h0

        # -------------------------------------------------------------------
        # PRESSURE FIELD - Solution of Reynolds equation
        kR = 0

        # index using for pressure vectorization
        kTETA = 0
        k = 0

        # number of volumes
        nk = (self.NR) * (self.NTETA)

        # Coefficients Matrix
        Mat_coef = np.zeros(nk, nk)
        b = np.zeros(nk, 1)
        cont = 0

        # for R in range(0, aux_dR)
        for R in np.arange(
            (self.R1 + 0.5 * self.dR), (self.R2 - 0.5 * self.dR), self.dR
        ):
            # for TETA in range(0, aux_dTETA):
            for TETA in np.arange(
                (self.TETA1 + 0.5 * self.dTETA),
                (self.TETA2 - 0.5 * self.dTETA),
                self.dTETA,
            ):

                cont = cont + 1
                TETAe = TETA + 0.5 * self.dTETA
                TETAw = TETA - 0.5 * self.dTETA
                Rn = R + 0.5 * self.dR
                Rs = R - 0.5 * self.dR

                Hne = (
                    H0
                    + As * [self.Rp - Rn * np.cos(self.teta0 * [TETAe - self.TETAp])]
                    + Ar * Rn * np.sin(self.teta0 * [TETAe - self.TETAp])
                )
                Hnw = (
                    H0
                    + As * [self.Rp - Rn * np.cos(self.teta0 * [TETAw - self.TETAp])]
                    + Ar * Rn * np.sin(self.teta0 * [TETAw - self.TETAp])
                )
                Hse = (
                    H0
                    + As * [self.Rp - Rs * np.cos(self.teta0 * [TETAe - self.TETAp])]
                    + Ar * Rs * np.sin(self.teta0 * [TETAe - self.TETAp])
                )
                Hsw = (
                    H0
                    + As * [self.Rp - Rs * np.cos(self.teta0 * [TETAw - self.TETAp])]
                    + Ar * Rs * np.sin(self.teta0 * [TETAw - self.TETAp])
                )

                if kTETA == 1 and kR == 1:
                    MI_e = 0.5 * (MI[kR, kTETA] + MI[kR, kTETA + 1])
                    MI_w = MI[kR, kTETA]
                    MI_n = 0.5 * (MI[kR, kTETA] + MI[kR + 1, kTETA])
                    MI_s = MI[kR, kTETA]

                if kTETA == 1 and kR > 1 and kR < self.NR:
                    MI_e = 0.5 * (MI[kR, kTETA] + MI[kR, kTETA + 1])
                    MI_w = MI[kR, kTETA]
                    MI_n = 0.5 * (MI[kR, kTETA] + MI[kR + 1, kTETA])
                    MI_s = 0.5 * (MI[kR, kTETA] + MI[kR - 1, kTETA])

                if kTETA == 1 and kR == self.NR:
                    MI_e = 0.5 * (MI[kR, kTETA] + MI[kR, kTETA + 1])
                    MI_w = MI[kR, kTETA]
                    MI_n = MI[kR, kTETA]
                    MI_s = 0.5 * (MI[kR, kTETA] + MI[kR - 1, kTETA])

                if kR == 1 and kTETA > 1 and kTETA < self.NTETA:
                    MI_e = 0.5 * (MI[kR, kTETA] + MI[kR, kTETA + 1])
                    MI_w = 0.5 * (MI[kR, kTETA] + MI[kR, kTETA - 1])
                    MI_n = 0.5 * (MI[kR, kTETA] + MI[kR + 1, kTETA])
                    MI_s = MI[kR, kTETA]

                if kTETA > 1 and kTETA < self.NTETA and kR > 1 and kR < self.NR:
                    MI_e = 0.5 * (MI[kR, kTETA] + MI[kR, kTETA + 1])
                    MI_w = 0.5 * (MI[kR, kTETA] + MI[kR, kTETA - 1])
                    MI_n = 0.5 * (MI[kR, kTETA] + MI[kR + 1, kTETA])
                    MI_s = 0.5 * (MI[kR, kTETA] + MI[kR - 1, kTETA])

                if kR == self.NR and kTETA > 1 and kTETA < self.NTETA:
                    MI_e = 0.5 * (MI[kR, kTETA] + MI[kR, kTETA + 1])
                    MI_w = 0.5 * (MI[kR, kTETA] + MI[kR, kTETA - 1])
                    MI_n = MI[kR, kTETA]
                    MI_s = 0.5 * (MI[kR, kTETA] + MI[kR - 1, kTETA])

                if kR == 1 and kTETA == self.NTETA:
                    MI_e = MI[kR, kTETA]
                    MI_w = 0.5 * (MI[kR, kTETA] + MI[kR, kTETA - 1])
                    MI_n = 0.5 * (MI[kR, kTETA] + MI[kR + 1, kTETA])
                    MI_s = MI[kR, kTETA]

                if kTETA == self.NTETA and kR > 1 and kR < self.NR:
                    MI_e = MI[kR, kTETA]
                    MI_w = 0.5 * (MI[kR, kTETA] + MI[kR, kTETA - 1])
                    MI_n = 0.5 * (MI[kR, kTETA] + MI[kR + 1, kTETA])
                    MI_s = 0.5 * (MI[kR, kTETA] + MI[kR - 1, kTETA])

                if kTETA == self.NTETA and kR == self.NR:
                    MI_e = MI[kR, kTETA]
                    MI_w = 0.5 * (MI[kR, kTETA] + MI[kR, kTETA - 1])
                    MI_n = MI[kR, kTETA]
                    MI_s = 0.5 * (MI[kR, kTETA] + MI[kR - 1, kTETA])

                # Coefficients for solving the Reynolds equation
                CE = (
                    1
                    / (24 * self.teta0 ** 2 * MI_e)
                    * (self.dR / self.dTETA)
                    * (Hne ** 3 / Rn + Hse ** 3 / Rs)
                )
                CW = (
                    1
                    / (24 * self.teta0 ** 2 * MI_w)
                    * (self.dR / self.dTETA)
                    * (Hnw ** 3 / Rn + Hsw ** 3 / Rs)
                )
                CN = Rn / (24 * MI_n) * (self.dTETA / self.dR) * (Hne ** 3 + Hnw ** 3)
                CS = Rs / (24 * MI_s) * (self.dTETA / self.dR) * (Hse ** 3 + Hsw ** 3)
                CP = -(CE + CW + CN + CS)

                # vectorization index
                k = k + 1

                b[k, 0] = (
                    self.dR
                    / (4 * self.teta0)
                    * (Rn * Hne + Rs * Hse - Rn * Hnw - Rs * Hsw)
                )

                if kTETA == 1 and kR == 1:
                    Mat_coef[k, k] = CP - CS - CW
                    Mat_coef[k, k + 1] = CE
                    Mat_coef[k, k + self.NTETA] = CN

                if kTETA == 1 and kR > 1 and kR < self.NR:
                    Mat_coef[k, k] = CP - CW
                    Mat_coef[k, k + 1] = CE
                    Mat_coef[k, k + self.NTETA] = CN
                    Mat_coef[k, k - self.NTETA] = CS

                if kTETA == 1 and kR == self.NR:
                    Mat_coef[k, k] = CP - CW - CN
                    Mat_coef[k, k + 1] = CE
                    Mat_coef[k, k - self.NTETA] = CS

                if kR == 1 and kTETA > 1 and kTETA < self.NTETA:
                    Mat_coef[k, k] = CP - CS
                    Mat_coef[k, k + 1] = CE
                    Mat_coef[k, k - 1] = CW
                    Mat_coef[k, k + self.NTETA] = CN

                if kTETA > 1 and kTETA < self.NTETA and kR > 1 and kR < self.NR:
                    Mat_coef[k, k] = CP
                    Mat_coef[k, k - 1] = CW
                    Mat_coef[k, k + self.NTETA] = CN
                    Mat_coef[k, k - self.NTETA] = CS
                    Mat_coef[k, k + 1] = CE

                if kR == self.NR and kTETA > 1 and kTETA < self.NTETA:
                    Mat_coef[k, k] = CP - CN
                    Mat_coef[k, k - 1] = CW
                    Mat_coef[k, k + 1] = CE
                    Mat_coef[k, k - self.NTETA] = CS

                if kR == 1 and kTETA == self.NTETA:
                    Mat_coef[k, k] = CP - CE - CS
                    Mat_coef[k, k - 1] = CW
                    Mat_coef[k, k + self.NTETA] = CN

                if kTETA == self.NTETA and kR > 1 and kR < self.NR:
                    Mat_coef[k, k] = CP - CE
                    Mat_coef[k, k - 1] = CW
                    Mat_coef[k, k - self.NTETA] = CS
                    Mat_coef[k, k + self.NTETA] = CN

                if kTETA == self.NTETA and kR == self.NR:
                    Mat_coef[k, k] = CP - CE - CN
                    Mat_coef[k, k - 1] = CW
                    Mat_coef[k, k - self.NTETA] = CS

                kTETA = kTETA + 1

        kR = kR + 1
        kTETA = 0

        # -------------------------------------------------------------------
        # PRESSURE FIELD SOLUTION
        p = np.linalg.solve(Mat_coef, b)
        cont = 0

        for ii in np.arange(self.nZ):
            for jj in np.arange(self.ntheta):
                P[ii, jj] = p[cont]
                cont = cont + 1
                if P[ii, jj] < 0:
                    P[ii, jj] = 0

        # non dimensional pressure matrix
        for ii in np.range(1, self.NR):
            for jj in np.range(1, self.NTETA):
                cont = cont + 1
                P[ii, jj] = p[cont]

        # boundary conditions of pressure
        for ii in np.range(1, self.NR):
            for jj in np.range(1, self.NTETA):
                if P[ii, jj] < 0:
                    P[ii, jj] = 0

        # dimensional pressure matrix
        Pdim = P * (self.r1 ** 2) * self.war * self.mi0 / (h0 ** 2)

        # -------------------------------------------------------------------------
        # RESULTING FORCE AND MOMENTUM: Equilibrium position
        XR = self.r1 * (
            np.arange((self.R1 + 0.5 * self.dR), (self.R2 - 0.5 * self.dR), self.dR)
        )
        Xrp = self.rp * (1 + (np.zeros(ZR.shape)))
        XTETA = self.teta0 * (
            np.arange(
                (self.TETA1 + 0.5 * self.dTETA),
                (self.TETA2 - 0.5 * self.dTETA),
                self.dTETA,
            )
        )

        for ii in range(1, self.NTETA):
            Mxr[:, ii] = (Pdim[:, ii] * (np.linalg.inv(XR) ** 2)) * np.sin(
                XTETA[ii] - self.tetap
            )
            Myr[:, ii] = (
                -Pdim[:, ii]
                * np.linalg.inv(XR)
                * np.linalg.inv(XR * np.cos(XTETA[ii] - self.tetap) - Xrp)
            )
            Frer[:, ii] = Pdim[:, ii] * np.linalg.inv(XR)

        mxr = np.trapz(XR, Mxr)
        myr = np.trapz(XR, Myr)
        frer = np.trapz(XR, Frer)

        mx = np.trapz(XTETA, mxr)
        my = np.trapz(XTETA, myr)
        fre = -np.trapz(XTETA, frer) + self.fz / self.Npad

        score = np.norm(
            [mx, my, fre], 2
        )  # the "2" option denotes the equivalent method to the matlab defaut one

        # Equilibrium position
        a_r = x(1)  # [rad]
        a_s = x(2)  # [rad]
        h0 = x(3)  # [m]

        # Viscosity field
        for ii in range(1, self.NR):
            for jj in range(1, self.NTETA):
                mi[ii, jj] = self.mi0  # [Pa.s]

        Ar = a_r * self.r1 / h0
        As = a_s * self.r1 / h0

        MI = 1 / self.mi0 * mi

        # -------------------------------------------------------------------------
        # PRESSURE FIELD - Solution of Reynolds equation
        kR = 0
        kTETA = 0

        # index using for pressure vectorization
        k = 0

        # number of volumes
        nk = (self.NR) * (self.NTETA)

        # Coefficients Matrix
        Mat_coef = np.zeros(nk, nk)
        b = np.zeros(nk, 1)
        cont = 0

        # for R in range(0, aux_dR)
        for R in np.arange(
            (self.R1 + 0.5 * self.dR), (self.R2 - 0.5 * self.dR), self.dR
        ):
            # for TETA in range(0, aux_dTETA):
            for TETA in np.arange(
                (self.TETA1 + 0.5 * self.dTETA),
                (self.TETA2 - 0.5 * self.dTETA),
                self.dTETA,
            ):

                cont = cont + 1
                TETAe = TETA + 0.5 * self.dTETA
                TETAw = TETA - 0.5 * self.dTETA
                Rn = R + 0.5 * self.dR
                Rs = R - 0.5 * self.dR

                H0[kR, kTETA] = (
                    h0 / h0
                    + As * (self.Rp - R * np.cos(self.teta0 * (TETA - self.TETAp)))
                    + Ar * R * np.sin(self.teta0 * (TETA - self.TETAp))
                )

                # oil film thickness - faces
                H0ne[kR, kTETA] = (
                    h0 / h0
                    + As * (self.Rp - Rn * np.cos(self.teta0 * (TETAe - self.TETAp)))
                    + Ar * Rn * np.sin(self.teta0 * (TETAe - self.TETAp))
                )
                H0nw[kR, kTETA] = (
                    h0 / h0
                    + As * (self.Rp - Rn * np.cos(self.teta0 * (TETAw - self.TETAp)))
                    + Ar * Rn * np.sin(self.teta0 * (TETAw - self.TETAp))
                )
                H0se[kR, kTETA] = (
                    h0 / h0
                    + As * (self.Rp - Rs * np.cos(self.teta0 * (TETAe - self.TETAp)))
                    + Ar * Rs * np.sin(self.teta0 * (TETAe - self.TETAp))
                )
                H0sw[kR, kTETA] = (
                    h0 / h0
                    + As * (self.Rp - Rs * np.cos(self.teta0 * (TETAw - self.TETAp)))
                    + Ar * Rs * np.sin(self.teta0 * (TETAw - self.TETAp))
                )

                if kTETA == 1 and kR == 1:
                    MI_e = 0.5 * (MI[kR, kTETA] + MI[kR, kTETA + 1])
                    MI_w = MI[kR, kTETA]
                    MI_n = 0.5 * (MI[kR, kTETA] + MI[kR + 1, kTETA])
                    MI_s = MI[kR, kTETA]

                if kTETA == 1 and kR > 1 and kR < self.NR:
                    MI_e = 0.5 * (MI[kR, kTETA] + MI[kR, kTETA + 1])
                    MI_w = MI[kR, kTETA]
                    MI_n = 0.5 * (MI[kR, kTETA] + MI[kR + 1, kTETA])
                    MI_s = 0.5 * (MI[kR, kTETA] + MI[kR - 1, kTETA])

                if kTETA == 1 and kR == self.NR:
                    MI_e = 0.5 * (MI[kR, kTETA] + MI[kR, kTETA + 1])
                    MI_w = MI[kR, kTETA]
                    MI_n = MI[kR, kTETA]
                    MI_s = 0.5 * (MI[kR, kTETA] + MI[kR - 1, kTETA])

                if kR == 1 and kTETA > 1 and kTETA < self.NTETA:
                    MI_e = 0.5 * (MI[kR, kTETA] + MI[kR, kTETA + 1])
                    MI_w = 0.5 * (MI[kR, kTETA] + MI[kR, kTETA - 1])
                    MI_n = 0.5 * (MI[kR, kTETA] + MI[kR + 1, kTETA])
                    MI_s = MI[kR, kTETA]

                if kTETA > 1 and kTETA < self.NTETA and kR > 1 and kR < self.NR:
                    MI_e = 0.5 * (MI[kR, kTETA] + MI[kR, kTETA + 1])
                    MI_w = 0.5 * (MI[kR, kTETA] + MI[kR, kTETA - 1])
                    MI_n = 0.5 * (MI[kR, kTETA] + MI[kR + 1, kTETA])
                    MI_s = 0.5 * (MI[kR, kTETA] + MI[kR - 1, kTETA])

                if kR == self.NR and kTETA > 1 and kTETA < self.NTETA:
                    MI_e = 0.5 * (MI[kR, kTETA] + MI[kR, kTETA + 1])
                    MI_w = 0.5 * (MI[kR, kTETA] + MI[kR, kTETA - 1])
                    MI_n = MI[kR, kTETA]
                    MI_s = 0.5 * (MI[kR, kTETA] + MI[kR - 1, kTETA])

                if kR == 1 and kTETA == self.NTETA:
                    MI_e = MI[kR, kTETA]
                    MI_w = 0.5 * (MI[kR, kTETA] + MI[kR, kTETA - 1])
                    MI_n = 0.5 * (MI[kR, kTETA] + MI[kR + 1, kTETA])
                    MI_s = MI[kR, kTETA]

                if kTETA == self.NTETA and kR > 1 and kR < self.NR:
                    MI_e = MI[kR, kTETA]
                    MI_w = 0.5 * (MI[kR, kTETA] + MI[kR, kTETA - 1])
                    MI_n = 0.5 * (MI[kR, kTETA] + MI[kR + 1, kTETA])
                    MI_s = 0.5 * (MI[kR, kTETA] + MI[kR - 1, kTETA])

                if kTETA == self.NTETA and kR == self.NR:
                    MI_e = MI[kR, kTETA]
                    MI_w = 0.5 * (MI[kR, kTETA] + MI[kR, kTETA - 1])
                    MI_n = MI[kR, kTETA]
                    MI_s = 0.5 * (MI[kR, kTETA] + MI[kR - 1, kTETA])

                # Coefficients for solving the Reynolds equation
                CE = (
                    1
                    / (24 * self.teta0 ** 2 * MI_e)
                    * (self.dR / self.dTETA)
                    * (H0ne[kR, kTETA] ** 3 / Rn + H0se[kR, kTETA] ** 3 / Rs)
                )
                CW = (
                    1
                    / (24 * self.teta0 ** 2 * MI_w)
                    * (self.dR / self.dTETA)
                    * (H0nw[kR, kTETA] ** 3 / Rn + H0sw[kR, kTETA] ** 3 / Rs)
                )
                CN = (
                    Rn
                    / (24 * MI_n)
                    * (self.dTETA / self.dR)
                    * (H0ne[kR, kTETA] ** 3 + H0nw[kR, kTETA] ** 3)
                )
                CS = (
                    Rs
                    / (24 * MI_s)
                    * (self.dTETA / self.dR)
                    * (H0se[kR, kTETA] ** 3 + H0sw[kR, kTETA] ** 3)
                )
                CP = -(CE + CW + CN + CS)

                k = k + 1

                b[k, 1] = (
                    self.dR
                    / (4 * self.teta0)
                    * (
                        Rn * H0ne[kR, kTETA]
                        + Rs * H0se[kR, kTETA]
                        - Rn * H0nw[kR, kTETA]
                        - Rs * H0sw[kR, kTETA]
                    )
                )

                if kTETA == 1 and kR == 1:
                    Mat_coef[k, k] = CP - CS - CW
                    Mat_coef[k, k + 1] = CE
                    Mat_coef[k, k + (self.NTETA)] = CN

                if kTETA == 1 and kR > 1 and kR < self.NR:
                    Mat_coef[k, k] = CP - CW
                    Mat_coef[k, k + 1] = CE
                    Mat_coef[k, k + (self.NTETA)] = CN
                    Mat_coef[k, k - (self.NTETA)] = CS

                if kTETA == 1 and kR == self.NR:
                    Mat_coef[k, k] = CP - CW - CN
                    Mat_coef[k, k + 1] = CE
                    Mat_coef[k, k - (self.NTETA)] = CS

                if kR == 1 and kTETA > 1 and kTETA < self.NTETA:
                    Mat_coef[k, k] = CP - CS
                    Mat_coef[k, k + 1] = CE
                    Mat_coef[k, k - 1] = CW
                    Mat_coef[k, k + (self.NTETA)] = CN

                if kTETA > 1 and kTETA < self.NTETA and kR > 1 and kR < self.NR:
                    Mat_coef[k, k] = CP
                    Mat_coef[k, k - 1] = CW
                    Mat_coef[k, k + (self.NTETA)] = CN
                    Mat_coef[k, k - (self.NTETA)] = CS
                    Mat_coef[k, k + 1] = CE

                if kR == self.NR and kTETA > 1 and kTETA < self.NTETA:
                    Mat_coef[k, k] = CP - CN
                    Mat_coef[k, k - 1] = CW
                    Mat_coef[k, k + 1] = CE
                    Mat_coef[k, k - (self.NTETA)] = CS

                if kR == 1 and kTETA == self.NTETA:
                    Mat_coef[k, k] = CP - CE - CS
                    Mat_coef[k, k - 1] = CW
                    Mat_coef[k, k + (self.NTETA)] = CN

                if kTETA == self.NTETA and kR > 1 and kR < self.NR:
                    Mat_coef[k, k] = CP - CE
                    Mat_coef[k, k - 1] = CW
                    Mat_coef[k, k - (self.NTETA)] = CS
                    Mat_coef[k, k + (self.NTETA)] = CN

                if kTETA == self.NTETA and kR == self.NR:
                    Mat_coef[k, k] = CP - CE - CN
                    Mat_coef[k, k - 1] = CW
                    Mat_coef[k, k - (self.NTETA)] = CS

                kTETA = kTETA + 1

            kR = kR + 1
            kTETA = 0

        # --------------------------------------------------------------------------
        # Vectorized pressure field solution
        p = np.linalg.solve(Mat_coef, b)
        cont = 0

        for ii in range(1, self.NR):
            for jj in range(1, self.NTETA):
                cont = cont + 1
                P0[ii, jj] = p(cont)  # matrix of pressure

        # boundary conditions of pressure
        for ii in range(1, self.NR):
            for jj in range(1, self.NTETA):
                if P0[ii, jj] < 0:
                    P0[ii, jj] = 0

        # --------------------------------------------------------------------------
        # Stiffness and Damping Coefficients
        # perturbation frequency [rad/s]
        wp = self.war
        WP = wp / self.war

        MI = (1 / self.mi0) * mi

        kR = 0
        kTETA = 0

        # index using for pressure vectorization
        k = 0

        # number of volumes
        nk = (self.NR) * (self.NTETA)

        # Coefficients Matrix
        Mat_coef = np.zeros(nk, nk)
        b = np.zeros(nk, 1)
        cont = 0

        # for R in range(0, aux_dR)
        for R in np.arange(
            (self.R1 + 0.5 * self.dR), (self.R2 - 0.5 * self.dR), self.dR
        ):
            # for TETA in range(0, aux_dTETA):
            for TETA in np.arange(
                (self.TETA1 + 0.5 * self.dTETA),
                (self.TETA2 - 0.5 * self.dTETA),
                self.dTETA,
            ):

                cont = cont + 1
                TETAe = TETA + 0.5 * self.dTETA
                TETAw = TETA - 0.5 * self.dTETA
                Rn = R + 0.5 * self.dR
                Rs = R - 0.5 * self.dR

                if kTETA == 1 and kR == 1:
                    MI_e = 0.5 * (MI[kR, kTETA] + MI[kR, kTETA + 1])
                    MI_w = MI[kR, kTETA]
                    MI_n = 0.5 * (MI[kR, kTETA] + MI[kR + 1, kTETA])
                    MI_s = MI[kR, kTETA]
                    dPdTETAe = (P0[kR, kTETA + 1] - P0[kR, kTETA]) / self.dTETA
                    dPdTETAw = P0[kR, kTETA] / (0.5 * self.dTETA)
                    dPdRn = (P0[kR + 1, kTETA] - P0[kR, kTETA]) / self.dR
                    dPdRs = P0[kR, kTETA] / (0.5 * self.dR)

                if kTETA == 1 and kR > 1 and kR < self.NR:
                    MI_e = 0.5 * (MI[kR, kTETA] + MI[kR, kTETA + 1])
                    MI_w = MI[kR, kTETA]
                    MI_n = 0.5 * (MI[kR, kTETA] + MI[kR + 1, kTETA])
                    MI_s = 0.5 * (MI[kR, kTETA] + MI[kR - 1, kTETA])
                    dPdTETAe = (P0[kR, kTETA + 1] - P0[kR, kTETA]) / self.dTETA
                    dPdTETAw = P0[kR, kTETA] / (0.5 * self.dTETA)
                    dPdRn = (P0[kR + 1, kTETA] - P0[kR, kTETA]) / self.dR
                    dPdRs = (P0[kR, kTETA] - P0[kR - 1, kTETA]) / self.dR

                if kTETA == 1 and kR == self.NR:
                    MI_e = 0.5 * (MI[kR, kTETA] + MI[kR, kTETA + 1])
                    MI_w = MI[kR, kTETA]
                    MI_n = MI[kR, kTETA]
                    MI_s = 0.5 * (MI[kR, kTETA] + MI[kR - 1, kTETA])
                    dPdTETAe = (P0[kR, kTETA + 1] - P0[kR, kTETA]) / self.dTETA
                    dPdTETAw = P0[kR, kTETA] / (0.5 * self.dTETA)
                    dPdRn = -P0[kR, kTETA] / (0.5 * self.dR)
                    dPdRs = (P0[kR, kTETA] - P0[kR - 1, kTETA]) / self.dR

                if kR == 1 and kTETA > 1 and kTETA < self.NTETA:
                    MI_e = 0.5 * (MI[kR, kTETA] + MI[kR, kTETA + 1])
                    MI_w = 0.5 * (MI[kR, kTETA] + MI[kR, kTETA - 1])
                    MI_n = 0.5 * (MI[kR, kTETA] + MI[kR + 1, kTETA])
                    MI_s = MI[kR, kTETA]
                    dPdTETAe = (P0[kR, kTETA + 1] - P0[kR, kTETA]) / self.dTETA
                    dPdTETAw = (P0[kR, kTETA] - P0[kR, kTETA - 1]) / self.dTETA
                    dPdRn = (P0[kR + 1, kTETA] - P0[kR, kTETA]) / self.dR
                    dPdRs = P0[kR, kTETA] / (0.5 * self.dR)

                if kTETA > 1 and kTETA < self.NTETA and kR > 1 and kR < self.NR:
                    MI_e = 0.5 * (MI[kR, kTETA] + MI[kR, kTETA + 1])
                    MI_w = 0.5 * (MI[kR, kTETA] + MI[kR, kTETA - 1])
                    MI_n = 0.5 * (MI[kR, kTETA] + MI[kR + 1, kTETA])
                    MI_s = 0.5 * (MI[kR, kTETA] + MI[kR - 1, kTETA])
                    dPdTETAe = (P0[kR, kTETA + 1] - P0[kR, kTETA]) / self.dTETA
                    dPdTETAw = (P0[kR, kTETA] - P0[kR, kTETA - 1]) / self.dTETA
                    dPdRn = (P0[kR + 1, kTETA] - P0[kR, kTETA]) / self.dR
                    dPdRs = (P0[kR, kTETA] - P0[kR - 1, kTETA]) / self.dR

                if kR == self.NR and kTETA > 1 and kTETA < self.NTETA:
                    MI_e = 0.5 * (MI[kR, kTETA] + MI[kR, kTETA + 1])
                    MI_w = 0.5 * (MI[kR, kTETA] + MI[kR, kTETA - 1])
                    MI_n = MI[kR, kTETA]
                    MI_s = 0.5 * (MI[kR, kTETA] + MI[kR - 1, kTETA])
                    dPdTETAe = (P0[kR, kTETA + 1] - P0[kR, kTETA]) / self.dTETA
                    dPdTETAw = (P0[kR, kTETA] - P0[kR, kTETA - 1]) / self.dTETA
                    dPdRn = -P0[kR, kTETA] / (0.5 * self.dR)
                    dPdRs = (P0[kR, kTETA] - P0[kR - 1, kTETA]) / self.dR

                if kR == 1 and kTETA == self.NTETA:
                    MI_e = MI[kR, kTETA]
                    MI_w = 0.5 * (MI[kR, kTETA] + MI[kR, kTETA - 1])
                    MI_n = 0.5 * (MI[kR, kTETA] + MI[kR + 1, kTETA])
                    MI_s = MI[kR, kTETA]
                    dPdTETAe = -P0[kR, kTETA] / self.dTETA
                    dPdTETAw = (P0[kR, kTETA] - P0[kR, kTETA - 1]) / self.dTETA
                    dPdRn = (P0[kR + 1, kTETA] - P0[kR, kTETA]) / self.dR
                    dPdRs = P0[kR, kTETA] / self.dR

                if kTETA == self.NTETA and kR > 1 and kR < self.NR:
                    MI_e = MI[kR, kTETA]
                    MI_w = 0.5 * (MI[kR, kTETA] + MI[kR, kTETA - 1])
                    MI_n = 0.5 * (MI[kR, kTETA] + MI[kR + 1, kTETA])
                    MI_s = 0.5 * (MI[kR, kTETA] + MI[kR - 1, kTETA])
                    dPdTETAe = -P0[kR, kTETA] / (0.5 * self.dTETA)
                    dPdTETAw = (P0[kR, kTETA] - P0[kR, kTETA - 1]) / self.dTETA
                    dPdRn = (P0[kR + 1, kTETA] - P0[kR, kTETA]) / self.dR
                    dPdRs = (P0[kR, kTETA] - P0[kR - 1, kTETA]) / self.dR

                if kTETA == self.NTETA and kR == self.NR:
                    MI_e = MI[kR, kTETA]
                    MI_w = 0.5 * (MI[kR, kTETA] + MI[kR, kTETA - 1])
                    MI_n = MI[kR, kTETA]
                    MI_s = 0.5 * (MI[kR, kTETA] + MI[kR - 1, kTETA])
                    dPdTETAe = -P0[kR, kTETA] / (0.5 * self.dTETA)
                    dPdTETAw = (P0[kR, kTETA] - P0[kR, kTETA - 1]) / self.dTETA
                    dPdRn = -P0[kR, kTETA] / (0.5 * self.dR)
                    dPdRs = (P0[kR, kTETA] - P0[kR - 1, kTETA]) / self.dR

                As_ne = 1
                As_nw = 1
                As_se = 1
                As_sw = 1

                # G1=dhpivotdR=0
                G1_ne = 0
                G1_nw = 0
                G1_se = 0
                G1_sw = 0

                # Gs=dhpivotdTETA=0
                G2_ne = 0
                G2_nw = 0
                G2_se = 0
                G2_sw = 0

                # Coefficients for solving the Reynolds equation
                CE_1 = (
                    1
                    / (24 * self.teta0 ** 2 * MI_e)
                    * (self.dR / self.dTETA)
                    * (
                        As_ne * H0ne[kR, kTETA] ** 3 / Rn
                        + As_se * H0se[kR, kTETA] ** 3 / Rs
                    )
                )
                CE_2 = (
                    self.dR
                    / (48 * self.teta0 ** 2 * MI_e)
                    * (
                        G2_ne * H0ne[kR, kTETA] ** 3 / Rn
                        + G2_se * H0se[kR, kTETA] ** 3 / Rs
                    )
                )
                CE = CE_1 + CE_2

                CW_1 = (
                    1
                    / (24 * self.teta0 ** 2 * MI_w)
                    * (self.dR / self.dTETA)
                    * (
                        As_nw * H0nw[kR, kTETA] ** 3 / Rn
                        + As_sw * H0sw[kR, kTETA] ** 3 / Rs
                    )
                )
                CW_2 = (
                    -self.dR
                    / (48 * self.teta0 ** 2 * MI_w)
                    * (
                        G2_nw * H0nw[kR, kTETA] ** 3 / Rn
                        + G2_sw * H0sw[kR, kTETA] ** 3 / Rs
                    )
                )
                CW = CW_1 + CW_2

                CN_1 = (
                    Rn
                    / (24 * MI_n)
                    * (self.dTETA / self.dR)
                    * (As_ne * H0ne[kR, kTETA] ** 3 + As_nw * H0nw[kR, kTETA] ** 3)
                )
                CN_2 = (
                    Rn
                    / (48 * MI_n)
                    * (self.dTETA)
                    * (G1_ne * H0ne[kR, kTETA] ** 3 + G1_nw * H0nw[kR, kTETA] ** 3)
                )
                CN = CN_1 + CN_2

                CS_1 = (
                    Rs
                    / (24 * MI_s)
                    * (self.dTETA / self.dR)
                    * (As_se * H0se[kR, kTETA] ** 3 + As_sw * H0sw[kR, kTETA] ** 3)
                )
                CS_2 = (
                    -Rs
                    / (48 * MI_s)
                    * (self.dTETA)
                    * (G1_se * H0se[kR, kTETA] ** 3 + G1_sw * H0sw[kR, kTETA] ** 3)
                )
                CS = CS_1 + CS_2

                CP = -(CE_1 + CW_1 + CN_1 + CS_1) + (CE_2 + CW_2 + CN_2 + CS_2)

                B_1 = (Rn * self.dTETA / (8 * MI_n)) * dPdRn * (
                    As_ne * H0ne[kR, kTETA] ** 2 + As_nw * H0nw[kR, kTETA] ** 2
                ) - (Rs * self.dTETA / (8 * MI_s)) * dPdRs * (
                    As_se * H0se[kR, kTETA] ** 2 + As_sw * H0sw[kR, kTETA] ** 2
                )
                B_2 = (self.dR / (8 * self.teta0 ** 2 * MI_e)) * dPdTETAe * (
                    As_ne * H0ne[kR, kTETA] ** 2 / Rn
                    + As_se * H0se[kR, kTETA] ** 2 / Rs
                ) - (self.dR / (8 * self.teta0 ** 2 * MI_w)) * dPdTETAw * (
                    As_nw * H0nw[kR, kTETA] ** 2 / Rn
                    + As_nw * H0sw[kR, kTETA] ** 2 / Rs
                )
                B_3 = self.dR / (4 * self.teta0) * (
                    As_ne * Rn + As_se * Rs
                ) - self.dR / (4 * self.teta0) * (As_nw * Rn + As_sw * Rs)
                B_4 = (
                    i
                    * WP
                    * self.dR
                    * self.dTETA
                    / 4
                    * (Rn * As_ne + Rn * As_nw + Rs * As_se + Rs * As_sw)
                )

                # vectorization index
                k = k + 1

                b[k, 1] = -(B_1 + B_2) + B_3 + B_4

                if kTETA == 1 and kR == 1:
                    Mat_coef[k, k] = CP - CW - CS
                    Mat_coef[k, k + 1] = CE
                    Mat_coef[k, k + (self.NTETA)] = CN

                if kTETA == 1 and kR > 1 and kR < self.NR:
                    Mat_coef[k, k] = CP - CW
                    Mat_coef[k, k + 1] = CE
                    Mat_coef[k, k + (self.NTETA)] = CN
                    Mat_coef[k, k - (self.NTETA)] = CS

                if kTETA == 1 and kR == self.NR:
                    Mat_coef[k, k] = CP - CW - CN
                    Mat_coef[k, k + 1] = CE
                    Mat_coef[k, k - (self.NTETA)] = CS

                if kR == 1 and kTETA > 1 and kTETA < self.NTETA:
                    Mat_coef[k, k] = CP - CS
                    Mat_coef[k, k + 1] = CE
                    Mat_coef[k, k - 1] = CW
                    Mat_coef[k, k + (self.NTETA)] = CN

                if kTETA > 1 and kTETA < self.NTETA and kR > 1 and kR < self.NR:
                    Mat_coef[k, k] = CP
                    Mat_coef[k, k - 1] = CW
                    Mat_coef[k, k + (self.NTETA)] = CN
                    Mat_coef[k, k - (self.NTETA)] = CS
                    Mat_coef[k, k + 1] = CE

                if kR == self.NR and kTETA > 1 and kTETA < self.NTETA:
                    Mat_coef[k, k] = CP - CN
                    Mat_coef[k, k - 1] = CW
                    Mat_coef[k, k + 1] = CE
                    Mat_coef[k, k - (self.NTETA)] = CS

                if kR == 1 and kTETA == self.NTETA:
                    Mat_coef[k, k] = CP - CE - CS
                    Mat_coef[k, k - 1] = CW
                    Mat_coef[k, k + (self.NTETA)] = CN

                if kTETA == self.NTETA and kR > 1 and kR < self.NR:
                    Mat_coef[k, k] = CP - CE
                    Mat_coef[k, k - 1] = CW
                    Mat_coef[k, k - (self.NTETA)] = CS
                    Mat_coef[k, k + (self.NTETA)] = CN

                if kTETA == self.NTETA and kR == self.NR:
                    Mat_coef[k, k] = CP - CE - CN
                    Mat_coef[k, k - 1] = CW
                    Mat_coef[k, k - (self.NTETA)] = CS

                kTETA = kTETA + 1

            kR = kR + 1
            kTETA = 0

        # -------------------------------------------------------------------------
        #  Pressure field solution
        p = np.linalg.solve(Mat_coef, b)

        cont = 0

        # pressure matrix
        for ii in range(1, self.NR):
            for jj in range(1, self.NTETA):
                cont = cont + 1
                P[ii, jj] = p[cont]

        # dimensional pressure
        Pdim = P * (self.r1 ** 2) * self.war * self.mi0 / (h0 ** 3)

        # -------------------------------------------------------------------------
        # RESULTING FORCE AND MOMENTUM: Equilibrium position
        XR = self.r1 * np.arange(
            self.R1 + 0.5 * self.dR, self.R2 - 0.5 * self.dR, self.dR
        )

        Xrp = self.rp * (1 + np.zeros(XR.shape))

        XTETA = self.teta0 * np.arange(
            self.TETA1 + 0.5 * self.dTETA, self.TETA2 - 0.5 * self.dTETA, self.dTETA
        )

        for ii in range(1, self.NTETA):
            Mxr[:, ii] = (Pdim[:, ii] * (np.inv(XR) ** 2)) * np.sin(
                XTETA[ii] - self.tetap
            )
            Myr[:, ii] = (
                -Pdim[:, ii]
                * np.inv(XR)
                * np.inv(XR * np.cos(XTETA[ii] - self.tetap) - Xrp)
            )
            Frer[:, ii] = Pdim[:, ii] * np.inv(XR)

        mxr = np.trapz(XR, Mxr)
        myr = np.trapz(XR, Myr)
        frer = np.trapz(XR, Frer)

        mx = -np.trapz(XTETA, mxr)
        my = -np.trapz(XTETA, myr)
        fre = -np.trapz(XTETA, frer)

        # Stiffness Coefficient
        K = self.Npad * np.real(kk_zz)

        # Damping Coefficient
        C = self.Npad * 1 / wp * np.imag(kk_zz)

        # Output values
        # results - Pmax [Pa]- hmax[m] - hmin[m] - h0[m]
        Pmax = np.max(PPdim)
        hmax = np.max(h0 * H0)
        hmin = np.min(h0 * H0)
        h0


def thrust_bearing_example():
    """Create an example of a thrust bearing with hydrodynamic effects. 
    This function returns pressure field and dynamic coefficient. The 
    purpose is to make available a simple model so that a doctest can be 
    written using it.

    Returns
    -------
    Thrust : ross.Thrust Object
        An instance of a hydrodynamic thrust bearing model object.
    Examples
    --------
    >>> bearing = thrust_bearing_example()
    >>> bearing.L
    0.263144
    """

    bearing = Thrust(
        r1=0.5 * 90e-3,  # pad inner radius          [m]
        r2=0.5 * 160e-3,  # pad outer radius          [m]
        rp=(r2 - r1) * 0.5 + r1,  # pad pivot radius          [m]
        teta0=35 * pi / 180,  # pad complete angle        [rad]
        tetap=19.5 * pi / 180,  # pad pivot angle           [rad]
        TC=40 + 273.15,  # Collar temperature        [K]
        Tin=40 + 273.15,  # Cold oil temperature      [K]
        T0=0.5 * (TC + Tin),  # Reference temperature     [K]
        rho=870,  # Oil density               [kg/m³]
        cp=1850 # Oil thermal capacity [J/kg/K]
        kt=0.15 # Oil thermal conductivity [W/m/K]
        k1=0.06246 # Coefficient for ISO VG 32 turbine oil - Vogel's equation
        k2=868.8 # Coefficient for ISO VG 32 turbine oil - Vogel's equation
        k3=170.4 # Coefficient for ISO VG 32 turbine oil - Vogel's equation
        mi0=1e-6 * rho * 22,  # Oil VG 22
        fz=370 * 9.81,  # Loading in Y direction    [N]
        Npad=3,  # Number of PADs
        NTETA=40,  # TETA direction N volumes
        NR=40,  # R direction N volumes
        war=(1200 * pi) / 30,  # Shaft rotation speed      [RPM]
        R1=1,  # Inner pad FEM radius
        R2=r2 / r1,  # Outer pad FEM radius
        TETA1=0,  # Initial angular coordinate
        TETA2=1,  # Final angular coordinate
        Rp=rp / r1,  # Radial pivot position
        TETAp=tetap / teta0,  # Angular pivot position
        dR=(R2 - R1) / (NR),  # R direction volumes length
        dTETA=(TETA2 - TETA1) / (NTETA),  # TETA direction volumes length
        Ti=T0 * ones(NR, NTETA),  # Initial temperature field [°C]
        x0=np.array(
            -2.251004554793839e-04, -1.332796067467349e-04, 2.152552477569639e-05
        ),  # Initial equilibrium position
    )

    return bearing
