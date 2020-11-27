# PADE-FMI Agent Example

## Building FMU
In this example, a Functional Mock-up Unit must be generated using `pade-fmi` build command.

An `fmu.json` file should be passed as an argument.
```bash
$ pade-fmi fmu.json
```

A `PadeSlave.fmu` file will be built in the current directory.

## Run agent
To test the FMU, the PADE runtime has to be running:
```bash
$ pade start-runtime fmi_agent.py
```

## Execute simulation
In another terminal, it is possible to simulate the `(Master <=> FMU <=> Agent)` communication and plot the simulation variables by running the `run_master.py` script.
```bash
$ python run_master.py
```