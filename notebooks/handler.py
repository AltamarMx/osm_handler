import pandas as pd
from io import open
import json as json
import re
import numpy as np
import pickle
import os


def __open_osm(osm_file): 
    archivo = open(osm_file,"r")
    osm = archivo.readlines()
#     print(osm)
    return osm
def __objects_to_list(osm):
    objeto = []
    coma   = []
    for i,renglon in enumerate(osm):
        if renglon.startswith("OS:"): #localiza el inicio de un objeto
            objeto.append(i)
        if ";" in renglon:  #localiza el final de un objeto
            coma.append(i)
    osm_lista = []
    for i,j in zip(objeto,coma):
        
        osm_lista.append(osm[i:j+1]) # el +1 porque las listas no son inclusivas
    return osm_lista    

def __separate_objects_rest(osm_list):

    OSM_OBJETO = "OS:Material,\n"
    object_list = []
    rest_list   = []
    for objeto in osm_list:
        if OSM_OBJETO in objeto:
            object_list.append(objeto)
        else:
            rest_list.append(objeto)
    return object_list, rest_list


def __clean_objects(object_list):
    object_list_cleaned = []
    for objeto in object_list:
        object_cleaned = []
        objeto[0]= objeto[0].replace(",","")
#         print(objeto[1])
        for campo in objeto:
            object_cleaned.append(campo.replace("\n","").
#                                        replace("","").
                                       replace("!- ","").
#                                        replace(" ","").
                                       strip())
        object_list_cleaned.append(object_cleaned)
    return(object_list_cleaned)
    
def load_dictionary(osm_file):
    osm      = __open_osm(osm_file)
    osm_list = __objects_to_list(osm)
    object_list, rest_list  = __separate_objects_rest(osm_list)
    object_list = __clean_objects(object_list)
    rest_list   = __clean_objects(rest_list)
#     print(object_list)
    return object_list,rest_list
    
#     return osm_list
#     print(osm)
#     return osm

    
    