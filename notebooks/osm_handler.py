import pandas as pd
from io import open
import json as json
import re
import numpy as np
import pickle
import os


def update_osm(file1,file2,new_file):
    with open(file1,"r") as f1:
        data1 = f1.read()
    with open(file2,"r") as f2:
        data2 = f2.read()
    data1 += "\n"
    data1 += data2

    with open (new_file, 'w') as fp:
        fp.write(data1)
    print("saved file:",new_file)    
    
def save_rest_osm(lista,file="rest.osm"):
    with open(file,"w") as f:
        for renglon in lista:
            for campo in renglon:
#                 print(campo)
                f.write(campo)
    print("saved:",file)
def open_osm(file): 
    archivo = open(file,"r")
    osm = archivo.readlines()
    return osm
    
def save_dict(file,dictionary):
    '''Write object to a JSON  file.
    Parameters
    ----------
    file : str or file handle to save json file
    with the dictionary.
    dictionary  : Python dictionary obtained with get_dictionary_material

    '''
    archivo = open(file, "w")
    json.dump(dictionary,archivo,indent=2)
    print("saved:",file)
    archivo.close()

def read_osm(file):
    tmp = open(file,"r")
    osm = tmp.readlines()
    return osm

def get_dictionary_material(file):
    '''Returns a dictionary containing the materials from the OSM file given
    
    Parameters
    ----------
    file : str
            The file location of the OSM file 
    Returns
    -------
    dictionary 
        dictionary containing the materials of the OSM file
    
    '''
    osm = open_osm(file)
    OSM_OBJETO = "OS:Material,\n"
    # identifica donde inicia un objeto y donde 
    # termina, y los pone en una lista    
    objeto = []
    coma   = []
    for i,renglon in enumerate(osm):
        if renglon.startswith("OS:"): #localiza el inicio de un objeto
            objeto.append(i-1)
        if ";" in renglon:  #localiza el final de un objeto
            coma.append(i+1)
#     en os_lista, guarda donde inicia y termina cada objeto
    osm_lista = []
    for i,j in zip(objeto,coma):
        osm_lista.append(osm[i:j])
# separa en dos listas, lista objeto y resto del osm
    objeto_lista = []
    resto_lista  = []
    for objeto in osm_lista:
#         print(objeto)
        if OSM_OBJETO in objeto:
            objeto_lista.append(objeto)
        else:
#             print(objeto)
            resto_lista.append(objeto)
# #             Limpia la lista que contiene el objeto
    lista_objetos = []
    for objeto in objeto_lista:
        objeto.pop(0)
        objeto.pop(-1)
#         print(objeto)
        
        lista_objeto = []
        objeto[0]= objeto[0].replace(",","")
#         print(objeto[1])
        for campo in objeto:
            lista_objeto.append(campo.replace("\n","").
                                 replace("","").
# #                                  replace("{","").
# #                                  replace("}","").
                                 replace("!- ","").
                                 strip())
        lista_objetos.append(lista_objeto)
#         print(lista_objetos)
    diccionario = {}
    for objeto in lista_objetos:
        nombre_objeto,_ = objeto[2].split(",")
        tmp = {"Handle":"texto",
               "Name":"nombre",
               "Roughness":"MediumRough",
               "Thickness {m}":0.1,
               "Conductivity {W/m-K}":0.1,
               "Density {kg/m3}":0.1,
               "Specific Heat {J/kg-K}":100.,
               "Thermal Absorptance":0.9,
               "Solar Absorptance":0.7,
               "Visible Absorptance":0.7}
        for propiedad in range(1,len(objeto)):
            valor,nombre = objeto[propiedad].split(",")
            try:
                valor = float(valor)
            except:
                pass
            tmp.update({nombre:valor})
        diccionario.update({nombre_objeto:tmp})
# diccionario
#     if kind=="dict":
#         return diccionario
#     if kind=="list":
    return diccionario
def load_dict(file):
    '''Returns a dictionary loaded from JSON file
    Parameters
    ----------
    file : File handle to OPEN json file
    with the dictionary.
    
    Returns
    -------
    dictionary 
        dictionary containing the JSON file of the OSM file

    '''
    with open(file) as json_file:
        dictionary = json.load(json_file)
    return dictionary

    
def save_material_osm(file,new_dict):
    objeto_archivo = []
    lista = ["Handle","Name","Roughness","Thickness {m}",
             "Conductivity {W/m-K}","Density {kg/m3}",
             "Specific Heat {J/kg-K}","Thermal Absorptance",
             "Solar Absorptance","Visible Absorptance"]
    for objeto in new_dict:
        cadena1 ="OS:Material,\n"
        objeto_archivo.append(cadena1)
        lista2 = lista[:-1]
        for propiedad in lista2:
    #         print(propiedad)
            cadena2 ="  " + str(new_dict[objeto][propiedad])+",!- "+str(propiedad+"\n")
            objeto_archivo.append(cadena2)

#         cadena3 ="  " + str(new_dict[objeto][lista[-1]])+";!- "+str("Visible Absorptance")
        cadena3 ="  " + str(new_dict[objeto]["Visible Absorptance"])+";!- "+str("Visible Absorptance")
    #     print(lista[-1])
        objeto_archivo.append(cadena3)
        objeto_archivo.append("\n")
        objeto_archivo.append("\n")
    save_rest_osm(objeto_archivo,file="material.osm")
    
def save_osm(file_osm,diccionario,new_osm):
    '''
    Remove materiales from file_osm and writes diccionario to new_osm file.

    Parameters
    ----------
    file_osm    : Original osm to extract materials contained
    diccionario : Materials dictionary to be added to new_osm
    new_osm     : Path and name for new OSM with diccionario included as materials
    
    '''

    resto_osm = separate_osm(file_osm)
    save_rest_osm(resto_osm)
    save_material_osm("material.osm",diccionario)
    update_osm("rest.osm","material.osm",new_osm)
    
#     return resto_osm




def separate_osm(file):
    osm = open_osm(file)
    OSM_OBJETO = "OS:Material,\n"
    objeto = []
    coma   = []
    for i,renglon in enumerate(osm):
        if renglon.startswith("OS:"): #localiza el inicio de un objeto
            objeto.append(i-1)
        if ";" in renglon:  #localiza el final de un objeto
            coma.append(i+1)
    osm_lista = []
    for i,j in zip(objeto,coma):
        osm_lista.append(osm[i:j])
    objeto_lista = []
    resto_lista  = []
    for objeto in osm_lista:
        if OSM_OBJETO in objeto:
            objeto_lista.append(objeto)
        else:
            resto_lista.append(objeto)
    return resto_lista