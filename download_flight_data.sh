#!/bin/bash

url="https://www.aerocivil.gov.co/atencion/estadisticas-de-las-actividades-aeronauticas/Estadsticas%20operacionales/Estad%C3%ADsticas%20de%20Oferta%20y%20Demanda%20-%20Transporte%20Pasajeros%20Enero%202023.xlsx"
file_name="data/vuelos-enero-2023.xlsx"

# Download the file
wget -O "$file_name" "$url"
    
# Check if the download was successful
if [ $? -eq 0 ]; then
    echo "Successfully downloaded $file_name"
else
    echo "Failed to download $file_name"
fi
