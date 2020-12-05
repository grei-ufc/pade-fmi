# PADE-FMI: PADE Functional Mock-up Interface

This project extends the [PADE](https://github.com/grei-ufc/pade) - _Python Agent DEvelopment framework_ - to make it possible for its agents to communicate with other FMUs in a co-simulated environment.
It does so by implementing an FMI adapter compatible with the [FMI 2.0 standard](https://fmi-standard.org), which translates variables coming from the simulation into an ACL message, commonly handled within the PADE development environment, and converts ACL messages back to output simulation variables.

The adapter is composed of two pieces:
- **_FMI Adapter Behaviour_**: A class that extends the `Behaviour` base class (from `pade.behaviours.protocols`) and can be seen as an endpoint for an agent to receive data coming from the Master (such as input variables, current simulation time and simulation step) and return values for output variables;
- **_FMU (Functional Mock-up Unit)_**: A piece of software that is loaded and directly executed by the Master, in compliance with FMI specs for Co-simulation. The FMU is given in advance the identifier of the agent (AID*) it must connect to. When called by the Master, the FMU methods forward the simulation variables to the PADE agent and waits for its response containing definitions for the FMU outputs.

*As stated in FIPA specs, the AID (Agent Identifier) labels an agent and contains the agent's transport address(es).

## Installation
### Using Anaconda

Run the following commands in a terminal to install all necessary packages:
```bash
pip install pade && pade create-pade-db
conda install -y -c conda-forge pythonfmu
conda install -y -c conda-forge pyfmi
git clone --depth=1 https://github.com/bressanmarcos/pade-fmi
pip install ./pade-fmi
```

## Usage
Example available [here](https://github.com/bressanmarcos/pade-fmi/tree/master/examples/pade_agent).

(Docs are still being developed. Please, be free to collaborate!)