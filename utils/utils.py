
def calculate_ports(ip):
    "Первый - для STATE_UDP_PORT, второй - VS_UDP_PORT"
    id = int(ip.split('.')[-1])
    return 9000 + id * 10, 11111 + id * 10
