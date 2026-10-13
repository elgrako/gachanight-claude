extends Node2D
## The toy store, built in code and stripped to what the game needs: walls and
## floor, the doors between its three scenes, and the things the player uses
## (floor coins, the power switch, the machines, the figure cabinet, the
## counter, the front door, the sofa). No decoration and nothing that moves by
## itself: the whole set is to be redone. Presentation only: it never changes
## game state.
##
## Units are world pixels. The back wall stands on the line y = 0 and rises to
## WALL_TOP; the floor is a deep plane from y = 0 (far) to FLOOR_DEPTH (near).
## Everything standing on the floor is anchored at the bottom centre of its
## picture and drawn in order of that y (see `floor_z`).

const Interactable = preload("res://scripts/world/interactable.gd")
const Sprites = preload("res://scripts/world/sprite_lib.gd")
const PriceSign = preload("res://scripts/world/price_tag.gd")

const C_INK: Color = Color("#161320")
const C_NIGHT: Color = Color("#0d1322")
## The store with the power off: light enough to find the way.
const DARK: Color = Color(0.38, 0.42, 0.64)
const SHADOW_COLOR: Color = Color(0.0, 0.0, 0.05, 0.28)

# --- Layout -----------------------------------------------------------------
const WALL_HEIGHT: float = 120.0
const WALL_TOP: float = -WALL_HEIGHT
const FLOOR_DEPTH: float = 232.0
const LEDGE_HEIGHT: float = 8.0
const CORNICE_HEIGHT: float = 8.0
const TRIM_HEIGHT: float = 6.0
const PILLAR_WIDTH: float = 14.0
## Rooms from left to right: name, first x, wall tile, floor tile, placeholder
## colours of wall and floor.
const ROOMS: Array = [
	["bath", 0.0, "wall_bath", "floor_bath", "#bfd9d6", "#9fb7b9"],
	["corridor", 140.0, "wall_corridor", "floor_hall", "#f1e2bd", "#c9a27a"],
	["hall", 240.0, "wall_hall", "floor_hall", "#f3dcb4", "#c9a27a"],
	["gallery", 540.0, "wall_gallery", "floor_gallery", "#1f2f66", "#6a4a36"],
	["reception", 680.0, "wall_reception", "floor_hall", "#f1e2bd", "#c9a27a"],
	["staff", 850.0, "wall_staff", "floor_staff", "#d4b88a", "#a9825a"],
]
const STORE_WIDTH: float = 1000.0
## Three scenes share this strip; only one shows at a time. Name -> first and last x.
const ZONES: Dictionary = {
	"bath": Vector2(0.0, 140.0),
	"store": Vector2(140.0, 850.0),
	"staff": Vector2(850.0, 1000.0),
}
## Doors between scenes, on the back wall: name, x, the zone it leads to and
## the x of the door on the other side.
const ZONE_DOORS: Array = [
	["BathroomDoor", 168.0, "bath", 116.0],
	["BathroomExit", 116.0, "store", 168.0],
	["StaffDoor", 702.0, "staff", 870.0],
	["StaffExit", 870.0, "store", 702.0],
]
const ZONE_DOOR_SIZE: Vector2 = Vector2(28.0, 62.0)
## The part of the floor feet may stand on.
const WALK_AREA: Rect2 = Rect2(12.0, 6.0, STORE_WIDTH - 24.0, FLOOR_DEPTH - 10.0)
## What the camera must show from top to bottom: the wall and the floor ledge.
const VIEW_TOP: float = WALL_TOP
const VIEW_BOTTOM: float = FLOOR_DEPTH + LEDGE_HEIGHT

# --- Draw order ---------------------------------------------------------------
const Z_WALL: int = 5
const Z_DECAL: int = 20
const Z_SHADOW: int = 30
## Things standing on the floor: this plus their floor y.
const FLOOR_Z_BASE: int = 100
const Z_LEDGE: int = 300
const Z_MASK: int = 950

# --- Things the player uses ---------------------------------------------------
const SPAWN: Vector2 = Vector2(60.0, 56.0)
const COIN_SPOTS: Array = [Vector2(84.0, 46.0), Vector2(98.0, 80.0), Vector2(70.0, 78.0)]
const COIN_REACH: float = 13.0
const COIN_SIZE: Vector2i = Vector2i(12, 12)
const SWITCH_AT: Vector2 = Vector2(212.0, -30.0)
## Things on the wall are used from the floor this far in front of it.
const WALL_USE_OFFSET: Vector2 = Vector2(0.0, 10.0)
const WALL_USE_REACH: float = 22.0
## Bottom centre of each machine: the front edge of its footprint.
const MACHINE_SPOTS: Dictionary = {
	"machine_001": Vector2(270.0, 14.0),
	"machine_002": Vector2(334.0, 14.0),
	"machine_005": Vector2(406.0, 16.0),
	"machine_006": Vector2(488.0, 16.0),
}
## World size of a capsule machine's picture, and of the crane's and the plinko's.
const GACHA_SIZE: Vector2i = Vector2i(48, 84)
const BIG_SIZE: Vector2i = Vector2i(72, 104)
const BIG_MACHINES: Array = ["machine_005", "machine_006"]
## A footprint is this much narrower than the picture.
const FOOTPRINT_INSET: float = 6.0
const MACHINE_USE_OFFSET: Vector2 = Vector2(0.0, 10.0)
const MACHINE_REACH: float = 20.0
## The price is plain text on the floor in front of each machine for now.
const PRICE_OFFSET: Vector2 = Vector2(0.0, 15.0)
const ROBOT_SIZE: Vector2i = Vector2i(28, 34)
## Where each robot of a team stands, relative to its machine's bottom centre.
const ROBOT_OFFSETS: Array = [Vector2(-22.0, 8.0), Vector2(24.0, 9.0), Vector2(-34.0, 18.0)]
const ROBOT_FLIPS: Array = [false, true, false]
const COUNTER_AT: Vector2 = Vector2(770.0, 64.0)
const COUNTER_SIZE: Vector2i = Vector2i(100, 50)
const COUNTER_DEPTH: float = 12.0
const COUNTER_REACH: float = 36.0
## Bottom centres of the computer and the key, relative to the counter's.
const COMPUTER_OFFSET: Vector2 = Vector2(-32.0, -38.0)
const KEY_OFFSET: Vector2 = Vector2(-7.0, -40.0)
const DOOR_X: float = 814.0
const DOOR_SIZE: Vector2i = Vector2i(58, 88)
const SOFA_AT: Vector2 = Vector2(957.0, 20.0)
const SOFA_SIZE: Vector2i = Vector2i(80, 46)
const SOFA_DEPTH: float = 20.0
const SOFA_REACH: float = 30.0
## Where the sleeping player sits, relative to the sofa's bottom centre.
const SOFA_SEAT: Vector2 = Vector2(0.0, -12.0)

# --- The figure cabinet: every figure as a miniature on its rarity base ---------
const GALLERY_SCALE: float = 0.25
## The same, as world pixels per sprite pixel of art drawn at Sprites.ART_SCALE.
const GALLERY_ART_SCALE: float = GALLERY_SCALE / Sprites.ART_SCALE
const GALLERY_PER_ROW: int = 10
## Centre of the first column and the step between columns.
const GALLERY_FIRST_X: float = 556.0
const GALLERY_STEP_X: float = 12.0
## y of the bottom of the bases on each shelf, top to bottom.
const GALLERY_ROW_YS: Array = [-68.0, -44.0]
## The cabinet's back board: left edge, top and size.
const GALLERY_CABINET: Rect2 = Rect2(546.0, -88.0, 128.0, 48.0)
const SILHOUETTE: Color = Color(0.07, 0.08, 0.12)

## machine_id -> {id, root, at, canvas, off, anim, price, robots, body, affordable}.
## `off` is the powered-off picture, `anim` the awake machine.
var machines: Dictionary = {}
var coins: Array = []
var power_switch: Node2D
var sofa: Node2D
var reception: Node2D
var door: Node2D
## Everything the player can use, for the player's reach test.
var interactables: Array = []
## Footprints (Rect2 on the floor plane) the player cannot walk into.
var solids: Array = []
## figure_id -> {figure: AnimatedSprite2D, base: AnimatedSprite2D or null}.
var gallery: Dictionary = {}
## The scene showing now: a key of ZONES.
var zone: String = "bath"
## Doors between scenes: {node, zone, to}; `to` is where the player comes out.
var zone_doors: Array = []

var _zone_masks: Array = []
var _modulate: CanvasModulate
var _switch_sprite: Sprite2D
var _computer: Sprite2D
var _key: Sprite2D
var _door_sprite: Sprite2D


func _ready() -> void:
	_modulate = CanvasModulate.new()
	add_child(_modulate)
	_build_shell()
	_build_coins()
	_build_switch()
	for machine_id in MACHINE_SPOTS:
		_build_machine(machine_id)
	_build_cabinet()
	_build_reception()
	_build_sofa()
	_build_zone_doors()
	set_power(false, false)
	set_zone(zone)


func _draw() -> void:
	# Night outside the store, so a wider or taller window never shows a void.
	draw_rect(Rect2(-2000.0, -2000.0, STORE_WIDTH + 4000.0, 4000.0), C_NIGHT)


## Draw order of something standing on the floor at depth `y`.
static func floor_z(y: float) -> int:
	return FLOOR_Z_BASE + int(y)


## The zone a floor point belongs to.
static func zone_at(x: float) -> String:
	for zone_name in ZONES:
		if x >= ZONES[zone_name].x and x < ZONES[zone_name].y:
			return zone_name
	return "store"


## The part of a zone's floor feet may stand on.
static func zone_walk_area(zone_name: String) -> Rect2:
	var span: Vector2 = ZONES[zone_name]
	return Rect2(span.x + 12.0, WALK_AREA.position.y, span.y - span.x - 24.0, WALK_AREA.size.y)


## First and last x of a room.
static func room_range(room_name: String) -> Vector2:
	for index in range(ROOMS.size()):
		if ROOMS[index][0] == room_name:
			var to_x: float = ROOMS[index + 1][1] if index + 1 < ROOMS.size() else STORE_WIDTH
			return Vector2(ROOMS[index][1], to_x)
	return Vector2(0.0, STORE_WIDTH)


## Bottom centre of the cabinet spot of the figure at `index` of the figure order.
static func gallery_spot(index: int) -> Vector2:
	var row: int = clampi(index / GALLERY_PER_ROW, 0, GALLERY_ROW_YS.size() - 1)
	return Vector2(GALLERY_FIRST_X + (index - row * GALLERY_PER_ROW) * GALLERY_STEP_X, GALLERY_ROW_YS[row])


# --- What the game tells the store ---------------------------------------------

## Shows one scene and hides the other two behind the night.
func set_zone(zone_name: String) -> void:
	zone = zone_name
	var span: Vector2 = ZONES[zone_name]
	_zone_masks[0].position = Vector2(span.x - 4000.0, -2000.0)
	_zone_masks[1].position = Vector2(span.y, -2000.0)


## Lights and machines on or off, at once. (`_animate` is kept for the caller;
## there is no power-on sequence any more.)
func set_power(is_on: bool, _animate: bool) -> void:
	_modulate.color = Color.WHITE if is_on else DARK
	var state: String = "on" if is_on else "off"
	Sprites.set_standing_texture(_switch_sprite, Sprites.texture("props/power_switch_%s" % state, Vector2i(20, 28), Color("#4a5160")))
	Sprites.set_standing_texture(_computer, Sprites.texture("props/computer_%s" % state, Vector2i(30, 30), C_INK))
	for machine_id in machines:
		var machine: Dictionary = machines[machine_id]
		machine["off"].visible = not is_on
		machine["anim"].visible = is_on
		if is_on:
			machine["anim"].play("%s_idle" % machine_id)
		else:
			machine["anim"].stop()


func set_coin_collected(index: int, collected: bool, _animate: bool = false) -> void:
	coins[index].visible = not collected


## `text` is the bare amount ("50", "250K").
func set_price_text(machine_id: String, text: String) -> void:
	machines[machine_id]["price"].text = text


## Whether the player could pay for a machine right now: its price lights up.
func set_affordable(machine_id: String, affordable: bool) -> void:
	machines[machine_id]["affordable"] = affordable
	machines[machine_id]["price"].affordable = affordable


## The exit key lies on the counter until the player buys it.
func set_key_on_counter(shown: bool) -> void:
	_key.visible = shown


## `rate` is spins per second for the whole team; 0 means the robots are idle.
func set_robots(machine_id: String, count: int, rate: float) -> void:
	var robots: Array = machines[machine_id]["robots"]
	for index in range(robots.size()):
		robots[index].visible = index < count
		if index < count:
			robots[index].play("robot_work" if rate > 0.0 else "robot_idle")


## Shows every figure in the cabinet. `figures` is an ordered Array of
## {id, discovered, rarity_id}. A discovered figure stands on the base of its
## rarity and plays its idle loop; an undiscovered one is its still picture as
## a dark silhouette with no base, so nothing gives its rarity away.
func set_display(figures: Array) -> void:
	for index in range(figures.size()):
		var figure_id: String = figures[index]["id"]
		var foot: Vector2 = gallery_spot(index)
		if not gallery.has(figure_id):
			var sprite: AnimatedSprite2D = Sprites.figure_sprite(figure_id)
			sprite.scale *= GALLERY_SCALE
			sprite.z_index = Z_WALL + 3
			add_child(sprite)
			gallery[figure_id] = {"figure": sprite, "base": null}
		var entry: Dictionary = gallery[figure_id]
		var shown: AnimatedSprite2D = entry["figure"]
		if not bool(figures[index]["discovered"]):
			shown.position = foot
			shown.modulate = SILHOUETTE
			shown.stop()
			shown.animation = Sprites.FIGURE_STILL
			continue
		if entry["base"] == null:
			var base: AnimatedSprite2D = Sprites.base_sprite(str(figures[index].get("rarity_id", "common")))
			base.position = foot - Vector2(Sprites.BASE_WORLD.x / 2.0, Sprites.BASE_WORLD.y) * GALLERY_SCALE
			base.scale *= GALLERY_SCALE
			base.z_index = Z_WALL + 2
			add_child(base)
			entry["base"] = base
		shown.position = foot + Vector2(0.0, (Sprites.BASE_STAND_WORLD.y - Sprites.BASE_WORLD.y) * GALLERY_SCALE)
		shown.modulate = Color.WHITE
		if shown.animation != Sprites.FIGURE_IDLE or not shown.is_playing():
			shown.play(Sprites.FIGURE_IDLE)


func play_door_open() -> void:
	Sprites.set_standing_texture(_door_sprite, Sprites.texture("props/door_open", DOOR_SIZE, Color("#f6e7c1")))


func reset_door() -> void:
	Sprites.set_standing_texture(_door_sprite, Sprites.texture("props/door_closed", DOOR_SIZE, Color("#1f3a8a")))


# --- Building --------------------------------------------------------------------

## Back wall, floor, cornice, skirting, pillars between rooms and the near ledge.
func _build_shell() -> void:
	for index in range(ROOMS.size()):
		var room: Array = ROOMS[index]
		var to_x: float = ROOMS[index + 1][1] if index + 1 < ROOMS.size() else STORE_WIDTH
		_tiled("tiles/%s" % room[2], Rect2(room[1], WALL_TOP, to_x - room[1], WALL_HEIGHT), Vector2i(16, 16), Color(room[4]))
		_tiled("tiles/%s" % room[3], Rect2(room[1], 0.0, to_x - room[1], FLOOR_DEPTH), Vector2i(16, 10), Color(room[5]))
	_tiled("tiles/wall_top", Rect2(0.0, WALL_TOP, STORE_WIDTH, CORNICE_HEIGHT), Vector2i(16, 8), Color("#4a5160"))
	_tiled("tiles/trim", Rect2(0.0, -TRIM_HEIGHT, STORE_WIDTH, TRIM_HEIGHT), Vector2i(16, 6), Color("#8a5a3a"))
	var pillar_xs: Array = [0.0, STORE_WIDTH - PILLAR_WIDTH]
	for index in range(1, ROOMS.size()):
		pillar_xs.append(ROOMS[index][1] - PILLAR_WIDTH / 2.0)
	for x in pillar_xs:
		_tiled("tiles/pillar", Rect2(x, WALL_TOP + CORNICE_HEIGHT, PILLAR_WIDTH, WALL_HEIGHT - CORNICE_HEIGHT), Vector2i(14, 16), Color("#dccaa6"))
	_tiled("tiles/front_ledge", Rect2(0.0, FLOOR_DEPTH, STORE_WIDTH, LEDGE_HEIGHT), Vector2i(16, 8), Color("#4a3a34")).z_index = Z_LEDGE


func _build_coins() -> void:
	for index in range(COIN_SPOTS.size()):
		var coin: Node2D = _interactable("Coin%d" % index, COIN_SPOTS[index], COIN_REACH)
		coin.z_index = floor_z(COIN_SPOTS[index].y)
		coin.set_meta("coin_index", index)
		var spin: AnimatedSprite2D = Sprites.animated(["coin_spin"], COIN_SIZE, Color("#f2b632"))
		spin.play("coin_spin")
		coin.add_child(spin)
		coins.append(coin)


func _build_switch() -> void:
	power_switch = _interactable("PowerSwitch", Vector2(SWITCH_AT.x, 0.0), WALL_USE_REACH)
	power_switch.use_offset = WALL_USE_OFFSET
	power_switch.z_index = Z_WALL
	_switch_sprite = Sprites.standing("props/power_switch_off", Vector2i(20, 28), Color("#4a5160"))
	_switch_sprite.position = Vector2(0.0, SWITCH_AT.y)
	power_switch.add_child(_switch_sprite)


func _build_machine(machine_id: String) -> void:
	var at: Vector2 = MACHINE_SPOTS[machine_id]
	var canvas: Vector2i = BIG_SIZE if BIG_MACHINES.has(machine_id) else GACHA_SIZE
	_shadow(at, canvas.x / 2.0)
	_solid(at, canvas.x - FOOTPRINT_INSET, at.y)
	var root: Node2D = Node2D.new()
	root.name = machine_id
	root.position = at
	root.z_index = floor_z(at.y)
	add_child(root)
	var off: Sprite2D = Sprites.standing("machines/%s" % machine_id, canvas, Color("#7a2a22"))
	root.add_child(off)
	var anim: AnimatedSprite2D = Sprites.animated(["%s_idle" % machine_id], canvas, Color("#e2231a"), off.texture)
	root.add_child(anim)
	var price: Node2D = PriceSign.new()
	price.name = "Price_%s" % machine_id
	price.position = at + PRICE_OFFSET
	price.z_index = Z_DECAL
	add_child(price)
	var robots: Array = []
	for index in range(ROBOT_OFFSETS.size()):
		var robot: AnimatedSprite2D = Sprites.animated(["robot_idle", "robot_work"], ROBOT_SIZE)
		robot.position = at + ROBOT_OFFSETS[index]
		robot.flip_h = ROBOT_FLIPS[index]
		robot.z_index = floor_z(robot.position.y)
		robot.visible = false
		add_child(robot)
		robots.append(robot)
	var body: Node2D = _interactable("Use_%s" % machine_id, at, MACHINE_REACH)
	body.use_offset = MACHINE_USE_OFFSET
	machines[machine_id] = {"id": machine_id, "root": root, "at": at, "canvas": canvas, "off": off, "anim": anim,
		"price": price, "robots": robots, "body": body, "affordable": false}


## The cabinet: a dark back board in an ink frame and one plank per shelf.
## `set_display` stands the figures on them.
func _build_cabinet() -> void:
	_rect(Rect2(GALLERY_CABINET.position - Vector2(2.0, 2.0), GALLERY_CABINET.size + Vector2(4.0, 2.0)), C_INK, Z_WALL)
	_rect(GALLERY_CABINET, Color("#3b2a24"), Z_WALL)
	for row_y in GALLERY_ROW_YS:
		_rect(Rect2(GALLERY_CABINET.position.x, row_y, GALLERY_CABINET.size.x, 2.0), Color("#b9743f"), Z_WALL + 1)


func _build_reception() -> void:
	door = _interactable("FrontDoor", Vector2(DOOR_X, 0.0), WALL_USE_REACH)
	door.use_offset = WALL_USE_OFFSET
	door.z_index = Z_WALL
	_door_sprite = Sprites.standing("props/door_closed", DOOR_SIZE, Color("#1f3a8a"))
	door.add_child(_door_sprite)
	reception = _interactable("Reception", COUNTER_AT, COUNTER_REACH)
	reception.use_offset = Vector2(0.0, 10.0)
	reception.z_index = floor_z(COUNTER_AT.y)
	_shadow(COUNTER_AT, COUNTER_SIZE.x / 2.0)
	_solid(COUNTER_AT, COUNTER_SIZE.x - FOOTPRINT_INSET, COUNTER_DEPTH)
	reception.add_child(Sprites.standing("props/counter", COUNTER_SIZE, Color("#9c1420")))
	_computer = Sprites.standing("props/computer_off", Vector2i(30, 30), C_INK)
	_computer.position = COMPUTER_OFFSET
	reception.add_child(_computer)
	_key = Sprites.standing("props/key", Vector2i(14, 10), Color("#f2b632"))
	_key.position = KEY_OFFSET
	reception.add_child(_key)


func _build_sofa() -> void:
	sofa = _interactable("Sofa", SOFA_AT, SOFA_REACH)
	sofa.use_offset = Vector2(0.0, 10.0)
	sofa.z_index = floor_z(SOFA_AT.y)
	_shadow(SOFA_AT, SOFA_SIZE.x / 2.0)
	_solid(SOFA_AT, SOFA_SIZE.x - FOOTPRINT_INSET, SOFA_DEPTH)
	sofa.add_child(Sprites.standing("props/sofa", SOFA_SIZE, Color("#9c1420")))


## Plain wooden doors on the back wall, and the two masks that hide whatever
## is outside the current scene.
func _build_zone_doors() -> void:
	for row in ZONE_DOORS:
		var node: Node2D = _interactable(row[0], Vector2(row[1], 0.0), WALL_USE_REACH)
		node.use_offset = WALL_USE_OFFSET
		node.z_index = Z_WALL
		var half: float = ZONE_DOOR_SIZE.x / 2.0
		var tall: float = ZONE_DOOR_SIZE.y
		for part in [[Rect2(-half - 2.0, -tall - 2.0, ZONE_DOOR_SIZE.x + 4.0, tall + 2.0), C_INK],
				[Rect2(-half, -tall, ZONE_DOOR_SIZE.x, tall), Color("#9c5a2e")],
				[Rect2(half - 7.0, -32.0, 3.0, 4.0), Color("#f2b632")]]:
			node.add_child(_plain(part[0], part[1]))
		zone_doors.append({"node": node, "zone": row[2], "to": Vector2(row[3], 0.0) + WALL_USE_OFFSET})
	for index in range(2):
		_zone_masks.append(_rect(Rect2(0.0, 0.0, 4000.0, 4000.0), C_NIGHT, Z_MASK))


# --- Helpers ------------------------------------------------------------------

func _tiled(path: String, area: Rect2, fallback_size: Vector2i, fallback_color: Color) -> TextureRect:
	var rect: TextureRect = Sprites.tiled(path, area, fallback_size, fallback_color)
	add_child(rect)
	return rect


func _plain(area: Rect2, color: Color) -> ColorRect:
	var rect: ColorRect = ColorRect.new()
	rect.position = area.position
	rect.size = area.size
	rect.color = color
	rect.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return rect


func _rect(area: Rect2, color: Color, layer: int) -> ColorRect:
	var rect: ColorRect = _plain(area, color)
	rect.z_index = layer
	add_child(rect)
	return rect


## A soft drop shadow on the floor under something `half_width` wide.
func _shadow(at: Vector2, half_width: float) -> void:
	var shadow: Polygon2D = Sprites.ellipse(Vector2(half_width + 2.0, 4.0), SHADOW_COLOR)
	shadow.position = at + Vector2(0.0, -1.0)
	shadow.z_index = Z_SHADOW
	add_child(shadow)


## Makes a footprint solid: `front` is its front edge's centre, and it reaches
## `depth` back from there (never past the wall line).
func _solid(front: Vector2, width: float, depth: float) -> void:
	var back: float = maxf(front.y - depth, 0.0)
	solids.append(Rect2(front.x - width / 2.0, back, width, front.y - back))


func _interactable(node_name: String, at: Vector2, reach: float) -> Node2D:
	var node: Node2D = Interactable.new()
	node.name = node_name
	node.position = at
	node.reach = reach
	add_child(node)
	interactables.append(node)
	return node
