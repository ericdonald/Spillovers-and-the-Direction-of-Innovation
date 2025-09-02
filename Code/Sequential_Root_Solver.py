"""""""""""
Sequential Root Solver

Notes: A function that solves block recursive root systems using Newton's method.
    
"""""""""""

import numpy as np
import quantecon as qe
from scipy.linalg import lu_factor, lu_solve



def SRS(X_g, Funcs, Init, Term, args, func_widths, dep_lag, dep_t, dep_lead, Maxiter=100, ε=10**(-7), δ=10**(-2)):
    "Sequential Root Solver"
    
    qe.tic()
    T = X_g.shape[0]
    N = X_g.shape[1]
    
    x = X_g.copy()
    x_index = np.where(x == x)[1].reshape(x.shape)
    ev = func_eval(Funcs, func_widths, dep_lag, dep_t, dep_lead, args)
    
    # ----------------------------------------------------------------

    # Iterate with Newton's Method.

    # ----------------------------------------------------------------
    
    for it in range(Maxiter):
        
        # ------------------- #
        # Unpack Lags & Leads #
        # ------------------- #
        x_lag = np.vstack((Init, x[:-1,:]))
        x_lead = np.vstack((x[1:,:], Term))
        
        # ------------------------ #
        # Evaluate Entire Function #
        # ------------------------ #
        y, blocks_base = ev.full_eval(x_lag, x, x_lead)
        
        # ----------------- #
        # Check Convergence #
        # ----------------- #
        max_resid = np.max(np.abs(y))
        
        #print(max_resid)
        
        if max_resid < ε:
            print("Root Found")
            qe.toc()
            break
        
        # --------------- #
        # Sparse Jacobian #
        # --------------- #
        Jac = np.zeros((T,N,N,3))
        
        for n in range(N):
            use_block_lag = ev.dep_lag[:,n]
            if np.any(use_block_lag):
                x_lag_prime = x_lag + δ*(x_index==n)
                y_pert = ev.partial_eval(x_lag_prime, x, x_lead, use_block_lag, blocks_base)
                Jac[:,:,n,0] = (y_pert - y)/δ
            
            use_block_t = ev.dep_t[:,n]
            if np.any(use_block_t):
                x_prime = x + δ*(x_index==n)
                y_pert = ev.partial_eval(x_lag, x_prime, x_lead, use_block_t, blocks_base)
                Jac[:,:,n,1] = (y_pert - y)/δ
                
            use_block_lead = ev.dep_lead[:,n]
            if np.any(use_block_lead):
                x_lead_prime = x_lead + δ*(x_index==n)
                y_pert = ev.partial_eval(x_lag, x, x_lead_prime, use_block_lead, blocks_base)
                Jac[:,:,n,2] = (y_pert - y)/δ
        
        
        # ------------ #
        # Build Blocks #
        # ------------ #
        A_blocks, B_blocks, C_blocks, d_blocks = [], [], [], []
        for t in range(T):
            A_t = Jac[t, :, :, 0] if t > 0 else np.zeros((N, N))
            B_t = Jac[t, :, :, 1]
            C_t = Jac[t, :, :, 2] if t < T - 1 else np.zeros((N, N))

            x_tm1 = x[t-1, :] if t > 0 else np.zeros(N)
            x_t   = x[t, :]
            x_tp1 = x[t+1, :] if t < T - 1 else np.zeros(N)

            y_t = y[t, :]

            d_t = A_t @ x_tm1 + B_t @ x_t + C_t @ x_tp1 - y_t

            A_blocks.append(A_t)
            B_blocks.append(B_t)
            C_blocks.append(C_t)
            d_blocks.append(d_t)
        
        # ------------ #
        # Update Guess #
        # ------------ #
        x_new = solve_block_tridiagonal(A_blocks, B_blocks, C_blocks, d_blocks)

        x = np.vstack(x_new)
        
        if it+1 == Maxiter:
            print("Maximum Iterations Reached")

    return x



class func_eval:
    "Object Evaluating Set of Functions"
    
    def __init__(self, Funcs, func_widths, dep_lag, dep_t, dep_lead, args):
        "Initialize Function Evaluator"
        
        self.Funcs = Funcs
        self.F = len(Funcs)
        self.func_widths = func_widths
        self.dep_lag = dep_lag
        self.dep_t = dep_t
        self.dep_lead = dep_lead
        self.args = args


    def full_eval(self, x_lag, x, x_lead):
        "Full Evaluation"
        
        blocks = []
        
        for f, fn in enumerate(self.Funcs):
            blocks.append(fn(x_lag, x, x_lead, *self.args))
        y_full = np.hstack(blocks)
        
        return y_full, blocks
    
    
    def partial_eval(self, x_lag, x, x_lead, use_block, cache_blocks):
        "Partial Evaluation"
        
        pieces = []
        
        for f, fn in enumerate(self.Funcs):
            if use_block[f]:
                pieces.append(fn(x_lag, x, x_lead, *self.args))
            else:
                pieces.append(cache_blocks[f])
                
        return np.hstack(pieces)



def solve_block_tridiagonal(A_blocks, B_blocks, C_blocks, d_blocks):
    "Newton Update for Block-Tridiagonal Jacobian"
    
    T = len(B_blocks)
    N = B_blocks[0].shape[0]

    B_fact = [None] * T
    d_tilde = [None] * T
    M = [np.zeros((N, N)) for _ in range(T)]

    # ---------- #
    # Factor B_0 #
    # ---------- #
    lu0 = lu_factor(B_blocks[0])
    B_fact[0] = lu0
    d_tilde[0] = lu_solve(lu0, d_blocks[0])
    M[0] = lu_solve(lu0, C_blocks[0])

    # ------------- #
    # Forward Sweep #
    # ------------- #
    for t in range(1, T):

        B_tilde = B_blocks[t] - A_blocks[t] @ M[t - 1]
        lu_t = lu_factor(B_tilde)
        B_fact[t] = lu_t

        rhs_t = d_blocks[t] - A_blocks[t] @ d_tilde[t - 1]
        d_tilde[t] = lu_solve(lu_t, rhs_t)

        M[t] = lu_solve(lu_t, C_blocks[t])

    # ----------------- #
    # Back Substitution #
    # ----------------- #
    x_new = [None] * T
    x_new[T-1] = d_tilde[T-1]
    for t in range(T-2, -1, -1):
        x_new[t] = d_tilde[t] - M[t] @ x_new[t + 1]

    return x_new


      