extends Node2D
## The toy store, built in code and stripped to what the game needs: walls and
## floor, the doors between its four scenes, and the things the player uses
## (floor coins, the machines, the counter, the front door, the sofa and, down
## in the cellar, the fuse box and the shelves of boxed figures). No decoration and nothing that moves by
## itself: the whole set is to be redone. Presentation only: it never changes
## game state.
##
## Seen flat from the side, after the owner's concept board: a tall, dark
## back wall, a shallow checkered floor in front of it to walk along, warm
## pools of light under hanging lamps, and a black edge with silhouettes in
## front of everything.
##
## Units are world pixels. The back wall stands on the line y = 0 and rises to
## WALL_TOP; the floor runs from y = 0 (far) to FLOOR_DEPTH (near). Everything
## standing on the floor is anchored at the bottom centre of its picture and
## drawn in order of that y (see `floor_z`).

const Interactable = preload("res://scripts/world/interactable.gd")
const Sprites = preload("res://scripts/world/sprite_lib.gd")
const PriceSign = preload("res://scripts/world/price_tag.gd")

const C_INK: Color = Color("#140c0a")
const C_NIGHT: Color = Color("#0b0706")
## Everything is dimmed by this and lit back up by the lamps: with the power
## on, a warm dusk; with it off, a cold dark still light enough to find the way.
const LIT: Color = Color(0.74, 0.62, 0.52)
const DARK: Color = Color(0.3, 0.33, 0.5)
const LAMP_LIGHT: Color = Color(1.0, 0.72, 0.38)
const SHADOW_COLOR: Color = Color(0.0, 0.0, 0.05, 0.28)

# --- Layout -----------------------------------------------------------------
const WALL_HEIGHT: float = 184.0
const WALL_TOP: float = -WALL_HEIGHT
const FLOOR_DEPTH: float = 44.0
const LEDGE_HEIGHT: float = 12.0
const CORNICE_HEIGHT: float = 8.0
const TRIM_HEIGHT: float = 6.0
const PILLAR_WIDTH: float = 14.0
## A darker band along the foot of the wall, under a rail.
const DADO_HEIGHT: float = 46.0
## The wall is boarded: a seam every so often.
const WALL_BOARD: float = 18.0
## The floor is a checkerboard drawn in perspective: tiles this wide at the
## wall, rows that deepen towards us, the whole fanning out from the middle of
## each scene.
const FLOOR_TILE: float = 22.0
const FLOOR_ROWS: Array = [0.0, 6.0, 14.0, 26.0, 44.0]
const FLOOR_FAN: float = 1.14
## Rooms from left to right: name, first x, wall colour, the floor's dark and
## light tile.
const ROOMS: Array = [
	["bath", 0.0, "#22403d", "#182b2a", "#7fa39a"],
	["corridor", 300.0, "#3b2318", "#2a1a13", "#a2703c"],
	["hall", 400.0, "#3b2318", "#2a1a13", "#a2703c"],
	["reception", 840.0, "#3b2318", "#2a1a13", "#a2703c"],
	["staff", 1010.0, "#33261a", "#2a1a13", "#8a6a3a"],
	["cellar", 1280.0, "#24262c", "#15161a", "#565a63"],
]
const STORE_WIDTH: float = 1640.0
## Four scenes share this strip; only one shows at a time. Name -> first and last x.
const ZONES: Dictionary = {
	"bath": Vector2(0.0, 300.0),
	"store": Vector2(300.0, 1010.0),
	"staff": Vector2(1010.0, 1280.0),
	"cellar": Vector2(1280.0, 1640.0),
}
## Doors between scenes, on the back wall: name, x, the zone it leads to, the
## x of the door on the other side and its kind ("door", or stairs going
## "down" or "up").
const ZONE_DOORS: Array = [
	["BathroomDoor", 328.0, "bath", 270.0, "door"],
	["BathroomExit", 270.0, "store", 328.0, "door"],
	["StaffDoor", 714.0, "staff", 1036.0, "door"],
	["StaffExit", 1036.0, "store", 714.0, "door"],
	["CellarStairs", 1244.0, "cellar", 1314.0, "down"],
	["CellarExit", 1314.0, "staff", 1244.0, "up"],
]
const ZONE_DOOR_SIZE: Vector2 = Vector2(28.0, 62.0)
## The part of the floor feet may stand on.
const WALK_AREA: Rect2 = Rect2(12.0, 6.0, STORE_WIDTH - 24.0, FLOOR_DEPTH - 8.0)
## What the camera must show from top to bottom: the wall and the floor ledge.
const VIEW_TOP: float = WALL_TOP
const VIEW_BOTTOM: float = FLOOR_DEPTH + LEDGE_HEIGHT

# --- Draw order ---------------------------------------------------------------
const Z_WALL: int = 5
const Z_DECAL: int = 20
const Z_SHADOW: int = 30
## Things standing on the floor: this plus their floor y.
const FLOOR_Z_BASE: int = 100
const Z_GLOW: int = 500
## The black edge in front of everything, and what stands on it.
const Z_FRONT: int = 600
const Z_MASK: int = 950

# --- Things the player uses ---------------------------------------------------
## Where every night starts: on the floor in front of the staff room sofa.
const SPAWN: Vector2 = Vector2(1126.0, 30.0)
## Three coins on the staff room floor.
const COIN_SPOTS: Array = [Vector2(1072.0, 36.0), Vector2(1092.0, 40.0), Vector2(1178.0, 38.0)]
const COIN_REACH: float = 13.0
const COIN_SIZE: Vector2i = Vector2i(12, 12)
## The fuse box that powers the store, on the cellar wall.
const SWITCH_AT: Vector2 = Vector2(1364.0, -30.0)
## Things on the wall are used from the floor this far in front of it.
const WALL_USE_OFFSET: Vector2 = Vector2(0.0, 10.0)
const WALL_USE_REACH: float = 22.0
## Bottom centre of each machine: the front edge of its footprint.
const MACHINE_SPOTS: Dictionary = {
	"machine_001": Vector2(430.0, 14.0),
	"machine_002": Vector2(494.0, 14.0),
	"machine_005": Vector2(566.0, 16.0),
	"machine_006": Vector2(648.0, 16.0),
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
const COUNTER_AT: Vector2 = Vector2(852.0, 22.0)
const COUNTER_SIZE: Vector2i = Vector2i(100, 50)
const COUNTER_DEPTH: float = 12.0
const COUNTER_REACH: float = 36.0
## Bottom centres of the computer and the key, relative to the counter's.
const COMPUTER_OFFSET: Vector2 = Vector2(-30.0, -37.0)
## The computer is the owner's picture, drawn far finer than the rest: three
## sprite pixels per world pixel, so one of them is one screen pixel.
const COMPUTER_SCALE: float = 1.0 / 3.0
const COMPUTER_SIZE: Vector2i = Vector2i(84, 84)
const KEY_OFFSET: Vector2 = Vector2(-7.0, -40.0)
const DOOR_X: float = 974.0
const DOOR_SIZE: Vector2i = Vector2i(58, 88)
## The sign hanging above the counter: its board, relative to the counter's
## bottom centre.
const RECEPTION_SIGN: Rect2 = Rect2(-33.0, -128.0, 66.0, 16.0)
const SIGN_TEXT_SCALE: float = 1.0 / 3.0
const SOFA_AT: Vector2 = Vector2(1126.0, 20.0)
const SOFA_SIZE: Vector2i = Vector2i(80, 46)
const SOFA_DEPTH: float = 20.0
const SOFA_REACH: float = 30.0
## Where the sleeping player sits, relative to the sofa's bottom centre.
const SOFA_SEAT: Vector2 = Vector2(0.0, -12.0)

# --- The cellar rack: one closed box per figure ------------------------------------
const GALLERY_PER_ROW: int = 10
## Centre of the first column and the step between columns.
const GALLERY_FIRST_X: float = 1498.0
const GALLERY_STEP_X: float = 12.0
## y of the bottom of the boxes on each deck, top to bottom.
const GALLERY_ROW_YS: Array = [-100.0, -76.0]
## The part of the rack the boxes stand in: left edge, top and size.
const GALLERY_CABINET: Rect2 = Rect2(1488.0, -121.0, 128.0, 49.0)
## A figure's box, relative to its bottom centre, and the sticker it gets once
## that figure has been found.
const BOX: Rect2 = Rect2(-5.0, -17.0, 10.0, 17.0)
const BOX_STICKER: Rect2 = Rect2(-3.0, -11.0, 6.0, 5.0)
## The rack is used from the floor in front of its middle.
const RACK_REACH: float = 40.0
## The poker table: bottom centre, world size, and where the candle's flame
## burns relative to that bottom centre.
const POKER_AT: Vector2 = Vector2(1426.0, 24.0)
const POKER_SIZE: Vector2i = Vector2i(92, 50)
const POKER_DEPTH: float = 10.0
const FLAME_OFFSET: Vector2 = Vector2(0.0, -34.0)
const CANDLE_LIGHT: Color = Color(1.0, 0.66, 0.3)
## The stock rack: old slotted steel, the kind every stockroom has.
const C_STEEL: Color = Color("#6f7c80")
const C_STEEL_LIGHT: Color = Color("#9aa7a8")
const C_STEEL_DARK: Color = Color("#3b4548")
const C_RUST: Color = Color("#8a4a2a")
const C_CARDBOARD: Color = Color("#b08a55")
const CAPSULE_COLORS: Array = ["#c8402e", "#e0a030", "#3d8a8f", "#e8d8b0", "#7a4a8a"]
## Its lower shelves (y of each deck) hold stock, not figures.
const RACK_STOCK_YS: Array = [-46.0, -12.0]

# --- Dressing: just enough to try the look ------------------------------------
## Hanging lamps, by x. Each lights a patch of wall and a pool on the floor.
const LAMP_XS: Array = [150.0, 398.0, 502.0, 607.0, 714.0, 852.0, 1126.0, 1552.0]
const LAMP_SIZE: Vector2i = Vector2i(30, 34)
const LAMP_CORD: float = 14.0
## Things on the wall: picture, bottom centre, world size.
const WALL_THINGS: Array = [
	["props/sign_gacha", Vector2(540.0, -128.0), Vector2i(110, 28)],
	["props/poster_a", Vector2(232.0, -84.0), Vector2i(28, 36)],
	["props/poster_c", Vector2(404.0, -88.0), Vector2i(28, 36)],
	["props/poster_b", Vector2(1104.0, -84.0), Vector2i(28, 36)],
	["props/poster_d", Vector2(762.0, -84.0), Vector2i(28, 36)],
]
## Silhouettes on the front edge: x and kind. They stand this far below the
## floor's near edge, so they never hide much of whoever walks behind them.
const FRONT_BASE: float = FLOOR_DEPTH + 9.0
const FRONT_THINGS: Array = [[40.0, "crate"], [262.0, "plant"], [384.0, "crate"], [520.0, "barrel"], [690.0, "plant"],
	[770.0, "crate"], [1200.0, "plant"], [1296.0, "barrel"], [1580.0, "crate"]]

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
## figure_id -> {box: ColorRect, sticker: ColorRect}. The sticker shows once
## the figure has been discovered.
var gallery: Dictionary = {}
## The stock rack: using it opens the record of figures.
var stock: Node2D
## The scene showing now: a key of ZONES.
var zone: String = "bath"
## Doors between scenes: {node, zone, to}; `to` is where the player comes out.
var zone_doors: Array = []

var _zone_masks: Array = []
var _modulate: CanvasModulate
var _switch_sprite: Sprite2D
var _computer: Sprite2D
var _powered: bool = false
var _computer_happy: bool = false
var _key: Sprite2D
var _door_sprite: Sprite2D
## {sprite, light} per hanging lamp.
var _lamps: Array = []


func _ready() -> void:
	_modulate = CanvasModulate.new()
	add_child(_modulate)
	_build_shell()
	_build_dressing()
	_build_coins()
	_build_switch()
	for machine_id in MACHINE_SPOTS:
		_build_machine(machine_id)
	_build_cabinet()
	_build_poker()
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
	_modulate.color = LIT if is_on else DARK
	var state: String = "on" if is_on else "off"
	for lamp in _lamps:
		lamp["sprite"].texture = Sprites.texture("props/lamp_%s" % state, LAMP_SIZE, Color("#4a5160"))
		lamp["light"].visible = is_on
	Sprites.set_standing_texture(_switch_sprite, Sprites.texture("props/power_switch_%s" % state, Vector2i(20, 28), Color("#4a5160")))
	_powered = is_on
	_show_computer()
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


## The computer lights up with delight (the owner's "kawai" picture) while
## `happy`: the game sets it when the player steps up to the counter.
func set_computer_happy(happy: bool) -> void:
	if happy != _computer_happy:
		_computer_happy = happy
		_show_computer()


func _show_computer() -> void:
	var picture: String = "pc_off"
	if _powered:
		picture = "pc_kawai" if _computer_happy else "pc_on"
	Sprites.set_standing_texture(_computer, Sprites.texture("props/%s" % picture, COMPUTER_SIZE, C_INK))


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


## One closed box per figure on the stock rack. `figures` is an ordered Array
## of {id, discovered, rarity_id}. Nothing of the figure shows: a box whose
## figure has been found only carries a sticker. The record itself is the
## catalog, opened by using the rack.
func set_display(figures: Array) -> void:
	for index in range(figures.size()):
		var figure_id: String = figures[index]["id"]
		if not gallery.has(figure_id):
			var foot: Vector2 = gallery_spot(index)
			_rect(Rect2(foot + BOX.position - Vector2(1.0, 1.0), BOX.size + Vector2(2.0, 1.0)), C_INK, Z_WALL + 1)
			var box: ColorRect = _rect(Rect2(foot + BOX.position, BOX.size), C_CARDBOARD, Z_WALL + 1)
			_rect(Rect2(foot + BOX.position, Vector2(BOX.size.x, 2.0)), Color("#d3ae74"), Z_WALL + 1)
			_rect(Rect2(foot.x - 1.0, foot.y + BOX.position.y, 2.0, 4.0), Color("#8a6a40"), Z_WALL + 1)          # tape
			var sticker: ColorRect = _rect(Rect2(foot + BOX_STICKER.position, BOX_STICKER.size), Color("#e8d8b0"), Z_WALL + 1)
			sticker.add_child(_plain(Rect2(1.0, 2.0, BOX_STICKER.size.x - 2.0, 1.0), Color("#c8402e")))
			gallery[figure_id] = {"box": box, "sticker": sticker}
		gallery[figure_id]["sticker"].visible = bool(figures[index]["discovered"])


func play_door_open() -> void:
	Sprites.set_standing_texture(_door_sprite, Sprites.texture("props/door_open", DOOR_SIZE, Color("#f6e7c1")))


func reset_door() -> void:
	Sprites.set_standing_texture(_door_sprite, Sprites.texture("props/door_closed", DOOR_SIZE, Color("#1f3a8a")))


# --- Building --------------------------------------------------------------------

## Back wall, floor and the black edge in front: flat colour and a few lines.
func _build_shell() -> void:
	for index in range(ROOMS.size()):
		var room: Array = ROOMS[index]
		var to_x: float = ROOMS[index + 1][1] if index + 1 < ROOMS.size() else STORE_WIDTH
		_rect(Rect2(room[1], WALL_TOP, to_x - room[1], WALL_HEIGHT), Color(room[2]), 0)
		_rect(Rect2(room[1], 0.0, to_x - room[1], FLOOR_DEPTH), Color(room[3]), 0)
	var x: float = WALL_BOARD
	while x < STORE_WIDTH:                                                              # seams between the wall's boards
		_rect(Rect2(x, WALL_TOP, 1.0, WALL_HEIGHT), Color(0.0, 0.0, 0.0, 0.2), 1)
		x += WALL_BOARD
	_rect(Rect2(0.0, -DADO_HEIGHT, STORE_WIDTH, DADO_HEIGHT), Color(0.0, 0.0, 0.0, 0.3), 1)
	_rect(Rect2(0.0, -DADO_HEIGHT - 3.0, STORE_WIDTH, 3.0), Color("#6b4226"), 2)
	_rect(Rect2(0.0, WALL_TOP, STORE_WIDTH, CORNICE_HEIGHT), C_INK, 2)
	_rect(Rect2(0.0, -TRIM_HEIGHT, STORE_WIDTH, TRIM_HEIGHT), C_INK, 2)
	for index in range(ROOMS.size() + 1):                                               # a post where two rooms meet
		var post_x: float = clampf((ROOMS[index][1] if index < ROOMS.size() else STORE_WIDTH) - PILLAR_WIDTH / 2.0, 0.0, STORE_WIDTH - PILLAR_WIDTH)
		_rect(Rect2(post_x, WALL_TOP, PILLAR_WIDTH, WALL_HEIGHT), Color("#1f120d"), 2)
		_rect(Rect2(post_x, WALL_TOP, 2.0, WALL_HEIGHT), Color("#5a3a26"), 2)
	_build_checker()
	_rect(Rect2(0.0, 0.0, STORE_WIDTH, 3.0), Color(0.0, 0.0, 0.0, 0.35), 2)                      # the wall's shadow on the floor
	_rect(Rect2(0.0, FLOOR_DEPTH, STORE_WIDTH, LEDGE_HEIGHT + 40.0), C_NIGHT, Z_FRONT)


## The light tiles of the checkerboard, each a quad: rows deepen towards the
## front and the columns fan out from the middle of their scene.
func _build_checker() -> void:
	for zone_name in ZONES:
		var span: Vector2 = ZONES[zone_name]
		var centre: float = (span.x + span.y) / 2.0
		var columns: int = int(ceil((span.y - span.x) / FLOOR_TILE))
		for row in range(FLOOR_ROWS.size() - 1):
			for column in range(columns):
				if (row + column) % 2 != 0:
					continue
				var left: float = span.x + column * FLOOR_TILE
				var corners: PackedVector2Array = PackedVector2Array()
				for corner in [[left, FLOOR_ROWS[row]], [left + FLOOR_TILE, FLOOR_ROWS[row]], [left + FLOOR_TILE, FLOOR_ROWS[row + 1]], [left, FLOOR_ROWS[row + 1]]]:
					var fan: float = 1.0 + (FLOOR_FAN - 1.0) * corner[1] / FLOOR_DEPTH
					corners.append(Vector2(clampf(centre + (corner[0] - centre) * fan, span.x, span.y), corner[1]))
				var tile: Polygon2D = Polygon2D.new()
				tile.polygon = corners
				tile.color = _light_tile(left + FLOOR_TILE / 2.0)
				tile.z_index = 1
				add_child(tile)


func _light_tile(x: float) -> Color:
	for index in range(ROOMS.size() - 1, -1, -1):
		if x >= ROOMS[index][1]:
			return Color(ROOMS[index][4])
	return Color(ROOMS[0][4])


## Lamps with their light, a sign and three posters on the wall, and the
## silhouettes that stand on the front edge.
func _build_dressing() -> void:
	for row in WALL_THINGS:
		var thing: Sprite2D = Sprites.standing(row[0], row[2])
		thing.position = row[1]
		thing.z_index = Z_WALL
		add_child(thing)
	var additive: CanvasItemMaterial = CanvasItemMaterial.new()
	additive.blend_mode = CanvasItemMaterial.BLEND_MODE_ADD
	for x in LAMP_XS:
		_rect(Rect2(x - 0.5, WALL_TOP, 1.0, LAMP_CORD), C_INK, Z_WALL + 4)
		var sprite: Sprite2D = Sprites.standing("props/lamp_off", LAMP_SIZE, Color("#4a5160"))
		sprite.position = Vector2(x, WALL_TOP + LAMP_CORD + LAMP_SIZE.y)
		sprite.z_index = Z_WALL + 4
		add_child(sprite)
		var bulb: Vector2 = sprite.position + Vector2(0.0, -6.0)
		var light: Node2D = Node2D.new()
		light.z_index = Z_GLOW
		for glow in [[Vector2(96.0, 84.0), 0.07], [Vector2(64.0, 58.0), 0.09], [Vector2(36.0, 34.0), 0.12]]:       # a halo on the wall
			var halo: Polygon2D = Sprites.ellipse(glow[0], Color(LAMP_LIGHT, glow[1]), 24)
			halo.position = bulb + Vector2(0.0, glow[0].y * 0.35)
			halo.material = additive
			light.add_child(halo)
		var beam: Polygon2D = Polygon2D.new()                                               # the cone down to the floor
		beam.polygon = PackedVector2Array([bulb + Vector2(-8.0, 0.0), bulb + Vector2(8.0, 0.0), Vector2(x + 58.0, FLOOR_DEPTH * 0.6), Vector2(x - 58.0, FLOOR_DEPTH * 0.6)])
		beam.color = Color(LAMP_LIGHT, 0.07)
		beam.material = additive
		light.add_child(beam)
		var pool: Polygon2D = Sprites.ellipse(Vector2(64.0, 13.0), Color(LAMP_LIGHT, 0.2), 24)       # and its pool there
		pool.position = Vector2(x, FLOOR_DEPTH * 0.55)
		pool.material = additive
		light.add_child(pool)
		add_child(light)
		_lamps.append({"sprite": sprite, "light": light})
	for row in FRONT_THINGS:
		_silhouette(row[0], row[1])


## One black shape standing on the front edge, between us and the floor.
func _silhouette(x: float, kind: String) -> void:
	var parts: Array = []
	match kind:
		"crate":
			parts = [Rect2(x, FRONT_BASE - 13.0, 26.0, 14.0), Rect2(x + 6.0, FRONT_BASE - 22.0, 16.0, 10.0)]
		"barrel":
			parts = [Rect2(x, FRONT_BASE - 16.0, 18.0, 17.0), Rect2(x - 1.0, FRONT_BASE - 12.0, 20.0, 8.0)]
		"plant":
			parts = [Rect2(x + 3.0, FRONT_BASE - 8.0, 12.0, 9.0)]
			for leaf in [[Vector2(x + 3.0, FRONT_BASE - 16.0), -0.7], [Vector2(x + 9.0, FRONT_BASE - 20.0), 0.0], [Vector2(x + 15.0, FRONT_BASE - 16.0), 0.7]]:
				var blade: Polygon2D = Sprites.ellipse(Vector2(4.0, 11.0), C_NIGHT, 12)
				blade.position = leaf[0]
				blade.rotation = leaf[1]
				blade.z_index = Z_FRONT
				add_child(blade)
	for part in parts:
		_rect(part, C_NIGHT, Z_FRONT)


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


## The stock rack: slotted steel uprights, thin steel decks, a cross brace
## behind, rust, and cartons and a bin of loose capsules on the lower decks.
## `set_display` stands one closed box per figure on the two upper decks.
func _build_cabinet() -> void:
	stock = _interactable("Stock", Vector2(GALLERY_CABINET.get_center().x, 0.0), RACK_REACH)
	stock.use_offset = WALL_USE_OFFSET
	var left: float = GALLERY_CABINET.position.x - 4.0
	var right: float = GALLERY_CABINET.end.x + 1.0
	var top: float = GALLERY_CABINET.position.y - 6.0
	var back: int = Z_WALL
	# The cross brace, behind everything on the rack.
	for ends in [[Vector2(left + 2.0, top + 4.0), Vector2(right, RACK_STOCK_YS[0])], [Vector2(right, top + 4.0), Vector2(left + 2.0, RACK_STOCK_YS[0])]]:
		_line(ends[0], ends[1], C_STEEL_DARK, back)
	# Decks: a lit top edge, the steel, a dark lip.
	for deck_y in GALLERY_ROW_YS + RACK_STOCK_YS + [top]:
		_rect(Rect2(left, deck_y, right - left + 3.0, 3.0), C_STEEL, back + 1)
		_rect(Rect2(left, deck_y, right - left + 3.0, 1.0), C_STEEL_LIGHT, back + 1)
		_rect(Rect2(left, deck_y + 3.0, right - left + 3.0, 1.0), C_STEEL_DARK, back + 1)
	# Uprights with their row of bolt slots, down to rubber feet on the floor.
	for x in [left, right]:
		_rect(Rect2(x - 1.0, top - 2.0, 5.0, -top + 4.0), C_INK, back + 2)
		_rect(Rect2(x, top - 1.0, 3.0, -top + 1.0), C_STEEL, back + 2)
		_rect(Rect2(x, top - 1.0, 1.0, -top + 1.0), C_STEEL_LIGHT, back + 2)
		var slot_y: float = top + 3.0
		while slot_y < -4.0:
			_rect(Rect2(x + 1.0, slot_y, 1.0, 2.0), C_STEEL_DARK, back + 2)
			slot_y += 6.0
		_rect(Rect2(x - 1.0, 0.0, 5.0, 2.0), C_INK, back + 2)
	for spot in [Vector2(left, -70.0), Vector2(right, -30.0), Vector2(left + 40.0, GALLERY_ROW_YS[1]), Vector2(right - 30.0, RACK_STOCK_YS[0]), Vector2(left, -8.0)]:
		_rect(Rect2(spot, Vector2(3.0, 2.0)), C_RUST, back + 2)                                  # rust
	# Middle deck: cartons of stock, some taped, one with a label.
	var x: float = left + 6.0
	for size in [Vector2(20.0, 16.0), Vector2(16.0, 12.0), Vector2(24.0, 18.0), Vector2(14.0, 10.0), Vector2(22.0, 15.0), Vector2(18.0, 13.0)]:
		_carton(Rect2(x, RACK_STOCK_YS[0] - size.y, size.x, size.y), back + 1)
		x += size.x + 2.0
	# Bottom deck: a wire bin of loose capsules, then more cartons.
	var bin: Rect2 = Rect2(left + 6.0, RACK_STOCK_YS[1] - 20.0, 40.0, 20.0)
	for index in range(30):
		var capsule: Polygon2D = Sprites.ellipse(Vector2(2.5, 2.5), Color(CAPSULE_COLORS[(index * 7) % CAPSULE_COLORS.size()]), 8)
		capsule.position = bin.position + Vector2(4.0 + (index * 13) % 33, 5.0 + (index * 5) % 13)
		capsule.z_index = back + 1
		add_child(capsule)
	for wire in range(0, 41, 5):
		_rect(Rect2(bin.position.x + wire, bin.position.y + 2.0, 1.0, bin.size.y - 2.0), C_STEEL_DARK, back + 1)
	for bar_y in [bin.position.y + 2.0, bin.position.y + 11.0, bin.end.y - 1.0]:
		_rect(Rect2(bin.position.x, bar_y, bin.size.x + 1.0, 1.0), C_STEEL, back + 1)
	x = bin.end.x + 6.0
	for size in [Vector2(26.0, 19.0), Vector2(18.0, 14.0), Vector2(24.0, 22.0)]:
		_carton(Rect2(x, RACK_STOCK_YS[1] - size.y, size.x, size.y), back + 1)
		x += size.x + 2.0
	_build_cellar_details()


## A cardboard carton: outline, face, a lit top edge and a strip of tape.
func _carton(area: Rect2, layer: int) -> void:
	_rect(area.grow(1.0), C_INK, layer)
	_rect(area, C_CARDBOARD, layer)
	_rect(Rect2(area.position, Vector2(area.size.x, 2.0)), Color("#d3ae74"), layer)
	_rect(Rect2(area.position.x + area.size.x / 2.0 - 1.0, area.position.y, 3.0, area.size.y), Color("#8a6a40"), layer)
	if area.size.x >= 20.0:
		_rect(Rect2(area.position.x + 3.0, area.position.y + 5.0, 6.0, 5.0), Color("#e8d8b0"), layer)       # a label
		_rect(Rect2(area.position.x + 4.0, area.position.y + 7.0, 4.0, 1.0), Color("#c8402e"), layer)


## What makes it a cellar: courses of brick, pipes under the ceiling, a small
## barred window on the night, and a cobweb in the corner.
func _build_cellar_details() -> void:
	var span: Vector2 = ZONES["cellar"]
	var mortar: Color = Color(0.0, 0.0, 0.0, 0.22)
	var course: int = 0
	var y: float = WALL_TOP + CORNICE_HEIGHT
	while y < -DADO_HEIGHT - 4.0:
		_rect(Rect2(span.x, y, span.y - span.x, 1.0), mortar, 1)
		var joint: float = span.x + (0.0 if course % 2 == 0 else 12.0)
		while joint < span.y:
			_rect(Rect2(joint, y, 1.0, 9.0), mortar, 1)
			joint += 24.0
		y += 9.0
		course += 1
	# Pipes: a thick one and a thin one along the ceiling, with collars, and a
	# drop down the wall by the stairs.
	for pipe in [[WALL_TOP + 14.0, 5.0, "#5b4a3a", "#8a7256"], [WALL_TOP + 22.0, 2.0, "#3b4548", "#6f7c80"]]:
		_rect(Rect2(span.x, pipe[0], span.y - span.x, pipe[1]), Color(pipe[2]), Z_WALL)
		_rect(Rect2(span.x, pipe[0], span.y - span.x, 1.0), Color(pipe[3]), Z_WALL)
	var collar_x: float = span.x + 40.0
	while collar_x < span.y:
		_rect(Rect2(collar_x, WALL_TOP + 13.0, 3.0, 7.0), Color("#3a2c22"), Z_WALL)
		collar_x += 78.0
	_rect(Rect2(span.x + 62.0, WALL_TOP + 19.0, 4.0, WALL_HEIGHT - DADO_HEIGHT - 19.0), Color("#5b4a3a"), Z_WALL)
	_rect(Rect2(span.x + 62.0, WALL_TOP + 19.0, 1.0, WALL_HEIGHT - DADO_HEIGHT - 19.0), Color("#8a7256"), Z_WALL)
	# The window: high on the wall, barred, a little night sky behind it.
	var window: Rect2 = Rect2(span.x + 120.0, WALL_TOP + 36.0, 34.0, 18.0)
	_rect(window.grow(2.0), C_INK, Z_WALL)
	_rect(window, Color("#16233f"), Z_WALL)
	_rect(Rect2(window.position + Vector2(22.0, 4.0), Vector2(5.0, 5.0)), Color("#e8e0b8"), Z_WALL)        # the moon
	for bar in range(1, 5):
		_rect(Rect2(window.position.x + bar * 7.0 - 1.0, window.position.y, 2.0, window.size.y), Color("#2a2f33"), Z_WALL)
	_rect(Rect2(window.position.x - 3.0, window.end.y + 2.0, window.size.x + 6.0, 2.0), Color("#4a4d52"), Z_WALL)
	# A cobweb in the far top corner.
	var corner: Vector2 = Vector2(span.y - PILLAR_WIDTH, WALL_TOP + CORNICE_HEIGHT)
	for end in [Vector2(-26.0, 0.0), Vector2(-20.0, 12.0), Vector2(-10.0, 20.0), Vector2(0.0, 24.0)]:
		_line(corner, corner + end, Color(0.85, 0.85, 0.8, 0.35), Z_WALL)
	for ring in [0.45, 0.8]:
		_line(corner + Vector2(-26.0, 0.0) * ring, corner + Vector2(-20.0, 12.0) * ring, Color(0.85, 0.85, 0.8, 0.3), Z_WALL)
		_line(corner + Vector2(-20.0, 12.0) * ring, corner + Vector2(-10.0, 20.0) * ring, Color(0.85, 0.85, 0.8, 0.3), Z_WALL)
		_line(corner + Vector2(-10.0, 20.0) * ring, corner + Vector2(0.0, 24.0) * ring, Color(0.85, 0.85, 0.8, 0.3), Z_WALL)
	# Stencilled on the bricks under the window.
	var stencil: Label = Label.new()
	stencil.text = "STOCK - DO NOT OPEN"
	stencil.add_theme_font_size_override("font_size", 24)
	stencil.add_theme_color_override("font_color", Color(0.9, 0.85, 0.7, 0.4))
	stencil.scale = Vector2(1.0 / 3.0, 1.0 / 3.0)
	stencil.position = Vector2(span.x + 110.0, WALL_TOP + 70.0)
	stencil.z_index = 2
	stencil.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(stencil)


## Two mice at cards by candlelight. The candle burns whether or not the
## store has power: it is the only light down here until the fuse goes in.
func _build_poker() -> void:
	_shadow(POKER_AT, POKER_SIZE.x / 2.0 - 8.0)
	_solid(POKER_AT, POKER_SIZE.x - 30.0, POKER_DEPTH)
	var table: Sprite2D = Sprites.standing("props/poker_table", POKER_SIZE, Color("#8a5a34"))
	table.position = POKER_AT
	table.z_index = floor_z(POKER_AT.y)
	add_child(table)
	var additive: CanvasItemMaterial = CanvasItemMaterial.new()
	additive.blend_mode = CanvasItemMaterial.BLEND_MODE_ADD
	var glow: Node2D = Node2D.new()
	glow.position = POKER_AT + FLAME_OFFSET
	glow.z_index = Z_GLOW
	add_child(glow)
	for ring in [[Vector2(74.0, 56.0), 0.1], [Vector2(48.0, 36.0), 0.16], [Vector2(24.0, 18.0), 0.26]]:
		var halo: Polygon2D = Sprites.ellipse(ring[0], Color(CANDLE_LIGHT, ring[1]), 24)
		halo.material = additive
		glow.add_child(halo)
	var flame: Polygon2D = Sprites.ellipse(Vector2(1.5, 3.0), Color("#ffd27a"), 8)
	flame.position = Vector2(0.0, -2.0)
	glow.add_child(flame)
	var flicker: Tween = create_tween().set_loops()
	for step in [[1.08, 0.9], [0.94, 1.15], [1.03, 0.82], [0.97, 1.0]]:
		flicker.tween_property(glow, "scale", Vector2(step[0], step[0]), 0.13)
		flicker.parallel().tween_property(flame, "scale", Vector2(1.0, step[1]), 0.13)


func _build_reception() -> void:
	door = _interactable("FrontDoor", Vector2(DOOR_X, 0.0), WALL_USE_REACH)
	door.use_offset = WALL_USE_OFFSET
	door.z_index = Z_WALL
	_door_sprite = Sprites.standing("props/door_closed", DOOR_SIZE, Color("#1f3a8a"))
	door.add_child(_door_sprite)
	var board: Rect2 = Rect2(COUNTER_AT + RECEPTION_SIGN.position, RECEPTION_SIGN.size)
	for chain_x in [board.position.x + 8.0, board.end.x - 9.0]:
		_rect(Rect2(chain_x, WALL_TOP, 1.0, board.position.y - WALL_TOP), C_INK, Z_WALL + 4)
	_rect(board.grow(2.0), C_INK, Z_WALL + 4)
	_rect(board, Color("#7a1f1a"), Z_WALL + 4)
	_rect(Rect2(board.position, Vector2(board.size.x, 2.0)), Color("#b0382a"), Z_WALL + 4)
	var title: Label = Label.new()
	title.text = "RECEPTION"
	title.add_theme_font_size_override("font_size", 30)
	title.add_theme_color_override("font_color", Color("#f1dca8"))
	title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	title.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	title.size = board.size / SIGN_TEXT_SCALE
	title.scale = Vector2(SIGN_TEXT_SCALE, SIGN_TEXT_SCALE)
	title.position = board.position
	title.z_index = Z_WALL + 4
	title.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(title)
	reception = _interactable("Reception", COUNTER_AT, COUNTER_REACH)
	reception.use_offset = Vector2(0.0, 10.0)
	reception.z_index = floor_z(COUNTER_AT.y)
	_shadow(COUNTER_AT, COUNTER_SIZE.x / 2.0)
	_solid(COUNTER_AT, COUNTER_SIZE.x - FOOTPRINT_INSET, COUNTER_DEPTH)
	reception.add_child(Sprites.standing("props/counter_wood", COUNTER_SIZE, Color("#68402a")))
	_computer = Sprite2D.new()
	_computer.centered = false
	_computer.scale = Vector2(COMPUTER_SCALE, COMPUTER_SCALE)
	_computer.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR
	_computer.position = COMPUTER_OFFSET
	_show_computer()
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


## Plain wooden doors and stair openings on the back wall, and the two masks
## that hide whatever is outside the current scene.
func _build_zone_doors() -> void:
	for row in ZONE_DOORS:
		var node: Node2D = _interactable(row[0], Vector2(row[1], 0.0), WALL_USE_REACH)
		node.use_offset = WALL_USE_OFFSET
		node.z_index = Z_WALL
		var half: float = ZONE_DOOR_SIZE.x / 2.0
		var tall: float = ZONE_DOOR_SIZE.y
		var parts: Array = [[Rect2(-half - 2.0, -tall - 2.0, ZONE_DOOR_SIZE.x + 4.0, tall + 2.0), C_INK]]
		if row[4] == "door":
			parts.append([Rect2(-half, -tall, ZONE_DOOR_SIZE.x, tall), Color("#9c5a2e")])
			parts.append([Rect2(half - 7.0, -32.0, 3.0, 4.0), Color("#f2b632")])
		else:
			# An open doorway on a flight of steps, seen from the side: it
			# sinks away to the right going down, climbs to the right going up.
			parts.append([Rect2(-half, -tall, ZONE_DOOR_SIZE.x, tall), Color("#060404")])
			var steps: int = 6
			var tread: float = ZONE_DOOR_SIZE.x / steps
			for step in range(steps):
				var height: float = 6.0 * (steps - step if row[4] == "down" else step + 1)
				parts.append([Rect2(-half + step * tread, -height, tread, height), Color("#3a2a20")])
				parts.append([Rect2(-half + step * tread, -height, tread, 1.0), Color("#8a6a48")])
			parts.append([Rect2(-half, -tall + 22.0, ZONE_DOOR_SIZE.x, 1.0), Color("#6b4226")])          # the handrail
		for part in parts:
			node.add_child(_plain(part[0], part[1]))
		zone_doors.append({"node": node, "zone": row[2], "to": Vector2(row[3], 0.0) + WALL_USE_OFFSET})
	for index in range(2):
		_zone_masks.append(_rect(Rect2(0.0, 0.0, 4000.0, 4000.0), C_NIGHT, Z_MASK))


# --- Helpers ------------------------------------------------------------------

func _line(from: Vector2, to: Vector2, color: Color, layer: int) -> void:
	var stroke: Line2D = Line2D.new()
	stroke.points = PackedVector2Array([from, to])
	stroke.width = 1.0
	stroke.default_color = color
	stroke.z_index = layer
	add_child(stroke)


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
