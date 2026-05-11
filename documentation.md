# DSA Battle Tanks — System Architecture Documentation

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Technology Stack](#2-technology-stack)
3. [High-Level Architecture](#3-high-level-architecture)
4. [Directory Structure](#4-directory-structure)
5. [Layer Breakdown](#5-layer-breakdown)
   - [Entry Points](#51-entry-points)
   - [Network Layer](#52-network-layer)
   - [Game Logic Layer](#53-game-logic-layer)
   - [Sprite Layer](#54-sprite-layer)
   - [Commons / Shared Utilities](#55-commons--shared-utilities)
   - [Components](#56-components)
   - [Server Module](#57-server-module)
   - [Assets](#58-assets)
6. [Data Flow](#6-data-flow)
7. [Communication Protocol](#7-communication-protocol)
8. [Key Design Patterns](#8-key-design-patterns)
9. [Game Features & Systems](#9-game-features--systems)

---

## 1. Project Overview

**DSA Battle Tanks** is a real-time multiplayer 2D tank combat game built with Python and Pygame. Players connect to a central game server over TCP and control tanks on a tile-based map. The game supports multiple weapons, destructible environments, landmines, powerups, a laser beam, and a burst-fire system.

The project follows a **client-server architecture**: the server is the single source of truth for game state (positions, damage, bricks), while each client renders the world locally using updates received from the server.

---

## 2. Technology Stack

| Dependency | Version | Role |
|---|---|---|
| Python | 3.10+ | Primary language |
| `pygame` | 2.5.0 | Game rendering, input, audio, sprites |
| `PyTMX` | 3.32 | Parsing `.tmx` tile map files |
| `socket` (stdlib) | — | Raw TCP networking |
| `threading` (stdlib) | — | Concurrent client handling |
| `struct` (stdlib) | — | Binary packet packing/unpacking |
| `pickle` (stdlib) | — | Serialization for level-map exchange |
| `queue` (stdlib) | — | Thread-safe inter-thread communication |
| `concurrent.futures` | — | Thread pool for client I/O |

---

## 3. High-Level Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                         CLIENT (client.py)                       │
│                                                                  │
│  ┌──────────┐   ┌──────────────┐   ┌──────────────────────────┐ │
│  │  Menu    │──▶│  Game Loop   │──▶│  Render / HUD / Camera   │ │
│  └──────────┘   └──────┬───────┘   └──────────────────────────┘ │
│                        │                                         │
│           ┌────────────▼────────────┐                           │
│           │     NetworkComponent    │  (TCP socket + 2 threads) │
│           └────────────┬────────────┘                           │
└────────────────────────┼───────────────────────────────────────-┘
                         │  TCP (binary packets)
┌────────────────────────▼────────────────────────────────────────┐
│                       SERVER (server.py / server/server.py)      │
│                                                                  │
│  ┌──────────────┐  ┌─────────────┐  ┌──────────────────────┐   │
│  │  _conexions  │  │_handle_client│  │    _receive (main)   │   │
│  │  (listener)  │  │ (per client) │  │  (queue dispatcher)  │   │
│  └──────────────┘  └─────────────┘  └──────────────────────┘   │
│                                                                  │
│  ┌──────────────┐  ┌─────────────┐  ┌──────────────────────┐   │
│  │  Collision   │  │ DatabaseMgr │  │       Struct         │   │
│  │  (physics)   │  │ (JSON DB)   │  │ (pack/unpack binary) │   │
│  └──────────────┘  └─────────────┘  └──────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 4. Directory Structure

```
DSA-Battle-Tanks-1/
│
├── client.py                   # Client entry point (game window + network)
├── server.py                   # Server entry point (reads env vars, launches Server)
├── requirements.txt
│
├── assets/
│   ├── images/                 # Sprites, HUD, backgrounds
│   ├── maps/                   # .tmx tile map files (zone_0.tmx, etc.)
│   └── sound/                  # .wav audio (shot, boom, background music)
│
├── battle_tanks/               # Main game package
│   ├── __init__.py             # Exports ROUTE() helper (asset path resolver)
│   ├── game.py                 # Game class — central client-side game manager
│   ├── menu.py                 # Menu class — connection screen & tank color picker
│   │
│   ├── commons/                # Shared data & drawing utilities
│   │   ├── municion.py         # CannonType — ammo state & HUD rendering
│   │   ├── package.py          # Struct — binary protocol pack/unpack + Collision
│   │   └── tank_surface.py     # draw_bullet(), tank_cover() — low-level drawing
│   │
│   ├── components/             # Reusable subsystems (no game-logic coupling)
│   │   ├── camera.py           # CameraComponent — viewport offset & shake
│   │   ├── collision.py        # Collision — server-side & shared physics
│   │   ├── movement.py         # MovementComponent — maps key presses to events
│   │   ├── network.py          # NetworkComponent — TCP client socket wrapper
│   │   ├── text.py             # TextComponent — Pygame text surface helper
│   │   └── tile_map.py         # TileMap — loads & renders .tmx maps via PyTMX
│   │
│   └── sprites/                # Pygame sprite classes
│       ├── player.py           # Player (extends Cannon) — tank entity
│       ├── cannon.py           # Cannon — turret rotation base class
│       ├── bullet.py           # Bullet — projectile movement & lifetime
│       ├── elements.py         # Brick, Block, Particle — environment sprites
│       ├── landmine.py         # LandMine — proximity explosive sprite
│       └── powerup.py          # PowerUp — collectible crate sprite
│
└── server/                     # Standalone server package
    ├── server.py               # Server class — connection manager & game loop
    └── conexions.py            # DatabaseManager — JSON file-based persistence
```

---

## 5. Layer Breakdown

### 5.1 Entry Points

#### `client.py`
The top-level script that launches the game window for a player.

| Function / Block | Role |
|---|---|
| `main()` | Initialises Pygame, creates the `Menu`, obtains a `Game` instance, starts two network threads, then runs the main 60 FPS game loop. |
| `handle_burst_fire(game, menu)` | Checks if `K` is held; fires up to 5 bullets rapidly, then enforces a 15-second cooldown before allowing another burst. State is stored directly on the player object. |
| `draw_burst_indicator(screen, game, x, y)` | Draws the burst-fire icon and a red arc overlay showing remaining cooldown time. |
| `network_client_consumer(client)` | Daemon thread — blocks on `recv_move_player()`, puts received data into `UPDATE_Q`. |
| `network_client_handler(client)` | Daemon thread — drains `SEND_Q` and calls `send_move_tcp()` to forward pending moves to the server. |

#### `server.py`
Reads environment variables (`IP_BIND`, `SERVER_PORT`, `MAP`) and instantiates the `Server` class.

---

### 5.2 Network Layer

#### `battle_tanks/components/network.py` — `NetworkComponent`

Wraps the client-side TCP socket. Created once per game session.

| Method | Role |
|---|---|
| `__init__` | Connects to the server via TCP, performs the handshake (`load_data`), receives initial player state and the full map game-state. |
| `load_data()` | Handshake: sends player name + tank colour byte, receives assigned position, x/y/angle, and the serialised map. |
| `recv_move_player()` | Blocking recv of up to 120 bytes, unpacks all player/event packets in the response via `Struct.unpack_all_data`. |
| `send_move_tcp(move)` | Sends a single raw byte event (e.g. move, fire, laser on/off) to the server. |
| `recv_to_queue()` | Drains `UPDATE_Q` and returns all pending parsed update dicts accumulated by the consumer thread. |
| `check_name(addr, name)` | Static — opens a temporary socket to verify a name is not already taken on the server (used in the menu). |
| `get_events_to_game_state()` | Unpacks the initial map game-state bytes into a list of tile events (bricks, etc). |
| `send_keys(keys)` | Enqueues a list of action bytes into `SEND_Q` for the sender thread. |

---

### 5.3 Game Logic Layer

#### `battle_tanks/game.py` — `Game`

The central client-side manager. Owns all sprite groups, the camera, the network component, and the update/draw cycle.

| Method | Role |
|---|---|
| `__init__` | Initialises the tile map, sprite groups (players, bullets, bricks, particles, powerups, landmines), places the local player, starts the camera and movement components, spawns initial powerups. |
| `load()` | Reads the initial game-state from the server and creates `Brick` sprites for all wall tiles. |
| `update()` | **Main game tick**: processes input, fires bullets, updates all sprites, handles bullet/brick collisions, processes all network updates received this frame, updates camera. |
| `draw(main_screen)` | **Render pass**: draws tile background → bullets → players (with laser beams, names, health/energy bars) → bricks → particles → powerups → landmines → telescopic sight → notifications. |
| `_spawn_powerups()` | Places 5 `PowerUp` crates at random positions. Respawns one whenever a player collects one. |
| `place_landmine()` | Drops a `LandMine` at the player's current position and broadcasts the event to the server. |
| `break_brick_locally(brick)` | Removes a brick from local sprite groups, spawns particles, plays sound. |
| `send_brick_break_to_server(brick)` | Sends a `BROKE_BRICK` event packet to the server so other clients are notified. |
| `_spawn_particles(x, y, count)` | Creates `count` `Particle` sprites at a world position (used for explosions/brick destruction). |
| `add_notification(text, duration)` | Adds a timed on-screen notification message (e.g. "Landmine Placed!"). |
| `close()` | Sends the close-connection byte, closes the TCP socket, and exits Pygame. |

---

### 5.4 Sprite Layer

#### `battle_tanks/sprites/player.py` — `Player(Cannon)`

Extends `Cannon` to represent a full tank entity.

| Attribute / Method | Role |
|---|---|
| `SPEED`, `ANGLE`, `DAMAGE`, `MAX_DAMAGE` | Class-level constants shared with the server for physics calculations. |
| `__init__` | Sets position, player number, colour, name, damage, fire state, angles, velocity, laser fields. |
| `fire` (property/setter) | When set to `True`, decrements `type_gun.count_available` (ammo). |
| `damage` (property/setter) | Tracks cumulative damage taken. |
| `update()` | Syncs `body_rect` and `rect_cannon` to the player's main rect each frame. |
| `rotate_rect(xbool, surface)` | Rotates the tank body by 10° steps. |
| `rotate_external(xbool, angle, ...)` | Static — rotates an arbitrary surface by `ANGLE` steps (used for remote players). |
| `telescopic_sight()` | Returns `{x, y, angle_cannon}` dict used to compute the aiming reticle's world position. |

#### `battle_tanks/sprites/bullet.py` — `Bullet`

| Method | Role |
|---|---|
| `__init__(start_pos, angle)` | Creates a circular 8px sprite; calculates `vx`/`vy` velocity components from the cannon angle. |
| `update(bounds_rect)` | Moves by velocity each frame; kills itself when it exceeds `MAX_DISTANCE` (500px) or leaves the map bounds. |

#### `battle_tanks/sprites/landmine.py` — `LandMine`

| Method | Role |
|---|---|
| `__init__` | Places mine at world coordinates; starts an arming timer (90 frames). |
| `_draw(armed)` | Draws the mine sprite — grey when unarmed, red with yellow spikes when armed. |
| `update(players, owner_name)` | Ticks down the arm timer; redraws to armed appearance once timer expires. |
| `check_trigger(players)` | Returns a non-empty list if any enemy enters trigger radius (≈24px). Used by `Game.update()` to detonate. |

#### `battle_tanks/sprites/elements.py` — `Brick`, `Block`, `Particle`

- **`Brick`** — destructible wall tile rendered as a coloured rectangle; can be removed by bullets or lasers.
- **`Block`** — indestructible terrain variant.
- **`Particle`** — short-lived debris sprite spawned at explosion points; fades out over its lifetime.

#### `battle_tanks/sprites/powerup.py` — `PowerUp`

A collectible crate that grants the player one landmine when picked up.

---

### 5.5 Commons / Shared Utilities

#### `battle_tanks/commons/municion.py` — `CannonType`

Tracks ammo state for a gun type and renders the ammo HUD strip.

| Method | Role |
|---|---|
| `__init__` | Initialises bullet count, reload timer fields, icon size, damage placeholder. |
| `count_available` (property) | Getter/setter for current bullet count. The setter is called by `Player.fire` on each shot. |
| `render(bullet_surface)` | Draws bullet icons side-by-side on the HUD surface; auto-reloads after 100 ticks when empty. |

#### `battle_tanks/commons/package.py` — `Struct`

The **binary protocol hub** — all packet formats live here.

| Method | Role |
|---|---|
| `pack_player(data, player_data, status)` | Packs a player update (status, position, x, y, angle, cannon angle, damage, colour) into 13 bytes. Also applies movement physics when `data` is a move event. |
| `unpack_player(data)` | Unpacks 13-byte player packet → tuple. |
| `pack_tile(data)` | Packs a tile event (type, x, y, w, h) into 11 bytes. |
| `unpack_event(data)` | Unpacks an 11-byte tile/event packet → tuple. |
| `unpack_all_data(data)` | Splits a raw byte buffer into individual player or event packets by reading size-prefix bytes. |
| `pack_players(data)` | Packs all players in the server's `_data` dict into a concatenated byte buffer (broadcast). |
| `pack_bullet_position(id, x, y)` | Packs a bullet position update (server-side bullet simulation, not yet used client-side). |
| `pack_event(player_data)` | Checks bullet-vs-brick and bullet-vs-player collisions; returns a packed event or `False`. |
| `pack / unpack` | Pickle-based serialisation for the level-map name exchange (legacy, largely replaced by binary struct). |

#### `battle_tanks/commons/tank_surface.py`

Low-level drawing functions for tank visuals.

| Function | Role |
|---|---|
| `draw_bullet(surface, pos, angle, size)` | Draws a single bullet icon at a position on a given surface (used by `CannonType.render`). |
| `tank_cover(color_id, rect, screen, ...)` | Draws a full tank (body + turret) at the given rect with the correct colour and rotation angles. Used both in-game and in the menu tank preview. |

---

### 5.6 Components

#### `battle_tanks/components/camera.py` — `CameraComponent`

| Method | Role |
|---|---|
| `update(player)` | Re-centres the camera on the player, clamped to map bounds; applies shake offset if active. |
| `apply(sprite)` | Returns the camera-offset rect for a sprite (used when blitting). |
| `apply_rect(rect)` | Same as `apply` but for raw `pg.Rect` objects. |
| `shake(duration, intensity)` | Triggers a screen shake effect for `duration` frames at ±`intensity` pixels. |

#### `battle_tanks/components/collision.py` — `Collision`

A class-level (static) collision registry shared between client and server.

| Method | Role |
|---|---|
| `load(lvl_map_tmx, func_tile_pack)` | Parses the `.tmx` map; populates `bricks`, `positions`, and `game_state`. |
| `add_player(player)` | Registers a player dict into the server's active player list. |
| `collide_with_objects(player)` | AABB collision resolution — pushes the player dict's x/y out of any overlapping brick. |
| `check_collision_bullet(player_data, radius)` | Ray-steps along the bullet path (0→100px); returns brick hit data if any brick is within `radius`. |
| `check_collision_player(player_data, radius)` | Same ray-step but checks other players; applies damage and respawns if `MAX_DAMAGE` is exceeded. |
| `check_bullet_at_point(x, y)` | Point-in-rect check used by the laser and server-side bullet simulation. |
| `calculate_bullet_position(player_data, distance)` | Converts a cannon angle + distance into world (x, y) coordinates. |
| `get_laser_intersections(player_data, range)` | Returns all bricks and players currently intersected by the laser beam. |

#### `battle_tanks/components/movement.py` — `MovementComponent`

| Method | Role |
|---|---|
| `keys()` | Reads `pg.key.get_pressed()` and calls `network.send_move_tcp()` with the appropriate event byte for WASD movement and turret rotation (I/P). |

#### `battle_tanks/components/tile_map.py` — `TileMap`

| Method | Role |
|---|---|
| `__init__(filename)` | Loads the `.tmx` file with PyTMX, reads tile dimensions and layer data. |
| `make_map()` | Renders all tile layers into a single `pg.Surface` (the background image). |

#### `battle_tanks/components/text.py` — `TextComponent`

A simple Pygame text wrapper with configurable font, size, and colour.

---

### 5.7 Server Module

#### `server/server.py` — `Server`

The authoritative game server. Runs three concurrent threads plus the main loop.

| Thread / Method | Role |
|---|---|
| `_conexions()` (thread) | Blocks on `socket.accept()`; performs the connection handshake, creates or retrieves a player record from the JSON DB, sends the player their initial state and the full map, then submits `_handle_client` to the thread pool. |
| `_handle_client(socket)` (thread pool) | Receives events from one client socket. Routes move events → physics → `q.put`, fire events (passthrough), brick-break events → collision state update → broadcast, laser on/off → state update, mine/damage events → broadcast. On disconnect: saves position, marks player deleted. |
| `_receive()` (main loop) | Drains the shared queue `q`. Dict items = new/deleted players; bytes items = broadcast to all sockets. Also runs the server-side tick: laser damage computation and server-simulated bullet movement (partial implementation). |
| `_handle_menu()` (thread) | Admin CLI — accepts `users`, `data`, `bricks`, `exit` commands from stdin. |
| `_get_player_position(conn)` | Maps a socket object back to its player position ID. |

#### `server/conexions.py` — `DatabaseManager`

A lightweight JSON file database used to persist player positions across sessions.

| Method | Role |
|---|---|
| `configure(config)` | Sets the JSON file path for the database. |
| `get()` | Returns the singleton `DatabaseManager` instance. |
| `save(collection, data)` | Appends a document to a collection. |
| `find(collection, query)` | Finds documents matching all key-value pairs in `query`. |
| `update(collection, query, update)` | Updates the first matching document with new field values. |

---

### 5.8 Assets

| Path | Contents |
|---|---|
| `assets/images/` | Tank sprites, bullet icons, HUD background, burst icon, telescopic sight, camo background |
| `assets/maps/zone_0.tmx` | Default PyTMX tile map (defines bricks, player spawn points) |
| `assets/sound/boom.wav` | Explosion sound effect |
| `assets/sound/shot.wav` | Bullet fire sound effect |
| `assets/sound/bg_track.wav` | Background music (looped) |
| `assets/Pixel Digivolve.otf` | Custom pixel font |

---

## 6. Data Flow

### Player Movement (Client → Server → All Clients)

```
Player presses W
  → MovementComponent.keys()
      → network.send_move_tcp(UP_EVENT_PLAYER)  [1 byte]
          → Server._handle_client receives byte
              → Struct.pack_player(UP_EVENT, player_data)
                  applies physics: x += -sin(angle)*SPEED
                  runs Collision.collide_with_objects()
              → q.put(packed_bytes)
          → Server._receive drains queue
              → broadcasts packed_bytes to all sockets
  → Each client's network_client_consumer receives bytes
      → UPDATE_Q.put(parsed_data)
      → Game.update() reads queue → updates player rect
```

### Bullet Fire

```
Player presses O (or K for burst)
  → game.player.fire = True
  → network.send_move_tcp(FIRE_EVENT_PLAYER)
  → Server receives FIRE_EVENT → (currently no server-side projectile)
  → Each client: game.update() sees player.fire == True
      → spawns Bullet(cannon_pos, angle) locally
      → Bullet.update() moves it 4px/frame
      → spritecollide() checks bricks → breaks + notifies server
      → rect.colliderect() checks other players → shake
```

### Laser Beam

```
Player holds L
  → client.py KEYDOWN → player.laser_active = True
  → network.send_move_tcp(LASER_ON_EVENT)
  → Server._handle_client → player_data["laser_active"] = True
  → Server tick: steps along laser ray, checks brick/player hits
  → Broadcasts updated game state
  → Client: player.laser_active renders a red/white line from turret
  → client.py decrements laser_energy 1.5/frame; regens 0.5/frame when off
```

---

## 7. Communication Protocol

All packets use `struct` binary encoding with a **1-byte size prefix**.

| Packet Type | Size | Format | Direction |
|---|---|---|---|
| Player update | 13 bytes | `B BBhhhhbB` (size + status, pos, x, y, angle, cannon, damage, colour) | Server → Client |
| Tile/Event | 11 bytes | `B bhhhh` (size + type, x, y, w, h) | Bidirectional |
| Move event | 1 byte | Single control byte (e.g. `\x05` = UP) | Client → Server |
| Fire event | 1 byte | `\x11` | Client → Server |
| Laser on/off | 1 byte | `\x12` / `\x13` | Client → Server |
| Close connection | 1 byte | `\x10` | Client → Server |
| OK / Join | 1 byte | `\x01` / `\x02` | Server → Client |
| Map name | 40 bytes | Pickled path string | Server → Client |
| Map game-state | Variable | Concatenated tile packets | Server → Client |

---

## 8. Key Design Patterns

### Shared Queue (`queue.SimpleQueue`)
The server uses a single shared queue `q` to safely pass data between the per-client `_handle_client` threads and the main `_receive` loop. This avoids locks on the main data structures.

### Binary Struct Protocol
Rather than JSON, all in-game messages are packed binary structs. This minimises bandwidth and latency — a player update is only 13 bytes.

### Component Pattern
Game subsystems (camera, movement, network, collision, tile map) are separated into `components/` and do not depend on each other, making them reusable across client and server contexts.

### Class-Level Collision Registry
`Collision` uses class attributes (`bricks`, `players`, `game_state`) as a global registry. Both the server and the commons `package.py` module share this state without passing it through constructor arguments.

### Property-Based Ammo Decrement
`Player.fire` is a property whose setter automatically decrements `CannonType.count_available`, keeping the ammo logic encapsulated in the data model rather than scattered in the game loop.

---

## 9. Game Features & Systems

| Feature | Where Implemented |
|---|---|
| Tank movement (WASD) | `MovementComponent` → `Struct.pack_player` (server physics) |
| Turret rotation (I / P) | `MovementComponent` → `Struct.pack_player` |
| Normal fire (O) | `client.py` KEYUP → `Bullet` sprite + `FIRE_EVENT_PLAYER` |
| Burst fire (K, 5 shots / 15s cooldown) | `handle_burst_fire()` in `client.py` |
| Laser beam (hold L) | `client.py` + server tick `_receive()` + `Collision.check_bullet_at_point` |
| Landmine (M) | `Game.place_landmine()` + `LandMine` sprite + broadcast |
| Powerup crates | `PowerUp` sprite; collected on overlap → grants 1 landmine |
| Destructible bricks | `Bullet` spritecollide + `send_brick_break_to_server` + `BROKE_BRICK` event |
| Camera follow + shake | `CameraComponent.update()` + `shake(duration, intensity)` |
| Player name tags + health bar | `Game.draw()` per-player rendering |
| Laser energy bar | `Game.draw()` energy bar for local player |
| Ammo HUD strip | `CannonType.render()` → `client.py` blit to bottom bar |
| Player persistence | `DatabaseManager` JSON file (position saved on disconnect) |
| Server admin CLI | `Server._handle_menu()` — `users`, `data`, `bricks`, `exit` commands |
| Tank colour picker | `Menu.multiplayer_mode()` → 24-colour grid → sent to server on connect |
| Notifications | `Game.add_notification()` → timed fading on-screen messages |
