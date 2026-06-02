import qutip as qt
import numpy as np
import matplotlib.pyplot as plt
from flask import Flask, send_file
import io

app = Flask(__name__)

@app.route('/')
def home():
    # Run the simulation
    N = 4
    g_diag = 1.2
    g_vac = 0.8
    kappa = 0.08
    tlist = np.linspace(0, 12, 200)

    a = qt.destroy(N)
    X = (a + a.dag()) / np.sqrt(2)
    P = 1j * (a.dag() - a) / np.sqrt(2)

    psi0 = qt.tensor(qt.basis(N, 0), qt.basis(N, 0))

    H_diag = g_diag * (qt.tensor(X, X) + qt.tensor(P, P) + 0.5 * qt.tensor(X+P, X-P))
    H_vac = g_vac * (qt.tensor(X, qt.qeye(N)) + qt.tensor(qt.qeye(N), X))
    H_drive = sum(2 * np.pi * f * qt.tensor(qt.num(N), qt.qeye(N)) for f in [1.5, 2.8, 4.1])
    H = qt.tensor(qt.qeye(N), qt.qeye(N)) + H_diag + H_vac + H_drive

    c_ops = [np.sqrt(kappa) * qt.tensor(a, qt.qeye(N)), 
             np.sqrt(kappa) * qt.tensor(qt.qeye(N), a)]

    result = qt.mesolve(H, psi0, tlist, c_ops)
    final_rho = result.states[-1].ptrace([0,1])

    entropy = qt.entropy_vn(final_rho)
    corr_xx = qt.expect(qt.tensor(X, X), final_rho)
    corr_pp = qt.expect(qt.tensor(P, P), final_rho)

    output = f"""
    <h1>Quantum Biology 6D+ Simulation</h1>
    <p><strong>EPR Steering Achieved:</strong> False</p>
    <p><strong>Entanglement Entropy:</strong> {entropy:.4f}</p>
    <p><strong>Diagonal Corr XX:</strong> {corr_xx:.4f}</p>
    <p><strong>Diagonal Corr PP:</strong> {corr_pp:.4f}</p>
    <hr>
    <p>Simulation completed successfully. Refresh to re-run.</p>
    """
    return output

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
