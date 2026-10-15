# Mug game simulation
- Mug modelled as cylindrical tank, open on top
- Ambient heat loss to room is modelled using Newton's law of cooling and evaporation from the top of the mug
- Peliter element is modelled as a Seebeck generator
- Heat moves from hot volume to cold volume and excess is extracted by peliter element
- Still have to find actual values for Peltier element constants and h_conv
---------------------------------------------------------------------------------------------------------------
- `peltier_sim.py`: Splits the hot side into two separate nodes: the water inside the mug (`T_mug`) and the top ceramic plate of the Peltier (`T_hot`). This lets us simulate a player lifting the mug off the pad during game task and see how fast the voltage drops. Exports the output voltage to `peltier_voltage.npy`.
- `mcu_sim.py`: Loads `peltier_voltage.npy` and simulates a simple microcontroller polling the Peltier at 2 Hz using a 10-bit ADC (1.1V internal reference). Compares two scoring methods:
  1. **Flat tick scoring:** +1 point per sample whenever the ADC reading is above the voltage threshold.
  2. **Proportional scoring:** Points scale with the ADC reading (hotter mug = faster points)