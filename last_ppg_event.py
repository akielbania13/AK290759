import arcpy
from math import sqrt, acos, pi
import pandas as pd

#FUNKCJE
#1. Dlugosc
def segment_length(point_1, point_2):
    return sqrt((point_1.X - point_2.X)**2 + (point_1.Y - point_2.Y)**2)

#2. Kat
def vertex_angle(point_1, point_2, point_3, object):

    side_a = segment_length(point_1, point_2)
    side_b = segment_length(point_2, point_3)
    side_c = segment_length(point_1, point_3)

    if round(side_a + side_b, 12) == round(side_c, 12):
        angle = 180
    else:
        angle = acos((side_a ** 2 + side_b ** 2 - side_c ** 2) / (2 * side_a * side_b)) * 180 / pi

        middle_point_c = arcpy.Point()
        middle_point_c.X = (point_1.X + point_3.X) / 2
        middle_point_c.Y = (point_1.Y + point_3.Y) / 2

        if intersect(middle_point_c, object):
            pass
        else:
            angle = 360 - angle

    return angle

#3. Czy wierzcholek jest wezlem sasiedztwa
def is_node(vertex, building, building_id, layer):
    arcpy.MakeFeatureLayer_management(layer, 'BUBD_lyr')
    arcpy.SelectLayerByLocation_management('BUBD_lyr', 'INTERSECT', building.buffer(1))

    expression = "gmlID <> " + "'" + building_id + "'"

    neighbour_count = 0
    matchcount = int(arcpy.GetCount_management('BUBD_lyr')[0])
    if matchcount == 0:
        pass
    else:
        for row in arcpy.da.SearchCursor('BUBD_lyr', ["SHAPE@"], where_clause=expression):
            polygon = arcpy.Polygon(row[0][0])
            if intersect(vertex, polygon):
                neighbour_count = neighbour_count + 1

    return neighbour_count

#4. Strzalka odleglosci
def deflection(vertex, line):
    return line.distanceTo(vertex)

#5. Przeciecie
def intersect(geom1, geom2):
    if geom1.disjoint(geom2):
        return False
    else:
        return True

#6. Fuknkcja minimalnych otoczek
def minimal_geometry(feature):
    arcpy.MinimumBoundingGeometry_management(feature, "D:\studia\mgr\semestr2\ppgII\egzamin\wyniki\Rectangle_By_Area.shp", "RECTANGLE_BY_AREA")
    arcpy.MinimumBoundingGeometry_management(feature, "D:\studia\mgr\semestr2\ppgII\egzamin\wyniki\Rectangle_By_Width.shp", "RECTANGLE_BY_WIDTH")
    arcpy.MinimumBoundingGeometry_management(feature, "D:\studia\mgr\semestr2\ppgII\egzamin\wyniki\Convex_Hull.shp", "CONVEX_HULL")
    arcpy.MinimumBoundingGeometry_management(feature, "D:\studia\mgr\semestr2\ppgII\egzamin\wyniki\Circle.shp", "CIRCLE")
    arcpy.MinimumBoundingGeometry_management(feature, "D:\studia\mgr\semestr2\ppgII\egzamin\wyniki\Envelope.shp", "ENVELOPE")

    arcpy.PolygonToLine_management("D:\studia\mgr\semestr2\ppgII\egzamin\wyniki\Rectangle_By_Area.shp","D:\studia\mgr\semestr2\ppgII\egzamin\wyniki\Rectangle_By_Area_Polyline.shp")
    arcpy.PolygonToLine_management("D:\studia\mgr\semestr2\ppgII\egzamin\wyniki\Rectangle_By_Width.shp", "D:\studia\mgr\semestr2\ppgII\egzamin\wyniki\Rectangle_By_Width_Polyline.shp")
    arcpy.PolygonToLine_management("D:\studia\mgr\semestr2\ppgII\egzamin\wyniki\Convex_Hull.shp", "D:\studia\mgr\semestr2\ppgII\egzamin\wyniki\Convex_Hull_Polyline.shp")
    arcpy.PolygonToLine_management("D:\studia\mgr\semestr2\ppgII\egzamin\wyniki\Circle.shp", "D:\studia\mgr\semestr2\ppgII\egzamin\wyniki\Circle_Polyline.shp")
    arcpy.PolygonToLine_management("D:\studia\mgr\semestr2\ppgII\egzamin\wyniki\Envelope.shp", "D:\studia\mgr\semestr2\ppgII\egzamin\wyniki\Envelope_Polyline.shp")

    list = ["D:\studia\mgr\semestr2\ppgII\egzamin\wyniki\Rectangle_By_Area_Polyline.shp", "D:\studia\mgr\semestr2\ppgII\egzamin\wyniki\Rectangle_By_Width_Polyline.shp", "D:\studia\mgr\semestr2\ppgII\egzamin\wyniki\Convex_Hull_Polyline.shp", "D:\studia\mgr\semestr2\ppgII\egzamin\wyniki\Circle_Polyline.shp", "D:\studia\mgr\semestr2\ppgII\egzamin\wyniki\Envelope_Polyline.shp"]

    geometry_polyline_list = []

    for i in list:
        for row in arcpy.da.SearchCursor(i, ["SHAPE@"]):
            geometry_polyline_list.append(row[0])

    return geometry_polyline_list

arcpy.env.overwriteOutput = 1

#CHARAKTERYSTYKA STATYSTYCZNA WIERZCHOLKOW BUDYNKU
path = r"D:\studia\mgr\semestr2\ppgII\egzamin\BUBD.shp"

building_gmlid = []
vertex_number = []
lgth_in = []
lgth_out = []
angles_in = []
deflection_to_side_area = []
deflection_to_side_width = []
deflection_to_side_convex_hull = []
deflection_to_side_circle = []
deflection_to_side_envelope = []

#Zad.1: Podanie id budynku
#building_id = raw_input("Put building ID (gmlId): ")

for row in arcpy.da.SearchCursor(path, ["SHAPE@", "gmlId"]):
    single_building_geom = row[0][0]
    min_geom_list = minimal_geometry(row[0])

    vertex_num = -1
    if None in single_building_geom:
        divide_index = list(single_building_geom).index(None)
        building_contour = single_building_geom[0:divide_index]

        for pnt in building_contour[:-1]:
            middle_vertex = pnt
            #Zad.2 numer wierzcholka
            vertex_num += 1
            previous_vertex = building_contour[:-1][vertex_num - 1]
            next_vertex = building_contour[vertex_num + 1]

            #Zad.3 dlugosc segmentu przed
            length_in = segment_length(previous_vertex, middle_vertex)
            #Zad.4 dlugosc segmentu po
            length_out = segment_length(middle_vertex, next_vertex)
            #Zad.5 kat wewnetrzny
            angle_in = vertex_angle(previous_vertex, middle_vertex, next_vertex, arcpy.Polygon(single_building_geom))
            #Zad.6 strzalka do boku rectangle_by_area
            deflection_to_rectangle_by_area = deflection(middle_vertex, min_geom_list[0])
            #Zad.7 strzalka do boku rectangle_by_width
            deflection_to_rectangle_by_width = deflection(middle_vertex, min_geom_list[1])
            #Zad.8 strzalka do boku convex_hull
            deflection_to_convex_hull = deflection(middle_vertex, min_geom_list[2])
            #Zad.9 strzalka do boku circle
            deflection_to_circle = deflection(middle_vertex, min_geom_list[3])
            #Zad.10 strzalka do boku envelope
            deflection_to_envelope = deflection(middle_vertex, min_geom_list[4])

            building_gmlid.append(row[1])
            vertex_number.append(vertex_num)
            lgth_in.append(length_in)
            lgth_out.append(length_out)
            angles_in.append(angle_in)
            deflection_to_side_area.append(deflection_to_rectangle_by_area)
            deflection_to_side_width.append(deflection_to_rectangle_by_width)
            deflection_to_side_convex_hull.append(deflection_to_convex_hull)
            deflection_to_side_circle.append(deflection_to_circle)
            deflection_to_side_envelope.append(deflection_to_envelope)

        interior_rings = single_building_geom[divide_index + 1:]

        rings_list = []
        if None in interior_rings:
            while None in interior_rings:
                division_index = list(interior_rings).index(None)
                interior_ring = interior_rings[:division_index]
                rings_list.append(interior_ring)
                interior_rings = interior_rings[division_index + 1:]
                if None in interior_rings:
                    pass
                else:
                    rings_list.append(interior_rings)
        else:
            rings_list.append(interior_rings)

        for ring in rings_list:
            vertex_num = -1
            for pnt in ring[:-1]:

                middle_vertex = pnt
                vertex_num += 1
                previous_vertex = ring[:-1][vertex_num - 1]
                next_vertex = ring[vertex_num + 1]

                length_in = segment_length(previous_vertex, middle_vertex)
                length_out = segment_length(middle_vertex, next_vertex)
                angle_in = vertex_angle(previous_vertex, middle_vertex, next_vertex, row[0])

                deflection_to_rectangle_by_area = deflection(middle_vertex, min_geom_list[0])
                deflection_to_rectangle_by_width = deflection(middle_vertex, min_geom_list[1])
                deflection_to_convex_hull = deflection(middle_vertex, min_geom_list[2])
                deflection_to_circle = deflection(middle_vertex, min_geom_list[3])
                deflection_to_envelope = deflection(middle_vertex, min_geom_list[4])

                building_gmlid.append(row[1])
                vertex_number.append(vertex_num)
                lgth_in.append(length_in)
                lgth_out.append(length_out)
                angles_in.append(angle_in)
                deflection_to_side_area.append(deflection_to_rectangle_by_area)
                deflection_to_side_width.append(deflection_to_rectangle_by_width)
                deflection_to_side_convex_hull.append(deflection_to_convex_hull)
                deflection_to_side_circle.append(deflection_to_circle)
                deflection_to_side_envelope.append(deflection_to_envelope)

    else:
        for pnt in single_building_geom[:-1]:

            middle_vertex = pnt
            vertex_num += 1
            previous_vertex = single_building_geom[:-1][vertex_num - 1]
            next_vertex = single_building_geom[vertex_num + 1]

            length_in = segment_length(previous_vertex, middle_vertex)
            length_out = segment_length(middle_vertex, next_vertex)
            angle_in = vertex_angle(previous_vertex, middle_vertex, next_vertex, row[0])

            deflection_to_rectangle_by_area = deflection(middle_vertex, min_geom_list[0])
            deflection_to_rectangle_by_width = deflection(middle_vertex, min_geom_list[1])
            deflection_to_convex_hull = deflection(middle_vertex, min_geom_list[2])
            deflection_to_circle = deflection(middle_vertex, min_geom_list[3])
            deflection_to_envelope = deflection(middle_vertex, min_geom_list[4])

            building_gmlid.append(row[1])
            vertex_number.append(vertex_num)
            lgth_in.append(length_in)
            lgth_out.append(length_out)
            angles_in.append(angle_in)
            deflection_to_side_area.append(deflection_to_rectangle_by_area)
            deflection_to_side_width.append(deflection_to_rectangle_by_width)
            deflection_to_side_convex_hull.append(deflection_to_convex_hull)
            deflection_to_side_circle.append(deflection_to_circle)
            deflection_to_side_envelope.append(deflection_to_envelope)



d = {'ID_budynku': building_gmlid, 'Wierzcholek': vertex_number, 'Dlugosc_przed': lgth_in, 'Dlugosc_po': lgth_out, 'Kat_wewnetrzny': angles_in, 'Strzalka_do_boku_RECTANGLE_BY_AREA': deflection_to_side_area, 'Strzalka_do_boku_RECTANGLE_BY_WIDTH': deflection_to_side_width, 'Strzalka_do_boku_CONVEX_HULL': deflection_to_side_convex_hull, 'Strzalka_do_boku_CIRCLE': deflection_to_side_circle, 'Strzalka_do_boku_ENVELOPE': deflection_to_side_envelope}
df = pd.DataFrame(data=d)
df.to_csv('D:\studia\mgr\semestr2\ppgII\egzamin\wyniki\Results.csv', index=False)
