import pandas as pd
from io import open
#2021/06/16 eapuertoc: Si no se pone un alias no es necesario el "as json"
import json
import re
import numpy as np
import pickle
import os


def __open_osm(osm_file):
    """Read an OSM file and save contents in a list
    
    Parameters:
    -----------
    osm_file -- File with OSM format
    
    Returns:
    --------
    osm -- list with lines of the read file
    """
    archivo = open(osm_file,"r")
    osm = archivo.readlines()
    archivo.close()
    return osm

def __objects_to_list(osm):
    """Converts a list with OSM contents in a list with lists of every object and another list with the types of these objects
    
    Parameters:
    -----------
    osm --  osm list
    
    Returns:
    --------
    objects_in_lists -- list with lists of every object in the osm list
    objType_list -- list with the types of objects within the osm list
    """
    objeto = []
    objType_list = [] #Nuevo elemento incluido para guardar tipos de objetos contenidos
    coma   = []
    for i,renglon in enumerate(osm):
        if renglon.startswith("OS:"): #localiza el índice del inicio de un objeto
            typeobj = renglon.split(":")[1].split(",")[0]
            if typeobj not in objType_list: #Si el tipo no está incluido se añade a la lista
                objType_list.append(typeobj)
            objeto.append(i)
        if ";" in renglon:  #localiza índice del final de un objeto
            coma.append(i)
    objects_in_lists = []
    for i,j in zip(objeto,coma): 
        objects_in_lists.append(osm[i:j+1]) # el +1 porque las listas no son inclusivas
    return objects_in_lists, objType_list 

        
def __separate_objects_rest(osm_list, objKey):
    #2021/06/16 eapuertoc: Acá se cambia para que separe cualquier objeto basado en el nombre clave
    """Create two lists based on an osm list: one with the object key and other with the rest ones
    
    Parameters:
    -----------
    osm_file -- File with OSM format
    objKey -- Key of the reference object to separate
    
    Returns:
    --------
    object_list -- list with the elements of the object extracted
    rest_list -- list with the rest of the elements
    """
    OSM_OBJETO = "OS:" + objKey + ",\n"
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
#     print(object_list[0])
    for objeto in object_list:
        object_cleaned = []
        objeto[0]= objeto[0].replace(",","")
        for campo in objeto:
            object_cleaned.append(campo.replace("\n","").
#                                        replace("","").
                                       replace("!- ","").
#                                        replace(" ","").
                                       strip())
        object_list_cleaned.append(object_cleaned)
#     print(object_list_cleaned[0])
    return(object_list_cleaned)
 
def __create_dictionary(object_list_cleaned, objKey):
    #2021/06/16 eapuertoc: Ajuste temporal, es necesario pensar en un archivo de validación para generalizar el programa
    diccionario = {}
    for objeto in object_list_cleaned:
        #2021/06/16 eapuertoc: Temporalmente el código sólo trabaja con la clave "Material"
        if (objKey == "Material"):
            nombre_objeto,_ = objeto[2].split(",")
#           print("nombre",len(nombre_objeto),nombre_objeto)
            tmp = {
                "Handle":"texto",
                "Name":"nombre",
                "Roughness":"MediumRough",
                "Thickness {m}":0.1,
                "Conductivity {W/m-K}":0.1,
                "Density {kg/m3}":0.1,
                "Specific Heat {J/kg-K}":100.,
                "Thermal Absorptance":0.9,
                "Solar Absorptance":0.7,
                "Visible Absorptance":0.7,
                "Comments":""}
                #print(objeto)
            for propiedad in range(1,len(objeto)-1):
                #print(propiedad)
                valor,nombre = objeto[propiedad].split(",")
                valor = valor.strip()
                nombre = nombre.strip()
                #print("valor",valor)
                #print("nombre",nombre)
                try:
                    valor = float(valor)
                except:
                    pass
                tmp.update({nombre:valor})
            #print(valor,nombre)
            valor,nombre = objeto[-1].split(";")
            valor  = valor.strip()
            nombre = nombre.strip()
            try:
                valor = float(valor)
            except:
                pass
            tmp.update({nombre:valor})
            diccionario.update({nombre_objeto:tmp}) 
            #Borra el Handle antes de entregar el diccionario
    return diccionario


def save_dict(file,dictionary, handle=False):
    """Write object to a JSON  file.
    Parameters
    ----------
    file -- str or file handle to save json file with the dictionary.
    dictionary -- Python dictionary obtained with get_dictionary_material
    handle -- False, writes dictionary without handle
    """
    if handle:
        archivo = open(file, "w")
        json.dump(dictionary,archivo,indent=2)
        print("saved:",file)
        archivo.close()
    else:
        for material in dictionary:
            try:
                dictionary[material].pop("Handle")
            except:
                pass
        archivo = open(file, "w")
        json.dump(dictionary,archivo,indent=2)
        print("saved:",file)
        archivo.close()


def load_dict(file, format="json", objKey=""):
    #2021/06/16 eapuertoc: Se extiende el uso para cargar dictionary de cualquier objeto y de archivos epJSON
    """Returns a dictionary loaded from JSON file
    Parameters:
    ----------
    file -- File handle to OPEN json file with the dictionary.
    format -- Indicates the format of the file loaded
    objKey -- Key of a specified object to extract
    
    Returns:
    -------
    dictionary -- dictionary containing the data of the specified file
    """
    dictionary = {}
    if (format == "json"):
        with open(file) as json_file:
            dictionary = json.load(json_file)
    elif (format == "epjson"):
        with open(file) as json_file:
            if (objKey == ""):
                dictionary = json.load(json_file)
            else:
                dictionary = json.load(json_file)[objKey]
    elif (format == "osm"):
        osm      = __open_osm(file)
        osm_list = __objects_to_list(osm)[0]
        if (objKey != ""):
            object_list, rest_list  = __separate_objects_rest(osm_list, objKey)
            object_list = __clean_objects(object_list)
            #rest_list   = __clean_objects(rest_list)
            dictionary = __create_dictionary(object_list, objKey)
    return dictionary

def update_dict(old_dict, new_dict):
    for material in new_dict.keys():
        for propiedad in new_dict[material].keys():
            old_dict[material][propiedad] = new_dict[material][propiedad]
    return old_dict


# def update_dict(old_dict,nuevo_dict):
    
#     old_dict.update(nuevo_dict)
#     return old_dict


def __save_rest_osm(lista,file="tmp.osm"):
    with open(file,"w") as f:
        for renglon in lista:
            for campo in renglon:
#                 print(campo)
                f.write(campo)
    print("saved:",file)

def __save_dict_osm(new_dict):
#     print(type(new_dict))
    objeto_archivo = []
    materiales = list(new_dict.keys())
    lista = list( new_dict[materiales[0]].keys())
#     print(lista)                      
#     lista  = ["Name","Roughness","Thickness {m}",
#              "Conductivity {W/m-K}","Density {kg/m3}",
#              "Specific Heat {J/kg-K}","Thermal Absorptance",
#              "Solar Absorptance","Visible Absorptance"]
    for objeto in new_dict:
        cadena1 ="OS:Material,\n"
        objeto_archivo.append(cadena1)
        lista2 = lista[:-2]
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
    __save_rest_osm(objeto_archivo,file="tmp2.osm")


def __merge_osm(new_file,file1="tmp.osm",file2="tmp2.osm"):
    
    with open(file1,"r") as f1:
        data1 = f1.read()
    with open(file2,"r") as f2:
        data2 = f2.read()
    data1 += "\n"
    data1 += data2

    with open (new_file, 'w') as fp:
        fp.write(data1)
    print("saved file:",new_file)   
    
def update_osm(osm_file,new_dict,delete=True,new_file="actualizado.osm", objKey=""):
    osm      = __open_osm(osm_file)
    osm_list = __objects_to_list(osm)[0]
    object_list, rest_list  = __separate_objects_rest(osm_list, objKey)
    object_list = __clean_objects(object_list)
#     rest_list   = __clean_objects(rest_list)
    diccionario = __create_dictionary(object_list, objKey)
    diccionario = update_dict(diccionario,new_dict)
    __save_rest_osm(rest_list)
    __save_dict_osm(diccionario)
    __merge_osm(new_file)
    if delete:
        os.remove("tmp.osm")
        os.remove("tmp2.osm")
        print("archivos tmp.osm y tmp2.osm borrados\n")
        
    
    
    
    
    
    
    
    
    