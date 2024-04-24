# OGS-Modelica-Interface
[![License: CC BY 4.0](https://img.shields.io/badge/License-CC_BY_4.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)
[![OpenGeoSys](https://img.shields.io/badge/OpenGeoSys-v6.5.1-blue?style=flat)](https://www.opengeosys.org/releases/)
[![Modelica](https://img.shields.io/badge/Modelica-v3.5-blue?style=flat)](https://modelica.org/documents.html)
[![SimulationX](https://img.shields.io/badge/SimulationX-v4.3-blue?style=flat&logo=data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAG8AAABuCAYAAAApmU3FAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAAHYYAAB2GAV2iE4EAAAcNSURBVHhe7d1fjNREHMDx3+xtez2WnByJ+uSD96o+qS9CVPwTEw1/jOEU9UmFQyKaYIyJmmhEUNHgP140YIiCRhJMfFGMEv8BJigmKBrxTyDhX0LQYIjs7Z9unV/bue55t9tpO22n0/kmkNu5h9vM57q7vZ3pkr+WjTpzzQrYDujc6ER0Ov7XGUcI/Vfxb/RvwCBAjo2NOiMGaDzMwUlwgNTmeBOZda0GOM06/SL8Z9eqFY03mUOPNtsGc9FKGLz9IX8su0khpgXN3e/DxNan6WE1gCPeN3qk8VhdcNY9T/iD2dfavwvqr67yboQc+YjH9wCrcpLAYWTWMD3qqv6t8MqNJxGcW7sR6aG6vHiywdGc8+foK922fyu8cuJJCIc5/5yhT3yt0Oc7VvnwJIXD7BN/0BMVev84KxeexHBOow724QNABuhLf87KgycxHGb/8i10Tv5ORfAcj69y4EkOhzW/+ZD+R19tRvjLjvp4BYBrH9oD7e8+BTAG/RG+1MYrAJzTmIDGjo30qJuIdNRh6uIVAA5r7HgJ7F/3A1RNf4Q/NfEKAtf8eDM0P3k7FhymHl5h4LbAxLb19P7SGzHfflILr1Bw67z7W4lPoA5eIeH4z+lmSg28EsJhxccrKRxWbLwSw2HFxSs5HFZMPA3nVjw8DTdZsfA03JSKg6fhpuXjEe+HuX+rkTANN2MeHv1hpHYB/QIRJQPUcD1z8ZxWA4wbloFx490A7aY8gBqub96R16FH3tBsGLpvLRjXj8kBqOFCC16w2N5iT2vFi/kDajiuAjw/UjXyBdRw3AV4XW8I5gao4SI17chjZQ6o4SLXEw/LDFDDxaovHpY6oIaLXSgelhqghksUFx4mHFDDJY4bDxMGqOGEFAkPSwyo4YQVGQ+LDajhhBYLD4sMqOGEFxsP4wbUcKmUCA8LBdRwqZUYD+sJqOFSTQgeNg0Qr5yn4VJNGB42CXgdBey0NVzKCcXDXMAH1oG1aqOGSznheJh9+HtofbUT7COH/BG5UgEOE47X/mkv1Dc9Au2DX0L9tVVgH/3Z/44cqQKHCcVz4d5Y7V5Di1g16Jw8AvVXHpQGUCU4TBheNxzQ5z03w4TOKTkAVYPDhODNCMeSAFBFOCwxXl84Vo6AqsJhifC44Fg5AKoMh8XGiwTHyhBQdTgsFl4sOFYGgGWAwyLjJYJjpQhYFjgsEp4QOFYKgGWCw7jxhMKxBAK2vt4JE9vxWl7lgMO48FKBYwkAbO39COpbngLo2KWBw0LxUoVjJQBs7aNwbz0O0DhfKjisL14mcKwYgC7cmwhXj/QxLqrUEy9TOFYEwLLDYQFe18KhXOBYHIAazivA8zdX5grH6gOo4YICPDoR7d9+yB+O1Q3ovyPvvqrUcJMNrLls5Bmr4gCZcxG0dm0F58xxd+KkaGAAOmdPg/3nQSDDc324f+l4zr9YEmRWiH/k0fOjyoWXgDF/CT0W6RCe6MoQvV/EsMC89g6oXj4fjKtv8ZYUhi2tL0keHk6GacHg0jVgLlzprrfMHRBPuEkFrHufBPO25UBqw2CNb+DfG1GCguc8nCwaLtfD9Za5AnbD3Xq/P9i1LlQDugV4XZfyyBWwBxxLAwYFeP8rF8AQOJYG9OqJh2UKyAnH0oAheFgmgBHhWGUHDMXDUgWMCccqMyAXHpYKYEI4VlkBufEwoYCC4FhlBIyEhwkBxGt7mkNgLV8vBI5VNsDIeFgiQIQbHIKhFS+AueAuf1Bc0wBlvei5gGLhYbEAGdw4ndx5i/1B8XmAG6B6zWL3M1lVLTYeFgmwG45OatqRapUe3c+DcdXN4OCH6SpYIjyMCzBjOBaZNQxDq18H48qblARMjIf1BcwJjoWfF6EqoBA8bEbAnOFYqgIKw8MmAfEcrt2SAo6lIqBQPMwFXDgOZDadLHo6IAMcSzVA4XiYtfRRsFa+TE8Hlvgj8qQSYCp4zc+2QePdtdD+cY8/IleqAArHc7dZbV8PnVNHob7pYXcdqIypACgUb8r+OHPQXf+J60A1YDoJw5txY2PV0IApJgSv745UDZhaifG4thJrwFRKhMcFx9KAwouN19z9HoV7jg+OpQGFFgsPt1lNvPMshXP44VgaUFiR8absj4sKx9KAQoqEJ3RjowZMHDdeKjtSNWCiuPBS3UqsAWMXipcqHEsDxqovXiZwLA0YuZ54mcKxNGCkAryu1cW5wLE0IHcBnr8zNlc4lgbkKsCjE9Y+8Hn+cKwpgPK+Iz/rsc1gzFsE7lUqMo4cGxt1Rio2wOgV0Dl9HJxzf+cP1127BWTkYjAW3AnEGKQDkuw9YE8z+Et29jQ0v/gAoNmYfARLu1q1AuTE2KXOXLMCNi7VI/RAdP/kJdPmDDoZHRucFn1okuludUfnjJj4i5VdtWoF/gM9yM3O8ss7wQAAAABJRU5ErkJggg==)](https://myesi.esi-group.com/downloads/software-downloads/simulationx-4.3.1)
[![Python](https://img.shields.io/badge/Python-v3.10.9-blue?style=flat&logo=data:image/png;base64,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)](https://www.python.org/downloads/)


This interface passes information from an OpenGeoSys (OGS) -Model to a Modelica-Model using the Transmission Control Protocol/Internet Protocol. The Co-simulation is controlled by _ProgramAndServerControl.py which starts a communication server, SimulationX (client) and OGS (client) as well as handeling the information transfer and saving the results.

## Requirements

**Modelica:**
To successfully run _ProgramAndServerControl.py without further adaptations SimulationX 4.3 as well as the GreenCity and InterfacesGeneral librarys have to be available. The Modelica model uses some custome componets based on the mentioned librarys that are included (Modelica-Model/CustomeComponents) and custome data (Modelica-Model/Data) that needs to be referenced.

**OpenGeoSys:**
The executable OGS file is already included, therefore no installation is needed.

## Simulation models
The Modelica model simulates a single family home that is thermally supplied by a heating system consisting of a heat pump, a heat storage, a plate heat exchanger (for cooling) and floor heating. The OGS model includes three double U-pipe borehole heat exchangers (BHE) with a length of 100 m and the surrounding soil.

![Model Scheme](img/ModelScheme.png "Scheme of the OGS model and the Modelica model")

## Communication
The communication protocol is mainly dictated by the [Modelica component](https://doc.simulationx.com/4.0/1033/Default.htm#Libraries/InterfacesGeneral/CoSimulation/Coupling.htm%3FTocPath%3DLibraries%7CGeneric%2520Interfaces%7CCo-Simulation%7CTCP%252FIP%2520Coupling%2520Element%7C_____0) and the number of BHEs. The simulation results volume flow and temperature are communicated at constant step sizes (initially 1 h). The calculation steps of OGS correspond to the communication steps but the calculation steps of the Modelica model are usually every couple of seconds or less. The resulting information loss from Modelica to OGS should be taken into account.

## Modifications
Exchange of the OGS model:
* the .prj file needs to contain the following lines as demonstrated in OGS-Model/3BHE.prj
  1.        <python_script>PreAndPostTimestep.py</python_script>
  2.        <use_server_communication>true</use_server_communication>
* changing the number or type of BHE will result in a different number of communication channels in OGS-Model/PreAndPostTimestep.py (Modelica model needs to be modified respectively)
* the final timestep (`simTimeFinalStep=3600`) and the project name (`OGS_project='3BHE'`) need to be defined in OGS-Model/_ProgramAndServerConrol.py
* more complex models will require a longer timeout off the barrier in OGS-Model/_ProgramAndServerConrol.py

Exchange of the Modelica model:
* parameters of the component `InterfacesGeneral.CoSimulation.Coupling` need to match the OGS model
* additional `GreenCity.Interfaces.Thermal.DefineVolumeFlow` may be required
* the final timestep (`simTimeFinalStep=3600`) and the project name (`simX_model='Validierung'`) need to be defined in _ProgramAndServerConrol.py

## Puplications
## License
Creative Commons Attribution 4.0 International Public License