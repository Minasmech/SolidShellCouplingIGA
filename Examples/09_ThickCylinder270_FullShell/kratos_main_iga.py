import KratosMultiphysics
import KratosMultiphysics.IgaApplication
from KratosMultiphysics.StructuralMechanicsApplication.structural_mechanics_analysis import StructuralMechanicsAnalysis

if __name__ == "__main__":
    with open("ProjectParameters.json",'r') as parameter_file:
        parameters = KratosMultiphysics.Parameters(parameter_file.read())

    model = KratosMultiphysics.Model()
    simulation = StructuralMechanicsAnalysis(model, parameters)

    simulation.Initialize()
    #Surf = simulation.model.GetModelPart("IgaModelPart").GetGeometry(2)
    #print("Show Global Coordinates of post process points")
    #print(Surf.GlobalCoordinates([0, 15, 0]))
    #print(Surf.GlobalCoordinates([21.205750411731103, 15, 0]))
    #print(Surf.GlobalCoordinates([0, 30, 0]))
    #print(Surf.GlobalCoordinates([21.205750411731103, 30, 0]))
    simulation.RunSolutionLoop()
    simulation.Finalize()
