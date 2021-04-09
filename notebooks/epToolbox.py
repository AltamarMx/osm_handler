from pandas import *
from datetime import timedelta
from io import open
import json
import pandas as pd

    
def exportMaterials(filename, materials):
    br = open(filename, "r")
    osm = br.readlines()
    br.close()
    i = 0
    while (i < len(osm)):
        if("OS:Material," in osm[i]):
            material = materials.loc[osm[i+2].split(',')[0][2:]]
            setOsmObject(osm, i, material)
        i += 1
    br = open(filename, "w")
    for line in osm:
        br.write(line)
    br.close()
    return True

    
        
def importMaterials(filename):
    br = open(filename, "r")
    osm = br.readlines()
    i = 0
    materials = []
    materiales = {}   # este es el nuevo diccionario que ir'a creciendo
#     osm_sin = open
    while (i < len(osm)):
        if("OS:Material," in osm[i]):
            i, material,nuevo = getOsmObject(osm, i)  # ahora regresa tres argumentos, el tercero el dic
            materiales.update(nuevo)  #actualiza el diccionario materiales con el nuevo encontrado
#             print(nuevo)
            materials.append(material)
        i += 1
    br.close()
    materials = pd.DataFrame(materials)
    materials.index = materials["Name"]
    return materials,materiales   # regresa ahora el diccionario materiales

def getOsmObject(list, index):
    object = {}
    index += 1
    while list[index] != "\n":
        if (',' in list[index]):
            sep = ','
        else:
            sep = ';'
        name = list[index].split(sep)[1]
        name = name.split('!')[1][2:]
        name = name.split('\n')[0]

        object[name] = getValue(list[index].split(sep)[0][2:])
        index += 1
    nombre = object["Name"]  #extrae el nombre del material para definir diccionario
    nuevo_dic = {nombre:object}  # crea nuevo diccionario con el nombre del material
    return index, object,nuevo_dic  # regresa nuevo diccionario

def getValue(strvalue):
    try:
        value = float(strvalue)
        if ("." not in strvalue):
            value = int(value)
    except ValueError:
        value = strvalue
    return value

def adjustTimestamp(strDate, year="2020"):
    strDate = year + "/" + strDate.strip()
    wDate = strDate.split()[0]
    wTime = strDate.split()[1]
    tsDate = to_datetime(wDate, format="%Y/%m/%d")
    wHour = int(wTime.split(":")[0])
    wMin = int(wTime.split(":")[1])
    if (wHour > 23):
        wHour = 0
        tsDate += timedelta(days=1)
    tsDate = tsDate.replace(hour=wHour, minute=wMin)
    return tsDate

def getEPVariables(filename):
    datainfo = read_csv(filename)
    datainfo["Date/Time"] = datainfo["Date/Time"].apply(lambda x: adjustTimestamp(x))
    datainfo.rename(columns={"Date/Time":"Timestamp"}, inplace=True)
    datainfo.set_index("Timestamp",drop=True,inplace=True)
    return datainfo

def getValue(strvalue):
    try:
        value = float(strvalue)
        if ("." not in strvalue):
            value = int(value)
    except ValueError:
        value = strvalue
    return value

 
def setOsmObject(list, index, object):
    index += 1
    for name, value in object.items():
        if str(value)=="nan":
          break
        if (',' in list[index]):
            sep = ','
        else:
            sep = ';'
        list[index] = "  " + str(value) + sep + "!- " + name + "\n"
        index += 1
    return True
