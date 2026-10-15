import numpy as np
import matplotlib.pyplot as plt

# load voltage from peltier simulation
data = np.load('peltier_voltage.npy')
ts_full = data[:, 0]
v_full = data[:, 1]

# MCU polls every 0.5 seconds (every 10th step of dt=0.05)
step = 10
ts = ts_full[::step]
v_in = v_full[::step]

# 10-bit ADC with 1.1V internal reference
V_ref = 1.1
adc_max = 1023
adc_thresh = 100   # ~0.11V cutoff 

adc_readings = []
score_flat = []
score_prop = []

s_flat = 0
s_prop = 0

for v in v_in:
    # small sensor noise + hardware clamping between 0V and V_ref
    v_pin = np.clip(v + np.random.normal(0, 0.002), 0.0, V_ref)
    adc = int((v_pin / V_ref) * adc_max)
    adc_readings.append(adc)

    # method 1: simple counter (+1 per tick whenever voltage is above threshold)
    if adc >= adc_thresh:
        s_flat += 1

    # method 2: proportional counter (hotter mug = faster points) we might wanna add this feature later on 
    if adc >= adc_thresh:
        s_prop += adc // 50

    score_flat.append(s_flat)
    score_prop.append(s_prop)

fig, axes = plt.subplots(2, 1, figsize=(8, 7), sharex=True)

axes[0].step(ts, adc_readings, where='post', color='tab:purple')
axes[0].axhline(adc_thresh, color='gray', linestyle='--')
axes[0].set_ylabel('10-bit ADC (0-1023)')
axes[0].set_title('Microcontroller ADC Reading')

axes[1].plot(ts, score_flat, label='Flat tick score (+1 / tick)')
axes[1].plot(ts, np.array(score_prop)/6, label='Proportional score (scaled)')
axes[1].set_ylabel('Registered Score')
axes[1].set_xlabel('Time (s)')
axes[1].legend()

plt.tight_layout()
plt.show()
