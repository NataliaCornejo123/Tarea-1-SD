from fastapi import FastAPI, HTTPException
import redis
import grpc
import dns_pb2
import dns_pb2_grpc
import logging

app = FastAPI(debug=True)

# Configuración de logging
logging.basicConfig(level=logging.INFO)

# Conexiones a múltiples instancias de Redis
# ESCENARIO 1 CON UNA PARTICIÓN
redis_clients = [
   redis.Redis(host='redis1', port=6379, decode_responses=True),
]

# Otras configuraciones (comenta/descomenta según sea necesario)
# 2 PARTICIONES
# redis_clients = [
#    redis.Redis(host='redis1', port=6379, decode_responses=True),
#    redis.Redis(host='redis2', port=6380, decode_responses=True),
# ]

# 4 PARTICIONES
# redis_clients = [
#    redis.Redis(host='redis1', port=6379, decode_responses=True),
#    redis.Redis(host='redis2', port=6380, decode_responses=True),
#    redis.Redis(host='redis3', port=6381, decode_responses=True),
#    redis.Redis(host='redis4', port=6382, decode_responses=True),
# ]

# Contadores globales de hits y misses
hits = 0
misses = 0

# Función para seleccionar el cliente Redis adecuado basado en el dominio
def get_redis_client(key: str):
    index = hash(key) % len(redis_clients)
    return redis_clients[index]

# Función para agregar una IP a Redis
def add_text_to_redis(key: str, value: str):
    try:
        client = get_redis_client(key)
        client.set(key, value)
        logging.info(f"Valor agregado a Redis: {key} -> {value}")
    except redis.RedisError as e:
        # Manejar error de Redis
        logging.error(f"Error al agregar valor a Redis: {e}")
        raise HTTPException(status_code=500, detail=f"Error al interactuar con Redis: {str(e)}")

# Función para obtener una IP desde Redis
def get_text_from_redis(key: str):
    try:
        client = get_redis_client(key)
        value = client.get(key)
        logging.info(f"Valor obtenido de Redis para {key}: {value}")
        return value
    except redis.RedisError as e:
        # Manejar error de Redis
        logging.error(f"Error al obtener valor de Redis: {e}")
        raise HTTPException(status_code=500, detail=f"Error al interactuar con Redis: {str(e)}")

# Función para resolver un dominio con gRPC
def resolve_domain_with_grpc(domain: str):
    try:
        logging.info(f"Resolviendo dominio con gRPC: {domain}")
        with grpc.insecure_channel('localhost:50051') as channel:
            stub = dns_pb2_grpc.DNSResolverStub(channel)
            response = stub.Resolve(dns_pb2.ResolveRequest(domain=domain))
            logging.info(f"IP resuelta con gRPC para {domain}: {response.ip}")
            return response.ip
    except grpc.RpcError as e:
        # Manejar error de gRPC
        logging.error(f"Error al resolver dominio con gRPC: {e}")
        raise HTTPException(status_code=500, detail=f"Error al resolver dominio con gRPC: {str(e)}")

# Endpoint para consultar un dominio y contar hits/misses
@app.get('/text/{text}')
def get_text(text: str):
    global hits, misses
    try:
        # Obtener valor de Redis (hit)
        cached_value = get_text_from_redis(text)
        
        if cached_value:
            hits += 1
            logging.info(f"HIT: {text} -> {cached_value}")
            return {"retrieved_value": cached_value, "hits": hits, "misses": misses}
        
        # Resolver dominio con gRPC (miss)
        logging.info(f"MISS: Resolviendo dominio {text}")
        misses += 1
        resolved_ip = resolve_domain_with_grpc(text)
        
        # Almacenar el resultado en Redis
        add_text_to_redis(text, resolved_ip)
        
        return {"retrieved_value": resolved_ip, "hits": hits, "misses": misses}

    except HTTPException as e:
        # Manejar errores HTTP y devolver el mensaje de error específico
        logging.error(f"Error HTTP: {e.detail}")
        raise e

    except Exception as e:
        # Manejar cualquier otro error
        logging.error(f"Error desconocido: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

