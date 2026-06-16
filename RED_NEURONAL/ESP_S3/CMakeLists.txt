# Archivo raiz de build de ESP-IDF: carga el sistema de build del framework
# (toma la ruta desde la variable de entorno IDF_PATH) y declara el nombre
# del proyecto. El contenido real del firmware esta en main/main.c.
cmake_minimum_required(VERSION 3.16)
include($ENV{IDF_PATH}/tools/cmake/project.cmake)
project(wifi_verificacion)
