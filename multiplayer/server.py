import socket
import threading
import time
import json
from gamestate import GameState, GamePhase


class GameServer:
    def __init__(self, tcp_host="127.0.0.1", tcp_port=12345, udp_port=12346):
        self.tcp_host = tcp_host
        self.tcp_port = tcp_port
        self.udp_port = udp_port

        self.game_state = GameState()
        self.tcp_clients = {}  # {player_id: (conn, addr)}
        self.udp_clients = {}  # {player_id: addr}
        self.clients_lock = threading.Lock()

        self.running = True
        self.tcp_sock = None
        self.udp_sock = None

    def start(self):
        """Start the game server"""
        self._setup_sockets()
        self._start_threads()
        self._accept_clients()

    def _setup_sockets(self):
        # TCP setup
        self.tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.tcp_sock.bind((self.tcp_host, self.tcp_port))
        self.tcp_sock.listen(2)
        print(f"[TCP] Server listening on {self.tcp_host}:{self.tcp_port}")

        # UDP setup
        self.udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_sock.bind((self.tcp_host, self.udp_port))
        print(f"[UDP] Server listening on {self.tcp_host}:{self.udp_port}")

    def _start_threads(self):
        # Start game loop thread
        threading.Thread(target=self._game_loop, daemon=True).start()

        # Start UDP handler
        threading.Thread(target=self._handle_udp, daemon=True).start()

    def _accept_clients(self):
        """Accept TCP clients"""
        player_id = 1
        try:
            while player_id <= 2 and self.running:
                conn, addr = self.tcp_sock.accept()

                with self.clients_lock:
                    self.tcp_clients[player_id] = (conn, addr)
                    self.game_state.add_player(player_id)

                threading.Thread(target=self._handle_tcp_client,
                                 args=(conn, addr, player_id), daemon=True).start()
                player_id += 1

            if len(self.tcp_clients) == 2:
                print("[SERVER] Two players connected. Starting picking phase...")
                self.game_state.set_phase(GamePhase.PICKING)

            # >>> keep the main thread alive <<<
            while self.running or len(self.tcp_clients) < 2:
                time.sleep(0.5)

        except KeyboardInterrupt:
            print("\n[SERVER] Shutting down...")
        finally:
            self._cleanup()

    def _game_loop(self):
        """Main game loop - handles phase transitions and state updates"""
        last_time = time.time()

        while self.running:
            current_time = time.time()
            delta_time = current_time - last_time
            last_time = current_time

            # Update game state based on current phase
            if self.game_state.phase == GamePhase.PICKING:
                self.game_state.update_picking_timer(delta_time)
                self._send_picking_updates()
                time.sleep(0.1)  # 10Hz for picking phase

            elif self.game_state.phase == GamePhase.BATTLE:
                if self.game_state.all_players_ready():
                    self._send_battle_state()
                    # Reset ready states after sending
                    for player in self.game_state.players.values():
                        player.ready = False
                time.sleep(0.5)  # 2Hz for battle phase
            else:
                time.sleep(1.0)  # 1Hz for other phases

    def _send_picking_updates(self):
        """Send frequent UDP updates during picking phase"""
        if not self.udp_clients:
            return

        picking_state = self.game_state.to_json("picking")
        with self.clients_lock:
            for player_id, addr in list(self.udp_clients.items()):
                try:
                    self.udp_sock.sendto(f"PICKING_UPDATE:{picking_state}".encode(), addr)
                except Exception as e:
                    print(f"[UDP] Failed to send picking update to Player {player_id}: {e}")

    def _send_battle_state(self):
        """Send complete battle state via TCP"""
        battle_state = self.game_state.to_json("battle")
        with self.clients_lock:
            for player_id, (conn, addr) in list(self.tcp_clients.items()):
                try:
                    message = f"BATTLE_STATE:{battle_state}\n"
                    conn.sendall(message.encode())
                except Exception as e:
                    print(f"[TCP] Failed to send battle state to Player {player_id}: {e}")

    def _handle_tcp_client(self, conn, addr, player_id):
        """Handle TCP client connection"""
        print(f"[TCP] Player {player_id} connected from {addr}")

        try:
            # Send player assignment
            conn.sendall(f"ASSIGN:{player_id}\n".encode())

            buffer = ""
            while self.running:
                data = conn.recv(1024)
                if not data:
                    break

                buffer += data.decode()
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    self._process_tcp_message(player_id, line.strip())

        except Exception as e:
            print(f"[TCP] Error handling Player {player_id}: {e}")
        finally:
            print(f"[TCP] Player {player_id} disconnected")
            with self.clients_lock:
                self.tcp_clients.pop(player_id, None)
                self.game_state.remove_player(player_id)
            conn.close()

    def _handle_udp(self):
        """Handle UDP messages"""
        while self.running:
            try:
                data, addr = self.udp_sock.recvfrom(1024)
                message = data.decode().strip()

                if message.startswith("REGISTER:"):
                    player_id = int(message.split(":")[1])
                    with self.clients_lock:
                        self.udp_clients[player_id] = addr
                    print(f"[UDP] Player {player_id} registered from {addr}")

            except Exception as e:
                if self.running:
                    print(f"[UDP] Error: {e}")

    def _process_tcp_message(self, player_id, message):
        """Process TCP messages from clients"""
        print(f"[TCP] Player {player_id}: {message}")

        try:
            if message.startswith("SELECT_CHARACTER:"):
                character = message.split(":", 1)[1]
                if self.game_state.select_character(player_id, character):
                    print(f"[GAME] Player {player_id} selected {character}")

            elif message == "BATTLE_READY":
                self.game_state.set_player_ready(player_id, True)
                print(f"[GAME] Player {player_id} is ready for battle")

        except Exception as e:
            print(f"[SERVER] Error processing message from Player {player_id}: {e}")

    def _cleanup(self):
        """Clean up server resources"""
        self.running = False
        try:
            if self.tcp_sock:
                self.tcp_sock.close()
            if self.udp_sock:
                self.udp_sock.close()
        except:
            pass


if __name__ == "__main__":
    server = GameServer()
    server.start()