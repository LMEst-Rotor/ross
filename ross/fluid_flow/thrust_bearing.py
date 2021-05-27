import numpy as np
from numpy.linalg import pinv
from scipy.linalg import solve
from scipy.optimize import fmin
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
        wa,
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
        mi,
        P0,
        MI,
        H0,
        H0ne,
        H0se,
        H0nw,
        H0sw,
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
        self.mi0 = (1e-3) * k1 * np.exp(k2 / (T0 - k3))
        self.fz = fz
        self.Npad = Npad
        self.NTETA = NTETA
        self.NR = NR
        self.wa = wa
        self.war = wa * (np.pi / 30)
        self.R1 = R1
        self.R2 = R2
        self.TETA1 = TETA1
        self.TETA2 = TETA2
        self.Rp = Rp
        self.TETAp = TETAp
        self.dR = dR
        self.dTETA = dTETA
        self.Ti = T0 * (1 + np.zeros(NR, NTETA))
        self.x0 = x0
        self.mi = mi
        self.P0 = P0
        self.MI = MI
        self.H0 = H0
        self.H0ne = H0ne
        self.H0se = H0se
        self.H0nw = H0nw
        self.H0sw = H0sw

        # --------------------------------------------------------------------------
        # Pre-processing loop counters for ease of understanding
        vec_R = np.arange((R1 + 0.5 * dR), (R2 - 0.5 * dR), dR)
        vec_TETA = np.arange((TETA1 + 0.5 * dTETA), (TETA2 - 0.5 * dTETA), dTETA)

        # --------------------------------------------------------------------------
        # WHILE LOOP INITIALIZATION
        ResFM = 1
        tolFM = 1e-8

        while ResFM >= tolFM:

            # --------------------------------------------------------------------------
            # Equilibrium position optimization [h0,ar,ap]
            x = scipy.optimize.fmin(
                ArAsh0Equilibrium,
                x0,
                args=(),
                xtol=tolFM,
                ftol=tolFM,
                maxiter=100000,
                maxfun=100000,
                full_output=0,
                disp=1,
                retall=0,
                callback=None,
                initial_simplex=None,
            )
            a_r = x[0]  # [rad]
            a_s = x[1]  # [rad]
            h0 = x[2]  # [m]

            # --------------------------------------------------------------------------
            #  Temperature field
            tolMI = 1e-6

            # TEMPERATURE ==============================================================
            # STARTS HERE ==============================================================

            dHdT=0

            # initial temperature field
            T_i=Ti

            for ii in range(0, NR):
                for jj in range(0, NTETA):
                    mi_i[ii,jj]=(1e-3)*k1*np.exp(k2/(T_i(ii,jj)-k3)) # [Pa.s]

            MI_new=(1/mi0)*mi_i
            MI=0.2*MI_new

            # TEMPERATURE FIELD - Solution of ENERGY equation

            for ii in range(0, NR):
                for jj in range(0, NTETA):
                    varMI=np.abs((MI_new[ii,jj]-MI[ii,jj])/MI[ii,jj])

            while max(varMI)>=tolMI:
                
                MI=MI_new

                # PRESSURE_THD =============================================================
                # STARTS HERE ==============================================================

                [P0,H0,dP0dR,dP0dTETA]= PRESSURE_THD(ar,as,h0,MI);

                # PRESSURE_THD =============================================================
                # ENDS HERE ================================================================
                
                kR=0
                kTETA=0

                # pressure vectorization index
                k=-1

                # volumes number
                nk=(NR)*(NTETA)
                
                # Coefficients Matrix
                Mat_coef=np.zeros(nk,nk) 
                b=np.zeros(nk,1)
                cont=0
                
                for R=(R1+0.5*dR):dR:(R2-0.5*dR)
                    
                    for TETA=(TETA1+0.5*dTETA):dTETA:(TETA2-0.5*dTETA)
                        
                        cont=cont+1;
                        TETAe=TETA+0.5*dTETA;
                        TETAw=TETA-0.5*dTETA;
                        Rn=R+0.5*dR;
                        Rs=R-0.5*dR;
                        
                        
                        %Coefficients for solving the energy equation
                        
                        aux_n=dTETA/12*(R*H0(kR,kTETA)^3/MI(kR,kTETA)*dP0dR(kR,kTETA));
                        
                        CN_1=0.5*aux_n;
                        
                        CS_1=-0.5*aux_n;
                        
                        CP_1=-(CS_1+CN_1);
                        
                        aux_e=(dR/(12*teta0^2)*(H0(kR,kTETA)^3/(R*MI(kR,kTETA))*dP0dTETA(kR,kTETA))-dR/(2*teta0)*H0(kR,kTETA)*R);
                        
                        CE_1=0*aux_e;
                        
                        CW_1=-1*aux_e;
                        
                        CP_2=-(CE_1+CW_1);
                        
                        
                        %difusive terms - central differences
                        CN_2=kt/(rho*cp*war*r1^2)*(dTETA*Rn)/(dR)*H0(kR,kTETA);
                        
                        CS_2=kt/(rho*cp*war*r1^2)*(dTETA*Rs)/(dR)*H0(kR,kTETA);
                        
                        CP_3=-(CN_2+CS_2);
                        
                        CE_2=kt/(rho*cp*war*r1^2)*dR/(teta0^2*dTETA)*H0(kR,kTETA)/R;
                        
                        CW_2=kt/(rho*cp*war*r1^2)*dR/(teta0^2*dTETA)*H0(kR,kTETA)/R;
                        
                        CP_4=-(CE_2+CW_2);
                        
                        CW=CW_1+CW_2; CS=CS_1+CS_2; CN=CN_1+CN_2; CE=CE_1+CE_2;
                        
                        CP=CP_1+CP_2+CP_3+CP_4;
                        
                        B_F=0;
                        
                        B_G=0;
                        
                        B_H=dR*dTETA/(12*teta0^2)*(H0(kR,kTETA)^3/(MI(kR,kTETA)*R)*dP0dTETA(kR,kTETA)^2);
                        
                        B_I=MI(kR,kTETA)*R^3/(H0(kR,kTETA))*dR*dTETA;
                        
                        B_J=dR*dTETA/12*(R*H0(kR,kTETA)^3/MI(kR,kTETA))*dP0dR(kR,kTETA)^2;
                        
                        B_K=dR*dTETA/(12*teta0)*(H0(kR,kTETA)^3/R)*dP0dTETA(kR,kTETA);
                        
                        B_L=dR*dTETA/60*(H0(kR,kTETA)^5/(MI(kR,kTETA)*R))*dP0dR(kR,kTETA)^2;
                        
                        B_M=2*dR*dTETA*(R*MI(kR,kTETA)/H0(kR,kTETA))*(dHdT)^2;
                        
                        B_N=dR*dTETA/3*R*MI(kR,kTETA)*H0(kR,kTETA);
                        
                        B_O=dR*dTETA/(120*teta0^2)*(H0(kR,kTETA)^5/(MI(kR,kTETA)*R^3))*dP0dTETA(kR,kTETA)^2;
                        
                        k=k+1; %vectorization index
                        
                        b(k,1)=-B_F+(war*mi0*r1^2/(rho*cp*h0^2*T0))*(B_G-B_H-B_I-B_J)+(mi0*war/(rho*cp*T0))*(B_K-B_L-B_M-B_N-B_O);
                        
                        if kTETA==1 && kR==1
                            Mat_coef(k,k)=CP+CS;
                            Mat_coef(k,k+1)=CE;
                            Mat_coef(k,k+(NTETA))=CN;
                            b(k,1)=b(k,1)-1*CW;
                        end
                        
                        
                        if kTETA==1 && kR>1 && kR<NR
                            Mat_coef(k,k)=CP;
                            Mat_coef(k,k+1)=CE;
                            Mat_coef(k,k+(NTETA))=CN;
                            Mat_coef(k,k-(NTETA))=CS;
                            b(k,1)=b(k,1)-1*CW;
                        end
                        
                        
                        if kTETA==1 && kR==NR
                            Mat_coef(k,k)=CP+CN;
                            Mat_coef(k,k+1)=CE;
                            Mat_coef(k,k-(NTETA))=CS;
                            b(k,1)=b(k,1)-1*CW;
                        end
                        
                        if kR==1 && kTETA>1 && kTETA<NTETA
                            Mat_coef(k,k)=CP+CS;
                            Mat_coef(k,k+1)=CE;
                            Mat_coef(k,k-1)=CW;
                            Mat_coef(k,k+(NTETA))=CN;
                        end
                        
                        if kTETA>1 && kTETA<NTETA && kR>1 && kR<NR
                            Mat_coef(k,k)=CP;
                            Mat_coef(k,k-1)=CW;
                            Mat_coef(k,k+(NTETA))=CN;
                            Mat_coef(k,k-(NTETA))=CS;
                            Mat_coef(k,k+1)=CE;
                        end
                        
                        if kR==NR && kTETA>1 && kTETA<NTETA
                            Mat_coef(k,k)=CP+CN;
                            Mat_coef(k,k-1)=CW;
                            Mat_coef(k,k+1)=CE;
                            Mat_coef(k,k-(NTETA))=CS;
                        end
                        
                        
                        if kR==1 && kTETA==NTETA
                            Mat_coef(k,k)=CP+CE+CS;
                            Mat_coef(k,k-1)=CW;
                            Mat_coef(k,k+(NTETA))=CN;
                        end
                        
                        if kTETA==NTETA && kR>1 && kR<NR
                            Mat_coef(k,k)=CP+CE;
                            Mat_coef(k,k-1)=CW;
                            Mat_coef(k,k-(NTETA))=CS;
                            Mat_coef(k,k+(NTETA))=CN;
                        end
                        
                        if kTETA==NTETA && kR==NR
                            Mat_coef(k,k)=CP+CN+CE;
                            Mat_coef(k,k-1)=CW;
                            Mat_coef(k,k-(NTETA))=CS;
                        end
                        
                        kTETA=kTETA+1;
                    end
                    kR=kR+1;
                    kTETA=1;
                end
                
                %%%%%%%%%%%%%%%%%%%%%% Pressure field solution %%%%%%%%%%%%%%%%%%%%
                
                t=Mat_coef\b; %solve pressure vectorized
                
                cont=0;
                
                for ii=1:NR
                    for jj=1:NTETA
                        cont=cont+1;
                        T_new(ii,jj)=t(cont); %matrix of pressure
                    end
                end
                
                %viscositu field
                for ii=1:NR
                    for jj=1:NTETA
                        MI_new(ii,jj)=(1e-3)*(1/mi0)*k1*exp(k2/(T0*T_new(ii,jj)-k3));
                        varMI(ii,jj)=abs((MI_new(ii,jj)-MI(ii,jj))/MI(ii,jj));
                    end
                end
                
            end
            T=T_new;


            % -------------------------------------------------------------------------
            % -------------------------------------------------------------------------
            %            RESULTING FORCE AND MOMENTUM: Equilibrium position
            % -------------------------------------------------------------------------
            % -------------------------------------------------------------------------

            Pdim=P0*(r1^2)*war*mi0/(h0^2); %dimensional pressure

            XR=r1*(R1+0.5*dR:dR:R2-0.5*dR);

            Xrp=rp*ones(size(XR));

            XTETA=teta0*(TETA1+0.5*dTETA:dTETA:TETA2-0.5*dTETA);

            for ii=1:NTETA
                Mxr(:,ii)=(Pdim(:,ii).*(XR'.^2)).*sin(XTETA(ii)-tetap);
                Myr(:,ii)=-Pdim(:,ii).*XR'.*(XR.*cos(XTETA(ii)-tetap)-Xrp)';
                Frer(:,ii)=Pdim(:,ii).*XR';
            end

            mxr=trapz(XR,Mxr);
            myr=trapz(XR,Myr);
            frer=trapz(XR,Frer);

            mx=trapz(XTETA,mxr);
            my=trapz(XTETA,myr);
            fre=-trapz(XTETA,frer)+fz/Npad;

            resMx=mx;
            resMy=my;
            resFre=fre;
            return

            # TEMPERATURE ==============================================================
            # ENDS HERE ================================================================

            Ti = T * T0
            ResFM = np.norm(resMx, resMy, resFre)
            xo = x

        # --------------------------------------------------------------------------
        # Full temperature field
        TT = 1 + np.zeros(NR + 1, Npad + 1)
        TT[1:NR, 1:Npad] = np.fliplr(Ti)
        TT[:, 0] = T0
        TT[0, :] = TT[1, :]
        TT[NR + 1, :] = TT[NR, :]
        TT[:, Npad + 1] = TT[:, Npad]
        TT = TT - 273.15

        # --------------------------------------------------------------------------
        # Viscosity field
        for ii in range(0, NR):
            for jj in range(0, Npad):
                mi[ii, jj] = (1e-3) * k1 * np.exp(k2 / (Ti[ii, jj] - k3))  # [Pa.s]

        # PRESSURE =================================================================
        # STARTS HERE ==============================================================

        Ar = a_r * r1 / h0
        As = a_s * r1 / h0
        MI = 1 / mi0 * mi

        # PRESSURE FIELD - Solution of Reynolds equation
        kR = 1
        kTETA = 1

        # index using for pressure vectorization
        k = 0

        # number of volumes
        nk = (NR) * (NTETA)

        # Coefficients Matrix
        Mat_coef = np.zeros(nk, nk)
        b = np.zeros(nk, 0)
        cont = -1

        for R in vec_R:
            for TETA in vec_TETA:

                cont = cont + 1
                TETAe = TETA + 0.5 * dTETA
                TETAw = TETA - 0.5 * dTETA
                Rn = R + 0.5 * dR
                Rs = R - 0.5 * dR

                H0[kR, kTETA] = (
                    h0 / h0
                    + As * (Rp - R * np.cos(teta0 * (TETA - TETAp)))
                    + Ar * R * np.sin(teta0 * (TETA - TETAp))
                )
                H0ne[kR, kTETA] = (
                    h0 / h0
                    + As * (Rp - Rn * np.cos(teta0 * (TETAe - TETAp)))
                    + Ar * Rn * np.sin(teta0 * (TETAe - TETAp))
                )
                H0nw[kR, kTETA] = (
                    h0 / h0
                    + As * (Rp - Rn * np.cos(teta0 * (TETAw - TETAp)))
                    + Ar * Rn * np.sin(teta0 * (TETAw - TETAp))
                )
                H0se[kR, kTETA] = (
                    h0 / h0
                    + As * (Rp - Rs * np.cos(teta0 * (TETAe - TETAp)))
                    + Ar * Rs * np.sin(teta0 * (TETAe - TETAp))
                )
                H0sw[kR, kTETA] = (
                    h0 / h0
                    + As * (Rp - Rs * np.cos(teta0 * (TETAw - TETAp)))
                    + Ar * Rs * np.sin(teta0 * (TETAw - TETAp))
                )

                if kTETA == 0 and kR == 0:
                    MI_e = 0.5 * (MI[kR, kTETA] + MI[kR, kTETA + 1])
                    MI_w = MI[kR, kTETA]
                    MI_n = 0.5 * (MI[kR, kTETA] + MI[kR + 1, kTETA])
                    MI_s = MI[kR, kTETA]

                if kTETA == 0 and kR > 0 and kR < NR:
                    MI_e = 0.5 * (MI[kR, kTETA] + MI[kR, kTETA + 1])
                    MI_w = MI[kR, kTETA]
                    MI_n = 0.5 * (MI[kR, kTETA] + MI[kR + 1, kTETA])
                    MI_s = 0.5 * (MI[kR, kTETA] + MI[kR - 1, kTETA])

                if kTETA == 0 and kR == NR:
                    MI_e = 0.5 * (MI[kR, kTETA] + MI[kR, kTETA + 1])
                    MI_w = MI[kR, kTETA]
                    MI_n = MI[kR, kTETA]
                    MI_s = 0.5 * (MI[kR, kTETA] + MI[kR - 1, kTETA])

                if kR == 0 and kTETA > 0 and kTETA < NTETA:
                    MI_e = 0.5 * (MI[kR, kTETA] + MI[kR, kTETA + 1])
                    MI_w = 0.5 * (MI[kR, kTETA] + MI[kR, kTETA - 1])
                    MI_n = 0.5 * (MI[kR, kTETA] + MI[kR + 1, kTETA])
                    MI_s = MI[kR, kTETA]

                if kTETA > 0 and kTETA < NTETA and kR > 0 and kR < NR:
                    MI_e = 0.5 * (MI[kR, kTETA] + MI[kR, kTETA + 1])
                    MI_w = 0.5 * (MI[kR, kTETA] + MI[kR, kTETA - 1])
                    MI_n = 0.5 * (MI[kR, kTETA] + MI[kR + 1, kTETA])
                    MI_s = 0.5 * (MI[kR, kTETA] + MI[kR - 1, kTETA])

                if kR == NR and kTETA > 0 and kTETA < NTETA:
                    MI_e = 0.5 * (MI[kR, kTETA] + MI[kR, kTETA + 1])
                    MI_w = 0.5 * (MI[kR, kTETA] + MI[kR, kTETA - 1])
                    MI_n = MI[kR, kTETA]
                    MI_s = 0.5 * (MI[kR, kTETA] + MI[kR - 1, kTETA])

                if kR == 0 and kTETA == NTETA:
                    MI_e = MI[kR, kTETA]
                    MI_w = 0.5 * (MI[kR, kTETA] + MI[kR, kTETA - 1])
                    MI_n = 0.5 * (MI[kR, kTETA] + MI[kR + 1, kTETA])
                    MI_s = MI[kR, kTETA]

                if kTETA == NTETA and kR > 0 and kR < NR:
                    MI_e = MI[kR, kTETA]
                    MI_w = 0.5 * (MI[kR, kTETA] + MI[kR, kTETA - 1])
                    MI_n = 0.5 * (MI[kR, kTETA] + MI[kR + 1, kTETA])
                    MI_s = 0.5 * (MI[kR, kTETA] + MI[kR - 1, kTETA])

                if kTETA == NTETA and kR == NR:
                    MI_e = MI[kR, kTETA]
                    MI_w = 0.5 * (MI[kR, kTETA] + MI[kR, kTETA - 1])
                    MI_n = MI[kR, kTETA]
                    MI_s = 0.5 * (MI[kR, kTETA] + MI[kR - 1, kTETA])

                # Coefficients for solving the Reynolds equation
                CE = (
                    1
                    / (24 * teta0 ** 2 * MI_e)
                    * (dR / dTETA)
                    * (H0ne[kR, kTETA] ** 3 / Rn + H0se[kR, kTETA] ** 3 / Rs)
                )
                CW = (
                    1
                    / (24 * teta0 ** 2 * MI_w)
                    * (dR / dTETA)
                    * (H0nw[kR, kTETA] ** 3 / Rn + H0sw[kR, kTETA] ** 3 / Rs)
                )
                CN = (
                    Rn
                    / (24 * MI_n)
                    * (dTETA / dR)
                    * (H0ne[kR, kTETA] ** 3 + H0nw[kR, kTETA] ** 3)
                )
                CS = (
                    Rs
                    / (24 * MI_s)
                    * (dTETA / dR)
                    * (H0se[kR, kTETA] ** 3 + H0sw[kR, kTETA] ** 3)
                )
                CP = -(CE + CW + CN + CS)

                # vectorization index
                k = k + 1

                b[k, 1] = (
                    dR
                    / (4 * teta0)
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
                    Mat_coef[k, k + NTETA] = CN

                if kTETA == 1 and kR > 1 and kR < NR:
                    Mat_coef[k, k] = CP - CW
                    Mat_coef[k, k + 1] = CE
                    Mat_coef[k, k + NTETA] = CN
                    Mat_coef[k, k - NTETA] = CS

                if kTETA == 1 and kR == NR:
                    Mat_coef[k, k] = CP - CW - CN
                    Mat_coef[k, k + 1] = CE
                    Mat_coef[k, k - NTETA] = CS

                if kR == 1 and kTETA > 1 and kTETA < NTETA:
                    Mat_coef[k, k] = CP - CS
                    Mat_coef[k, k + 1] = CE
                    Mat_coef[k, k - 1] = CW
                    Mat_coef[k, k + NTETA] = CN

                if kTETA > 1 and kTETA < NTETA and kR > 1 and kR < NR:
                    Mat_coef[k, k] = CP
                    Mat_coef[k, k - 1] = CW
                    Mat_coef[k, k + NTETA] = CN
                    Mat_coef[k, k - NTETA] = CS
                    Mat_coef[k, k + 1] = CE

                if kR == NR and kTETA > 1 and kTETA < NTETA:
                    Mat_coef[k, k] = CP - CN
                    Mat_coef[k, k - 1] = CW
                    Mat_coef[k, k + 1] = CE
                    Mat_coef[k, k - NTETA] = CS

                if kR == 1 and kTETA == NTETA:
                    Mat_coef[k, k] = CP - CE - CS
                    Mat_coef[k, k - 1] = CW
                    Mat_coef[k, k + NTETA] = CN

                if kTETA == NTETA and kR > 1 and kR < NR:
                    Mat_coef[k, k] = CP - CE
                    Mat_coef[k, k - 1] = CW
                    Mat_coef[k, k - NTETA] = CS
                    Mat_coef[k, k + NTETA] = CN

                if kTETA == NTETA and kR == NR:
                    Mat_coef[k, k] = CP - CE - CN
                    Mat_coef[k, k - 1] = CW
                    Mat_coef[k, k - NTETA] = CS

                kTETA = kTETA + 1

            kR = kR + 1
            kTETA = 1

        # Pressure field solution
        p = np.linalg.solve(Mat_coef, b)
        cont = -1

        # pressure matrix
        for ii in range(0, NR):
            for jj in range(0, NTETA):
                cont = cont + 1
                P0[ii, jj] = p[cont]

        # pressure boundary conditions
        for ii in range(0, NR):
            for jj in range(0, NTETA):
                if P0[ii, jj] < 0:
                    P0[ii, jj] = 0

        # PRESSURE =================================================================
        # ENDS HERE ================================================================

        # --------------------------------------------------------------------------
        # Stiffness and Damping Coefficients
        wp = war  # perturbation frequency [rad/s]
        WP = wp / war

        # HYDROCOEFF_z =============================================================
        # STARTS HERE ==============================================================

        MI = (1 / mi0) * mi

        kR = 0
        kTETA = 0
        k = -1  # pressure vectorization index
        nk = NR * Npad  # volumes number

        # coefficients matrix
        Mat_coef = np.zeros(nk, nk)
        b = np.zeros(nk, 1)
        cont = -1

        for R in vec_R:
            for TETA in vec_TETA:

                cont = cont + 1
                TETAe = TETA + 0.5 * dTETA
                TETAw = TETA - 0.5 * dTETA
                Rn = R + 0.5 * dR
                Rs = R - 0.5 * dR

                if kTETA == 0 and kR == 0:
                    MI_e = 0.5 * (MI[kR, kTETA] + MI[kR, kTETA + 1])
                    MI_w = MI[kR, kTETA]
                    MI_n = 0.5 * (MI[kR, kTETA] + MI[kR + 1, kTETA])
                    MI_s = MI[kR, kTETA]
                    dPdTETAe = (P0[kR, kTETA + 1] - P0[kR, kTETA]) / dTETA
                    dPdTETAw = P0[kR, kTETA] / (0.5 * dTETA)
                    dPdRn = (P0[kR + 1, kTETA] - P0[kR, kTETA]) / dR
                    dPdRs = P0[kR, kTETA] / (0.5 * dR)

                if kTETA == 0 and kR > 0 and kR < NR - 1:
                    MI_e = 0.5 * (MI[kR, kTETA] + MI[kR, kTETA + 1])
                    MI_w = MI[kR, kTETA]
                    MI_n = 0.5 * (MI[kR, kTETA] + MI[kR + 1, kTETA])
                    MI_s = 0.5 * (MI[kR, kTETA] + MI[kR - 1, kTETA])
                    dPdTETAe = (P0[kR, kTETA + 1] - P0[kR, kTETA]) / dTETA
                    dPdTETAw = P0[kR, kTETA] / (0.5 * dTETA)
                    dPdRn = (P0[kR + 1, kTETA] - P0[kR, kTETA]) / dR
                    dPdRs = (P0[kR, kTETA] - P0[kR - 1, kTETA]) / dR

                if kTETA == 0 and kR == NR - 1:
                    MI_e = 0.5 * (MI[kR, kTETA] + MI[kR, kTETA + 1])
                    MI_w = MI[kR, kTETA]
                    MI_n = MI[kR, kTETA]
                    MI_s = 0.5 * (MI[kR, kTETA] + MI[kR - 1, kTETA])
                    dPdTETAe = (P0[kR, kTETA + 1] - P0[kR, kTETA]) / dTETA
                    dPdTETAw = P0[kR, kTETA] / (0.5 * dTETA)
                    dPdRn = -P0[kR, kTETA] / (0.5 * dR)
                    dPdRs = (P0[kR, kTETA] - P0[kR - 1, kTETA]) / dR

                if kR == 0 and kTETA > 0 and kTETA < Npad:
                    MI_e = 0.5 * (MI[kR, kTETA] + MI[kR, kTETA + 1])
                    MI_w = 0.5 * (MI[kR, kTETA] + MI[kR, kTETA - 1])
                    MI_n = 0.5 * (MI[kR, kTETA] + MI[kR + 1, kTETA])
                    MI_s = MI[kR, kTETA]
                    dPdTETAe = (P0[kR, kTETA + 1] - P0[kR, kTETA]) / dTETA
                    dPdTETAw = (P0[kR, kTETA] - P0[kR, kTETA - 1]) / dTETA
                    dPdRn = (P0[kR + 1, kTETA] - P0[kR, kTETA]) / dR
                    dPdRs = P0[kR, kTETA] / (0.5 * dR)

                if kTETA > 0 and kTETA < Npad and kR > 0 and kR < NR:
                    MI_e = 0.5 * (MI[kR, kTETA] + MI[kR, kTETA + 1])
                    MI_w = 0.5 * (MI[kR, kTETA] + MI[kR, kTETA - 1])
                    MI_n = 0.5 * (MI[kR, kTETA] + MI[kR + 1, kTETA])
                    MI_s = 0.5 * (MI[kR, kTETA] + MI[kR - 1, kTETA])
                    dPdTETAe = (P0[kR, kTETA + 1] - P0[kR, kTETA]) / dTETA
                    dPdTETAw = (P0[kR, kTETA] - P0[kR, kTETA - 1]) / dTETA
                    dPdRn = (P0[kR + 1, kTETA] - P0[kR, kTETA]) / dR
                    dPdRs = (P0[kR, kTETA] - P0[kR - 1, kTETA]) / dR

                if kR == NR and kTETA > 0 and kTETA < Npad:
                    MI_e = 0.5 * (MI[kR, kTETA] + MI[kR, kTETA + 1])
                    MI_w = 0.5 * (MI[kR, kTETA] + MI[kR, kTETA - 1])
                    MI_n = MI[kR, kTETA]
                    MI_s = 0.5 * (MI[kR, kTETA] + MI[kR - 1, kTETA])
                    dPdTETAe = (P0[kR, kTETA + 1] - P0[kR, kTETA]) / dTETA
                    dPdTETAw = (P0[kR, kTETA] - P0[kR, kTETA - 1]) / dTETA
                    dPdRn = -P0[kR, kTETA] / (0.5 * dR)
                    dPdRs = (P0[kR, kTETA] - P0[kR - 1, kTETA]) / dR

                if kR == 0 and kTETA == Npad:
                    MI_e = MI[kR, kTETA]
                    MI_w = 0.5 * (MI[kR, kTETA] + MI[kR, kTETA - 1])
                    MI_n = 0.5 * (MI[kR, kTETA] + MI[kR + 1, kTETA])
                    MI_s = MI[kR, kTETA]
                    dPdTETAe = -P0[kR, kTETA] / (0.5 * dTETA)
                    dPdTETAw = (P0[kR, kTETA] - P0[kR, kTETA - 1]) / dTETA
                    dPdRn = (P0[kR + 1, kTETA] - P0[kR, kTETA]) / dR
                    dPdRs = P0[kR, kTETA] / (0.5 * dR)

                if kTETA == Npad and kR > 0 and kR < NR:
                    MI_e = MI[kR, kTETA]
                    MI_w = 0.5 * (MI[kR, kTETA] + MI[kR, kTETA - 1])
                    MI_n = 0.5 * (MI[kR, kTETA] + MI[kR + 1, kTETA])
                    MI_s = 0.5 * (MI[kR, kTETA] + MI[kR - 1, kTETA])
                    dPdTETAe = -P0[kR, kTETA] / (0.5 * dTETA)
                    dPdTETAw = (P0[kR, kTETA] - P0[kR, kTETA - 1]) / dTETA
                    dPdRn = (P0[kR + 1, kTETA] - P0[kR, kTETA]) / dR
                    dPdRs = (P0[kR, kTETA] - P0[kR - 1, kTETA]) / dR

                if kTETA == Npad and kR == NR:
                    MI_e = MI[kR, kTETA]
                    MI_w = 0.5 * (MI[kR, kTETA] + MI[kR, kTETA - 1])
                    MI_n = MI[kR, kTETA]
                    MI_s = 0.5 * (MI[kR, kTETA] + MI[kR - 1, kTETA])
                    dPdTETAe = -P0[kR, kTETA] / (0.5 * dTETA)
                    dPdTETAw = (P0[kR, kTETA] - P0[kR, kTETA - 1]) / dTETA
                    dPdRn = -P0[kR, kTETA] / (0.5 * dR)
                    dPdRs = (P0[kR, kTETA] - P0[kR - 1, kTETA]) / dR

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
                    / (24 * teta0 ** 2 * MI_e)
                    * (dR / dTETA)
                    * (
                        As_ne * H0ne[kR, kTETA] ** 3 / Rn
                        + As_se * H0se[kR, kTETA] ** 3 / Rs
                    )
                )
                CE_2 = (
                    dR
                    / (48 * teta0 ** 2 * MI_e)
                    * (
                        G2_ne * H0ne[kR, kTETA] ** 3 / Rn
                        + G2_se * H0se[kR, kTETA] ** 3 / Rs
                    )
                )
                CE = CE_1 + CE_2

                CW_1 = (
                    1
                    / (24 * teta0 ** 2 * MI_w)
                    * (dR / dTETA)
                    * (
                        As_nw * H0nw[kR, kTETA] ** 3 / Rn
                        + As_sw * H0sw[kR, kTETA] ** 3 / Rs
                    )
                )
                CW_2 = (
                    -dR
                    / (48 * teta0 ** 2 * MI_w)
                    * (
                        G2_nw * H0nw[kR, kTETA] ** 3 / Rn
                        + G2_sw * H0sw[kR, kTETA] ** 3 / Rs
                    )
                )
                CW = CW_1 + CW_2

                CN_1 = (
                    Rn
                    / (24 * MI_n)
                    * (dTETA / dR)
                    * (As_ne * H0ne[kR, kTETA] ** 3 + As_nw * H0nw[kR, kTETA] ** 3)
                )
                CN_2 = (
                    Rn
                    / (48 * MI_n)
                    * (dTETA)
                    * (G1_ne * H0ne[kR, kTETA] ** 3 + G1_nw * H0nw[kR, kTETA] ** 3)
                )
                CN = CN_1 + CN_2

                CS_1 = (
                    Rs
                    / (24 * MI_s)
                    * (dTETA / dR)
                    * (As_se * H0se[kR, kTETA] ** 3 + As_sw * H0sw[kR, kTETA] ** 3)
                )
                CS_2 = (
                    -Rs
                    / (48 * MI_s)
                    * (dTETA)
                    * (G1_se * H0se[kR, kTETA] ** 3 + G1_sw * H0sw[kR, kTETA] ** 3)
                )
                CS = CS_1 + CS_2

                CP = -(CE_1 + CW_1 + CN_1 + CS_1) + (CE_2 + CW_2 + CN_2 + CS_2)

                B_1 = (Rn * dTETA / (8 * MI_n)) * dPdRn * (
                    As_ne * H0ne[kR, kTETA] ** 2 + As_nw * H0nw[kR, kTETA] ** 2
                ) - (Rs * dTETA / (8 * MI_s)) * dPdRs * (
                    As_se * H0se[kR, kTETA] ** 2 + As_sw * H0sw[kR, kTETA] ** 2
                )
                B_2 = (dR / (8 * teta0 ** 2 * MI_e)) * dPdTETAe * (
                    As_ne * H0ne[kR, kTETA] ** 2 / Rn
                    + As_se * H0se[kR, kTETA] ** 2 / Rs
                ) - (dR / (8 * teta0 ** 2 * MI_w)) * dPdTETAw * (
                    As_nw * H0nw[kR, kTETA] ** 2 / Rn
                    + As_sw * H0sw[kR, kTETA] ** 2 / Rs
                )
                B_3 = dR / (4 * teta0) * (As_ne * Rn + As_se * Rs) - dR / (
                    4 * teta0
                ) * (As_nw * Rn + As_sw * Rs)
                B_4 = (
                    complex(0, 1)
                    * WP
                    * dR
                    * dTETA
                    / 4
                    * (Rn * As_ne + Rn * As_nw + Rs * As_se + Rs * As_sw)
                )

                # vectorization index
                k = k + 1

                b[k, 0] = -(B_1 + B_2) + B_3 + B_4

                if kTETA == 0 and kR == 0:
                    Mat_coef[k, k] = CP - CW - CS
                    Mat_coef[k, k + 1] = CE
                    Mat_coef[k, k + Npad] = CN

                if kTETA == 0 and kR > 0 and kR < NR:
                    Mat_coef[k, k] = CP - CW
                    Mat_coef[k, k + 1] = CE
                    Mat_coef[k, k + Npad] = CN
                    Mat_coef[k, k - Npad] = CS

                if kTETA == 0 and kR == NR:
                    Mat_coef[k, k] = CP - CW - CN
                    Mat_coef[k, k + 1] = CE
                    Mat_coef[k, k - Npad] = CS

                if kR == 0 and kTETA > 0 and kTETA < Npad:
                    Mat_coef[k, k] = CP - CS
                    Mat_coef[k, k + 1] = CE
                    Mat_coef[k, k - 1] = CW
                    Mat_coef[k, k + Npad] = CN

                if kTETA > 0 and kTETA < Npad and kR > 0 and kR < NR:
                    Mat_coef[k, k] = CP
                    Mat_coef[k, k - 1] = CW
                    Mat_coef[k, k + Npad] = CN
                    Mat_coef[k, k - Npad] = CS
                    Mat_coef[k, k + 1] = CE

                if kR == NR and kTETA > 0 and kTETA < Npad:
                    Mat_coef[k, k] = CP - CN
                    Mat_coef[k, k - 1] = CW
                    Mat_coef[k, k + 1] = CE
                    Mat_coef[k, k - Npad] = CS

                if kR == 0 and kTETA == Npad:
                    Mat_coef[k, k] = CP - CE - CS
                    Mat_coef[k, k - 1] = CW
                    Mat_coef[k, k + Npad] = CN

                if kTETA == Npad and kR > 0 and kR < NR:
                    Mat_coef[k, k] = CP - CE
                    Mat_coef[k, k - 1] = CW
                    Mat_coef[k, k - Npad] = CS
                    Mat_coef[k, k + Npad] = CN

                if kTETA == Npad and kR == NR:
                    Mat_coef[k, k] = CP - CE - CN
                    Mat_coef[k, k - 1] = CW
                    Mat_coef[k, k - Npad] = CS

                kTETA = kTETA + 1

            kR = kR + 1
            kTETA = 0

        # vectorized pressure field solution
        p = np.linalg.solve(Mat_coef, b)
        cont = -1

        # pressure matrix
        for ii in range(0, NR):
            for jj in range(0, Npad):
                cont = cont + 1
                P[ii, jj] = p[cont]

        # dimensional pressure
        Pdim = P * (r1 ** 2) * war * mi0 / (h0 ** 3)

        # RESULTING FORCE AND MOMENTUM: Equilibrium position
        XR = r1 * vec_R
        XTETA = teta0 * vec_TETA
        Xrp = rp * (1 + np.zeros(XR, XR))

        for ii in range(0, Npad):
            Mxr[:, ii] = (Pdim[:, ii] * (np.transpose(XR) ** 2)) * np.sin(
                XTETA(ii) - tetap
            )
            Myr[:, ii] = (
                -Pdim[:, ii]
                * np.transpose(XR)
                * np.transpose(XR * np.cos(XTETA(ii) - tetap) - Xrp)
            )
            Frer[:, ii] = Pdim[:, ii] * np.transpose(XR)

        mxr = np.trapz[XR, Mxr]
        myr = np.trapz[XR, Myr]
        frer = np.trapz[XR, Frer]

        mx = -np.trapz[XTETA, mxr]
        my = -np.trapz[XTETA, myr]
        fre = -np.trapz[XTETA, frer]

        # HYDROCOEFF_z =============================================================
        # ENDS HERE ================================================================

        K = Npad * np.real(kk_zz)  # Stiffness Coefficient
        C = Npad * 1 / wp * np.imag(kk_zz)  # Damping Coefficient

        # --------------------------------------------------------------------------
        # Output values - Pmax [Pa]- hmax[m] - hmin[m] - h0[m]
        Pmax = np.max(PPdim)
        hmax = np.max(h0 * H0)
        hmin = np.min(h0 * H0)
        Tmax = np.max(TT)
        h0


def ArAsh0Equilibrium(
    r1,
    rp,
    teta0,
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
    dR,
    dTETA,
    k1,
    k2,
    k3,
    T1,
    x,
    MI,
    TETAp,
    Ti,
):

    # loop counters for ease of understanding
    vec_R = np.arange((R1 + 0.5 * dR), (R2 - 0.5 * dR), dR)
    vec_TETA = np.arange((TETA1 + 0.5 * dTETA), (TETA2 - 0.5 * dTETA), dTETA)

    # Pitch angles alpha_r and alpha_p and oil filme thickness at pivot h0
    a_r = x[1]  # [rad]
    a_s = x[2]  # [rad]
    h0 = x[3]  # [m]

    for ii in range(0, NR):
        for jj in range(0, Npad):
            MI[ii, jj] = (
                1 / mi0 * (1e-3) * k1 * np.exp(k2 / (Ti[ii, jj] - k3))
            )  # dimensionless

    # Dimensioneless Parameters
    Ar = a_r * r1 / h0
    As = a_s * r1 / h0
    H0 = h0 / h0

    # PRESSURE FIELD - Solution of Reynolds equation
    kR = 0
    kTETA = 0

    # pressure vectorization index
    k = -1

    # number of volumes
    nk = (NR) * (Npad)  # number of volumes

    # Coefficients Matrix
    Mat_coef = np.zeros(nk, nk)
    b = np.zeros(nk, 0)
    cont = -1

    for R in vec_R:
        for TETA in vec_TETA:

            cont = cont + 1
            TETAe = TETA + 0.5 * dTETA
            TETAw = TETA - 0.5 * dTETA
            Rn = R + 0.5 * dR
            Rs = R - 0.5 * dR

            Hne = (
                H0
                + As * (Rp - Rn * np.cos(teta0 * (TETAe - TETAp)))
                + Ar * Rn * np.sin(teta0 * (TETAe - TETAp))
            )
            Hnw = (
                H0
                + As * (Rp - Rn * np.cos(teta0 * (TETAw - TETAp)))
                + Ar * Rn * np.sin(teta0 * (TETAw - TETAp))
            )
            Hse = (
                H0
                + As * (Rp - Rs * np.cos(teta0 * (TETAe - TETAp)))
                + Ar * Rs * np.sin(teta0 * (TETAe - TETAp))
            )
            Hsw = (
                H0
                + As * (Rp - Rs * np.cos(teta0 * (TETAw - TETAp)))
                + Ar * Rs * np.sin(teta0 * (TETAw - TETAp))
            )

            if kTETA == 0 and kR == 0:
                MI_e = 0.5 * (MI[kR, kTETA] + MI[kR, kTETA + 1])
                MI_w = MI[kR, kTETA]
                MI_n = 0.5 * (MI[kR, kTETA] + MI[kR + 1, kTETA])
                MI_s = MI[kR, kTETA]

            if kTETA == 0 and kR > 0 and kR < NR:
                MI_e = 0.5 * (MI[kR, kTETA] + MI[kR, kTETA + 1])
                MI_w = MI[kR, kTETA]
                MI_n = 0.5 * (MI[kR, kTETA] + MI[kR + 1, kTETA])
                MI_s = 0.5 * (MI[kR, kTETA] + MI[kR - 1, kTETA])

            if kTETA == 0 and kR == NR:
                MI_e = 0.5 * (MI[kR, kTETA] + MI[kR, kTETA + 1])
                MI_w = MI[kR, kTETA]
                MI_n = MI[kR, kTETA]
                MI_s = 0.5 * (MI[kR, kTETA] + MI[kR - 1, kTETA])

            if kR == 0 and kTETA > 0 and kTETA < Npad:
                MI_e = 0.5 * (MI[kR, kTETA] + MI[kR, kTETA + 1])
                MI_w = 0.5 * (MI[kR, kTETA] + MI[kR, kTETA - 1])
                MI_n = 0.5 * (MI[kR, kTETA] + MI[kR + 1, kTETA])
                MI_s = MI[kR, kTETA]

            if kTETA > 0 and kTETA < Npad and kR > 0 and kR < NR:
                MI_e = 0.5 * (MI[kR, kTETA] + MI[kR, kTETA + 1])
                MI_w = 0.5 * (MI[kR, kTETA] + MI[kR, kTETA - 1])
                MI_n = 0.5 * (MI[kR, kTETA] + MI[kR + 1, kTETA])
                MI_s = 0.5 * (MI[kR, kTETA] + MI[kR - 1, kTETA])

            if kR == NR and kTETA > 0 and kTETA < Npad:
                MI_e = 0.5 * (MI[kR, kTETA] + MI[kR, kTETA + 1])
                MI_w = 0.5 * (MI[kR, kTETA] + MI[kR, kTETA - 1])
                MI_n = MI[kR, kTETA]
                MI_s = 0.5 * (MI[kR, kTETA] + MI[kR - 1, kTETA])

            if kR == 0 and kTETA == Npad:
                MI_e = MI[kR, kTETA]
                MI_w = 0.5 * (MI[kR, kTETA] + MI[kR, kTETA - 1])
                MI_n = 0.5 * (MI[kR, kTETA] + MI[kR + 1, kTETA])
                MI_s = MI[kR, kTETA]

            if kTETA == Npad and kR > 0 and kR < NR:
                MI_e = MI[kR, kTETA]
                MI_w = 0.5 * (MI[kR, kTETA] + MI[kR, kTETA - 1])
                MI_n = 0.5 * (MI[kR, kTETA] + MI[kR + 1, kTETA])
                MI_s = 0.5 * (MI[kR, kTETA] + MI[kR - 1, kTETA])

            if kTETA == Npad and kR == NR:
                MI_e = MI[kR, kTETA]
                MI_w = 0.5 * (MI[kR, kTETA] + MI[kR, kTETA - 1])
                MI_n = MI[kR, kTETA]
                MI_s = 0.5 * (MI[kR, kTETA] + MI[kR - 1, kTETA])

            # Coefficients for solving the Reynolds equation
            CE = (
                1
                / (24 * teta0 ** 2 * MI_e)
                * (dR / dTETA)
                * (Hne ** 3 / Rn + Hse ** 3 / Rs)
            )
            CW = (
                1
                / (24 * teta0 ** 2 * MI_w)
                * (dR / dTETA)
                * (Hnw ** 3 / Rn + Hsw ** 3 / Rs)
            )
            CN = Rn / (24 * MI_n) * (dTETA / dR) * (Hne ** 3 + Hnw ** 3)
            CS = Rs / (24 * MI_s) * (dTETA / dR) * (Hse ** 3 + Hsw ** 3)
            CP = -(CE + CW + CN + CS)

            # vectorization index
            k = k + 1

            b[k, 1] = dR / (4 * teta0) * (Rn * Hne + Rs * Hse - Rn * Hnw - Rs * Hsw)

            if kTETA == 1 and kR == 1:
                Mat_coef[k, k] = CP - CS - CW
                Mat_coef[k, k + 1] = CE
                Mat_coef[k, k + Npad] = CN

            if kTETA == 1 and kR > 1 and kR < NR:
                Mat_coef[k, k] = CP - CW
                Mat_coef[k, k + 1] = CE
                Mat_coef[k, k + Npad] = CN
                Mat_coef[k, k - Npad] = CS

            if kTETA == 1 and kR == NR:
                Mat_coef[k, k] = CP - CW - CN
                Mat_coef[k, k + 1] = CE
                Mat_coef[k, k - Npad] = CS

            if kR == 1 and kTETA > 1 and kTETA < Npad:
                Mat_coef[k, k] = CP - CS
                Mat_coef[k, k + 1] = CE
                Mat_coef[k, k - 1] = CW
                Mat_coef[k, k + Npad] = CN

            if kTETA > 1 and kTETA < Npad and kR > 1 and kR < NR:
                Mat_coef[k, k] = CP
                Mat_coef[k, k - 1] = CW
                Mat_coef[k, k + Npad] = CN
                Mat_coef[k, k - Npad] = CS
                Mat_coef[k, k + 1] = CE

            if kR == NR and kTETA > 1 and kTETA < Npad:
                Mat_coef[k, k] = CP - CN
                Mat_coef[k, k - 1] = CW
                Mat_coef[k, k + 1] = CE
                Mat_coef[k, k - Npad] = CS

            if kR == 1 and kTETA == Npad:
                Mat_coef[k, k] = CP - CE - CS
                Mat_coef[k, k - 1] = CW
                Mat_coef[k, k + Npad] = CN

            if kTETA == Npad and kR > 1 and kR < NR:
                Mat_coef[k, k] = CP - CE
                Mat_coef[k, k - 1] = CW
                Mat_coef[k, k - Npad] = CS
                Mat_coef[k, k + Npad] = CN

            if kTETA == Npad and kR == NR:
                Mat_coef[k, k] = CP - CE - CN
                Mat_coef[k, k - 1] = CW
                Mat_coef[k, k - Npad] = CS

            kTETA = kTETA + 1

        kR = kR + 1
        kTETA = 1

    # Pressure field solution
    p = np.linalg.solve(Mat_coef, b)

    cont = -1

    # pressure matrix
    for ii in range(0, NR):
        for jj in range(0, Npad):
            cont = cont + 1
            P[ii, jj] = p[cont]

    # boundary conditions of pressure
    for ii in range(0, NR):
        for jj in range(0, Npad):
            if P[ii, jj] < 0:
                P[ii, jj] = 0

    # dimensional pressure
    Pdim = P * (r1 ** 2) * war * mi0 / (h0 ** 2)

    # RESULTING FORCE AND MOMENTUM: Equilibrium position
    XR = r1 * vec_R
    XTETA = teta0 * vec_TETA
    Xrp = rp * (1 + np.zeros(XR, XR))

    for ii in range(0, Npad):
        Mxr[:, ii] = (Pdim[:, ii] * (np.transpose(XR) ** 2)) * np.sin(XTETA[ii] - tetap)
        Myr[:, ii] = (
            -Pdim[:, ii]
            * np.transpose(XR)
            * np.transpose(XR * np.cos(XTETA(ii) - tetap) - Xrp)
        )
        Frer[:, ii] = Pdim[:, ii] * np.transpose(XR)

    mxr = np.trapz(XR, Mxr)
    myr = np.trapz(XR, Myr)
    frer = np.trapz(XR, Frer)

    mx = np.trapz(XTETA, mxr)
    my = np.trapz(XTETA, myr)
    fre = -np.trapz(XTETA, frer) + fz / Npad

    score = np.norm(mx, my, fre)

    return score


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
        r1=0.5 * 90e-3,  # pad inner radius [m]
        r2=0.5 * 160e-3,  # pad outer radius [m]
        rp=(r2 - r1) * 0.5 + r1,  # pad pivot radius [m]
        teta0=35 * pi / 180,  # pad complete angle [rad]
        tetap=19.5 * pi / 180,  # pad pivot angle [rad]
        TC=40 + 273.15,  # Collar temperature [K]
        Tin=40 + 273.15,  # Cold oil temperature [K]
        T0=0.5 * (TC + Tin),  # Reference temperature [K]
        rho=870,  # Oil density [kg/m³]
        cp=1850,  # Oil thermal capacity [J/kg/K]
        kt=0.15,  # Oil thermal conductivity [W/m/K]
        k1=0.06246,  # Coefficient for ISO VG 32 turbine oil - Vogel's equation
        k2=868.8,  # Coefficient for ISO VG 32 turbine oil - Vogel's equation
        k3=170.4,  # Coefficient for ISO VG 32 turbine oil - Vogel's equation
        mi0=1e-6 * rho * 22,  # Oil VG 22
        fz=370 * 9.81,  # Loading in Y direction [N]
        Npad=3,  # Number of PADs
        NTETA=40,  # TETA direction N volumes
        NR=40,  # R direction N volumes
        war=(1200 * pi) / 30,  # Shaft rotation speed [RPM]
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
