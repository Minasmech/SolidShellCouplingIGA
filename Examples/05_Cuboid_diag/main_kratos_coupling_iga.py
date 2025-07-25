# Project imports
from QuESo_PythonApplication.PyQuESo import PyQuESo
from KratosMultiphysics.StructuralMechanicsApplication.structural_mechanics_analysis import StructuralMechanicsAnalysis
import KratosMultiphysics as KM
import KratosMultiphysics.IgaApplication as IgaApplication
import QuESo_PythonApplication as QuESo_App
from kratos_interface.model_part_utilities import ModelPartUtilities

class CouplingSolidShellAnalysisStage(StructuralMechanicsAnalysis):
    def __init__(self, model, queso_settings, kratos_settings_filename, elements, boundary_conditions):
        """The constructor."""
        # Read kratos settings
        with open(kratos_settings_filename,'r') as parameter_file:
            analysis_parameters = KM.Parameters(parameter_file.read())

        self.boundary_conditions = boundary_conditions
        self.elements = elements
        self.queso_settings = queso_settings

        self.lagrange_dofs_required = False
        CoupledInterfacesSize = 0
        for condition_param in self.queso_settings.GetList("conditions_settings_list"):
            if( condition_param.GetString("condition_type") == "LagrangeSupportCondition" ):
                self.lagrange_dofs_required = True
            if( condition_param.GetString("condition_type") == "SurfaceLoadCondition" ):
                CoupledInterfacesSize += 1 # Count Shell-Solid coupled cases 

        nurbs_model_part = model.CreateModelPart("NurbsMesh")
        nurbs_model_part.AddNodalSolutionStepVariable(KM.DISPLACEMENT)
        nurbs_model_part.AddNodalSolutionStepVariable(KM.REACTION)
        nurbs_model_part.CreateSubModelPart("Dirichlet_BC")
        nurbs_model_part.CreateSubModelPart("Neumann_BC")
        for i in range(CoupledInterfacesSize): #Create new Model Part for each coupled case
            string_number = str(i+1)
            model_part_name = 'Neumann_BC' + "_" + string_number
            nurbs_model_part.CreateSubModelPart(model_part_name)

        if self.lagrange_dofs_required:
            nurbs_model_part.AddNodalSolutionStepVariable(KM.VECTOR_LAGRANGE_MULTIPLIER)
            nurbs_model_part.AddNodalSolutionStepVariable(IgaApplication.VECTOR_LAGRANGE_MULTIPLIER_REACTION)

        grid_settings = self.queso_settings["background_grid_settings"]
        #Override the NurbsGeometryModeler input parameters
        for modeler in analysis_parameters["modelers"].values():
            if modeler["modeler_name"].GetString() == "NurbsGeometryModeler":
                parameters = modeler["Parameters"]
                parameters.AddEmptyValue("lower_point_xyz")
                parameters["lower_point_xyz"].SetVector(grid_settings.GetDoubleVector("lower_bound_xyz"))
                parameters.AddEmptyValue("upper_point_xyz")
                parameters["upper_point_xyz"].SetVector(grid_settings.GetDoubleVector("upper_bound_xyz"))

                parameters.AddEmptyValue("lower_point_uvw")
                parameters["lower_point_uvw"].SetVector(grid_settings.GetDoubleVector("lower_bound_uvw"))
                parameters.AddEmptyValue("upper_point_uvw")
                parameters["upper_point_uvw"].SetVector(grid_settings.GetDoubleVector("upper_bound_uvw"))

                parameters.AddEmptyValue("polynomial_order")
                parameters["polynomial_order"].SetVector(grid_settings.GetIntVector("polynomial_order"))
                parameters.AddEmptyValue("number_of_knot_spans")
                parameters["number_of_knot_spans"].SetVector(grid_settings.GetIntVector("number_of_elements"))

        self.Initialized = False

        IgaModelPart = model.CreateModelPart("IgaModelPart")
        IgaModelPart.AddNodalSolutionStepVariable(KM.DISPLACEMENT)
        IgaModelPart.AddNodalSolutionStepVariable(KM.REACTION)
        
        CoupledSolidShellModelPart = model.CreateModelPart("CoupledSolidShellModelPart")
        CoupledSolidShellModelPart.CreateSubModelPart("CouplingInterface_1")
              
        super().__init__(model, analysis_parameters)

    def _ModelersSetupModelPart(self):
        """Override BaseClass to run NURBS modelers."""
        embedded_model_part = self.model.CreateModelPart('EmbeddedModelPart')
        embedded_model_part.AddNodalSolutionStepVariable(KM.DISPLACEMENT)
        embedded_model_part.AddNodalSolutionStepVariable(KM.REACTION)
        embedded_model_part.ProcessInfo.SetValue(KM.DOMAIN_SIZE, 3)
        filename = self.queso_settings["general_settings"].GetString("input_filename")
        self.triangle_mesh = QuESo_App.TriangleMesh()
        QuESo_App.IO.ReadMeshFromSTL(self.triangle_mesh, filename)
        ModelPartUtilities.ReadModelPartFromTriangleMesh(embedded_model_part, self.triangle_mesh)
        return super()._ModelersSetupModelPart()
        
    def ModifyInitialGeometry(self):
        """Override BaseClass to pass integration points to Kratos."""
        model_part = self.model.GetModelPart('NurbsMesh')
        ModelPartUtilities.RemoveAllElements(model_part)
        ModelPartUtilities.RemoveAllConditions(model_part)
        ModelPartUtilities.AddElementsToModelPart(model_part, self.elements)
        grid_settings = self.queso_settings["background_grid_settings"]
        bounds_xyz = [grid_settings.GetDoubleVector("lower_bound_xyz"),
                      grid_settings.GetDoubleVector("upper_bound_xyz")]
        bounds_uvw = [grid_settings.GetDoubleVector("lower_bound_uvw"),
                      grid_settings.GetDoubleVector("upper_bound_uvw")]
        ModelPartUtilities.AddConditionsToModelPart(model_part, self.boundary_conditions, bounds_xyz, bounds_uvw)

        print(model_part)

        # Add Dofs
        KM.VariableUtils().AddDof(KM.DISPLACEMENT_X, KM.REACTION_X, model_part)
        KM.VariableUtils().AddDof(KM.DISPLACEMENT_Y, KM.REACTION_Y, model_part)
        KM.VariableUtils().AddDof(KM.DISPLACEMENT_Z, KM.REACTION_Z, model_part)

        if self.lagrange_dofs_required:
            KM.VariableUtils().AddDof(KM.VECTOR_LAGRANGE_MULTIPLIER_X, IgaApplication.VECTOR_LAGRANGE_MULTIPLIER_REACTION_X, model_part)
            KM.VariableUtils().AddDof(KM.VECTOR_LAGRANGE_MULTIPLIER_Y, IgaApplication.VECTOR_LAGRANGE_MULTIPLIER_REACTION_Y, model_part)
            KM.VariableUtils().AddDof(KM.VECTOR_LAGRANGE_MULTIPLIER_Z, IgaApplication.VECTOR_LAGRANGE_MULTIPLIER_REACTION_Z, model_part)

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
    simulation.Initialize()
    Surf = simulation.model.GetModelPart("IgaModelPart").GetGeometry(2)
    #print("Show Global Coordinates of post process points")
    #print(Surf.GlobalCoordinates([21.6667 , 20 , 0]))
    #print(Surf.GlobalCoordinates([18.3333 , 0 , 0]))
    #print(Surf.GlobalCoordinates([28 , 20 , 0]))
    #print(Surf.GlobalCoordinates([28 , 0 , 0]))
    simulation.RunSolutionLoop()
    simulation.Finalize()

   
if __name__ == "__main__":
    main()
