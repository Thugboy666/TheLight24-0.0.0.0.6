# TheLight24 v6 – Units helpers
G_SI = 6.67430e-11           # m^3 kg^-1 s^-2
EPS0_SI = 8.8541878128e-12   # F/m

def clamp(v, vmin, vmax):
    return max(vmin, min(v, vmax))
