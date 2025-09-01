"""""""""""
Objective Functions

Notes: Functions that describe the objectives and optimality conditions of the economy.
    
"""""""""""

import numpy as np
from numba import njit
import scipy as sp
import Production_Functions as pf
import Research_Functions as rf



def Eqbm_Path(A_0, T_plus, η, φ_hat, χ, γ, α, λ, ν, σ, L, r_tilde, ξ, Θ, o):
    "Simulation of Equilibrium Path"
    
    J = 2*Θ + 1
        
    s = np.zeros((T_plus+1,J))
    A = np.zeros((T_plus+1,J))
    
    # ------------------ #
    # Initial Conditions #
    # ------------------ #
    A[0,:] = A_0
    
    # ---------------- #
    # Equilibrium Path #
    # ---------------- #
    for t in range(1, T_plus+1):
        s[t,:] = rf.ScienceEqbm(A[t-1,:], η, φ_hat, χ, γ, α, λ, ν, σ, L, r_tilde, ξ, Θ, o)
        A[t,:] = rf.A_new(s[t,:], A[t-1,:], η, φ_hat, χ, γ, ν, o)
        
    return (s,A)



def Carb_Path(C1_0, C2_0, T_time, A, sum_Em_out, ψ_p, ψ_0, ψ, C_bar, var_ρ, r_tilde, α, σ, λ, ν, L, ω, Θ):
    "Simulation of Carbon Path"
    
    J = 2*Θ+1
    C_g = np.zeros((T_time,2))
    
    # ------------------ #
    # Initial Conditions #
    # ------------------ #
    C_g[0,0] = pf.Perm_Carb(C1_0, sum_Em_out[0,:], ψ_p)
    C_g[0,1] = pf.Tran_Carb(C2_0, sum_Em_out[0,:], ψ_p, ψ_0, ψ)
    
    # ---------------- #
    # Equilibrium Path #
    # ---------------- #
    for t in range(1,T_time):
        C_g[t,0] = pf.Perm_Carb(C_g[t-1,0], sum_Em_out[t,:], ψ_p)
        C_g[t,1] = pf.Tran_Carb(C_g[t-1,1], sum_Em_out[t,:], ψ_p, ψ_0, ψ)
        
    r_tilde_adjust = np.tile(r_tilde.reshape((1,J)), (T_time, 1))
    ν_adjust = np.tile(ν.reshape((1,Θ+1)), (T_time, 1))
    ω_adjust = np.tile(ω.reshape((1,J)), (T_time, 1))
    
    Carb = sp.optimize.root(CarbRoot, C_g,
                      args=(C1_0, C2_0, T_time, A, sum_Em_out, ψ_p, ψ_0, ψ, C_bar, var_ρ, r_tilde_adjust, α, σ, λ, ν_adjust, L, ω_adjust, Θ),
                      method='lm')
        
    C = Carb.x.reshape((T_time,2))
     
    return np.sum(C,1).reshape((-1,1))



def CarbRoot(C_g, C1_0, C2_0, T_time, A, sum_Em_out, ψ_p, ψ_0, ψ, C_bar, var_ρ, r_tilde_adjust, α, σ, λ, ν_adjust, L, ω_adjust, Θ):
    "Carbon Path Root"
    
    C_g = C_g.reshape((T_time,2))
    Ω = pf.Damage(np.sum(C_g,1).reshape((-1,1)), C_bar, var_ρ)
    Em = sum_Em_out + pf.GHG(r_tilde_adjust, A, α, σ, λ, ν_adjust, Ω, L, ω_adjust, Θ)
    
    C1_glag = np.vstack((np.array([C1_0]), C_g[:-1,0].reshape((-1,1))))
    C2_glag = np.vstack((np.array([C2_0]), C_g[:-1,1].reshape((-1,1))))
    
    C1 = pf.Perm_Carb(C1_glag, Em, ψ_p)
    C2 = pf.Tran_Carb(C2_glag, Em, ψ_p, ψ_0, ψ)
    
    C_mat = np.hstack((C1, C2))
    
    return np.abs(C_mat-C_g).flatten()



@njit
def Util(c, var_θ):
    "Period Utility Function"
    
    if var_θ == 1:
        return np.log(c)
    else:
        return (c**(1-var_θ))/(1-var_θ)
    
    

@njit
def MUtil(c, var_θ):
    "Marginal Utility Function"
    
    return c**(-var_θ)



def Welfare(c, var_θ, T, ρ, g_ss):
    "Welfare Calculator"
    
    times = np.arange(0, T, 1).reshape((-1,1))
    discount = (1+ρ)**(-times)
    u = Util(c, var_θ)
    
    c_ss = (1+g_ss)*c[-1,-1]
    Rtilde_inv = (1+g_ss)**(1-var_θ) / (1+ρ)
    term = Util(c_ss, var_θ) / (1 - Rtilde_inv)
    if var_θ == 1:
        term = term + np.log(1+g_ss) * Rtilde_inv / ((1-Rtilde_inv)**2)
    
    welfare = np.sum(discount*u) + ((1+ρ)**(-T)) * term
    
    return welfare



def Consump_Eq(W_2, c, var_θ, T, ρ, g_ss):
    "Consumption Equivalence Calculator"
    
    CE = sp.optimize.root(CE_root, 1,
                      args=(W_2, c, var_θ, T, ρ, g_ss),
                      method='lm')
        
    return CE.x



def CE_root(CE, W_2, c, var_θ, T, ρ, g_ss):
    "Consumption Equivalence Root"
        
    W_alt = Welfare(CE * c, var_θ, T, ρ, g_ss)
    
    return W_2 - W_alt



def τ_root(x_lag, x_t, x_lead, T, ρ, var_θ, φ_hat, γ, χ, η, r, α, σ, λ, ν, L, ω, C_bar, var_ρ, ψ_p, ψ_0, ψ, sum_Em_out, Θ, SCC_frac, o):
    "Optimality Condition for Carbon Price"
    
    # ------------------------------------------------------------------------------------------- #
    # Unpack Carbon Price, Carbon Concentration, Subsidies, Technology, and Crazy Recursion Guess #
    # ------------------------------------------------------------------------------------------- #
    J = 2*Θ + 1
    
    (τ_1_t, τ_2_t, C_1_t, C_2_t, ξtilde_t, A_t, ς_1_t, ς_2_t) = unpack(x_t, J, T)
    
    (τ_1_lead, τ_2_lead, C_1_lead, C_2_lead, ξtilde_lead, A_lead, ς_1_lead, ς_2_lead) = unpack(x_lead, J, T)
    
    # -------- #
    # Outcomes #
    # -------- #
    X = np.ones((1,J))
    
    τ_t = (τ_1_t + τ_2_t) @ X
    r_tilde_t = r + ω*SCC_frac*τ_t
    
    C_t = C_1_t + C_2_t
    Ω_t = pf.Damage(C_t, C_bar, var_ρ)
    
    g_ss = A_lead[-1,0]
    
    Y_t = pf.Output(r_tilde_t, A_t, α, σ, λ, ν, Ω_t, L, Θ)
    Y_leadss = (1+g_ss) * Y_t
    Y_lead = np.vstack((Y_t[1:,:], Y_leadss[-1,:]))
    
    con_t = pf.Consump(r, r_tilde_t, A_t, α, σ, λ, ν, Ω_t, L, Θ)
    con_leadss = (1+g_ss) * con_t
    con_lead = np.vstack((con_t[1:,:], con_leadss[-1,:]))
    
    τ_1_lead[-1,:] = Y_lead[-1,:] * τ_1_lead[-1,:]
    τ_2_lead[-1,:] = Y_lead[-1,:] * τ_2_lead[-1,:]
    
    # --- #
    # MRS #
    # --- #
    MU_t = MUtil(con_t, var_θ)
    MU_lead = MUtil(con_lead, var_θ)
    R_inv = MU_lead / MU_t / (1+ρ)

    # ----- #
    # Roots #
    # ----- #
    RHS_1 = Y_t * var_ρ * ψ_p + R_inv * τ_1_lead
    RHS_2 = Y_t * var_ρ * (1-ψ_p) * ψ_0 + R_inv * ψ * τ_2_lead
    
    Root_1 = np.log(τ_1_t) - np.log(RHS_1)
    Root_2 = np.log(τ_2_t) - np.log(RHS_2)
    
    return np.hstack((Root_1, Root_2))



def C_root(x_lag, x_t, x_lead, T, ρ, var_θ, φ_hat, γ, χ, η, r, α, σ, λ, ν, L, ω, C_bar, var_ρ, ψ_p, ψ_0, ψ, sum_Em_out, Θ, SCC_frac, o):
    "Law of Motion for Carbon Concentrations"
    
    # ------------------------------------------------------------------------------------------- #
    # Unpack Carbon Price, Carbon Concentration, Subsidies, Technology, and Crazy Recursion Guess #
    # ------------------------------------------------------------------------------------------- #
    J = 2*Θ + 1
    
    (τ_1_lag, τ_2_lag, C_1_lag, C_2_lag, ξtilde_lag, A_lag, ς_1_lag, ς_2_lag) = unpack(x_lag, J, T)
    
    (τ_1_t, τ_2_t, C_1_t, C_2_t, ξtilde_t, A_t, ς_1_t, ς_2_t) = unpack(x_t, J, T)
        
    # -------- #
    # Outcomes #
    # -------- #
    X = np.ones((1,J))
    
    τ_t = (τ_1_t + τ_2_t) @ X
    r_tilde_t = r + ω*SCC_frac*τ_t
    
    C_t = C_1_t + C_2_t
    Ω_t = pf.Damage(C_t, C_bar, var_ρ)
    
    Em_t = sum_Em_out + pf.GHG(r_tilde_t, A_t, α, σ, λ, ν, Ω_t, L, ω, Θ)

    # ----- #
    # Roots #
    # ----- #
    RHS_1 = pf.Perm_Carb(C_1_lag, Em_t, ψ_p)
    RHS_2 = pf.Tran_Carb(C_2_lag, Em_t, ψ_p, ψ_0, ψ)
    
    Root_1 = np.log(C_1_t) - np.log(RHS_1)
    Root_2 = np.log(C_2_t) - np.log(RHS_2)

    return np.hstack([Root_1, Root_2])



def ξtilde_root(x_lag, x_t, x_lead, T, ρ, var_θ, φ_hat, γ, χ, η, r, α, σ, λ, ν, L, ω, C_bar, var_ρ, ψ_p, ψ_0, ψ, sum_Em_out, Θ, SCC_frac, o):
    "Optimality Condition for Innovation Subsidies x Shares"

    # ------------------------------------------------------------------------------------------- #
    # Unpack Carbon Price, Carbon Concentration, Subsidies, Technology, and Crazy Recursion Guess #
    # ------------------------------------------------------------------------------------------- #
    J = 2*Θ + 1
    
    (τ_1_t, τ_2_t, C_1_t, C_2_t, ξtilde_t, A_t, ς_1_t, ς_2_t) = unpack(x_t, J, T)
    
    (τ_1_lead, τ_2_lead, C_1_lead, C_2_lead, ξtilde_lead, A_lead, ς_1_lead, ς_2_lead) = unpack(x_lead, J, T)
    
    # -------- #
    # Outcomes #
    # -------- #
    X = np.ones((1,J))
    
    τ_t = (τ_1_t + τ_2_t) @ X
    r_tilde_t = r + ω*SCC_frac*τ_t
    
    C_t = C_1_t + C_2_t
    Ω_t = pf.Damage(C_t, C_bar, var_ρ)
    
    g_lead = np.log(A_lead) - np.log(A_t)
    g_lead[-1,:] = A_lead[-1,:]
    g_ss = A_lead[-1,0]
    
    Y_t = pf.Output(r_tilde_t, A_t, α, σ, λ, ν, Ω_t, L, Θ) @ X
    Y_leadss = (1+g_ss) * Y_t
    Y_lead = np.vstack((Y_t[1:,:], Y_leadss[-1,:]))
    
    con_t = pf.Consump(r, r_tilde_t, A_t, α, σ, λ, ν, Ω_t, L, Θ) @ X
    con_leadss = (1+g_ss) * con_t
    con_lead = np.vstack((con_t[1:,:], con_leadss[-1,:]))
    
    Sj_t = pf.Shares_j(r_tilde_t, A_t, α, σ, λ, ν, Θ)
    
    Em_t = pf.GHG(r_tilde_t, A_t, α, σ, λ, ν, Ω_t, L, ω, Θ) @ X    
    ΔEm_t = pf.δGHG_δA(r_tilde_t, A_t, α, σ, λ, ν, ω, Θ) / (1 - α + var_ρ * (ψ_p + (1-ψ_p)*ψ_0) * Em_t)
    Cal_T_t = ΔEm_t * ((1-SCC_frac)*τ_t + (ς_1_lead + ς_2_lead) @ X)
    
    φ_lead = rf.SpillNet(φ_hat, A_t, o)
    
    # --- #
    # MRS #
    # --- #
    MU_t = MUtil(con_t, var_θ)
    MU_lead = MUtil(con_lead, var_θ)
    R_inv = MU_lead / MU_t / (1+ρ)
    
    # ----- #
    # Roots #
    # ----- #
    RHS = np.empty((T,J))
    for t in range(T):
        RHS[t,:] = (Sj_t[t,:] - Cal_T_t[t,:]) / (γ-1) + R_inv[t,:] * (Y_lead[t,:]/Y_t[t,:]) * (ξtilde_lead[t,:] + ((ξtilde_lead[t,:]*g_lead[t,:]) @ φ_lead[t,:,:]))
    
    Root = ξtilde_t - RHS
    
    return Root
        


def A_root(x_lag, x_t, x_lead, T, ρ, var_θ, φ_hat, γ, χ, η, r, α, σ, λ, ν, L, ω, C_bar, var_ρ, ψ_p, ψ_0, ψ, sum_Em_out, Θ, SCC_frac, o):
    "Technology Law of Motion"
    
    # ------------------------------------------------------------------------------------------- #
    # Unpack Carbon Price, Carbon Concentration, Subsidies, Technology, and Crazy Recursion Guess #
    # ------------------------------------------------------------------------------------------- #
    J = 2*Θ + 1
    
    (τ_1_lag, τ_2_lag, C_1_lag, C_2_lag, ξtilde_lag, A_lag, ς_1_lag, ς_2_lag) = unpack(x_lag, J, T)
    
    (τ_1_t, τ_2_t, C_1_t, C_2_t, ξtilde_t, A_t, ς_1_t, ς_2_t) = unpack(x_t, J, T)

    # -------- #
    # Outcomes #
    # -------- #
    s_t = rf.Science(A_lag, ξtilde_t, η, φ_hat, ν, Θ, o)
    
    # ----- #
    # Roots #
    # ----- #
    RHS = rf.A_new(s_t, A_lag, η, φ_hat, χ, γ, ν, o)
    Root = np.log(A_t) - np.log(RHS)
    
    return Root



def ς_root(x_lag, x_t, x_lead, T, ρ, var_θ, φ_hat, γ, χ, η, r, α, σ, λ, ν, L, ω, C_bar, var_ρ, ψ_p, ψ_0, ψ, sum_Em_out, Θ, SCC_frac, o):
    "Crazy Recursion"
    
    # ------------------------------------------------------------------------------------------- #
    # Unpack Carbon Price, Carbon Concentration, Subsidies, Technology, and Crazy Recursion Guess #
    # ------------------------------------------------------------------------------------------- #
    J = 2*Θ + 1
    
    (τ_1_t, τ_2_t, C_1_t, C_2_t, ξtilde_t, A_t, ς_1_t, ς_2_t) = unpack(x_t, J, T)
    
    (τ_1_lead, τ_2_lead, C_1_lead, C_2_lead, ξtilde_lead, A_lead, ς_1_lead, ς_2_lead) = unpack(x_lead, J, T)
    
    # -------- #
    # Outcomes #
    # -------- #
    X = np.ones((1,J))
    
    τ_t = (τ_1_t + τ_2_t) @ X
    r_tilde_t = r + ω*SCC_frac*τ_t
    τ_lead = τ_1_lead + τ_2_lead
    
    C_t = C_1_t + C_2_t
    Ω_t = pf.Damage(C_t, C_bar, var_ρ)
    
    g_ss = A_lead[-1,0]
    
    Em_t = pf.GHG(r_tilde_t, A_t, α, σ, λ, ν, Ω_t, L, ω, Θ)
    Em_leadss = 0 * Em_t
    Em_lead = np.vstack((Em_t[1:,:], Em_leadss[-1,:]))
    
    Z_lead = Em_lead / (1 - α + var_ρ * (ψ_p + (1-ψ_p)*ψ_0) * Em_lead)
    
    con_t = pf.Consump(r, r_tilde_t, A_t, α, σ, λ, ν, Ω_t, L, Θ)
    con_leadss = (1+g_ss) * con_t
    con_lead = np.vstack((con_t[1:,:], con_leadss[-1,:]))
    
    # --- #
    # MRS #
    # --- #
    MU_t = MUtil(con_t, var_θ)
    MU_lead = MUtil(con_lead, var_θ)
    R_inv = MU_lead / MU_t / (1+ρ)

    # ----- #
    # Roots #
    # ----- #
    RHS_1 = R_inv * (-Z_lead * var_ρ * ψ_p * (1-SCC_frac) * τ_lead + ς_1_lead - Z_lead * var_ρ * ψ_p * (ς_1_lead+ς_2_lead))
    RHS_2 = R_inv * (-Z_lead * var_ρ * (1-ψ_p) * ψ_0 * ψ * (1-SCC_frac) * τ_lead + ψ * ς_2_lead - Z_lead * var_ρ * (1-ψ_p) * ψ_0 * ψ * (ς_1_lead+ς_2_lead))
    
    Root_1 = ς_1_t - RHS_1
    Root_2 = ς_2_t - RHS_2
    
    return np.hstack((Root_1, Root_2))



def unpack(x, J, T):
    "Unpack Allocation Sequence"

    # ------------------------------------------------------------------------------------------- #
    # Unpack Carbon Price, Carbon Concentration, Subsidies, Technology, and Crazy Recursion Guess #
    # ------------------------------------------------------------------------------------------- #
    
    τ_1 = np.exp(x[:,0].reshape((T,1)))
    τ_2 = np.exp(x[:,1].reshape((T,1)))
    C_1 = np.exp(x[:,2].reshape((T,1)))
    C_2 = np.exp(x[:,3].reshape((T,1)))
    ξtilde = x[:,4:4+J]
    A = np.exp(x[:,4+J:4+2*J])
    ς_1 = x[:,-2].reshape((T,1))
    ς_2 = x[:,-1].reshape((T,1))

    return (τ_1, τ_2, C_1, C_2, ξtilde, A, ς_1, ς_2)




