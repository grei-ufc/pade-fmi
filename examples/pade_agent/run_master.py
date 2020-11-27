import matplotlib.pyplot as plt
import numpy as np
from pyfmi import load_fmu

model = load_fmu('./PadeSlave.fmu')

inputs = ('inputVariable', lambda t: 5. * np.cos(t))
simulation = model.simulate(final_time=30, input=inputs)

plt.plot(simulation['time'], simulation['inputVariable'])
plt.plot(simulation['time'], simulation['outputVariable'])

plt.legend(['inputVariable', 'outputVariable'])
plt.xlabel('time')
plt.show()
