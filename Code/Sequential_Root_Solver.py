"""""""""""
Sequential Root Solver

Notes: A function that solves block recursive root systems using Newton's method.
    
"""""""""""

import numpy as np
import quantecon as qe



def SRS(X_g, Funcs, Init, Term, args, N_lag, N_t, N_lead, Maxiter=100, ε=10**(-7), δ=10**(-2)):
    "Sequential Root Solver"
    
    qe.tic()
    T = X_g.shape[0]
    N = X_g.shape[1]
    
    x = X_g
    x_index = np.where(x == x)[1].reshape(x.shape)
    
    for it in range(Maxiter):
        
        # ------------------- #
        # Unpack Lags & Leads #
        # ------------------- #
        x_lag = np.vstack((Init, x[:-1,:]))
        x_lead = np.vstack((x[1:,:], Term))
        
        # ------------------------ #
        # Evaluate Entire Function #
        # ------------------------ #
        y = func_eval(x_lag, x, x_lead, Funcs, *args)
        
        # ----------------- #
        # Check Convergence #
        # ----------------- #
        if np.max(np.abs(y)) < ε:
            print("Root Found")
            qe.toc()
            break
        
        # --------------- #
        # Sparse Jacobian #
        # --------------- #
        Jac = np.zeros((T,N,N,3))
        
        for n in N_lag:
            x_lag_prime = x_lag + δ*(x_index==n)
            Jac[:,:,n,0] = (func_eval(x_lag_prime, x, x_lead, Funcs, *args) - y)/δ
                
        for n in N_t:
            x_prime = x + δ*(x_index==n)
            Jac[:,:,n,1] = (func_eval(x_lag, x_prime, x_lead, Funcs, *args) - y)/δ
                
        for n in N_lead:
            x_lead_prime = x_lead + δ*(x_index==n)
            Jac[:,:,n,2] = (func_eval(x_lag, x, x_lead_prime, Funcs, *args) - y)/δ
        
        Jacob = np.zeros((T*N, T*N))
        
        # -------------- #
        # Initial Period #
        # -------------- #
        for n in range(N):
            Jacob[n, :N] = Jac[0,n,:,1]
            Jacob[n, N:N+N] = Jac[0,n,:,2]
        
        # -------------------- #
        # Intermediate Periods #
        # -------------------- #
        for t in range(1, T-1):
            for n in range(N):
                Jacob[t*N+n, t*N-N:t*N] = Jac[t,n,:,0]
                Jacob[t*N+n, t*N:t*N+N] = Jac[t,n,:,1]
                Jacob[t*N+n, t*N+N:t*N+2*N] = Jac[t,n,:,2]
        
        # ------------ #
        # Final Period #
        # ------------ #
        for n in range(N):
            Jacob[(T-1)*N+n, -2*N:-N] = Jac[-1,n,:,0]
            Jacob[(T-1)*N+n, -N:] = Jac[-1,n,:,1]
        
        # ------------ #
        # Update Guess #
        # ------------ #
        x = x.reshape(T*N)
        y = y.reshape(T*N)
        
        b = Jacob @ x - y
        x_new = np.linalg.solve(Jacob, b)
        x = x_new.reshape((T,N))
        
        if it+1 == Maxiter:
            print("Maximum Iterations Reached")

    return x



def func_eval(x_lag, x, x_lead, Funcs, *args):
    "Evaluate Set of Functions"
    
    F = len(Funcs)
    
    y = Funcs[0](x_lag, x, x_lead, *args)
    for f in range(1,F):
        y = np.hstack((y, Funcs[f](x_lag, x, x_lead, *args)))
        
    return y






      