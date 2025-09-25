# gameserver.py
import socket
import threading
import json
import time
from gamestate import GameState
from utils.constants import EventTypes


class GameServer:
    def __init__(self, host="0.0.0.0", port=5555, tick_rate=20):

        self.host = host
        self.port = port
        self.tick_rate = tick_rate
        self.clients = []
        self.lock = threading.Lock()

        self.game_state = GameState()
        self.last_update = time.time()

    def start(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))
        self.sock.listen()
        print(f"[SERVER] Listening on {self.host}:{self.port}")

        self.running = True
        threading.Thread(target=self._accept_clients, daemon=True).start()
        threading.Thread(target=self._broadcast_loop, daemon=True).start()

    def _accept_clients(self):
        while self.running:
            conn, addr = self.sock.accept()
            print(f"[SERVER] New client {addr}")
            with self.lock:
                self.clients.append(conn)
            threading.Thread(target=self._handle_client, args=(conn,), daemon=True).start()

    def _handle_client(self, conn):
        buffer = ""
        try:
            while self.running:
                data = conn.recv(4096).decode("utf-8")
                if not data:
                    break
                buffer += data
                while "\n" in buffer:
                    msg, buffer = buffer.split("\n", 1)
                    self._handle_message(conn, msg)
        except Exception as e:
            print(f"[SERVER] Client error: {e}")
        finally:
            print("[SERVER] Client disconnected")
            with self.lock:
                if conn in self.clients:
                    self.clients.remove(conn)
            conn.close()

    def _handle_message(self, conn, msg):
        try:
            payload = json.loads(msg)
            self._process_action(conn, payload)
            print("received: ", payload)
        except Exception as e:
            print(f"[SERVER] Invalid message: {e}")

    def _process_action(self, conn, data):
        """Update game state based on player input."""
        player_id = str(id(conn))  # simple unique ID based on connection
        with self.lock:
            if player_id not in self.game_state.players:
                self.game_state.players[player_id] = {EventTypes.SELECTION_MADE: False, EventTypes.BATTLE_FINISHED: False}  # default pos

            if data.get("action") == EventTypes.SELECTION_MADE:
                self.game_state.players[player_id][EventTypes.SELECTION_MADE] = True


            elif data.get("action") == EventTypes.BATTLE_FINISHED:
                self.game_state.players[player_id][EventTypes.BATTLE_FINISHED] = True

    # -------------------
    # GAME LOOP
    # -------------------
    def tick(self):
        """Game logic per tick, based on current phase."""
        with self.lock:
            now = time.time()
            elapsed = now - self.last_update
            self.last_update = now

            # Reduce timeRemaining by the actual time passed
            self.game_state.timeRemaining -= elapsed

            # Handle phase transitions
            if self.game_state.phase == "picking":
                print("picking")
                amount_done = 0
                for player in self.game_state.players.values():
                    if player[EventTypes.SELECTION_MADE]:
                        amount_done += 1
                if amount_done == 2 or self.game_state.timeRemaining < 0:
                    for player in self.game_state.players.values():
                        player[EventTypes.SELECTION_MADE] = False
                    self.game_state.phase = "battle"
                    self.game_state.timeRemaining = -1
            elif self.game_state.phase == "battle":
                print("battle")

                amount_done = 0
                for player in self.game_state.players.values():
                    if player[EventTypes.BATTLE_FINISHED]:
                        amount_done += 1
                if amount_done == 2:
                    self.game_state.phase = "picking"
                    self.game_state.timeRemaining = 30
                    for player in self.game_state.players.values():
                        player[EventTypes.BATTLE_FINISHED] = False

    def _broadcast_loop(self):
        while self.running:
            self.tick()  # update game logic
            self.broadcast_state()
            time.sleep(1 / self.tick_rate)

    def broadcast_state(self):
        state_json = json.dumps(self.game_state.to_dict()) + "\n"
        with self.lock:
            dead_clients = []
            for conn in self.clients:
                try:
                    conn.sendall(state_json.encode("utf-8"))
                except Exception:
                    dead_clients.append(conn)
            for dc in dead_clients:
                self.clients.remove(dc)

    def stop(self):
        self.running = False
        self.sock.close()
        with self.lock:
            for conn in self.clients:
                conn.close()
            self.clients.clear()


if __name__ == "__main__":
    server = GameServer(port=5555)
    server.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("[SERVER] Shutting down...")
        server.stop()
