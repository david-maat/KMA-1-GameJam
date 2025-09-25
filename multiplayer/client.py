# gameclient.py
import socket
import threading
import json
from multiplayer import gamestate


class GameClient:
    def __init__(self, server_host="127.0.0.1", server_port=5555):
        self.server_host = server_host
        self.server_port = server_port
        self.sock = None
        self.running = False
        self.lock = threading.Lock()

        # Shared gamestate with the server
        self.game_state = gamestate.GameState()

    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.server_host, self.server_port))
        self.running = True

        # Start background listener
        threading.Thread(target=self._listen_to_server, daemon=True).start()

    def _listen_to_server(self):
        buffer = ""
        while self.running:
            try:
                data = self.sock.recv(4096).decode("utf-8")
                if not data:
                    break
                buffer += data

                # Split by newline, assume each message ends with "\n"
                while "\n" in buffer:
                    msg, buffer = buffer.split("\n", 1)
                    self._handle_message(msg)

            except Exception as e:
                print(f"[CLIENT] Error receiving: {e}")
                self.running = False
                break

    def _handle_message(self, msg):
        try:
            payload = json.loads(msg)
            with self.lock:
                # reconstruct gamestate from JSON
                # print("Received: {payload}".format(payload=payload))
                self.game_state = gamestate.GameState.from_dict(payload)
        except Exception as e:
            print(f"[CLIENT] Failed to parse message: {e}")

    def send(self, data: dict):
        """Send player input or other data to server."""
        try:
            msg = json.dumps(data) + "\n"
            self.sock.sendall(msg.encode("utf-8"))
        except Exception as e:
            print(f"[CLIENT] Send failed: {e}")

    def get_state(self) -> gamestate.GameState:
        """Thread-safe getter for the latest gamestate."""
        with self.lock:
            return self.game_state

    def disconnect(self):
        self.running = False
        if self.sock:
            self.sock.close()
