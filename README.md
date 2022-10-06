# OGS-Modelica-Interface
This interface passes information from an OpenGeoSys-Model to a Modelica-Model using the Transmission Control Protocol/Internet Protocol. The Co-simulation is controlled by _ProgrammAndServerControl.py which starts a communication server, SimulationX (client) and OGS (client) as well as handeling the information transfer and saving the results.

## Requirements
To successfully run _ProgrammAndServerControl.py without further adaptations SimulationX 4.3 as well as the GreenCity and InterfacesGeneral librarys have to be available. The Modelica model uses some custome componets based on the mentioned librarys that are included (Modelica-Model/CustomeComponents) and custome data (Modelica-Model/Data) that needs to be referenced.

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
* the final timestep (`simTimeFinalStep=3600`) and the project name (`OGS_project='3BHE'`) need to be defined in OGS-Model/_ProgrammAndServerConrol.py
* more complex models will require a longer timeout off the barrier in OGS-Model/_ProgrammAndServerConrol.py

Exchange of the Modelica model:
* parameters of the component `InterfacesGeneral.CoSimulation.Coupling` need to match the OGS model
* additional `GreenCity.Interfaces.Thermal.DefineVolumeFlow` may be required
* the final timestep (`simTimeFinalStep=3600`) and the project name (`simX_model='Validierung'`) need to be defined in OGS-Model/_ProgrammAndServerConrol.py

## Puplications
## License
