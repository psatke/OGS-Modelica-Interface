// CP: 65001
// SimulationX Version: 4.3.1.71220
within Custome_Blocks.InterfacesGeneral;
model I2RO "Signal Input to Real Output"
	parameter Integer n(min=0)=0 "Dimension of input and output vector" annotation(HideResult=true);
	input SignalBlocks.InputPin x[n] annotation(Placement(
		transformation(extent={{-20,-20},{20,20}}),
		iconTransformation(extent={{-70,-20},{-30,20}})));
	Modelica.Blocks.Interfaces.RealVectorOutput y[n] annotation(Placement(
		transformation(extent={{50,-10},{70,10}}),
		iconTransformation(extent={{50,-10},{70,10}})));
	equation
		y = x;
	annotation(Icon(
		coordinateSystem(extent={{-50,-50},{50,50}}),
		graphics={
			Line(
				points={{-50,0},{0,0},{0,0}},
				color={0,0,255}),
			Line(
				points={{0,0},{50,0}},
				color={0,0,127})}));
end I2RO;
