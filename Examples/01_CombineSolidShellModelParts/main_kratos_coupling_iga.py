# Project imports
from QuESo_PythonApplication.PyQuESo import PyQuESo
from KratosMultiphysics.StructuralMechanicsApplication.structural_mechanics_analysis import StructuralMechanicsAnalysis
import KratosMultiphysics as KM
import KratosMultiphysics.IgaApplication as IgaApplication
import QuESo_PythonApplication as QuESo_App
from kratos_interface.model_part_utilities import ModelPartUtilities
from kratos_interface.custom_analysis_stage import CustomAnalysisStage
# C:\Users\minas\Documents\Thesis\Examples\02_newPartModels\main_kratos_coupling_iga.py
from AdditionalModules.GetAndSaveIntpointsFromQuesoConditions import GetIntergrationPointsFromQuesoConditions, SavePointsToVTK
import os

class CouplingSolidShellAnalysisStage(CustomAnalysisStage):
    def __init__(self, model, queso_settings, kratos_settings_filename, elements, boundary_conditions):
        super().__init__(model, queso_settings, kratos_settings_filename, elements, boundary_conditions)
       

def main():
    #First run queso
    pyqueso = PyQuESo("QuESoSettings.json")
    pyqueso.Run()
    
    #Create custom analysis
    model = KM.Model()
    queso_settings = pyqueso.GetSettings()
    queso_elements = pyqueso.GetElements()
    queso_boundary_conditions = pyqueso.GetConditions()
    # Write integration points for boundary 1
    Conditon_1 = queso_boundary_conditions[0]
    IntegrationPoints_Condition1 = GetIntergrationPointsFromQuesoConditions(Conditon_1)
    base_directory = 'data'
    filename = 'Queso_IntPoints_Cond1.vtk'
    file_path = os.path.join(base_directory, filename)
    SavePointsToVTK(IntegrationPoints_Condition1,file_path)
    print("Number of Integration points for Condition1 : ",len(IntegrationPoints_Condition1))

    # Write integration points for boundary 2
    Conditon_2 = queso_boundary_conditions[1]
    IntegrationPoints_Condition2 = GetIntergrationPointsFromQuesoConditions(Conditon_2)
    base_directory = 'data'
    filename = 'Queso_IntPoints_Cond2.vtk'
    file_path = os.path.join(base_directory, filename)
    SavePointsToVTK(IntegrationPoints_Condition2,file_path)
    print("Number of Integration points for Condition2 : ",len(IntegrationPoints_Condition2))



    kratos_settings="KratosParameters.json"
    simulation = CouplingSolidShellAnalysisStage(model,queso_settings, kratos_settings, queso_elements, queso_boundary_conditions)
    simulation.Initialize()
    CoupledSolidShellModelPart = simulation.model.GetModelPart("CoupledSolidShellModelPart")
    print(CoupledSolidShellModelPart)
   
if __name__ == "__main__":
    main()
