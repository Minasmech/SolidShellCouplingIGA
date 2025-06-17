# Project imports
from QuESo_PythonApplication.PyQuESo import PyQuESo
from KratosMultiphysics.StructuralMechanicsApplication.structural_mechanics_analysis import StructuralMechanicsAnalysis
import KratosMultiphysics as KM
import KratosMultiphysics.IgaApplication as IgaApplication
import QuESo_PythonApplication as QuESo_App
from kratos_interface.model_part_utilities import ModelPartUtilities
from kratos_interface.custom_analysis_stage import CustomAnalysisStage
from AdditionalModules.GetAndSaveIntpointsFromQuesoConditions import GetIntergrationPointsFromQuesoConditions, SavePointsToVTK, GetNormalFromQuesoConditions, SaveVectorsToTXT
import os

class CouplingSolidShellAnalysisStage(CustomAnalysisStage):
    def __init__(self, model, queso_settings, kratos_settings_filename, elements, boundary_conditions):
        IgaModelPart = model.CreateModelPart("IgaModelPart")
        IgaModelPart.AddNodalSolutionStepVariable(KM.DISPLACEMENT)
        IgaModelPart.AddNodalSolutionStepVariable(KM.REACTION)

        CoupledSolidShellModelPart = model.CreateModelPart("CoupledSolidShellModelPart")
        CoupledSolidShellModelPart.CreateSubModelPart("CouplingInterface_1")
        CoupledSolidShellModelPart.CreateSubModelPart("CouplingInterface_2")
              
        super().__init__(model, queso_settings, kratos_settings_filename, elements, boundary_conditions)
        
    def ModifyInitialGeometry(self):
        IgaModelPart = self.model.GetModelPart("IgaModelPart")
        # Add Dofs
        KM.VariableUtils().AddDof(KM.DISPLACEMENT_X, KM.REACTION_X, IgaModelPart)
        KM.VariableUtils().AddDof(KM.DISPLACEMENT_Y, KM.REACTION_Y, IgaModelPart)
        KM.VariableUtils().AddDof(KM.DISPLACEMENT_Z, KM.REACTION_Z, IgaModelPart)

        if self.lagrange_dofs_required:
            KM.VariableUtils().AddDof(KM.VECTOR_LAGRANGE_MULTIPLIER_X, IgaApplication.VECTOR_LAGRANGE_MULTIPLIER_REACTION_X, IgaModelPart)
            KM.VariableUtils().AddDof(KM.VECTOR_LAGRANGE_MULTIPLIER_Y, IgaApplication.VECTOR_LAGRANGE_MULTIPLIER_REACTION_Y, IgaModelPart)
            KM.VariableUtils().AddDof(KM.VECTOR_LAGRANGE_MULTIPLIER_Z, IgaApplication.VECTOR_LAGRANGE_MULTIPLIER_REACTION_Z, IgaModelPart)
        
        return super().ModifyInitialGeometry()
    
    def _GetOrderOfProcessesInitialization(self):
        return ["neumann_process_list","additional_processes", "dirichlet_process_list"]
       

def main():
    #First run queso
    pyqueso = PyQuESo("QuESoSettings.json")
    pyqueso.Run()
    
    #Create custom analysis
    model = KM.Model()
    queso_settings = pyqueso.GetSettings()
    queso_elements = pyqueso.GetElements()
    queso_boundary_conditions = pyqueso.GetConditions()

    kratos_settings="KratosParameters.json"
    simulation = CouplingSolidShellAnalysisStage(model,queso_settings, kratos_settings, queso_elements, queso_boundary_conditions)
    simulation.Run()
   
if __name__ == "__main__":
    main()
