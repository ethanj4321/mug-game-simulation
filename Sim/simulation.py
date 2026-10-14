
import numpy as np
import matplotlib.pyplot as plt

# surrounding medium (room)
T_room = 293.15
phi = 0.5
# peltier params 
S = 0.05    # Seebeck coefficient (V/K)
R = 2.0     # electrical resistance (ohm)
K = 0.5     # thermal conductance (W/K)

# hot volume (mug)
A = 0.00785 #(m^2) area at top of mug
h = 0.025477707 #(m)
m_hot = 0.2
c_hot = 4186
T_hot = 353.15  # K (80 C)

# cold volume
m_cold = 0.5
c_cold = 4186
T_cold = 293.15  # K (20 C)

# ambient convection (guessed values, tune to your hardware)
h_conv = 10.0                                  # W/(m^2 K)
A_hot = A + 2*np.sqrt(np.pi*A)*h               # top + side wall of mug (m^2)
A_cold = 0.01                                  # exposed area of cold sink (m^2)
L_vap = 2.26e6                                 # latent heat of vaporisation (J/kg)

def p_sat(T):
    """Saturation vapour pressure (Pa) at T in K (Magnus)."""
    Tc = T - 273.15
    return 610.94*np.exp(17.625*Tc/(Tc + 243.04))

dt = 0.01
temps_hot = []
temps_cold = []
power = []
ts = np.arange(0, 3600, dt)
for t in ts:
    # surface vapour pressure at T_hot, room vapour pressure at T_room
    p_w = phi*p_sat(T_room)
    # heat lost to evaporation (W, positive = mug loses heat); air velocity in a room is around 0
    dQ_evaporation = A*(p_sat(T_hot) - p_w)*0.089

    delta_temp = T_hot - T_cold
    I = (S*delta_temp)/(2*R)
    # heat drawn out of the hot side / delivered to the cold side (W)
    dQ_hot = S*I*T_hot + K*delta_temp - 0.5*I**2*R
    dQ_cold = S*I*T_cold + K*delta_temp + 0.5*I**2*R

    # convection to the room
    dQ_loss_hot = h_conv*A_hot*(T_hot - T_room)
    dQ_loss_cold = h_conv*A_cold*(T_cold - T_room)

    dT_hot = -(dQ_hot + dQ_evaporation + dQ_loss_hot)*dt/(c_hot*m_hot)
    dT_cold = (dQ_cold - dQ_loss_cold)*dt/(c_cold*m_cold)

    P = dQ_hot - dQ_cold    # electrical power = S*I*dT - I^2*R
    T_hot = T_hot + dT_hot
    T_cold = T_cold + dT_cold
    m_hot = m_hot - dQ_evaporation/L_vap*dt   # evaporated water leaves the mug
    temps_hot.append(T_hot)
    temps_cold.append(T_cold)
    power.append(P)

fig, axes = plt.subplots(3, 1, figsize=(8, 10), sharex=True)

axes[0].plot(ts, temps_hot, color='tab:red')
axes[0].set_ylabel('T_hot (K)')
axes[0].set_title('Hot side temperature')

axes[1].plot(ts, temps_cold, color='tab:blue')
axes[1].set_ylabel('T_cold (K)')
axes[1].set_title('Cold side temperature')

axes[2].plot(ts, power, color='tab:green')
axes[2].plot(ts, [0.005 for _ in range(len(ts))])
axes[2].set_ylabel('Power (W)')
axes[2].set_xlabel('Time (s)')
axes[2].set_title('Net heat flow (Q_hot - Q_cold)')

plt.tight_layout()
plt.savefig('mug_game_results.png')
plt.show()
