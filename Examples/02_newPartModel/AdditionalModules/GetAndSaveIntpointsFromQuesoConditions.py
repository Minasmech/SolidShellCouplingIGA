import vtk
import numpy as np

def GetNormalFromQuesoConditions(condition):
    Normals= []
    for condition_segment in condition.GetSegments():
        triangle_mesh_segment = condition_segment.GetTriangleMesh()
        num_triangles = triangle_mesh_segment.NumOfTriangles()
        for tri_id in range(num_triangles):
            integration_method = 0
            global_points = triangle_mesh_segment.GetIntegrationPointsGlobal(tri_id, integration_method)
            for point in global_points:
                normal = point.Normal()
                Normals.append([normal[0],normal[1],normal[2],point[0],point[1],point[2]],)
    
    return Normals

def GetIntergrationPointsFromQuesoConditions(condition):
    IntegrationPoints = []
    condition_settings = condition.GetSettings()
    condition_id = condition_settings.GetInt("condition_id")
    for condition_segment in condition.GetSegments():
        triangle_mesh_segment = condition_segment.GetTriangleMesh()
        num_triangles = triangle_mesh_segment.NumOfTriangles()
        for tri_id in range(num_triangles):
            integration_method = 0
            global_points = triangle_mesh_segment.GetIntegrationPointsGlobal(tri_id, integration_method)
            for point in global_points:
                IntegrationPoints.append([point[0],point[1],point[2]])
                
    return IntegrationPoints 

def SavePointsToVTK(points, filename):
    # Create a vtkPoints object and add the points
    vtk_points = vtk.vtkPoints()
    for point in points:
        vtk_points.InsertNextPoint(point)

    # Create a vtkPolyData object and set the points
    polydata = vtk.vtkPolyData()
    polydata.SetPoints(vtk_points)

    # Create a vtkVertexGlyphFilter to create vertices from the points
    vertex_filter = vtk.vtkVertexGlyphFilter()
    vertex_filter.SetInputData(polydata)
    vertex_filter.Update()

    # Create a vtkPolyDataWriter and write the data to a VTK file
    writer = vtk.vtkPolyDataWriter()
    writer.SetFileName(filename)
    writer.SetInputConnection(vertex_filter.GetOutputPort())
    writer.Write()

    print(f"VTK file '{filename}' has been written.")

def write_vtk_file(input_filename, output_filename):
    # Read points from the input file
    points = []
    with open(input_filename, 'r') as input_file:
        for line in input_file:
            parts = line.split()
            if len(parts) == 3:
                try:
                    x, y, z = map(float, parts)
                    points.append((x, y, z))
                except ValueError:
                    print(f"Skipping invalid line: {line.strip()}")

    # Write the VTK file
    with open(output_filename, 'w') as output_file:
        output_file.write("# vtk DataFile Version 3.0\n")
        output_file.write("Vertices example\n")
        output_file.write("ASCII\n")
        output_file.write("DATASET POLYDATA\n")
        output_file.write(f"POINTS {len(points)} double\n")

        for point in points:
            output_file.write(f"{point[0]} {point[1]} {point[2]}\n")

    print(f"VTK file written successfully: {output_filename}")

def SaveVectorsToTXT(vectors, filename):
    with open(filename, 'w') as file:
        for vector in vectors:
            # Write each vector and point as a line in the file
            line = ' '.join(map(str, vector))
            file.write(line + '\n')

if __name__ == "__main__":
    # Example usage
    input_filename = "Intergration_Points_on_Solid_Coupling_Surface.txt"  # Replace with your input file name
    output_filename = "Intergration_Points_on_Solid_Coupling_Surface.vtk"
    write_vtk_file(input_filename, output_filename)