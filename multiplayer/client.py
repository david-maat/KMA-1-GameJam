import socket
import threading
import time
import json
from typing import Optional, Dict, Any


class GameClient:
    def __init__(self, tcp_host="127.0.0.1", tcp_port=12345, udp_port=12346):
        self.tcp_host = tcp_host
        self.tcp_port = tcp_port
        self.udp_port = udp_port

        self.player_id: Optional[int] = None
        self.current_phase = "waiting"
        self.game_state: Dict[str, Any] = {}

        self.running = True
        self.tcp_sock = None
        self.udp_sock = None

    def start(self):
        """Start the client"""
        try:
            self._connect_tcp()
            self._setup_udp()
            self._start_handlers()
            self._input_loop()
        except Exception as e:
            print(f"[ERROR] {e}")
        finally:
            self._cleanup()

    def _connect_tcp(self):
        """Connect to TCP server"""
        self.tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_sock.connect((self.tcp_host, self.tcp_port))
        print("[INFO] Connected to server via TCP")

    def _setup_udp(self):
        """Setup UDP connection"""
        self.udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_sock.bind(('', 0))

        # Wait for player ID assignment
        while self.player_id is None and self.running:
            time.sleep(0.1)

        if self.player_id:
            # Register with UDP server
            self.udp_sock.sendto(f"REGISTER:{self.player_id}".encode(),
                                 (self.tcp_host, self.udp_port))
            print("[INFO] Registered with UDP server")

    def _start_handlers(self):
        """Start message handler threads"""
        threading.Thread(target=self._tcp_handler, daemon=True).start()
        threading.Thread(target=self._udp_handler, daemon=True).start()

    def _tcp_handler(self):
        """Handle TCP messages"""
        buffer = ""
        try:
            while self.running:
                data = self.tcp_sock.recv(1024)
                if not data:
                    break

                buffer += data.decode()
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    self._process_tcp_message(line.strip())

        except Exception as e:
            if self.running:
                print(f"[TCP] Connection error: {e}")
        finally:
            self.running = False

    def _udp_handler(self):
        """Handle UDP messages"""
        try:
            while self.running:
                data, _ = self.udp_sock.recvfrom(1024)
                message = data.decode().strip()
                self._process_udp_message(message)
        except Exception as e:
            if self.running:
                print(f"[UDP] Error: {e}")

    def _process_tcp_message(self, message):
        """Process TCP messages"""
        if message.startswith("ASSIGN:"):
            self.player_id = int(message.split(":")[1])
            print(f"\n[INFO] You are Player {self.player_id}")
            self._show_commands()

        elif message.startswith("BATTLE_STATE:"):
            state_json = message.split(":", 1)[1]
            self.game_state = json.loads(state_json)
            self.current_phase = self.game_state["phase"]
            self._display_battle_state()

    def _process_udp_message(self, message):
        """Process UDP messages"""
        if message.startswith("PICKING_UPDATE:"):
            state_json = message.split(":", 1)[1]
            self.game_state = json.loads(state_json)
            self.current_phase = self.game_state["phase"]
            self._display_picking_state()

    def _display_picking_state(self):
        """Display picking phase information"""
        time_left = self.game_state.get("time_remaining", 0)
        selections = self.game_state.get("player_selections", {})

        print(f"\r[PICKING] Time: {time_left:.1f}s | Selections: {selections}", end="", flush=True)

    def _display_battle_state(self):
        """Display battle phase information"""
        print(f"\n[BATTLE] Received battle state:")
        players = self.game_state.get("players", {})
        for pid, player_data in players.items():
            health = player_data.get("health", 0)
            character = player_data.get("selected_character", "Unknown")
            position = player_data.get("position", {})
            print(f"  Player {pid}: {character} | Health: {health} | Pos: {position}")

        print("\nType 'ready' when you've processed the battle state:")

    def _show_commands(self):
        """Show available commands"""
        print("\nCommands:")
        print("  select <character> - Select character during picking (warrior/mage/archer/rogue)")
        print("  ready             - Mark ready during battle phase")
        print("  quit              - Exit game")

    def _input_loop(self):
        """Main input loop"""
        print("\nWaiting for game to start...")

        while self.running:
            try:
                user_input = input().strip().lower()

                if user_input == 'quit':
                    break
                elif user_input.startswith('select '):
                    character = user_input.split(' ', 1)[1]
                    if self.current_phase == "picking":
                        self.tcp_sock.sendall(f"SELECT_CHARACTER:{character}\n".encode())
                    else:
                        print("Character selection only available during picking phase!")

                elif user_input == 'ready':
                    if self.current_phase == "battle":
                        self.tcp_sock.sendall("BATTLE_READY\n".encode())
                        print("Marked as ready!")
                    else:
                        print("Ready command only available during battle phase!")
                else:
                    print("Unknown command. Type 'quit' to exit.")

            except KeyboardInterrupt:
                break
            except EOFError:
                break

    def _cleanup(self):
        """Clean up client resources"""
        self.running = False
        try:
            if self.tcp_sock:
                self.tcp_sock.close()
            if self.udp_sock:
                self.udp_sock.close()
        except:
            pass
        print("\n[INFO] Disconnected")



if __name__ == "__main__":
    client = GameClient()
    client.start()