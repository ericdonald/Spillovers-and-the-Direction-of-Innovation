"""""""""""
Production Functions

Notes: Functions that describe the production block of the economy.
    
"""""""""""

import numpy as np
from numba import njit



@njit
def PseudoP_j(r_tilde, A, α):
    "Pseudo Prices"
    
    p_j = np.ascontiguousarray((r_tilde**(α)) / (A**(1-α)))
    
    return p_j



@njit
def PseudoP_θ(r_tilde, A, α, σ, Θ):
    "Sector Pseudo Prices"
    
    p_j = PseudoP_j(r_tilde, A, α)
    
    x = np.ones((2,1))
    X = np.ascontiguousarray(np.kron(np.eye(Θ+1), x)[:-1,:])
    
    p_θ = ((p_j**(1-σ)) @ X)**(1/(1-σ))
    
    return p_θ



@njit
def PseudoP(r_tilde, A, α, σ, λ, ν, Ω, Θ):
    "Final Output Pseudo Price"
    
    p_θ = PseudoP_θ(r_tilde, A, α, σ, Θ)
    
    X = np.ascontiguousarray(np.ones((Θ+1,1)))
    
    P = (Ω**(-1)) * ((ν * p_θ**(1-λ)) @ X)**(1/(1-λ))
    
    return P



@njit
def Output(r_tilde, A, α, σ, λ, ν, Ω, L, Θ):
    "Final Output"
    
    P = PseudoP(r_tilde, A, α, σ, λ, ν, Ω, Θ)
    Y = (α**(α/(1-α))) * L * (P**(-1/(1-α)))
    
    return Y



@njit
def Shares_θ(r_tilde, A, α, σ, λ, ν, Θ):
    "Sector Shares"
    
    p_θ = PseudoP_θ(r_tilde, A, α, σ, Θ)
    
    X = np.ascontiguousarray(np.ones((1,Θ+1)))
    
    P = PseudoP(r_tilde, A, α, σ, λ, ν, 1, Θ) @ X
    S_θ = ν * (p_θ / P)**(1-λ)
    
    return S_θ



@njit
def Shares_e(r_tilde, A, α, σ, Θ):
    "Shares Within Sectors"
    
    p_j = PseudoP_j(r_tilde, A, α)
    
    p_θ = Θ_Expand(PseudoP_θ(r_tilde, A, α, σ, Θ), Θ)
    S_e = (p_j / p_θ)**(1-σ)
    
    return S_e



@njit
def q_c(r_tilde, A, α, σ, Θ):
    "Clean Quantity Shares Within Sectors"
    
    p_j = PseudoP_j(r_tilde, A, α)
    
    x = np.array([[1],[-1]])
    X = np.ascontiguousarray(np.kron(np.eye(Θ+1), x)[:-1,:-1])
    
    rel_p = np.exp(np.log(p_j) @ X)
    q_c = 1 / (1 + rel_p**σ)
    
    return q_c



@njit
def Shares_j(r_tilde, A, α, σ, λ, ν, Θ):
    "Technology Shares"
    
    S_e = Shares_e(r_tilde, A, α, σ, Θ)
    S_θ = Θ_Expand(Shares_θ(r_tilde, A, α, σ, λ, ν, Θ), Θ)
    
    S_j = S_θ * S_e
    
    return S_j



@njit
def Lambda_j(r_tilde, A, α, σ, λ, ν, Ω, L, Θ):
    "Inputs"
    
    J = 2*Θ + 1
    S_j = Shares_j(r_tilde, A, α, σ, λ, ν, Θ)
    
    X = np.ascontiguousarray(np.ones((1,J)))
    
    Y = Output(r_tilde, A, α, σ, λ, ν, Ω, L, Θ) @ X
    Λ_j = α * Y * S_j / r_tilde
    
    return Λ_j



@njit
def GHG(r_tilde, A, α, σ, λ, ν, Ω, L, ω, Θ):
    "Total Emissions"
    
    Λ_j = Lambda_j(r_tilde, A, α, σ, λ, ν, Ω, L, Θ)
        
    X = np.ascontiguousarray(np.ones((2*Θ+1,1)))
    
    Em = (ω * Λ_j) @ X
    
    return Em



@njit
def omega_bar(r_tilde, A, α, σ, λ, ν, Ω, L, ω, Θ):
    "Total Emission Intensity"
    
    Y = Output(r_tilde, A, α, σ, λ, ν, Ω, L, Θ)
    Em = GHG(r_tilde, A, α, σ, λ, ν, Ω, L, ω, Θ)
    
    ωbar = Em / Y
    
    return ωbar



@njit
def Consump(r, r_tilde, A, α, σ, λ, ν, Ω, L, Θ):
    "Consumption"

    Y = Output(r_tilde, A, α, σ, λ, ν, Ω, L, Θ)
    Λ_j = Lambda_j(r_tilde, A, α, σ, λ, ν, Ω, L, Θ)
        
    X = np.ascontiguousarray(np.ones((2*Θ+1,1)))
    
    c = Y - (r*Λ_j) @ X
    
    return c



@njit
def Output_θ(r_tilde, A, α, σ, λ, ν, Ω, L, Θ):
    "Sector Output"
    
    p_θ = PseudoP_θ(r_tilde, A, α, σ, Θ)
    S_θ = Shares_θ(r_tilde, A, α, σ, λ, ν, Θ)
    
    X = np.ascontiguousarray(np.ones((1,Θ+1)))
    
    Y = Output(r_tilde, A, α, σ, λ, ν, Ω, L, Θ) @ X
    P = PseudoP(r_tilde, A, α, σ, λ, ν, Ω, Θ) @ X
    E_θ = (S_θ / p_θ) * P * Y 
    
    return E_θ



@njit
def GHG_θ(r_tilde, A, α, σ, λ, ν, Ω, L, ω, Θ):
    "Sector Emissions"
    
    Λ_j = Lambda_j(r_tilde, A, α, σ, λ, ν, Ω, L, Θ)
    
    x = np.ones((2,1))
    X = np.ascontiguousarray(np.kron(np.eye(Θ+1), x)[:-1,:])
    
    Em_θ = (ω * Λ_j) @ X
    
    return Em_θ



@njit
def omega_barθ(r_tilde, A, α, σ, λ, ν, Ω, L, ω, Θ):
    "Sector Emission Intensity"
    
    p_θ = PseudoP_θ(r_tilde, A, α, σ, Θ)
    P = PseudoP(r_tilde, A, α, σ, λ, ν, Ω, Θ)
    E_θ = Output_θ(r_tilde, A, α, σ, λ, ν, Ω, L, Θ)
    Em_θ = GHG_θ(r_tilde, A, α, σ, λ, ν, Ω, L, ω, Θ)
    
    ωbar_θ = P * Em_θ / (p_θ * E_θ)
    
    return ωbar_θ



@njit
def Output_j(r_tilde, A, α, σ, λ, ν, Ω, L, Θ):
    "Technology Output"
    
    p_j = PseudoP_j(r_tilde, A, α)
    
    p_θ = Θ_Expand(PseudoP_θ(r_tilde, A, α, σ, Θ), Θ)
    E_θ = Θ_Expand(Output_θ(r_tilde, A, α, σ, λ, ν, Ω, L, Θ), Θ)
    
    Y_j = E_θ * (p_θ / p_j)**σ
    
    return Y_j



@njit
def δGHG_δA(r_tilde, A, α, σ, λ, ν, ω, Θ):
    "Direct Impact of Innovation on Equilibrium Emissions"
    
    J = 2*Θ + 1
    
    S_j = Shares_j(r_tilde, A, α, σ, λ, ν, Θ)
    S_e = Shares_e(r_tilde, A, α, σ, Θ)
    
    Dirt = α * ω * S_j / r_tilde
    x = np.ones((2,2))
    X = np.ascontiguousarray(np.kron(np.eye(Θ+1), x)[:-1,:-1])
    
    a = (1+(1-α)*(1-λ)) * S_j * (Dirt @ np.ones((J,J)))
    b = (1-α)*(λ-σ) * S_e * (Dirt @ X)
    c = (1-α)*(σ-1) * Dirt
    
    ΔEm = a + b + c
    
    return ΔEm

@njit
def Perm_Carb(C_1, GHG, ψ_p):
    "Recursion for Permanent Carbon Concentrations"
    
    C1_lead = ψ_p*GHG + C_1
    
    return C1_lead



@njit
def Tran_Carb(C_2, GHG, ψ_p, ψ_0, ψ):
    "Recursion for Transitory Carbon Concentrations"
    
    C2_lead = (1-ψ_p)*ψ_0*GHG + ψ*C_2
    
    return C2_lead



@njit
def Damage(C, C_bar, var_ρ):
    "Climate Damage Function"
    
    Ω = np.exp(-var_ρ*(C - C_bar))
    
    return Ω



@njit
def Temp(C, C_bar, Γ=3):
    "Temperature Function"
    
    Cel = Γ * np.log(C/C_bar) / np.log(2)
    
    return Cel



@njit
def Θ_Expand(v, Θ):
    "Expand Θ Vector to J Vector"
    
    x = np.ones((1,2))
    X = np.ascontiguousarray(np.kron(np.eye(Θ+1), x)[:,:-1])
    
    v_j = v @ X
    
    return v_j



@njit
def var_bar(v, J):
    "Make Variable Relative"
    
    X = np.ascontiguousarray(np.vstack((np.eye(J-1), -np.ones((1,J-1)))))
    
    v_bar = np.exp(np.log(v) @ X)
    
    return v_bar
    


def _to_sigma_vec(σ, Θ):
    s = np.asarray(σ)
    if s.ndim == 0:
        return np.ones(Θ + 1) * s.item()
    return s
 
    
 
def _pseudo_p_theta(p_j, σ_vec, Θ):
    p_θ = np.empty(Θ + 1)
    for θ in range(Θ):
        s = σ_vec[θ]
        c_idx = 2 * θ
        d_idx = 2 * θ + 1
        p_θ[θ] = (p_j[c_idx] ** (1 - s) + p_j[d_idx] ** (1 - s)) ** (1.0 / (1 - s))
    p_θ[Θ] = p_j[2 * Θ]
    return p_θ



def Shares_e_robust(r_tilde, A, α, σ, Θ):
   
    σ_vec = _to_sigma_vec(σ, Θ)
    p_j = PseudoP_j(r_tilde, A, α)
    p_θ   = _pseudo_p_theta(p_j, σ_vec, Θ)
 
    J   = 2 * Θ + 1
    S_e = np.empty(J)
 
    for θ in range(Θ):
        s     = σ_vec[θ]
        p_sec = p_θ[θ]
        c_idx = 2 * θ
        d_idx = 2 * θ + 1
        S_e[c_idx] = (p_j[c_idx] / p_sec) ** (1 - s)
        S_e[d_idx] = (p_j[d_idx] / p_sec) ** (1 - s)
 
    S_e[2 * Θ] = 1.0
    return S_e



def Output_j_robust(r_tilde, A, α, σ, λ, ν, Ω, L, Θ):
    
    σ_vec = _to_sigma_vec(σ, Θ)
    p_j = PseudoP_j(r_tilde, A, α)
    p_θ   = _pseudo_p_theta(p_j, σ_vec, Θ)
 
    P_inner = 0.0
    for θ in range(Θ + 1):
        P_inner += ν[θ] * p_θ[θ] ** (1 - λ)
    P = (Ω ** (-1)) * P_inner ** (1.0 / (1 - λ))
 
    Y = (α ** (α / (1 - α))) * L * (P ** (-1.0 / (1 - α)))
 
    J   = 2 * Θ + 1
    Y_j = np.empty(J)
 
    for θ in range(Θ):
        s     = σ_vec[θ]
        S_θ   = ν[θ] * (p_θ[θ] / P) ** (1 - λ)
        E_θ   = (S_θ / p_θ[θ]) * P * Y
        c_idx = 2 * θ
        d_idx = 2 * θ + 1
        Y_j[c_idx] = E_θ * (p_θ[θ] / p_j[c_idx]) ** s
        Y_j[d_idx] = E_θ * (p_θ[θ] / p_j[d_idx]) ** s
 
    S_θ_gen    = ν[Θ] * (p_θ[Θ] / P) ** (1 - λ)
    E_θ_gen    = (S_θ_gen / p_θ[Θ]) * P * Y
    Y_j[2 * Θ] = E_θ_gen
 
    return Y_j
    
    
    
    