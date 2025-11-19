# TheLight24 v6 – Physics core (3D N-body, Coulomb, optional Yukawa/drag), NumPy vectorized
import numpy as np
from .units import G_SI, EPS0_SI, clamp

class PhysicsConfig:
    def __init__(self,
                 grav=True,
                 coulomb=False,
                 yukawa=False,
                 yukawa_lambda=1e9,
                 yukawa_alpha=0.1,
                 drag=False,
                 drag_gamma=0.0,
                 softening=1e3):
        self.grav = grav
        self.coulomb = coulomb
        self.yukawa = yukawa
        self.yukawa_lambda = yukawa_lambda
        self.yukawa_alpha = yukawa_alpha
        self.drag = drag
        self.drag_gamma = drag_gamma
        self.softening = softening

class PhysicsCore:
    """
    Stato come array strutturati (pos[N,3], vel[N,3], m[N], q[N]).
    Force-model: Gravità Newtoniana, Coulomb, Yukawa opzionale, Drag lineare.
    Integrazione RK4 con dt adattivo (CFL-like semplice).
    """
    def __init__(self, pos, vel, mass, charge=None, cfg: PhysicsConfig = None):
        self.pos = np.asarray(pos, dtype=np.float64)   # (N,3)
        self.vel = np.asarray(vel, dtype=np.float64)   # (N,3)
        self.mass = np.asarray(mass, dtype=np.float64) # (N,)
        self.charge = np.zeros_like(self.mass) if charge is None else np.asarray(charge, dtype=np.float64)
        self.N = self.pos.shape[0]
        self.cfg = cfg or PhysicsConfig()

        # sanity
        assert self.pos.shape == (self.N,3)
        assert self.vel.shape == (self.N,3)
        assert self.mass.shape == (self.N,)
        assert self.charge.shape == (self.N,)

    def _pairwise_diffs(self, x):
        # x: (N,3) -> dx[i,j,3] = x[j]-x[i]
        return x[np.newaxis,:,:] - x[:,np.newaxis,:]  # (N,N,3)

    def _forces(self, pos, vel):
        N = self.N
        dx = self._pairwise_diffs(pos)                  # (N,N,3)
        r2 = np.sum(dx*dx, axis=-1) + (self.cfg.softening**2) # (N,N)
        inv_r3 = r2**(-1.5)

        # mask self interaction
        np.fill_diagonal(inv_r3, 0.0)

        F = np.zeros_like(pos)

        if self.cfg.grav:
            # Fg_i = G * sum_j m_i m_j * (x_j - x_i)/|r|^3
            mprod = self.mass[:,None] * self.mass[None,:]
            coef = G_SI * mprod * inv_r3
            Fg = np.einsum('ij,ijc->ic', coef, dx)
            F += Fg

        if self.cfg.coulomb:
            # Fe_i = (1/(4π eps0)) * qi qj * (x_j - x_i)/|r|^3
            qprod = self.charge[:,None] * self.charge[None,:]
            coef = (1.0/(4.0*np.pi*EPS0_SI)) * qprod * inv_r3
            Fe = np.einsum('ij,ijc->ic', coef, dx)
            F += Fe

        if self.cfg.yukawa:
            # Yukawa approx: Fy ~ alpha * (x_j-x_i)/r^3 * exp(-r/lambda)
            r = np.sqrt(r2)
            np.fill_diagonal(r, 1.0)   # avoid exp(-0) for diag, not used
            coef = self.cfg.yukawa_alpha * np.exp(-r / self.cfg.yukawa_lambda) * (r**-3)
            np.fill_diagonal(coef, 0.0)
            Fy = np.einsum('ij,ijc->ic', coef, dx)
            F += Fy

        if self.cfg.drag:
            # Fd = -gamma * v
            F += -self.cfg.drag_gamma * vel

        return F

    def _derivatives(self, state):
        # state tuple: (pos, vel)
        pos, vel = state
        acc = self._forces(pos, vel) / self.mass[:,None]
        return vel, acc

    def _rk4_step(self, dt):
        pos0, vel0 = self.pos, self.vel

        k1_v, k1_a = self._derivatives((pos0, vel0))
        k2_v, k2_a = self._derivatives((pos0 + 0.5*dt*k1_v, vel0 + 0.5*dt*k1_a))
        k3_v, k3_a = self._derivatives((pos0 + 0.5*dt*k2_v, vel0 + 0.5*dt*k2_a))
        k4_v, k4_a = self._derivatives((pos0 + dt*k3_v, vel0 + dt*k3_a))

        self.pos = pos0 + (dt/6.0)*(k1_v + 2*k2_v + 2*k3_v + k4_v)
        self.vel = vel0 + (dt/6.0)*(k1_a + 2*k2_a + 2*k3_a + k4_a)

    def suggest_dt(self, dt_max=10.0, safety=0.4):
        # Heuristica: basato su max velocità e min distanza tra particelle
        v = np.linalg.norm(self.vel, axis=1)
        vmax = max(1e-6, np.max(v))
        dx = self._pairwise_diffs(self.pos)
        r = np.sqrt(np.sum(dx*dx, axis=-1))
        r[r==0] = np.inf
        rmin = np.min(r)
        dt = safety * rmin / vmax
        return clamp(dt, 1e-4, dt_max)

    def step(self, dt=None):
        if dt is None:
            dt = self.suggest_dt()
        self._rk4_step(dt)
        return dt
