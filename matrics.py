import numpy as np

def compute_metrics(t, response, control, setpoint=0.0, initial_error=0.2, 
                    settle_pct=0.05, rise_lo=0.1, rise_hi=0.9, sse_window=0.5):
    error = response - setpoint
    abs_error = np.abs(error)
    dt = t[1] - t[0]
    
    # Rise time: time for error to go from 90% to 10% of initial error
    err_mag = np.abs(error)
    thresh_hi = rise_hi * abs(initial_error)  # 90% of initial
    thresh_lo = rise_lo * abs(initial_error)  # 10% of initial
    t_hi = t[err_mag < thresh_hi][0] if np.any(err_mag < thresh_hi) else t[-1]
    t_lo = t[err_mag < thresh_lo][0] if np.any(err_mag < thresh_lo) else t[-1]
    Tr = t_lo - t_hi
    
    # Settling time: last time response leaves ±5% band
    band = settle_pct * abs(initial_error)
    outside = np.where(err_mag > band)[0]
    Ts = t[outside[-1]] if len(outside) > 0 else 0.0
    
    # Percentage overshoot: peak deviation past setpoint
    # If initial error is positive, overshoot is the most negative error
    if initial_error > 0:
        peak_overshoot = np.min(error)  # most negative = crossed past zero
    else:
        peak_overshoot = np.max(error)
    PO = (peak_overshoot / initial_error) * 100  # will be negative if overshooting
    
    # Steady-state error: mean of final window
    sse_samples = int(sse_window / dt)
    SSE = np.mean(error[-sse_samples:])
    
    # IAE: integral of |e(t)| dt
    IAE = np.trapz(abs_error, t)
    
    # ITAE: integral of t * |e(t)| dt
    ITAE = np.trapz(t * abs_error, t)
    
    # ISC: integral of u(t)^2 dt
    ISC = np.trapz(control**2, t)
    
    return {
        'Tr': Tr, 'Ts': Ts, 'PO': PO, 'SSE': SSE,
        'IAE': IAE, 'ITAE': ITAE, 'ISC': ISC
    }