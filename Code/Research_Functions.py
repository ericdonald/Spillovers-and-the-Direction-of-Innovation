"""""""""""
Research Functions

Notes: Functions that describe the research block of the economy.
    
Output:
"""""""""""

import numpy as np
import scipy as sp
from numba import njit
import Production_Functions as pf



@njit
def Spill(φ_hat, A, o):
    "Spillover Functions"
    
    φ_hat_64 = φ_hat.astype(A.dtype)
    
    if o==1:
        phi = np.exp(np.log(A) @ φ_hat_64.T) / A
        
    else:
        A_CES = A**((o-1)/o)
        φ_hat_CES = (φ_hat_64**(1/o)).T
        
        phi_inner = A_CES @ φ_hat_CES
        phi = phi_inner**(o/(o-1)) / A

    return phi



@njit
def Spill_tilde(φ_hat, A, o):
    "Gross Spillover Functions"
    
    φ_hat_64 = φ_hat.astype(A.dtype)
    
    if o==1:
        phi_tilde = np.exp(np.log(A) @ φ_hat_64.T)
        
    else:
        A_CES = A**((o-1)/o)
        φ_hat_CES = (φ_hat_64**(1/o)).T
        
        phi_inner = A_CES @ φ_hat_CES
        phi_tilde = phi_inner**(o/(o-1))

    return phi_tilde



@njit
def SpillNet(φ_hat, A, o):
    "Spillover Network"
    
    if A.ndim == 1:
        A2d = A.reshape((1,-1))
    else:
        A2d = A
        
    T,J = A2d.shape
    
    A_CES = A2d**((o-1)/o)
    φ_hat_CES = (φ_hat**(1/o)).T
    
    phi_inner = A_CES @ φ_hat_CES
    
    φ = np.zeros((T,J,J))
    I = np.eye(J)
    
    for t in range(T):
        for i in range(J):
            for j in range(J):
                φ[t,i,j] = φ_hat[i,j]**(1/o) * A2d[t,j]**((o-1)/o) / phi_inner[t,i]
                
        φ[t,:,:] -= I #Make spillover network net

    return φ



@njit
def A_new(s, A, η, φ_hat, χ, γ, ν, o):
    "Technology Evolution"
    
    J = φ_hat.shape[0]
    Θ = int(np.rint((J-1)/2))
    ν_j = pf.Θ_Expand(ν, Θ)
    
    phi_spill = Spill(φ_hat, A, o)
    
    A_new = A * γ**(χ * ((s/ν_j)**η) * phi_spill)
        
    return A_new



def ScienceEqbm(A, η, φ_hat, χ, γ, α, λ, ν, σ, L, r_tilde, ξ, Θ, o):
    "Scientist Equilibrium"
    
    J = 2*Θ+1
    sg = np.full(J,1/J)
    
    s = sp.optimize.root(ScienceRoot, sg,
                      args=(A, η, φ_hat, χ, γ, α, λ, ν, σ, L, r_tilde, ξ, Θ, o),
                      method='lm')
    
    return s.x



@njit
def ScienceRoot(s, A, η, φ_hat, χ, γ, α, λ, ν, σ, L, r_tilde, ξ, Θ, o):
    "Scientist Equilibrium Root"
    
    J = 2*Θ+1
    ν_j = pf.Θ_Expand(ν, Θ)
    
    s_bar = pf.var_bar(s, J)
    A_prime = A_new(s, A, η, φ_hat, χ, γ, ν, o) 
    
    S_j = pf.Shares_j(r_tilde, A_prime, α, σ, λ, ν, Θ)
    phi_spill = Spill(φ_hat, A, o)
    
    Ξ = pf.var_bar(ξ, J)
    V = pf.var_bar(ν_j, J)
    Φ_rel = pf.var_bar(phi_spill, J)
    Π = pf.var_bar(S_j, J)
    
    XR = ((1-η)*np.log(s_bar) 
          - (np.log(Ξ) - η*np.log(V) + np.log(Φ_rel) + np.log(Π))) #Research FOC
    
    XS = 1 - s @ np.ones(J) #Scientist Supply Constraint
    
    return np.append(XR, XS)



def Science(A_lag, ξ_tilde, η, φ_hat, ν, Θ, o):
    "Science Allocation from Technology & Innovation Subsidies x Shares"
    
    J = 2*Θ+1
    ν_j = pf.Θ_Expand(ν, Θ)
    
    ξ_tilde_prime = np.maximum(ξ_tilde, 0)
    phi_spill = Spill(φ_hat, A_lag, o)
    
    c = ν_j**(-η/(1-η)) * ξ_tilde_prime**(1/(1-η)) * phi_spill**(1/(1-η))
    
    row_sums = c @ np.ones((J, J))
    zero_rows = (row_sums == 0)
    row_sums[zero_rows] = 1
    
    s = c / row_sums
    
    return s
    
    
    
    
    
    
    
    
