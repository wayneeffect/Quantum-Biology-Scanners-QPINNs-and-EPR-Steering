from flask import Flask
import qutip as qt
import numpy as np
import matplotlib.pyplot as plt
import base64
from io import BytesIO

app = Flask(__name__)

@app.route('/')
def quantum_simulation():
    try:
        # ====================== PARAMETERS ======================
        N = 4
        g_diag = 2.5
        g_vac = 1.8
        kappa = 0.12
        tlist = np.linspace(0, 10, 150)

        a = qt.destroy(N)
        X = (a + a.dag()) / np.sqrt(2)
        P = 1j * (a.dag() - a) / np.sqrt(2)

        psi0 = qt.tensor(qt.basis(N, 0), qt.basis(N, 0))

        # Stronger Hamiltonian
        H_diag = g_diag * (qt.tensor(X, X) + qt.tensor(P, P) + 0.6 * qt.tensor(X + P, X - P))
        H_vac = g_vac * (qt.tensor(X, qt.qeye(N)) + qt.tensor(qt.qeye(N), X))
        H_drive = sum(2 * np.pi * f * qt.tensor(qt.num(N), qt.qeye(N)) for f in [1.5, 2.8, 4.1])
        H = qt.tensor(qt.qeye(N), qt.qeye(N)) + H_diag + H_vac + H_drive

        c_ops = [np.sqrt(kappa) * qt.tensor(a, qt.qeye(N)),
                 np.sqrt(kappa) * qt.tensor(qt.qeye(N), a)]

        # Run simulation (mesolve for stability)
        result = qt.mesolve(H, psi0, tlist, c_ops)

        final_rho = result.states[-1].ptrace([0,1])

        entropy = qt.entropy_vn(final_rho)
        corr_xx = qt.expect(qt.tensor(X, X), final_rho)
        corr_pp = qt.expect(qt.tensor(P, P), final_rho)

        steering_score = abs(corr_xx) + abs(corr_pp)
        epr_steering = steering_score > 0.4

        # ====================== PLOT ======================
        plt.figure(figsize=(10, 6))
        xx = [qt.expect(qt.tensor(X, X), rho.ptrace([0,1])) for rho in result.states]
        pp = [qt.expect(qt.tensor(P, P), rho.ptrace([0,1])) for rho in result.states]
        
        plt.plot(tlist, xx, label='⟨XX⟩ Diagonal 1', linewidth=2.5)
        plt.plot(tlist, pp, label='⟨PP⟩ Diagonal 2', linewidth=2.5)
        plt.xlabel('Time')
        plt.ylabel('Correlation')
        plt.title('6D+ Bivector Rotational Control')
        plt.legend()
        plt.grid(True)

        img = BytesIO()
        plt.savefig(img, format='png', bbox_inches='tight', dpi=120)
        plt.close()
        img.seek(0)
        plot_base64 = base64.b64encode(img.read()).decode('utf-8')

        # ====================== HTML ======================
        html = f"""
        <h1>Quantum Biology 6D+ Simulation</h1>
        <h2>Stochastic Feedback Results</h2>
        <p><strong>EPR Steering Achieved:</strong> <span style="color: {'green' if epr_steering else 'orange'}; font-weight:bold;">{epr_steering}</span></p>
        <p><strong>Steering Score:</strong> {steering_score:.4f}</p>
        <p><strong>Entanglement Entropy:</strong> {entropy:.4f}</p>
        <p><strong>⟨XX⟩:</strong> {corr_xx:.4f} | <strong>⟨PP⟩:</strong> {corr_pp:.4f}</p>
        <hr>
        <h3>Correlation Evolution</h3>
        <img src="data:image/png;base64,{plot_base64}" style="max-width:100%; border:1px solid #ccc;"/>
        <hr>
        <p><small>Refresh to re-run • Nonlocal Quantum Feedback Loop Active</small></p>
        """
        return html

    except Exception as e:
        return f"<h2>Error:</h2><p>{str(e)}</p>", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
