"""""""""""
Steady-State Functions

Notes: Functions that describe the steady-state of the economy.
    
"""""""""""

import numpy as np
from scipy import optimize
import scipy as sp
from numba import njit
import Production_Functions as pf
import Research_Functions as rf



def Abar_SS(η, φ_hat, α, σ, λ, ν, r_tilde, ξ, Θ, o):
    "Descriptive Interior Steady-State Relative Technology"
    
    J = 2*Θ+1
    Abar_g = np.ones(J-1)
    
    Abar_ss = optimize.root(SS_root, Abar_g,
                       args=(η, φ_hat, α, σ, λ, ν, r_tilde, ξ, Θ, o),
                       method='lm')
   
    return Abar_ss.x



@njit
def SS_root(Abar_g, η, φ_hat, α, σ, λ, ν, r_tilde, ξ, Θ, o):
    "Descriptive Interior Steady-State Relative Technology Root"
    
    J = 2*Θ+1    
    A_g = np.append(Abar_g,1)
    
    ν_j = pf.Θ_Expand(ν, Θ)
    Y_j = pf.Output_j(r_tilde, A_g, α, σ, λ, ν, 1, 100, Θ)
    phi_spill = rf.Spill(φ_hat, A_g, o)

    Ξ = pf.var_bar(ξ, J)
    V = pf.var_bar(ν_j, J)
    Φ_rel = pf.var_bar(phi_spill, J)
    R = pf.var_bar(r_tilde, J)
    Y_rel = pf.var_bar(Y_j, J)

    ln_Abar_ss = (1/(1-α)) * (np.log(Ξ) - np.log(V) + (1/η) * np.log(Φ_rel) + α*np.log(R) + np.log(Y_rel))
    
    return np.log(Abar_g) - ln_Abar_ss



@njit
def Abar_SS_corn(α, λ, r_tilde, ξ, Θ):
    "Descriptive Corner Steady-State Relative Technology"
     
    J = 2*Θ+1
    
    Ξ = pf.var_bar(ξ, J)
    R = pf.var_bar(r_tilde, J)
        
    ln_Abar_ss_corn = np.log(Ξ) / (1-α) / (1-λ) + α * np.log(R) / (1-α)
    Abar_ss_corn = np.exp(ln_Abar_ss_corn)
    
    return Abar_ss_corn



def omega_bar_corn(α, λ, ν, ω, r_tilde, ξ, Θ, car, elec):
    "Emissions Intensity of Corner Steady-State"
    
    Abar_ss_cornfull = Abar_SS_corn(α, λ, r_tilde, ξ, Θ)
    
    X = np.ascontiguousarray(np.ones((Θ+1,1)))
    
    #0 denotes clean, 1 denotes dirty
    if car == 0:
        if elec == 0:
            #Clean car, clean elec
            ω_bar = 0
            
        else:
            #Clean car, dirty elec
            Abar_ss_corn = np.array([Abar_ss_cornfull[0], Abar_ss_cornfull[3]])
            r_tilde_corn = np.array([r_tilde[0], r_tilde[3], r_tilde[-1]])
            ω_corn = np.array([ω[0], ω[3], ω[-1]])
            
            p_θ = pf.PseudoP_j(r_tilde_corn, np.append(Abar_ss_corn, 1), α)
            P = ((ν * p_θ**(1-λ)) @ X)**(1/(1-λ))
            S_θ = ν * (p_θ / P)**(1-λ)
            ω_bar = (α * ω_corn * S_θ / r_tilde_corn) @ X
            
    if car == 1:
        if elec == 0:
            #Dirty car, clean elec
            Abar_ss_corn = np.array([Abar_ss_cornfull[1], Abar_ss_cornfull[2]])
            r_tilde_corn = np.array([r_tilde[1], r_tilde[2], r_tilde[-1]])
            ω_corn = np.array([ω[1], ω[2], ω[-1]])
            
            p_θ = pf.PseudoP_j(r_tilde_corn, np.append(Abar_ss_corn, 1), α)
            P = ((ν * p_θ**(1-λ)) @ X)**(1/(1-λ))
            S_θ = ν * (p_θ / P)**(1-λ)
            ω_bar = (α * ω_corn * S_θ / r_tilde_corn) @ X
        else:
            #Dirty car, dirty elec
            Abar_ss_corn = np.array([Abar_ss_cornfull[1], Abar_ss_cornfull[3]])
            r_tilde_corn = np.array([r_tilde[1], r_tilde[3], r_tilde[-1]])
            ω_corn = np.array([ω[1], ω[3], ω[-1]])
            
            p_θ = pf.PseudoP_j(r_tilde_corn, np.append(Abar_ss_corn, 1), α)
            P = ((ν * p_θ**(1-λ)) @ X)**(1/(1-λ))
            S_θ = ν * (p_θ / P)**(1-λ)
            ω_bar = (α * ω_corn * S_θ / r_tilde_corn) @ X
            
    
    return ω_bar



def Jacob(Abar_ss, η, φ_hat, α, σ, λ, r_tilde, χ, γ, Θ, ν, o):
    "Transition Matrix"
    
    J = 2*Θ+1
    I = np.eye(J-1)
    A_ss = np.append(Abar_ss, 1)
    
    g = Growth_SS(Abar_ss, φ_hat, η, ν, γ, χ, Θ, o)
    φ = rf.SpillNet(φ_hat, A_ss, o)[0,:,:]
    
    Φ = Phi(φ, J) #Spillover Matrix
    Σ = Sigma(Abar_ss, r_tilde, α, σ, λ, Θ) #Substitution Matrix
    
    J = np.linalg.inv((1-η)*I - g*η*(1-α)*(Σ-I)) @ ((1-η)*I - g*Φ) 

    return J        
            
    
   
def Amp(Abar_ss, η, φ_hat, α, σ, λ, r_tilde, Θ, o):
    "Amplification Matrix"
    
    J = 2*Θ+1
    I = np.eye(J-1)
    A_ss = np.append(Abar_ss, 1)
    
    φ = rf.SpillNet(φ_hat, A_ss, o)[0,:,:]
        
    Φ = Phi(φ, J) #Spillover Matrix
    Σ = Sigma(Abar_ss, r_tilde, α, σ, λ, Θ) #Substitution Matrix
    
    M = np.linalg.inv(Φ - η * (1-α) * (Σ-I))
    
    return M


    
@njit
def Phi(φ, J):
    "Spillover Matrix"
    
    X = np.ascontiguousarray(np.hstack((-np.eye(J)[:-1,:-1], np.ones((J-1,1)))))
    
    Φ = (X @ φ)[:,:-1]
    
    return Φ
    

         
def Sigma(Abar_ss, r_tilde, α, σ, λ, Θ):
    "Substitution Matrix"
    
    A_ss = np.append(Abar_ss, 1)
    
    fS_Eθe = 1 - pf.Shares_e(r_tilde, A_ss, α, σ, Θ)
    
    Σ = np.array([])
    for θ in range(Θ):
        ε = np.array([(σ-λ)*fS_Eθe[2*θ],
                      (λ-σ)*fS_Eθe[2*θ+1]])
        Σ_tilde = λ*np.eye(2) + np.vstack((ε,-ε))
        Σ = sp.linalg.block_diag(Σ,Σ_tilde)
    Σ = Σ[1:,:]
    
    return Σ



@njit
def X_mat(Θ):
    "Linear Transformation of Technologies into Sectors"
    
    x = np.array([1,-1])
    X = np.kron(np.eye(Θ), x)
        
    return X



def Half_Life(Q, κ, β, Θ):
    "Sector Convergence Half-Lives"
    
    t_g = np.full(Θ,np.max(np.log(1/2)/np.log(κ)))
    
    
    t_half = optimize.root(HL_root, t_g,
                       args=(Q, κ, β, Θ),
                       method='lm')
    
    return np.ceil(t_half.x)
    
    

@njit
def HL_root(t, Q, κ, β, Θ):
    "Sector Convergence Half-Lives Root"
    
    X = X_mat(Θ)
    
    B_fan0 = X @ Q @ β
    
    B_fan = np.zeros(Θ)
    
    for θ in range(Θ):
        D = np.diag(κ)**t[θ]
        B_fan[θ] = (X @ Q @ D @ β)[θ]
        
    HL = B_fan/B_fan0
    
    return np.full(Θ, 1/2) - HL



def Opt_SS(r, α, λ, γ, χ, ν, η, φ_hat, ρ, var_θ, Θ, o):
    "Optimal Steady-State"
    
    J = 2*Θ+1
    
    # ----------------- #
    # Super Smart Guess #
    # ----------------- #
    Sj_g = np.array([ν[0], 0, ν[1], 0, ν[-1]])
    I = np.eye(J)
    g = 0.02
    Rtilde_inv = (1+g)**(1-var_θ) / (1+ρ)
    B = np.linalg.inv((1-Rtilde_inv)*I - Rtilde_inv*g*(φ_hat-I))

    ξtilde_g = (Sj_g @ B)/(γ-1)
    
    Φ = Phi(φ_hat-I, J)
    ν_j = pf.Θ_Expand(ν, Θ)

    Ξtilde = pf.var_bar(ξtilde_g, J)
    V = pf.var_bar(ν_j, J)
    ln_Abar_ss_g = η * np.linalg.inv(Φ) @ (np.log(Ξtilde) - np.log(V))
    Abar_ss_g = np.exp(ln_Abar_ss_g)
    
    SS_g = np.concatenate((ξtilde_g, Abar_ss_g))
    
    # ----- #
    # Solve #
    # ----- #
    if o==1:
        SS_find = optimize.root(Opt_SS_root, SS_g,
                           args=(r, α, λ, γ, χ, ν, η, φ_hat, ρ, var_θ, Θ, o),
                           method='lm')
                
        ξtilde_ss = SS_find.x[:J]
        Abar_ss = SS_find.x[J:]
        
    else:
        J_trunc = Θ+1
        SS_g_trunc = np.zeros(2*J_trunc-1)
        r_trunc = np.zeros(J_trunc)
        φ_hat_trunc = np.zeros((J_trunc, J_trunc))
        for j in range(J_trunc):
            SS_g_trunc[j] = SS_g[2*j]
            r_trunc[j] = r[2*j]
            for i in range(J_trunc):
                φ_hat_trunc[i,j] = φ_hat[2*i,2*j]
                
        for j in range(J_trunc-1):
            SS_g_trunc[J_trunc+j] = SS_g[2*(J_trunc+j)-1]
            
        for it in range(1000):
            
            SS_trunc = Opt_SS_Iterator(SS_g_trunc, r_trunc, α, λ, γ, χ, ν, η, φ_hat_trunc, ρ, var_θ, Θ, o)
                        
            if np.max(np.abs(np.log(SS_trunc) - np.log(SS_g_trunc))) < 10**(-7):
                break
            SS_g_trunc = SS_trunc
            
        ξtilde_ss = np.ones(J)*0.000001
        Abar_ss = np.ones(J-1)*0.000001
        
        for j in range(J_trunc):
            ξtilde_ss[2*j] = SS_trunc[j]
       
        for j in range(J_trunc-1):
            Abar_ss[2*j] = SS_trunc[J_trunc+j]
   
    return (ξtilde_ss, Abar_ss)
  
    

@njit
def Opt_SS_root(SS, r, α, λ, γ, χ, ν, η, φ_hat, ρ, var_θ, Θ, o):
    "Optimal Steady-State Root"
    
    J = 2*Θ+1
    I = np.eye(J)
    
    ξtilde = SS[:J]
    Abar_ss = SS[J:]
    A_ss = np.append(Abar_ss, 1)
    
    # ------------------- #
    # Steady-State Growth #
    # ------------------- #
    g_ss = Growth_SS(Abar_ss, φ_hat, η, ν, γ, χ, Θ, o)
    
    # ----------- #
    # ξtilde Root #
    # ----------- #
    φ = rf.SpillNet(φ_hat, A_ss, o)[0,:,:]
    Rtilde_inv = (1+g_ss)**(1-var_θ) / (1+ρ)
    p_j = pf.PseudoP_j(r, A_ss, α)
    p_θ = np.array([p_j[0], p_j[2], p_j[-1]])
    P = (np.sum(ν * p_θ**(1-λ)))**(1/(1-λ))
    S_θ = ν * (p_θ / P)**(1-λ)
    S_j = np.array([S_θ[0], 0, S_θ[1], 0, S_θ[-1]])
    
    B = np.linalg.inv((1-Rtilde_inv)*I - Rtilde_inv*g_ss*φ)
    RHS1 = (S_j @ B)/(γ-1)
    
    Root1 = ξtilde - RHS1
    
    # --------- #
    # Abar Root #
    # --------- #
    ν_j = pf.Θ_Expand(ν, Θ)
    V = pf.var_bar(ν_j, J)
    Ξtilde = pf.var_bar(ξtilde, J)
    
    phi_tilde_spill = rf.Spill_tilde(φ_hat, A_ss, o)
    Φ_tilde_rel = pf.var_bar(phi_tilde_spill, J)
    
    Root2 = Abar_ss - V**(-η) * Ξtilde**(η) * Φ_tilde_rel
    
    return np.concatenate((Root1, Root2))



@njit
def Opt_SS_Iterator(SS_g, r, α, λ, γ, χ, ν, η, φ_hat, ρ, var_θ, Θ, o):
    "Optimal Steady-State Iterator for CES Corner"
    
    J = Θ+1
    I = np.eye(J)
    
    ξtilde = SS_g[:J]
    Abar_ss = SS_g[J:]
    A_ss = np.append(Abar_ss, 1)
    
    # ------------------- #
    # Steady-State Growth #
    # ------------------- #
    phi_spill = rf.Spill(φ_hat, A_ss, o)
    
    x_j = χ * ν**(-η) * phi_spill
    g_CES = np.sum(x_j**(-1/η))**(-η)
    
    g_ss = np.log(γ) * g_CES
    
    # ------------- #
    # ξtilde Update #
    # ------------- #
    φ = rf.SpillNet(φ_hat, A_ss, o)[0,:,:]
    Rtilde_inv = (1+g_ss)**(1-var_θ) / (1+ρ)
    p_j = pf.PseudoP_j(r, A_ss, α)
    P = (np.sum(ν * p_j**(1-λ)))**(1/(1-λ))
    S_j = ν * (p_j / P)**(1-λ)
    
    B = np.linalg.inv((1-Rtilde_inv)*I - Rtilde_inv*g_ss*φ)
    ξtilde_new = (S_j @ B)/(γ-1)
    
    # ----------- #
    # Abar Update #
    # ----------- #
    V = pf.var_bar(ν, J)
    Ξtilde = pf.var_bar(ξtilde, J)
    
    phi_tilde_spill = rf.Spill_tilde(φ_hat, A_ss, o)
    Φ_tilde_rel = pf.var_bar(phi_tilde_spill, J)
    
    Abar_ss_new = V**(-η) * Ξtilde**(η) * Φ_tilde_rel
    
    SS_new = np.concatenate((ξtilde_new, Abar_ss_new))
    
    return SS_new
    
    

@njit
def Growth_SS(Abar_ss, φ_hat, η, ν, γ, χ, Θ, o):
    "Steady-State Growth Rate"
    
    A_ss = np.append(Abar_ss, 1)
    phi_spill = rf.Spill(φ_hat, A_ss, o)
    ν_j = pf.Θ_Expand(ν, Θ)
    
    x_j = χ * ν_j**(-η) * phi_spill
    CES = np.sum(x_j**(-1/η))**(-η)
    
    g_ss = np.log(γ) * CES
    
    return g_ss
    
    
