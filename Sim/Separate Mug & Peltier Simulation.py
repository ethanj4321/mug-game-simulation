import numpy as np
import matplotlib.pyplot as plt

# surrounding medium (room)
T_room = 293.15
phi = 0.5

# peltier params
S = 0.05     # Seebeck coefficient (V/K)
R = 2.0      # internal electrical resistance (ohm)
R_load = 10.0 # external load resistance on the board (ohm)
K = 0.5      # thermal conductance of peltier (W/K)
mc_plate = 12.0 # heat capacity of peltier top ceramic plate (J/K)

# hot volume (mug water)
A = 0.00785
h = 0.025477707
m_mug = 0.2
c_mug = 4186
T_mug = 353.15  # K (80 C)
K_contact = 1.2 # conductance through mug base to peltier (W/K)

# peltier hot face and cold sink (aluminum heatsink instead of 0.5kg water)
T_hot = 293.15
m_cold = 0.15
c_cold = 900    # aluminum (J/kg K)
T_cold = 293.15

# ambient convection
h_conv = 10.0
A_mug = A + 2*np.sqrt(np.pi*A)*h
A_cold = 0.025
L_vap = 2.26e6

def p_sat(T):
    Tc = T - 273.15
    return 610.94*np.exp(17.625*Tc/(Tc + 243.04))

def mug_on_pad(t):
    # player lifts mug to do some task between 180-240s and 600-690s
    if (180 <= t <= 240) or (600 <= t <= 690):
        return False
    return True

dt = 0.05
ts = np.arange(0, 1800, dt)
temps_mug = []
temps_hot = []
temps_cold = []
volts = []

for t in ts:
    p_w = phi*p_sat(T_room)
    dQ_evaporation = A*(p_sat(T_mug) - p_w)*0.089
    dQ_loss_mug = h_conv*A_mug*(T_mug - T_room)

    if mug_on_pad(t):
        dQ_contact = K_contact*(T_mug - T_hot)
        dQ_loss_plate = 0.0
    else:
        dQ_contact = 0.0
        dQ_loss_plate = h_conv*A*(T_hot - T_room)

    delta_temp = T_hot - T_cold
    I = (S*delta_temp)/(R + R_load)
    V = I*R_load

    dQ_hot = S*I*T_hot + K*delta_temp - 0.5*I**2*R
    dQ_cold = S*I*T_cold + K*delta_temp + 0.5*I**2*R
    dQ_loss_cold = h_conv*A_cold*(T_cold - T_room)

    T_mug += -(dQ_contact + dQ_evaporation + dQ_loss_mug)*dt/(c_mug*m_mug)
    T_hot += (dQ_contact - dQ_hot - dQ_loss_plate)*dt/mc_plate
    T_cold += (dQ_cold - dQ_loss_cold)*dt/(c_cold*m_cold)
    m_mug -= dQ_evaporation/L_vap*dt

    temps_mug.append(T_mug)
    temps_hot.append(T_hot)
    temps_cold.append(T_cold)
    volts.append(V)

# save voltage trace so the MCU script can load it directly
np.save('peltier_voltage.npy', np.column_stack((ts, volts)))

fig, axes = plt.subplots(2, 1, figsize=(8, 7), sharex=True)

axes[0].plot(ts, temps_mug, label='T_mug (water)', color='tab:orange')
axes[0].plot(ts, temps_hot, label='T_hot (peltier top)', color='tab:red')
axes[0].plot(ts, temps_cold, label='T_cold (heatsink)', color='tab:blue')
axes[0].set_ylabel('Temperature (K)')
axes[0].legend()

axes[1].plot(ts, volts, color='tab:green')
axes[1].axhline(0.11, color='gray', linestyle='--', label='MCU cutoff')
axes[1].set_ylabel('Terminal Voltage (V)')
axes[1].set_xlabel('Time (s)')
axes[1].legend()

plt.tight_layout()
plt.show()
