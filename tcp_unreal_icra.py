import socket
import time
import pickle

    
# Load file containing positios and orientations for target
def load_lhs_data(start_line: int, end_line: int):
    lhs_data = []
    with open('test_data.txt', 'r') as f:
        for i , line in enumerate(f):
            if start_line <= i < end_line:
                sample = list(map(float, line.strip().split(',')))
                lhs_data.append(sample)
    return lhs_data



class TCP:
    def __init__(self, ip_address: str='127.0.0.1', port: int=8000, start_line: int = 0, end_line: int = None):
        self.running = True
        self.ip_address = ip_address
        self.port = port
        self.debug = True
        self.lhs_data = load_lhs_data(start_line, end_line)

        # Create TCP socket
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Bind server socket to IP address and port
        self.server_address = (self.ip_address, self.port)
        self.server_socket.bind(self.server_address)

    def listen(self):
        # Listening  for incoming connections
        self.server_socket.listen(1)
        print("Server started. Waiting for connections...")

        # Accept client connection
        self.client_socket, self.client_address = self.server_socket.accept()
        print(f"Client connected: {self.client_address}")

    def send_lhs_data(self):
        # for each sample send x, y, z and orientations at t=0, t=5, t=10, t=15
        for row_index, sample in enumerate(self.lhs_data):
            x, y, z = sample[:3]
            orientations = [
                (sample[3:6], 0),    # ox, oy, oz at t=0
                (sample[6:9], 5),    # ox, oy, oz at t=5
                (sample[9:12], 10),  # ox, oy, oz at t=10
                (sample[12:15], 15)  # ox, oy, oz at t=15
            ]

            angular_velocity = sample[15:18]

            print(f'Sending row {row_index +1 } with data {sample}')

            for (ox, oy, oz), t in orientations:
                data_string = f"{x}, {y}, {z}, {ox}, {oy}, {oz}, {t}"

                print(f'Sending data: {data_string}')   
                self.send_data(data_string)
                time.sleep(2)  

    def get_incoming(self):
        try:
            self.send_lhs_data()
            while True:
                data = self.client_socket.recv(4096)
                if data:
                    print("Received")
                else:
                    break
        except Exception as e:
            print(e)

    def send_data(self, data_string, encoding='utf-8'):
        # Convert from string bytes to send data to unreal engine
        reply_data = bytes(data_string, encoding)

        try:
            # Sending back to Unreal Engine
            self.client_socket.send(reply_data)
            print(f"Sent data to Unreal Engine: {data_string}")
        except socket.error as e:
            print(f"Failed to send data: {e}")

    def close_connection(self):
        self.client_socket.close()
        self.server_socket.close()
        print("Connection closed.")

# Running TCP server
server = TCP(start_line = 0, end_line= 3)
server.listen()
try:
    server.get_incoming()
finally:
    server.close_connection()
