import requests
import pandas as pd
import random
import time
import grpc
import dns_pb2
import dns_pb2_grpc

# Cargar el dataset CSV
df = pd.read_csv('dataset_limit.csv', header=None)

# URL base de la API
api_url = 'http://app:8000/text/'

# Realizar 75,000 consultas
for _ in range(75000):
    # Seleccionar un dominio aleatorio del dataset
    domain = random.choice(df[0])  # Selecciona un dominio de la columna 0
    
    try:
        # Realizar la consulta GET a la API
        response = requests.get(f'{api_url}{domain}', timeout=5)  # Tiempo de espera de 5 segundos
        
        # Verificar si la respuesta fue exitosa (código de estado 200)
        if response.status_code == 200:
            # Intentar decodificar la respuesta como JSON
            try:
                data = response.json()
                print(data)  # Imprimir la respuesta decodificada
            except requests.exceptions.JSONDecodeError:
                print("Error: La respuesta no es JSON válida")
        else:
            print(f"Error: La API devolvió el código de estado {response.status_code}")
    
    except requests.exceptions.Timeout:
        print("Error: La solicitud excedió el tiempo de espera")
    
    except requests.exceptions.RequestException as e:
        print(f"Error en la solicitud: {e}")
    
    # Retrasar un poco las consultas para no sobrecargar el servidor
    time.sleep(0.01)  # Esperar 10 milisegundos entre consultas
