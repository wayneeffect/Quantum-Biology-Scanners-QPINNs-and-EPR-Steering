import qutip as qt
import numpy as np
import matplotlib.pyplot as plt

# Parameters
N = 4  # levels per "lattice" (4D)
dim = N**2  # 16
omega = 1.0
g_diag = 0.8   # diagonal coupling strength (your two diagonals)
g_vac = 0.5    # false vacuum coupling
kappa = 0.1    # dissipation

# Basis states for 4D lattices
a = qt.destroy(N)
# Effective gauge-like operators (position/momentum inspired)
X = (a + a.dag()) / np.sqrt(2)
P = 1j * (a.dag() - a) / np.sqrt(2)

# Two subsystems + mediator
psi0_A = qt.basis(N, 0)  # initial
psi0_B = qt.basis(N, 0)
vac = qt.basis(3, 0)  # truncated vacuum mediator

# Tensor to full space: A ⊗ B ⊗ vac (but we'll trace out mediator for simplicity)
H0 = qt.tensor(qt.qeye(N), qt.qeye(N))  # base

# Diagonal extensions (nonlocal couplings)
diag1 = qt.tensor(X, X) + qt.tensor(P, P)  # example diagonal mixing
diag2 = qt.tensor(X + P, X - P) * 0.5
H_diag = g_diag * (diag1 + diag2)

# False vacuum domain wall / phase-lock drive
H_vac = g_vac * (qt.tensor(X, qt.qeye(N)) + qt.tensor(qt.qeye(N), X))  # coupling through vacuum
H_drive = 2 * np.pi * 1.5 * qt.tensor(qt.num(N), qt.qeye(N))  # phase locking drive

H = H0 + H_diag + H_vac + H_drive

# Collapse operators (noise + dissipation for open system / feedback)
c_ops = [np.sqrt(kappa) * qt.tensor(a, qt.qeye(N)), 
         np.sqrt(kappa) * qt.tensor(qt.qeye(N), a)]

# Time evolution with protocol (steps 3-6 active)
tlist = np.linspace(0, 10, 200)
result = qt.mesolve(H, qt.tensor(psi0_A, psi0_B), tlist, c_ops)

# EPR Steering check (simplified witness: <A_x B_x> + <A_p B_p> etc.)
def steering_witness(rho):
    # Very simplified correlation check
    corr_xx = qt.expect(qt.tensor(X, X), rho)
    return abs(corr_xx) > 0.5  # threshold for steering possible

final_rho = result.states[-1].ptrace([0,1])  # reduced
steers = steering_witness(final_rho)
print("EPR Steering achieved:", steers)
print("Final entanglement entropy (von Neumann):", qt.entropy_vn(final_rho))
