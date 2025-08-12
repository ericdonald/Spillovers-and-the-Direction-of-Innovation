"""""""""""
Calibration Functions

Notes: Functions the define the calibration roots of the economy.
    
Output:
"""""""""""

import numpy as np
from numba import njit
import Production_Functions as pf
import SteadyState_Functions as ssf
import Objective_Functions as of
import Research_Functions as rf



@njit
def phi_hat_root(φ_hat, φ_tilde_0, A_0, o):
    "Root to Calibate CES Spillover Shares"
    
    J = φ_tilde_0.shape[0]
    φ_hat = φ_hat.reshape((J, J))
    φ = rf.SpillNet(φ_hat, A_0, o)
    I = np.eye(J)

    roots = φ_tilde_0 - (φ+I)

    roots[:,-1] = 1 - np.sum(φ_hat,1)

    return roots.ravel()
 
    


@njit
def chi_root(χ, Abar_ss, g, η, φ_hat, γ, ν, T, Θ, o):
    "Root to Calibrate Research Productivity"
    
    g_hat = ssf.Growth_SS(Abar_ss, φ_hat, η, ν, γ, χ, Θ, o)
    
    growth = ((1+g)**T - 1) - g_hat
    
    return growth

    

@njit
def A0_root(A_0, Mom_A0, Mom_Y0, r_tilde, α, Θ, σ, λ, ν, L, Ω_0):
    "Root to Calibrate Initial Technology"
    
    ###############################################
    ### Moments for Initial Relative Technology ###
    ###############################################
    q = pf.q_c(r_tilde, A_0, α, σ, Θ)
    Q = Mom_A0[:Θ] - q #Clean quantity shares
    
    S_θ = pf.Shares_θ(r_tilde, A_0, α, σ, λ, ν, Θ)[:-1]
    Sh = Mom_A0[Θ:] - S_θ #Sector shares
    
    ##############################################
    ### Moment for Initial Absolute Technology ###
    ##############################################
    Y0 = pf.Output(r_tilde, A_0, α, σ, λ, ν, Ω_0, L, Θ)
    Cal_y = Mom_Y0 - Y0 #Initial output level
    
    
    return np.concatenate((Q, Sh, Cal_y))



def ξ0_root(ξ_0, Mom_ξ, A_0, T, Year_0, r_tilde, α, Θ, σ, λ, ν, L, η, φ_hat, χ, γ, o):
    "Root to Calibrate Status Quo Innovation Subsidies"
    
    J = 2*Θ+1
    ξ = np.append(ξ_0, 1)
    
    T_plus = int(np.ceil((2020 - Year_0)/T))-1
    s = of.Eqbm_Path(A_0, T_plus, η, φ_hat, χ, γ, α, λ, ν, σ, L, r_tilde, ξ, Θ, o)[0]
        
    ξ_relsub = np.zeros((T_plus,J-1))
    
    for t in range(T_plus):
        ξ_relsub[t,:] = ((ξ_0-1)/ξ_0) * s[t+1,:-1] / η
    
    InnSub = Mom_ξ - np.mean(ξ_relsub, 0)
    
    return InnSub



@njit
def omega_root(ω_d, Mom_ω, A_0, r_tilde, α, σ, λ, ν, Ω_0, L, Θ):
    "Root to Calibrate Carbon Intensities"
    
    J = 2*Θ+1
    ω = np.zeros(J)
    for θ in range(Θ):
        ω[2*θ+1] = ω_d[θ]
    
    Em_θ = pf.GHG_θ(r_tilde, A_0, α, σ, λ, ν, Ω_0, L, ω, Θ)[:-1]
    
    EPA = Mom_ω - Em_θ
    
    return EPA



@njit
def psi_root(psi_g, C_data, Em, C1_Start, C2_start, ψ_p):
    "Root to Calibrate Climate Parameters"
    
    #########################
    ### Unpack Parameters ###
    #########################
    ψ = np.exp(psi_g[0]) / (1 + np.exp(psi_g[0]))
    ψ_0 = np.exp(psi_g[1]) / (1 + np.exp(psi_g[1]))
    
    #####################
    ### Simulate Path ###
    #####################
    C1 = np.ones(Em.size)*C1_Start
    C2 = np.ones(Em.size)*C2_start
    
    for t in range(1, Em.size):
        C1[t] = pf.Perm_Carb(C1[t-1], Em[t], ψ_p)
        C2[t] = pf.Tran_Carb(C2[t-1], Em[t], ψ_p, ψ_0, ψ)
    
    C = C1 + C2
        
    Δ = np.sum(np.abs(C - C_data))
    
    return Δ
    
    
        
        
        
        
        
        
        
        
        