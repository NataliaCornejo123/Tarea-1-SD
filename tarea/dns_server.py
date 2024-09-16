import grpc
from concurrent import futures
import subprocess
import dns_pb2
import dns_pb2_grpc

class DNSResolverServicer(dns_pb2_grpc.DNSResolverServicer):
    def Resolve(self, request, context):
        domain = request.domain
        print(f"Received request to resolve domain: {domain}")
        try:
            result = subprocess.run(['dig', '+short', domain], capture_output=True, text=True, check=True)
            ip = result.stdout.strip()
            if not ip:
                context.set_details('No IP address found for domain')
                context.set_code(grpc.StatusCode.NOT_FOUND)
                print(f"Domain resolution failed for {domain}: No IP address found")
            else:
                print(f"Domain {domain} resolved to IP: {ip}")
            return dns_pb2.ResolveResponse(ip=ip)
        except subprocess.CalledProcessError as e:
            context.set_details(f'Error running dig command: {e}')
            context.set_code(grpc.StatusCode.INTERNAL)
            print(f"Error resolving domain {domain}: {e}")
            return dns_pb2.ResolveResponse(ip='')

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    dns_pb2_grpc.add_DNSResolverServicer_to_server(DNSResolverServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("gRPC DNS resolver started on port 50051")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()

