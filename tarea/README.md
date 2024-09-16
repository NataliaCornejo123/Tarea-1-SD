# Para definir la cantidad de redis, existe una carpeta en donde existen
# los docker-compose.yml con una determinada cantidad de redis, para su uso
# se debe trasladar el archivo a la carpeta principal para que funcione todo,
# también se tiene que realizar la modificación en el "main.py" en donde
# se debe comentar el bloque de código que de las particiones. 

# (Se debe tener en cuenta que ambas cantidades deben ser la misma para que no 
# se generen errores). 

# COMANDOS A UTILIZAR

    sudo docker-compose up --build 

# Si se quiere cambiar se recomienza utilizar
    sudo docker-compose down 



