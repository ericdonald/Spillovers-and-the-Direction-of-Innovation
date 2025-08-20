"""""""""""
Economy Module

Notes: This file defines a class for the economy of "Spillovers and the Direction of Innovation".
    
Output:
"""""""""""

import numpy as np
import pandas as pd
import scipy as sp
from pathlib import Path
import SteadyState_Functions as ssf
import Calibration_Functions as cf
import Production_Functions as pf
import Sequential_Root_Solver as srs
import Objective_Functions as of
import Research_Functions as rf



class Economy:
    "Object Describing Simulated Economy"
    
    def __init__(self):
        "Initialize Economy Object"
        
        self.Directory = Path(__file__).resolve().parent.parent.parent
        
        # --------------------------------------- #
        # Define Externally Calibrated Parameters #
        # --------------------------------------- #
        self.Θ = 2 #Number of Climate-Specific Sectors
        self.T = 1 #Years per period
        self.σ = 1.86 #Elasticity of Substitution between Clean & Dirty
        self.λ = 0.10 #Elasticity of Substitution across Sectors
        self.γ = 1.07 #Innovation Size
        self.α = 0.40 #Income Share of Input
        self.L = 100 #Number of Workers
        self.η = 0.50 #Elasticity of Research Effort
        self.ρ_h = 0.015 #Nordhaus Rate of Pure Time Preference
        self.ρ_l = 0.001 #Stern Rate of Pure Time Preference
        self.C_bar = 596.4 #Pre-Industrial Carbon Concentration
        self.var_ρ = 5.3 * 10**(-5) #Climate Damage Semi-Elasticity
        self.ψ_p = 0.25 #Permanent Carbon Fraction
        self.var_θ = 1 #Inverse Intertemporal Elasticity of Substitution
        self.r_d = 2.25 #Relative Input Price for Dirty Technology
        self.o = 1 #Elasticity of Substitution of Spillover Function
        
        J = 2*self.Θ+1
        
        # -------------------------- #
        # Define Calibration Moments #
        # -------------------------- #
        self.g = 0.02 #Steady State Growth
        self.Y0 = 100 #Normalized Initial Output
        self.Year_0 = 2021 #Initial Calibration Year
        self.φ_tilde_0 = np.zeros((J,J)) #Empirical Gross Spillover Network
        self.C_frac_20 = 0.6 #Fraction of Carbon in Atmosphere after 20 Years
        self.C_frac_100 = 0.41 #Fraction of Carbon in Atmosphere after 100 Years
        
        # --------------------------------------- #
        # Define Internally Calibrated Parameters #
        # --------------------------------------- #
        self.r = np.zeros(J) #Input Prices
        self.ν = np.zeros(self.Θ+1) #CES Sector Share
        self.ξbar_0 = np.zeros(J) #Initial Input Subsidies
        self.ψ_0 = 0 #Carbon Remainder
        self.ψ = 0 #Carbon Decay Rate
        self.C1_0 = 0 #Initial Permanent Carbon Concentration
        self.C2_0 = 0 #Initial Transitory Carbon Concentration
        self.A_0 = np.zeros(J) #Initial Technology
        self.ω = np.zeros(J) #Carbon Intensity
        self.φ_hat = np.zeros((J,J)) #CES Spillover Shares
        self.χ = 0 #Research Productivity
        
        
    
    def Calibrate(self):
        "Calibrate Parameters and Initial Conditions"
        
        J = 2*self.Θ + 1
        ξ_lf = np.ones(J)
        cal_panel = pd.io.stata.read_stata(f'{self.Directory}/Empirical/Clean Data/cal_panel.dta')
        cal_panel['year'] = cal_panel['year'].dt.year
        clim_cal_panel = pd.io.stata.read_stata(f'{self.Directory}/Empirical/Clean Data/clim_cal_panel.dta')
        
        # ------------ #
        # Input Prices #
        # ------------ #
        r_θ = np.array([1, self.r_d])
        self.r = np.concatenate((np.tile(r_θ, self.Θ), np.ones(1)))
        
        
        # ---------------- #
        # CES Sector Share #
        # ----------------- #
        S_θ_nu = cal_panel.loc[(cal_panel.year >= 2000) & (cal_panel.year <= 2020), ['S_car','S_elec']].to_numpy()
        nu = np.mean(S_θ_nu, 0)
        nu = np.append(nu, 1-np.sum(nu))
        
        self.ν = nu
        
        
        # -------------------------------- #
        # Status Quo Clean Input Subsidies #
        # -------------------------------- #
        S_car_ξbar = cal_panel.loc[(cal_panel.year >= 2011) & (cal_panel.year <= 2018), ['car_clean_relsub']].to_numpy()
        Mom_car_ξbar = np.mean(S_car_ξbar, 0) #CRS report on EV tax credit published in 2019
        
        q_car_hat = cal_panel.loc[(cal_panel.year >= 2011) & (cal_panel.year <= 2018), ['q_car_clean']].to_numpy()
        S_car_hat = 1 - 1/((q_car_hat/(1-q_car_hat))**((self.σ - 1)/self.σ) + 1)
        Mom_S_car_hat = np.mean(S_car_hat)
        
        z_car = Mom_car_ξbar / self.α / Mom_S_car_hat
        self.ξbar_0[0] = z_car/(1+z_car)
        
        S_elec_ξbar = cal_panel.loc[(cal_panel.year >= 2011) & (cal_panel.year <= 2020), ['elec_clean_relsub']].to_numpy()
        Mom_elec_ξbar = np.mean(S_elec_ξbar, 0) #CRS report on energy investment tax credit published in 2021
        
        q_elec_hat = cal_panel.loc[(cal_panel.year >= 2011) & (cal_panel.year <= 2020), ['q_elec_clean']].to_numpy()
        S_elec_hat = 1 - 1/((q_elec_hat/(1-q_elec_hat))**((self.σ - 1)/self.σ) + 1)
        Mom_S_elec_hat = np.mean(S_elec_hat)
        
        z_elec = Mom_elec_ξbar / self.α / Mom_S_elec_hat
        self.ξbar_0[2] = z_elec/(1+z_elec)
        
        
        # ----------------- #
        # Carbon Parameters #
        # ----------------- #
        t_1 = 20
        t_2 = 100
        dt = t_2 - t_1
        
        frac_1 = self.C_frac_20 - self.ψ_p
        frac_2 = self.C_frac_100 - self.ψ_p
        
        self.ψ_0 = frac_1**(t_2/dt) / frac_2**(t_1/dt) / (1 - self.ψ_p)
        self.ψ = (frac_1 / self.ψ_0 / (1 - self.ψ_p))**(1/t_1)
        
        
        # ------------------------- #
        # Carbon Initial Conditions #
        # ------------------------- #
        self.C1_0 = self.C_bar + self.ψ_p*np.sum(clim_cal_panel.loc[clim_cal_panel.year < self.Year_0 + self.T, ['C_em']].to_numpy())
        self.C2_0 = np.mean(clim_cal_panel.loc[(clim_cal_panel.year >= self.Year_0) & (clim_cal_panel.year < self.Year_0 + self.T), ['C_stock']].to_numpy()) - self.C1_0
        
        
        # ------------------ #
        # Initial Technology #
        # ------------------ #
        S_A0 = cal_panel.loc[(cal_panel.year >= self.Year_0) & (cal_panel.year < self.Year_0 + self.T), ['q_car_clean','q_elec_clean','S_car','S_elec']].to_numpy()
        Mom_A0 = np.mean(S_A0, 0)
        
        r_tilde = (1-self.ξbar_0)*self.r
        
        C_0 = self.C1_0 + self.C2_0
        Ω_0 = pf.Damage(C_0, self.C_bar, self.var_ρ)

        A_0g = np.ones(J)
    
        A_init = sp.optimize.root(cf.A0_root, A_0g,
                      args=(Mom_A0, self.Y0, r_tilde, self.α, self.Θ, self.σ, self.λ, self.ν, self.L, Ω_0),
                      method='lm')
       
        self.A_0 = A_init.x
        
        
        # ---------------- #
        # Carbon Intensity #
        # ---------------- #
        C_ω = cal_panel.loc[(cal_panel.year >= self.Year_0) & (cal_panel.year < self.Year_0 + self.T), ['car_C_em','elec_C_em']].to_numpy()
        Mom_ω = np.sum(C_ω, 0)
        
        omega_dg = np.ones(self.Θ)
    
        omega_d = sp.optimize.root(cf.omega_root, omega_dg,
                      args=(Mom_ω, self.A_0, r_tilde, self.α, self.σ, self.λ, self.ν, Ω_0, self.L, self.Θ),
                      method='lm')
      
        for θ in range(self.Θ):
           self.ω[2*θ+1] = omega_d.x[θ]
        
        
        # ----------------- #
        # Spillover Network #
        # ----------------- #
        self.φ_tilde_0 = pd.io.stata.read_stata(f'{self.Directory}/Empirical/Clean Data/citation_shares.dta').to_numpy()
        
        φ_hatg = self.φ_tilde_0.ravel()
    
        phi_hat_init = sp.optimize.root(cf.phi_hat_root, φ_hatg,
                      args=(self.φ_tilde_0, self.A_0, self.o),
                      method='lm')
       
        self.φ_hat = phi_hat_init.x.reshape((J,J))
        
        
        # --------------------- #
        # Research Productivity #
        # --------------------- #
        Abar_ss = ssf.Abar_SS(self.η, self.φ_hat, self.α, self.σ, self.λ, self.ν, self.r, ξ_lf, self.Θ, self.o)
        chi_g = 1
    
        chi = sp.optimize.root(cf.chi_root, chi_g,
                      args=(Abar_ss, self.g, self.η, self.φ_hat, self.γ, self.ν, self.T, self.Θ, self.o),
                      method='lm')
        
        self.χ = chi.x
        


    def TensMatch(self, Year_start, Year_end):
        "Output Match of 2010s Experience"    
        
        J = 2*self.Θ + 1
        cal_panel = pd.io.stata.read_stata(f'{self.Directory}/Empirical/Clean Data/cal_panel.dta')
        cal_panel['year'] = cal_panel['year'].dt.year
        clim_cal_panel = pd.io.stata.read_stata(f'{self.Directory}/Empirical/Clean Data/clim_cal_panel.dta')
    
        # ------------------ #
        # Initial Technology #
        # ------------------ #
        S_A0 = cal_panel.loc[(cal_panel.year >= Year_start) & (cal_panel.year < Year_start + self.T), ['q_car_clean','q_elec_clean','S_car','S_elec']].to_numpy()
        Mom_A0 = np.mean(S_A0, 0)
        
        r_tilde = (1-self.ξbar_0)*self.r
        
        C_0 = np.mean(clim_cal_panel.loc[(clim_cal_panel.year >= Year_start) & (clim_cal_panel.year < Year_start + self.T), ['C_stock']].to_numpy())
        Ω_0 = pf.Damage(C_0, self.C_bar, self.var_ρ)

        A_0g = np.ones(J)
    
        A_0 = sp.optimize.root(cf.A0_root, A_0g,
                      args=(Mom_A0, self.Y0, r_tilde, self.α, self.Θ, self.σ, self.λ, self.ν, self.L, Ω_0),
                      method='lm')
        
        A_start = A_0.x
        
        # ------------------------------- #
        # Status Quo Innovation Subsidies #
        # ------------------------------- #
        S_ξ = cal_panel.loc[(cal_panel.year >= Year_start) & (cal_panel.year <= 2015), ['car_clean_RD_relsub', 'car_dirty_RD_relsub', 'elec_clean_RD_relsub', 'elec_dirty_RD_relsub']].to_numpy()
        Mom_ξ = np.mean(S_ξ, 0) #IEA innovation subsidy data stop after 2015
        
        ξ_0g = np.ones(J-1)
    
        ξ_init = sp.optimize.root(cf.ξ0_root, ξ_0g,
                      args=(Mom_ξ, A_start, self.T, Year_start, r_tilde, self.α, self.Θ, self.σ, self.λ, self.ν, self.L, self.η, self.φ_hat, self.χ, self.γ, self.o),
                      method='lm')
       
        ξ_0 = np.ones(J)
        ξ_0[:-1] = ξ_init.x
        
        # ----------------------------------- #
        # Calibration for Low Spillover Model #
        # ----------------------------------- #
        φ_hat_low = np.eye(J)
        
        ξ_init_low = sp.optimize.root(cf.ξ0_root, ξ_0[:-1],
                      args=(Mom_ξ, A_start, self.T, Year_start, r_tilde, self.α, self.Θ, self.σ, self.λ, self.ν, self.L, self.η, φ_hat_low, self.χ, self.γ, self.o),
                      method='lm')
       
        ξ_0low = np.ones(J)
        ξ_0low[:-1] = ξ_init_low.x
        
        # -------------------------- #
        # Simulate Equilibrium Paths #
        # -------------------------- #
        T_plus = int(np.ceil((Year_end - Year_start)/self.T))
        
        A_ten = of.Eqbm_Path(A_start, T_plus, self.η, self.φ_hat, self.χ, self.γ, self.α, self.λ, self.ν, self.σ, self.L, r_tilde, ξ_0, self.Θ, self.o)[1]
        A_ten_low = of.Eqbm_Path(A_start, T_plus, self.η, φ_hat_low, self.χ, self.γ, self.α, self.λ, self.ν, self.σ, self.L, r_tilde, ξ_0low, self.Θ, self.o)[1]

        T_year = Year_end - Year_start + 1
        q_θc = np.zeros((T_year, self.Θ))
        q_θc_low = np.zeros((T_year, self.Θ))
        for t in range(T_year):
            T_up = int(np.ceil(t/self.T))
            T_down = int(np.floor(t/self.T))
            T_wght = t/self.T - T_down
            q_θc[t,:] = (1-T_wght) * pf.q_c(r_tilde, A_ten[T_down,:], self.α, self.σ, self.Θ) + T_wght * pf.q_c(r_tilde, A_ten[T_up,:], self.α, self.σ, self.Θ)
            q_θc_low[t,:] = (1-T_wght) * pf.q_c(r_tilde, A_ten_low[T_down,:], self.α, self.σ, self.Θ) + T_wght * pf.q_c(r_tilde, A_ten_low[T_up,:], self.α, self.σ, self.Θ)
        
        return (q_θc, q_θc_low, A_start, ξ_0, ξ_0low)
        
    
    
    def IAM(self, Periods, T_time, SCC_frac, disc_high, spill_low, dam_high):
        "Simulation of IAM"
        
        J = 2*self.Θ + 1
        N = 6 + 2*J
        
        # -------------------- #
        # Select Discount Rate #
        # -------------------- #
        if disc_high == 1:
            ρ = (1+self.ρ_h)**self.T - 1
        else:
            ρ = (1+self.ρ_l)**self.T - 1
            
        # ------------------------ #
        # Select Spillover Network #
        # ------------------------ #
        if spill_low == 1:
            φ_hat_IAM = np.eye(J)
        else:
            φ_hat_IAM = self.φ_hat
            
        # -------------- #
        # Select Damages #
        # -------------- #
        if dam_high == 1:
            var_ρ = 4*self.var_ρ
        else:
            var_ρ = self.var_ρ
            
        # ----------------- #
        # Outside Emissions #
        # ----------------- #
        cal_panel = pd.io.stata.read_stata(f'{self.Directory}/Empirical/Clean Data/cal_panel.dta')
        cal_panel['year'] = cal_panel['year'].dt.year
        C_ω = cal_panel.loc[(cal_panel.year >= 2000) & (cal_panel.year <= 2020), ['car_C_relem','elec_C_relem']].to_numpy()
        relEm = np.sum(np.mean(C_ω, 0))
        
        RICE = pd.io.stata.read_stata(f'{self.Directory}/Empirical/Clean Data/RICE.dta')
        RICE_optEm = RICE.loc[(RICE.year >= self.Year_0 + self.T) & (RICE.year <= self.Year_0 + Periods*self.T), ['Optimal_Global_Em', 'Optimal_US_Em']].to_numpy()
        Em_out = RICE_optEm[:,0] - relEm * RICE_optEm[:,1]
        
        sum_Em_out = np.zeros((Periods,1))
        for t in range(Periods):
            start_idx = t * self.T
            end_idx = start_idx + self.T
            group_sum = np.sum(Em_out[start_idx:end_idx])
            sum_Em_out[t,:] = group_sum
            
        # ------------------- #
        # Steady-State Policy #
        # ------------------- #
        if spill_low == 1:
            g_ss = np.log(self.γ) * self.χ
            Rtilde_inv = (1+g_ss)**(1-self.var_θ) / (1+ρ)
            ξtilde_ss = np.array([self.ν[0], 0, self.ν[1], 0, self.ν[-1]]) / (self.γ-1) / (1-Rtilde_inv)
        elif SCC_frac == 0:
            Rtilde_inv = 1 / (1+ρ)
            ξtilde_ss = np.array([self.ν[0], 0, self.ν[1], 0, self.ν[-1]]) / (self.γ-1) / (1-Rtilde_inv)
            g_ss = 10**(-7)
        else:
            (ξtilde_ss, Abar_ss) = ssf.Opt_SS(self.r, self.α, self.λ, self.γ, self.χ, self.ν, self.η, φ_hat_IAM, ρ, self.var_θ, self.Θ, self.o)
            g_ss = ssf.Growth_SS(Abar_ss, φ_hat_IAM, self.η, self.ν, self.γ, self.χ, self.Θ, self.o)
            Rtilde_inv = (1+g_ss)**(1-self.var_θ) / (1+ρ)
            
        τtilde_1ss = var_ρ * self.ψ_p / (1-Rtilde_inv)
        τtilde_2ss = var_ρ * (1-self.ψ_p) * self.ψ_0 / (1-self.ψ*Rtilde_inv)
        
        ς1_ss = 0
        ς2_ss = 0
        
        # ------------- #
        # Initial Guess #
        # ------------- #
        τ1_g = τtilde_1ss * self.Y0 * (1+self.g)**(np.arange(Periods)+1)
        τ1_g = τ1_g.reshape((Periods, 1))
        
        τ2_g = τtilde_2ss * self.Y0 * (1+self.g)**(np.arange(Periods)+1)
        τ2_g = τ2_g.reshape((Periods, 1))
        
        C1_g = np.zeros((Periods,1))
        C2_g = np.zeros((Periods,1))
        
        C1_g[0,:] = pf.Perm_Carb(self.C1_0, sum_Em_out[0,:], self.ψ_p)
        C2_g[0,:] = pf.Tran_Carb(self.C2_0, sum_Em_out[0,:], self.ψ_p, self.ψ_0, self.ψ)
        
        for t in range(1,Periods):
            C1_g[t,:] = pf.Perm_Carb(C1_g[t-1,:], sum_Em_out[t,:], self.ψ_p)
            C2_g[t,:] = pf.Tran_Carb(C2_g[t-1,:], sum_Em_out[t,:], self.ψ_p, self.ψ_0, self.ψ)
        
        if spill_low == 1:
            d = (0.975**np.arange(Periods)).reshape((Periods,1))
            ξtilde_g = np.hstack((np.full((Periods,1), self.ν[0]), self.ν[0]*d, np.full((Periods,1), self.ν[1]), self.ν[1]*d, np.full((Periods,1), self.ν[-1]))) / (self.γ-1) / (1-Rtilde_inv)
        else:
            ξtilde_g = np.tile(ξtilde_ss.reshape((1,J)), (Periods,1))
            if SCC_frac == 0:
                ξtilde_g[:,:-1] = 1.25*ξtilde_g[:,:-1]
        
        s_g = np.zeros((Periods,J))
        A_g = np.zeros((Periods,J))
        
        s_g[0,:] = rf.Science(self.A_0, ξtilde_g[0,:], self.η, φ_hat_IAM, self.ν, self.Θ, self.o)
        A_g[0,:] = rf.A_new(s_g[0,:], self.A_0, self.η, φ_hat_IAM, self.χ, self.γ, self.ν, self.o)
        
        for t in range(1, Periods):
            s_g[t,:] = rf.Science(A_g[t-1,:], ξtilde_g[t,:], self.η, φ_hat_IAM, self.ν, self.Θ, self.o)
            A_g[t,:] = rf.A_new(s_g[t,:], A_g[t-1,:], self.η, φ_hat_IAM, self.χ, self.γ, self.ν, self.o)
                
        ς1_g = np.zeros((Periods,1))
        ς2_g = np.zeros((Periods,1))
        
        X_g = np.hstack((np.log(τ1_g), np.log(τ2_g), np.log(C1_g), np.log(C2_g), ξtilde_g, np.log(A_g), ς1_g, ς2_g))
        
        # --------- #
        # Functions #
        # --------- #
        Funcs = (of.τ_root, of.C_root, of.ξtilde_root, of.A_root, of.ς_root)
        
        N_lag = tuple([2,3]) + tuple(range(J + 4, J*2 + 4))
        N_t = tuple(range(N))
        N_lead = tuple(range(N))
        
        r_adjust = np.tile(self.r.reshape((1,J)), (Periods, 1))
        ν_adjust = np.tile(self.ν.reshape((1,self.Θ+1)), (Periods, 1))
        ω_adjust = np.tile(self.ω.reshape((1,J)), (Periods, 1))
        args = (Periods, ρ, self.var_θ, φ_hat_IAM, self.γ, self.χ, self.η, r_adjust, self.α, self.σ, self.λ, ν_adjust, self.L, ω_adjust, self.C_bar, var_ρ, self.ψ_p, self.ψ_0, self.ψ, sum_Em_out, self.Θ, SCC_frac, self.o)
        
        # ----------------------------- #
        # Initial & Terminal Conditions #
        # ----------------------------- #
        Init = np.ones((1,N))
        Init[0,2] = np.log(self.C1_0)
        Init[0,3] = np.log(self.C2_0)
        Init[0,4+J:-2] = np.log(self.A_0)

        Term = np.ones((1,N))
        Term[0,0] = np.log(τtilde_1ss)
        Term[0,1] = np.log(τtilde_2ss)
        Term[0,4:4+J] = ξtilde_ss
        Term[0,4+J:-2] = np.log(np.full(J, g_ss))
        Term[0,-2] = ς1_ss
        Term[0,-1] = ς2_ss
        
        # ----- #
        # Solve #
        # ----- #
        X = srs.SRS(X_g, Funcs, Init, Term, args, N_lag, N_t, N_lead)
    
        # -------------------------------------------------------------------- #
        # Unpack Carbon Price, Carbon Concentration, Subsidies, and Technology #
        # -------------------------------------------------------------------- #
        τ = (np.exp(X[:T_time,0]) + np.exp(X[:T_time,1])).reshape((T_time,1))
        C = (np.exp(X[:T_time,2]) + np.exp(X[:T_time,3])).reshape((T_time,1))
        ξtilde = X[:T_time,4:4+J]
        A = np.exp(X[:T_time,4+J:-2])
        
                
        return (τ, C, ξtilde, A)



    def CES_IAM(self, Periods, T_time, o):
        "Simulation of IAM with CES Spillovers"
        
        self.o = o
        J = 2*self.Θ + 1
        N = 6 + 2*J
        
        
        # ----------------------------------------------------------------

        # Recalibrate research parameters.

        # ----------------------------------------------------------------
        
        # ----------------- #
        # Spillover Network #
        # ----------------- #
        φ_hatg = self.φ_tilde_0.ravel()
    
        phi_hat_init = sp.optimize.root(cf.phi_hat_root, φ_hatg,
                      args=(self.φ_tilde_0, self.A_0, self.o),
                      method='lm')
       
        self.φ_hat = phi_hat_init.x.reshape((J,J))
        
        
        # --------------------- #
        # Research Productivity #
        # --------------------- #
        ξ_lf = np.ones(J)
        Abar_ss = ssf.Abar_SS(self.η, self.φ_hat, self.α, self.σ, self.λ, self.ν, self.r, ξ_lf, self.Θ, self.o)
        chi_g = 1
    
        chi = sp.optimize.root(cf.chi_root, chi_g,
                      args=(Abar_ss, self.g, self.η, self.φ_hat, self.γ, self.ν, self.T, self.Θ, self.o),
                      method='lm')
        
        self.χ = chi.x
        
        
        # ----------------------------------------------------------------

        # IAM.

        # ----------------------------------------------------------------
        
        # ----------------- #
        # Outside Emissions #
        # ----------------- #
        cal_panel = pd.io.stata.read_stata(f'{self.Directory}/Empirical/Clean Data/cal_panel.dta')
        cal_panel['year'] = cal_panel['year'].dt.year
        C_ω = cal_panel.loc[(cal_panel.year >= 2000) & (cal_panel.year <= 2020), ['car_C_relem','elec_C_relem']].to_numpy()
        relEm = np.sum(np.mean(C_ω, 0))
        
        RICE = pd.io.stata.read_stata(f'{self.Directory}/Empirical/Clean Data/RICE.dta')
        RICE_optEm = RICE.loc[(RICE.year >= self.Year_0 + self.T) & (RICE.year <= self.Year_0 + Periods*self.T), ['Optimal_Global_Em', 'Optimal_US_Em']].to_numpy()
        Em_out = RICE_optEm[:,0] - relEm * RICE_optEm[:,1]
        
        sum_Em_out = np.zeros((Periods,1))
        for t in range(Periods):
            start_idx = t * self.T
            end_idx = start_idx + self.T
            group_sum = np.sum(Em_out[start_idx:end_idx])
            sum_Em_out[t,:] = group_sum
            
        # ------------------- #
        # Steady-State Policy #
        # ------------------- #
        ρ = (1+self.ρ_l)**self.T - 1
        (ξtilde_ss, Abar_ss) = ssf.Opt_SS(self.r, self.α, self.λ, self.γ, self.χ, self.ν, self.η, self.φ_hat, ρ, self.var_θ, self.Θ, self.o)
        g_ss = ssf.Growth_SS(Abar_ss, self.φ_hat, self.η, self.ν, self.γ, self.χ, self.Θ, self.o)
        Rtilde_inv = (1+g_ss)**(1-self.var_θ) / (1+ρ)
            
        τtilde_1ss = self.var_ρ * self.ψ_p / (1-Rtilde_inv)
        τtilde_2ss = self.var_ρ * (1-self.ψ_p) * self.ψ_0 / (1-self.ψ*Rtilde_inv)
        
        ς1_ss = 0
        ς2_ss = 0
        
        # ------------- #
        # Initial Guess #
        # ------------- #
        τ1_g = τtilde_1ss * self.Y0 * (1+self.g)**(np.arange(Periods)+1)
        τ1_g = τ1_g.reshape((Periods, 1))
        
        τ2_g = τtilde_2ss * self.Y0 * (1+self.g)**(np.arange(Periods)+1)
        τ2_g = τ2_g.reshape((Periods, 1))
        
        C1_g = np.zeros((Periods,1))
        C2_g = np.zeros((Periods,1))
        
        C1_g[0,:] = pf.Perm_Carb(self.C1_0, sum_Em_out[0,:], self.ψ_p)
        C2_g[0,:] = pf.Tran_Carb(self.C2_0, sum_Em_out[0,:], self.ψ_p, self.ψ_0, self.ψ)
        
        for t in range(1,Periods):
            C1_g[t,:] = pf.Perm_Carb(C1_g[t-1,:], sum_Em_out[t,:], self.ψ_p)
            C2_g[t,:] = pf.Tran_Carb(C2_g[t-1,:], sum_Em_out[t,:], self.ψ_p, self.ψ_0, self.ψ)
        
        ξtilde_g = np.tile(ξtilde_ss.reshape((1,J)), (Periods,1))
        ξtilde_g[:,1] = ξtilde_g[:,0]
        ξtilde_g[:,3] = ξtilde_g[:,2]
            
        s_g = np.zeros((Periods,J))
        A_g = np.zeros((Periods,J))
        
        s_g[0,:] = rf.Science(self.A_0, ξtilde_g[0,:], self.η, self.φ_hat, self.ν, self.Θ, self.o)
        A_g[0,:] = rf.A_new(s_g[0,:], self.A_0, self.η, self.φ_hat, self.χ, self.γ, self.ν, self.o)
        
        for t in range(1, Periods):
            s_g[t,:] = rf.Science(A_g[t-1,:], ξtilde_g[t,:], self.η, self.φ_hat, self.ν, self.Θ, self.o)
            A_g[t,:] = rf.A_new(s_g[t,:], A_g[t-1,:], self.η, self.φ_hat, self.χ, self.γ, self.ν, self.o)
                
        ς1_g = np.zeros((Periods,1))
        ς2_g = np.zeros((Periods,1))
        
        X_g = np.hstack((np.log(τ1_g), np.log(τ2_g), np.log(C1_g), np.log(C2_g), ξtilde_g, np.log(A_g), ς1_g, ς2_g))
        
        # --------- #
        # Functions #
        # --------- #
        Funcs = (of.τ_root, of.C_root, of.ξtilde_root, of.A_root, of.ς_root)
        
        N_lag = tuple([2,3]) + tuple(range(J + 4, J*2 + 4))
        N_t = tuple(range(N))
        N_lead = tuple(range(N))
        
        r_adjust = np.tile(self.r.reshape((1,J)), (Periods, 1))
        ν_adjust = np.tile(self.ν.reshape((1,self.Θ+1)), (Periods, 1))
        ω_adjust = np.tile(self.ω.reshape((1,J)), (Periods, 1))
        args = (Periods, ρ, self.var_θ, self.φ_hat, self.γ, self.χ, self.η, r_adjust, self.α, self.σ, self.λ, ν_adjust, self.L, ω_adjust, self.C_bar, self.var_ρ, self.ψ_p, self.ψ_0, self.ψ, sum_Em_out, self.Θ, 1, self.o)
        
        # ----------------------------- #
        # Initial & Terminal Conditions #
        # ----------------------------- #
        Init = np.ones((1,N))
        Init[0,2] = np.log(self.C1_0)
        Init[0,3] = np.log(self.C2_0)
        Init[0,4+J:-2] = np.log(self.A_0)

        Term = np.ones((1,N))
        Term[0,0] = np.log(τtilde_1ss)
        Term[0,1] = np.log(τtilde_2ss)
        Term[0,4:4+J] = ξtilde_ss
        Term[0,4+J:-2] = np.log(np.full(J, g_ss))
        Term[0,-2] = ς1_ss
        Term[0,-1] = ς2_ss
        
        # ----- #
        # Solve #
        # ----- #
        X = srs.SRS(X_g, Funcs, Init, Term, args, N_lag, N_t, N_lead)
    
        # -------------------------------------------------------------------- #
        # Unpack Carbon Price, Carbon Concentration, Subsidies, and Technology #
        # -------------------------------------------------------------------- #
        τ = (np.exp(X[:T_time,0]) + np.exp(X[:T_time,1])).reshape((T_time,1))
        C = (np.exp(X[:T_time,2]) + np.exp(X[:T_time,3])).reshape((T_time,1))
        ξtilde = X[:T_time,4:4+J]
        A = np.exp(X[:T_time,4+J:-2])
        
                
        return (τ, C, ξtilde, A)
















   
    
   
    
        