import KratosMultiphysics
import KratosMultiphysics.IgaApplication
from KratosMultiphysics.StructuralMechanicsApplication.structural_mechanics_analysis import StructuralMechanicsAnalysis

if __name__ == "__main__":
    with open("ProjectParameters.json",'r') as parameter_file:
        parameters = KratosMultiphysics.Parameters(parameter_file.read())

    model = KratosMultiphysics.Model()
    simulation = StructuralMechanicsAnalysis(model, parameters)
    simulation.Initialize()
    print("Show Global Coordinates of post process points")
    Surf = simulation.model.GetModelPart("IgaModelPart").GetGeometry(3)
    print(Surf.GlobalCoordinates([0 , 0 , 0]))
    print(Surf.GlobalCoordinates([0 , 3 , 0]))
    print(Surf.GlobalCoordinates([0 , 6 , 0]))
    print(Surf.GlobalCoordinates([8 , 0 , 0]))
    print(Surf.GlobalCoordinates([8 , 3 ,0 ]))
    print(Surf.GlobalCoordinates([8 , 6 ,0 ]))
    simulation.RunSolutionLoop()
    simulation.Finalize()
