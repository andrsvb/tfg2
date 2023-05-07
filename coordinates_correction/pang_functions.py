import numpy as np
import scipy as sc
# algo mas?

def rot(alpha):
    '''clockwise rotation

    :param: alpha in 360 degrees
    '''
    alpha_rad = alpha*np.pi/180
    return np.array([
        [np.cos(alpha_rad), np.sin(alpha_rad)],
        [-np.sin(alpha_rad), np.cos(alpha_rad)]
    ])


def trans(C1, C2, initial_guess=None, method='SLSQP'):
    def sq(xs):
        x0, y0, angle, scale = xs
        C1_trans = np.array([[x0,y0]]) + scale*C1@rot(angle)
        return ((C1_trans - C2)**2).sum()
    if initial_guess is None:
        x0, y0 = C2[0,:] - C1[0,:]
        initial_guess = (x0, y0, 1, 0)
    sol = sc.optimize.minimize(sq, initial_guess, tol=1e-9, method=method)
    if not sol['success']:
        raise RuntimeError('Numerical error: could not find transformation matrix')
    return tuple(sol['x'])
