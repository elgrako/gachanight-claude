extends Node2D
## The toy store seen from a raised, oblique angle, built in code from the
## pixel-art sprites. Presentation only: it never changes game state.
##
## Units are world pixels. The back wall stands on the line y = 0 and rises to
## WALL_TOP; the floor is a deep plane from y = 0 (far) to FLOOR_DEPTH (near).
## Everything standing on the floor is anchored at the bottom centre of its
## picture, which is the front edge of its footprint, and is drawn in order of
## that y (see `floor_z`), so nearer things cover farther ones.

const Interactable = preload("res://scripts/world/interactable.gd")
const Sprites = preload("res://scripts/world/sprite_lib.gd")
const Ambient = preload("res://scripts/world/ambient.gd")
const PriceSign = preload("res://scripts/world/price_tag.gd")
const Swing = preload("res://scripts/world/swing.gd")

const C_INK: Color = Color("#161320")
const C_CREAM: Color = Color("#f6e7c1")
const C_MUSTARD: Color = Color("#f2b632")
const C_NIGHT: Color = Color("#0d1322")

# --- Layout -----------------------------------------------------------------
const WALL_HEIGHT: float = 112.0
const WALL_TOP: float = -WALL_HEIGHT
const FLOOR_DEPTH: float = 120.0
const LEDGE_HEIGHT: float = 8.0
const CORNICE_HEIGHT: float = 8.0
const TRIM_HEIGHT: float = 6.0
const WALL_TILE: Vector2i = Vector2i(16, 16)
const FLOOR_TILE: Vector2i = Vector2i(16, 10)
## Rooms from left to right: name, first x, wall tile, floor tile, placeholder
## colours of wall and floor.
const ROOMS: Array = [
	["bath", 0.0, "wall_bath", "floor_bath", "#bfd9d6", "#9fb7b9"],
	["corridor", 140.0, "wall_corridor", "floor_hall", "#f1e2bd", "#c9a27a"],
	["hall", 240.0, "wall_hall", "floor_hall", "#f3dcb4", "#c9a27a"],
	["gallery", 670.0, "wall_gallery", "floor_gallery", "#1f2f66", "#6a4a36"],
	["reception", 810.0, "wall_reception", "floor_hall", "#f1e2bd", "#c9a27a"],
	["staff", 980.0, "wall_staff", "floor_staff", "#d4b88a", "#a9825a"],
]
const STORE_WIDTH: float = 1130.0
## Three separate scenes share this strip: the bathroom, the store itself and
## the staff room. Only one shows at a time (the others are masked out), walls
## close each one, and doors lead from one to another. Name -> first and last x.
const ZONES: Dictionary = {
	"bath": Vector2(0.0, 140.0),
	"store": Vector2(140.0, 980.0),
	"staff": Vector2(980.0, 1130.0),
}
## Doors between scenes, on the back wall: name, x, the zone it leads to and
## the x of the door on the other side.
const ZONE_DOORS: Array = [
	["BathroomDoor", 168.0, "bath", 116.0],
	["BathroomExit", 116.0, "store", 168.0],
	["StaffDoor", 832.0, "staff", 1000.0],
	["StaffExit", 1000.0, "store", 832.0],
]
const ZONE_DOOR_SIZE: Vector2 = Vector2(28.0, 62.0)
## The drawn door (a 45 x 96 picture, so 30 x 64 in the world); the plain
## rectangles above are used only while it is missing.
const ZONE_DOOR_SPRITE: String = "props/zone_door"
const ZONE_DOOR_SPRITE_SIZE: Vector2i = Vector2i(30, 64)
const Z_MASK: int = 950
const PILLAR_WIDTH: float = 14.0
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
const Z_HANGING: int = 400
const Z_GLOW: int = 500
const Z_LABEL: int = 600

# --- Bathroom and corridor ------------------------------------------------------
const SPAWN: Vector2 = Vector2(60.0, 56.0)
const TOILET_AT: Vector2 = Vector2(24.0, 18.0)
const SINK_AT: Vector2 = Vector2(62.0, 10.0)
const COIN_SPOTS: Array = [Vector2(84.0, 46.0), Vector2(98.0, 80.0), Vector2(70.0, 78.0)]
const COIN_REACH: float = 13.0
const SWITCH_X: float = 212.0
const SWITCH_Y: float = -30.0
## Wall things are used from the floor this far in front of the wall.
const WALL_USE_OFFSET: Vector2 = Vector2(0.0, 10.0)
const WALL_USE_REACH: float = 22.0

# --- Hall: the machines ---------------------------------------------------------
## Bottom centre of each machine: the front edge of its footprint.
const MACHINE_SPOTS: Dictionary = {
	"machine_001": Vector2(270.0, 14.0),
	"machine_002": Vector2(334.0, 14.0),
	"machine_003": Vector2(398.0, 14.0),
	"machine_004": Vector2(462.0, 14.0),
	"machine_005": Vector2(534.0, 16.0),
	"machine_006": Vector2(618.0, 16.0),
}
const GACHA_SIZE: Vector2i = Vector2i(48, 84)
const BIG_SIZE: Vector2i = Vector2i(72, 104)
## A footprint is this much narrower than the cabinet's picture.
const FOOTPRINT_INSET: float = 6.0
const MACHINE_USE_OFFSET: Vector2 = Vector2(0.0, 10.0)
const MACHINE_REACH: float = 20.0
const MACHINE_FALLBACKS: Array = ["#e2231a", "#2e9e4f", "#f2b632", "#2f7de1", "#f0802a", "#f59ab5"]
## Used when `machines/anchors.json` is missing or lacks a value. Like that
## file, in SPRITE pixels (Sprites.ART_SCALE per world pixel), origin at the
## top-left corner of the machine's picture; `rows` is a count.
const DEFAULT_ANCHORS: Dictionary = {
	"gacha": {"chute": [36, 111]},
	"claw": {"chute": [84, 138], "claw_rail_y": 21, "claw_min_x": 27, "claw_max_x": 81, "claw_rest_x": 30, "grab_y": 51, "drop_x": 84, "drop_y": 78},
	"plinko": {"chute": [54, 141], "ball_start": [54, 21], "rows": 6, "row_step": 9, "column_step": 7.5, "slot_y": 90, "slot_xs": [24, 39, 54, 69, 84]},
}
const ANCHORS_FILE: String = "res://assets/sprites/machines/anchors.json"
## Where the tossed coin lands, relative to the machine's bottom centre: the
## coin slot drawn on the crank plate (capsule machines) or beside the chute.
const COIN_SLOTS: Dictionary = {"gacha": Vector2(4.0, -23.0), "claw": Vector2(-16.0, -20.0), "plinko": Vector2(-18.0, -15.0)}
const CAPSULE_SIZE: Vector2i = Vector2i(12, 12)
const CLAW_SIZE: Vector2i = Vector2i(20, 20)
## Centre of a held capsule below the claw's hanging point.
const CLAW_HOLD: Vector2 = Vector2(0.0, 17.0)
const CAPSULE_COLORS: Array = ["red", "blue", "green", "mustard", "gold"]
const CAPSULE_FALLBACKS: Dictionary = {"red": "#e2231a", "blue": "#2f7de1", "green": "#2e9e4f", "mustard": "#f2b632", "gold": "#ffd75e"}
## The price is a little roof sign standing on top of each machine (see
## price_tag.gd). Its feet stand this far below the top of the machine's
## canvas: the pictures leave some empty rows above the cap or the marquee.
const SIGN_SEAT: Dictionary = {"gacha": 8.0, "claw": 7.0, "plinko": 7.0}
const MAX_ROBOT_SPRITES: int = 3
const ROBOT_SIZE: Vector2i = Vector2i(28, 34)
## Where each robot of a team stands, relative to its machine's bottom centre:
## on the floor in front of it, clear of the chute. `robot_work` reaches to the
## robot's right, so the ones standing right of the controls are mirrored.
const ROBOT_OFFSETS_GACHA: Array = [Vector2(-20.0, 8.0), Vector2(20.0, 8.0), Vector2(-30.0, 18.0)]
const ROBOT_OFFSETS_BIG: Array = [Vector2(-26.0, 8.0), Vector2(40.0, 10.0), Vector2(-42.0, 18.0)]
const ROBOT_FLIPS: Array = [false, true, false]
## Team mates neither start on the same frame nor keep the same pace.
const ROBOT_FRAME_OFFSETS: Array = [0, 3, 6]
const ROBOT_PACES: Array = [1.0, 0.91, 1.08]
const ROBOT_SHADOW: Vector2 = Vector2(10.0, 3.0)
## Machines breathe at slightly different paces so the row never moves in step.
const MACHINE_IDLE_PACES: Array = [1.0, 0.93, 1.07, 0.97, 1.04, 0.9]

# --- Machines noticing the player ---------------------------------------------
## A machine greets a player who comes this close: this far to each side of it
## and no farther than this in front of it.
const NOTICE_HALF_WIDTH: float = 30.0
const NOTICE_DEPTH: float = 46.0
const GREET_HOP: float = 2.0
const NUDGE_HOP: float = 1.0
const HOP_UP_TIME: float = 0.07
const HOP_DOWN_TIME: float = 0.09
## A machine the player can pay for calls for attention this often, in seconds.
const NUDGE_EVERY: Vector2 = Vector2(5.0, 9.0)
## Kicks to the price sign's wobble, in radians per second.
const SIGN_GREET_KICK: float = 0.9
const SIGN_NUDGE_KICK: float = 0.7
const SIGN_RATTLE_KICK: float = 1.3
## The sign leans at most a fraction of what a hanging lamp swings.
const SIGN_WOBBLE: float = 0.35
## The "thinking" bubble over a machine that costs more than the player has.
const BUBBLE_SIZE: Vector2i = Vector2i(20, 14)
const BUBBLE_TIME: float = 1.5
## Its bottom centre, relative to the top centre of the machine's canvas: up
## and to the right of the head, clear of the price sign.
const BUBBLE_OFFSETS: Dictionary = {"gacha": Vector2(26.0, 14.0), "claw": Vector2(42.0, 26.0), "plinko": Vector2(42.0, 26.0)}
## Running past something that hangs stirs it: the player must be this fast.
const BREEZE_MIN_SPEED: float = 60.0
const LAMP_BREEZE_KICK: float = 0.5
## A cranking or grabbing machine shakes the lamps this near to it.
const RATTLE_REACH: float = 75.0
const LAMP_RATTLE_KICK: float = 0.6
## The crane's grab shakes the whole view by this many world pixels, this long.
const GRAB_SHAKE: float = 1.0
const GRAB_SHAKE_TIME: float = 0.14
## A capsule landing in the tray flattens for a moment: scale steps, seconds each.
const SQUASH_STEPS: Array = [Vector2(1.34, 0.67), Vector2(0.84, 1.17), Vector2.ONE]
const SQUASH_STEP_TIME: float = 0.045

# --- Gallery: one display cabinet with every figure on its rarity base ---------
## Three shelves of ten in a single cabinet on the wall. Figures and bases are
## shown at a quarter of their world size here, as miniatures; the prize panel
## and the catalog show them full size.
const GALLERY_SCALE: float = 0.25
## The same, as the scale of a node showing figure or base art, and as world
## pixels per sprite pixel of that art.
const GALLERY_ART_SCALE: float = GALLERY_SCALE / Sprites.ART_SCALE
const GALLERY_PER_ROW: int = 10
## Centre of the first column and the step between columns.
const GALLERY_FIRST_X: float = 686.0
const GALLERY_STEP_X: float = 12.0
## y of the bottom of the bases on each shelf, top to bottom.
const GALLERY_ROW_YS: Array = [-70.0, -50.0, -30.0]
## The cabinet's back board: left edge, top and size.
const GALLERY_CABINET: Rect2 = Rect2(676.0, -90.0, 128.0, 64.0)
const GALLERY_BOARD_COLOR: Color = Color("#3b2a24")
## No lamps hang in the gallery: they would cover the top shelf.
const GALLERY_GAP_XS: Array = []
const GALLERY_CONE_BOTTOM: float = 17.0
## A discovered figure hops when the player walks by this close (in x).
const GALLERY_HOP_REACH: float = 5.0
const GALLERY_HOP: float = 1.0
## Neighbours do not loop in step: start frame and pace by position.
const GALLERY_FRAME_STRIDE: int = 3
const GALLERY_PACES: Array = [1.0, 0.92, 1.08, 0.96, 1.04]
const GALLERY_SHELF_SIZE: Vector2i = Vector2i(34, 12)
## A base's bottom row sits this far below the top edge of the shelf picture.
const GALLERY_SHELF_SEAT: float = 9.0
## Silhouettes have no base: they stand straight on the shelf, a little back.
const GALLERY_SILHOUETTE_LIFT: float = 0.0
const SILHOUETTE: Color = Color(0.07, 0.08, 0.12)

# --- Reception and staff room -----------------------------------------------------
const COUNTER_AT: Vector2 = Vector2(900.0, 64.0)
const COUNTER_SIZE: Vector2i = Vector2i(100, 50)
const COUNTER_DEPTH: float = 12.0
const COUNTER_USE_OFFSET: Vector2 = Vector2(0.0, 10.0)
const COUNTER_REACH: float = 36.0
## Bottom centres of the things on the counter top, relative to the counter.
## The counter's top is the upper 14 px of its picture, and its bell is drawn
## at the right end: everything stands on the top, clear of the bell.
const COMPUTER_OFFSET: Vector2 = Vector2(-32.0, -38.0)
const KEY_OFFSET: Vector2 = Vector2(-7.0, -40.0)
## The salesman on the screen perks up when the player steps to the counter.
const COMPUTER_HOP: float = 1.0
const COMPUTER_BUBBLE: Vector2 = Vector2(13.0, -29.0)
const DOOR_X: float = 944.0
const DOOR_SIZE: Vector2i = Vector2i(58, 88)
## The glass opening inside the door picture, relative to its bottom centre.
const DOOR_OPENING: Rect2 = Rect2(-24.0, -74.0, 47.0, 70.0)
const SHELF_A_AT: Vector2 = Vector2(1956.0, 8.0)
const LOCKER_AT: Vector2 = Vector2(1030.0, 7.0)
const SOFA_AT: Vector2 = Vector2(1084.0, 20.0)
const SOFA_SIZE: Vector2i = Vector2i(80, 46)
const SOFA_DEPTH: float = 20.0
const SOFA_USE_OFFSET: Vector2 = Vector2(0.0, 10.0)
const SOFA_REACH: float = 30.0
## Where the sleeping player lies, relative to the sofa's bottom centre.
const SOFA_SEAT: Vector2 = Vector2(0.0, -12.0)
const SHELF_B_AT: Vector2 = Vector2(2300.0, 8.0)
const TABLE_AT: Vector2 = Vector2(1066.0, 92.0)
const POSTER_B_AT: Vector2 = Vector2(1084.0, -44.0)
## A one-plank wall shelf in the staff room (the radio plays on it): top-left
## corner of its picture.
const STAFF_SHELF_AT: Vector2 = Vector2(2233.0, -38.0)
const CRATE_AT: Vector2 = Vector2(782.0, 38.0)
const HALL_RUG_AT: Vector2 = Vector2(476.0, 92.0)
const GALLERY_RUG_AT: Vector2 = Vector2(1335.0, 88.0)
const POSTER_D_AT: Vector2 = Vector2(1169.0, -32.0)

# --- Lamps -------------------------------------------------------------------------
## The gallery's own lamps hang in its gaps (GALLERY_GAP_XS) and come after these.
const LAMP_XS: Array = [60.0, 302.0, 430.0, 576.0, 890.0, 1066.0]
const LAMP_SIZE: Vector2i = Vector2i(30, 34)
## The bulb sits this far below the top of the lamp picture; light starts there.
const LAMP_BULB_Y: float = 28.0
## The shade swings on its cord by this angle, in radians, at this pace.
const LAMP_SWAY: float = 0.03
const LAMP_SWAY_SPEED: float = 1.1
const LAMP_GLOW_ALPHA: float = 0.2
const LAMP_POOL_ALPHA: float = 0.13
const LAMP_GLOW_COLOR: Color = Color(1.0, 0.93, 0.66)
## The light cone: half widths at the shade and at the floor, and the floor y it reaches.
const LAMP_CONE_TOP: float = 9.0
const LAMP_CONE_BOTTOM: float = 46.0
const LAMP_POOL_Y: float = 58.0
const LAMP_POOL_RADIUS: Vector2 = Vector2(50.0, 17.0)
const MOTES_SIZE: Vector2i = Vector2i(48, 48)
## A tube coming on: lit or not, then seconds until the next step.
const LAMP_FLICKER: Array = [[true, 0.04], [false, 0.05], [true, 0.03], [false, 0.07], [true, 0.0]]

# --- Animation timing, seconds at speed 1 -----------------------------------
## From `play_prize_animation` to its tween finishing: gacha 1.2 s, crane 2.7 s,
## plinko 2.3 s at most, lead-in included.
const GACHA_BUDGET: float = 1.2
## Gacha: lead-in + the machine cranking itself + clunk + chute drop.
const CRANK_DEFAULT_TIME: float = 0.45
const CRANK_MIN_TIME: float = 0.2
const CRANK_CLUNK_TIME: float = 0.05
const CRANK_MARGIN: float = 0.02
const RATTLE_STEPS: float = 10.0
# Crane: lead-in + 2.24 s.
const CLAW_MOVE_TIME: float = 0.38
const CLAW_SETTLE_TIME: float = 0.1
const CLAW_LOWER_TIME: float = 0.32
const CLAW_GRAB_TIME: float = 0.16
const CLAW_LIFT_TIME: float = 0.36
const CLAW_CARRY_TIME: float = 0.42
const CLAW_RELEASE_TIME: float = 0.16
const CLAW_RETURN_TIME: float = 0.45
const CLAW_SWAY: float = 0.24
## The claw never picks nearer to the drop hole than this.
const CLAW_PICK_MARGIN: float = 12.0
# Plinko: lead-in + drop + hops + slot + blink + chute drop = lead-in + 1.86 s.
const PLINKO_DROP_TIME: float = 0.14
const PLINKO_HOPS_TIME: float = 1.02
const PLINKO_HOP_HEIGHT: float = 2.5
## The pegs reach this many columns to each side of the top one.
const PLINKO_MAX_COLUMNS: float = 5.0
const PLINKO_SLOT_TIME: float = 0.1
const PLINKO_HOLD_TIME: float = 0.3
const PLINKO_BLINKS: float = 3.0
const PEG_FLASH_TIME: float = 0.16
const CHUTE_DROP_TIME: float = 0.26
const CHUTE_DROP_HEIGHT: float = 7.0
const POWER_LEAD_TIME: float = 0.25
const POWER_LAMP_STEP: float = 0.07
const POWER_MACHINE_STEP: float = 0.13
## Light enough that black limbs still read against the night floor.
const DARK: Color = Color(0.38, 0.42, 0.64)
const DOOR_OPEN_TIME: float = 0.9
const DOOR_GLOW_ALPHA: float = 0.7
## How much wider than the doorway the daylight is at the near edge of the floor.
const DOOR_LIGHT_SPREAD: float = 44.0
const DOOR_MOTES: Array = [Vector2(-8.0, -44.0), Vector2(9.0, -28.0), Vector2(-3.0, -14.0), Vector2(6.0, 30.0)]
const COIN_BOB_SPEED: float = 3.0
const COIN_TWINKLE_EVERY: float = 1.7
const COIN_SIZE: Vector2i = Vector2i(12, 12)
## While robots work a machine it acts by itself, at most this often.
const ROBOT_PLAY_GAP: float = 0.15
const SHADOW_COLOR: Color = Color(0.0, 0.0, 0.05, 0.28)

# --- Celebrations ---------------------------------------------------------------
const CONFETTI_COLORS: Array = ["#e2231a", "#f2b632", "#2f7de1", "#2e9e4f", "#f59ab5", "#fff8e3"]
const CONFETTI_AMOUNT: int = 80
const CONFETTI_TIME: float = 1.7
## Half width of the strip under the cornice the confetti falls from.
const CONFETTI_SPREAD: float = 110.0
const CONFETTI_FALL: float = 95.0
const CELEBRATION_SPARKLES: int = 7
const CELEBRATION_RING: Vector2 = Vector2(26.0, 18.0)
## Sparkles ring this point, relative to the feet of whoever is celebrated.
const CELEBRATION_CENTRE: Vector2 = Vector2(0.0, -28.0)
const CELEBRATION_STEP: float = 0.07
const ROBOT_CHEER_HOP: float = 5.0
const ROBOT_CHEER_HOPS: int = 3
const LAMP_CHEER_KICK: float = 0.7

## One bounce of the plinko ball, for the sound.
signal plinko_bounced
## One machine waking up during the power-on sequence, for the sound.
signal machine_lit
## Something heavy moved: the view should shake by `pixels` for `seconds`.
signal shaken(pixels: float, seconds: float)

## machine_id -> {root, at, type, canvas, off, anim, body, price, robots, capsule, anchors..., claw, rope, ball, slot_lamp}
## `off` is the powered-off picture; `anim` the living, powered machine; `price`
## the roof sign (price_tag.gd) and `sign_swing` its wobble.
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
## figure_id -> {figure: AnimatedSprite2D, base: AnimatedSprite2D or null,
## discovered: bool, foot: Vector2, rest: Vector2, near: bool}. `foot` is the
## bottom centre of the spot (see `gallery_spot`), `rest` where the figure stands.
var gallery: Dictionary = {}
## Named furniture positions that ambient props stand on.
var furniture: Dictionary = {}
## The scene showing now: a key of ZONES.
var zone: String = "bath"
## Doors between scenes: {node, zone, to}; `to` is where the player comes out.
var zone_doors: Array = []
var _zone_masks: Array = []
## The ambient life of the store (see ambient.gd).
var ambient: Node2D
## Where the camera looks, so off-screen life can come into view. Set by main.
var view_x: float = 0.0
## The player's feet and speed on the floor, set by main every frame: the store
## only reacts to them (machines greet, figures hop, lamps stir).
var player_at: Vector2 = Vector2(-10000.0, 0.0)
var player_velocity: Vector2 = Vector2.ZERO

var _modulate: CanvasModulate
var _lamps: Array = []
var _switch_sprite: Sprite2D
var _computer: Sprite2D
var _computer_near: bool = false
var _key: Sprite2D
var _gallery_lights: Array = []
## The player's x on the previous frame and on this one (see `breeze`).
var _breeze_from: float = -10000.0
var _breeze_to: float = -10000.0
var _door_sprite: Sprite2D
var _door_glow: Polygon2D
var _door_tween: Tween
var _power_tween: Tween
var _flicker_tweens: Array = []
var _power_on: bool = false
var _anchors: Dictionary = {}
var _rng: RandomNumberGenerator = RandomNumberGenerator.new()
var _time: float = 0.0
var _next_twinkle: float = COIN_TWINKLE_EVERY

## Colour name of the capsule the last prize animation used, so the prize
## reveal can open the same capsule.
var last_capsule_color: String = "red"


func _ready() -> void:
	_rng.randomize()
	_load_anchors()
	_modulate = CanvasModulate.new()
	_modulate.color = DARK
	add_child(_modulate)
	_build_shell()
	_build_bathroom()
	_build_corridor()
	_build_hall()
	_build_gallery()
	_build_reception()
	_build_staff_room()
	_build_zone_doors()
	_build_lamps()
	ambient = Ambient.new()
	ambient.name = "Ambient"
	add_child(ambient)
	ambient.setup(self)
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


## Shows one scene and hides the other two behind the night.
func set_zone(zone_name: String) -> void:
	zone = zone_name
	var span: Vector2 = ZONES[zone_name]
	_zone_masks[0].position = Vector2(span.x - 4000.0, -2000.0)
	_zone_masks[1].position = Vector2(span.y, -2000.0)


## Plain wooden doors on the back wall, and the two masks that hide whatever
## is outside the current scene.
func _build_zone_doors() -> void:
	for row in ZONE_DOORS:
		var node: Node2D = _interactable(row[0], Vector2(row[1], 0.0), WALL_USE_REACH)
		node.use_offset = WALL_USE_OFFSET
		node.z_index = Z_WALL
		if Sprites.has_texture(ZONE_DOOR_SPRITE):
			# Bottom centre on the wall's foot line, like the plain door.
			node.add_child(Sprites.standing(ZONE_DOOR_SPRITE, ZONE_DOOR_SPRITE_SIZE))
			zone_doors.append({"node": node, "zone": row[2], "to": Vector2(row[3], 0.0) + WALL_USE_OFFSET})
			continue
		var half: float = ZONE_DOOR_SIZE.x / 2.0
		var tall: float = ZONE_DOOR_SIZE.y
		# Frame, leaf, two panels and a knob.
		var parts: Array = [
			[Rect2(-half - 2.0, -tall - 2.0, ZONE_DOOR_SIZE.x + 4.0, tall + 2.0), C_INK],
			[Rect2(-half, -tall, ZONE_DOOR_SIZE.x, tall), Color("#9c5a2e")],
			[Rect2(-half + 4.0, -tall + 5.0, ZONE_DOOR_SIZE.x - 8.0, 22.0), Color("#b9743f")],
			[Rect2(-half + 4.0, -30.0, ZONE_DOOR_SIZE.x - 8.0, 25.0), Color("#b9743f")],
			[Rect2(half - 7.0, -32.0, 3.0, 4.0), C_MUSTARD],
		]
		for part in parts:
			var piece: ColorRect = ColorRect.new()
			piece.position = part[0].position
			piece.size = part[0].size
			piece.color = part[1]
			piece.mouse_filter = Control.MOUSE_FILTER_IGNORE
			node.add_child(piece)
		zone_doors.append({"node": node, "zone": row[2], "to": Vector2(row[3], 0.0) + WALL_USE_OFFSET})
	for index in range(2):
		var mask: ColorRect = ColorRect.new()
		mask.color = C_NIGHT
		mask.size = Vector2(4000.0, 4000.0)
		mask.mouse_filter = Control.MOUSE_FILTER_IGNORE
		mask.z_index = Z_MASK
		add_child(mask)
		_zone_masks.append(mask)


## First and last x of a room.
static func room_range(room_name: String) -> Vector2:
	for index in range(ROOMS.size()):
		if ROOMS[index][0] == room_name:
			var to_x: float = ROOMS[index + 1][1] if index + 1 < ROOMS.size() else STORE_WIDTH
			return Vector2(ROOMS[index][1], to_x)
	return Vector2(0.0, STORE_WIDTH)


## Bottom centre of the gallery spot of the figure at `index` of the figure
## order: where its base stands (or the silhouette's feet, a little higher).
static func gallery_spot(index: int) -> Vector2:
	var row: int = clampi(index / GALLERY_PER_ROW, 0, GALLERY_ROW_YS.size() - 1)
	var column: int = index - row * GALLERY_PER_ROW
	return Vector2(GALLERY_FIRST_X + column * GALLERY_STEP_X, GALLERY_ROW_YS[row])


func is_power_on() -> bool:
	return _power_on


## +1 or -1 when the player ran past world x `x` during this frame (rightwards
## or leftwards), else 0: the draught that stirs whatever hangs there.
func breeze(x: float) -> float:
	if absf(player_velocity.x) < BREEZE_MIN_SPEED:
		return 0.0
	if (_breeze_from < x) == (_breeze_to < x):
		return 0.0
	return signf(_breeze_to - _breeze_from)


## Back wall, floor, cornice, skirting, pillars between rooms and the near ledge.
func _build_shell() -> void:
	for index in range(ROOMS.size()):
		var room: Array = ROOMS[index]
		var from_x: float = room[1]
		var to_x: float = ROOMS[index + 1][1] if index + 1 < ROOMS.size() else STORE_WIDTH
		_tiled("tiles/%s" % room[2], Rect2(from_x, WALL_TOP, to_x - from_x, WALL_HEIGHT), WALL_TILE, Color(room[4]))
		_tiled("tiles/%s" % room[3], Rect2(from_x, 0.0, to_x - from_x, FLOOR_DEPTH), FLOOR_TILE, Color(room[5]))
	_tiled("tiles/wall_top", Rect2(0.0, WALL_TOP, STORE_WIDTH, CORNICE_HEIGHT), Vector2i(16, 8), Color("#4a5160"))
	_tiled("tiles/trim", Rect2(0.0, -TRIM_HEIGHT, STORE_WIDTH, TRIM_HEIGHT), Vector2i(16, 6), Color("#8a5a3a"))
	var pillar_xs: Array = [0.0, STORE_WIDTH - PILLAR_WIDTH]
	for index in range(1, ROOMS.size()):
		pillar_xs.append(ROOMS[index][1] - PILLAR_WIDTH / 2.0)
	for x in pillar_xs:
		_tiled("tiles/pillar", Rect2(x, WALL_TOP + CORNICE_HEIGHT, PILLAR_WIDTH, WALL_HEIGHT - CORNICE_HEIGHT), Vector2i(14, 16), Color("#dccaa6"))
	var ledge: TextureRect = _tiled("tiles/front_ledge", Rect2(0.0, FLOOR_DEPTH, STORE_WIDTH, LEDGE_HEIGHT), Vector2i(16, 8), Color("#4a3a34"))
	ledge.z_index = Z_LEDGE


func _tiled(path: String, area: Rect2, fallback_size: Vector2i, fallback_color: Color) -> TextureRect:
	var rect: TextureRect = Sprites.tiled(path, area, fallback_size, fallback_color)
	add_child(rect)
	return rect

# --- Public presentation API --------------------------------------------------

func set_power(is_on: bool, animate: bool) -> void:
	if _power_tween != null:
		_power_tween.kill()
		_power_tween = null
	for tween in _flicker_tweens:
		if tween.is_valid():
			tween.kill()
	_flicker_tweens.clear()
	_power_on = is_on
	if is_on and animate:
		_play_power_on()
		return
	_set_switch(is_on)
	_modulate.color = Color.WHITE if is_on else DARK
	for lamp in _lamps:
		_set_lamp(lamp, is_on)
	_set_computer(is_on)
	_set_gallery_lights(is_on)
	for machine_id in machines:
		var machine: Dictionary = machines[machine_id]
		if not is_on:
			_rest_machine(machine)
		_set_machine_awake(machine, is_on, false)
	if ambient != null:
		ambient.set_power(is_on)


func set_coin_collected(index: int, collected: bool, animate: bool = false) -> void:
	var coin: Node2D = coins[index]
	if collected and animate and coin.visible:
		# The effect's first frame has the coin at the bottom of its frame.
		Sprites.burst(self, "coin_pickup", coin.position + Vector2(0.0, -14.0), Vector2i(20, 28))
	coin.visible = not collected
	coin.get_meta("shadow").visible = not collected


## `text` is the bare amount ("50", "250K"); the sign has the coin painted on.
func set_price_text(machine_id: String, text: String) -> void:
	machines[machine_id]["price"].text = text


## Tells a machine whether the player could pay for it right now. Its price
## sign lights up, and the machine calls for attention now and then.
func set_affordable(machine_id: String, affordable: bool) -> void:
	var machine: Dictionary = machines[machine_id]
	if affordable and not machine["affordable"]:
		# It has just come within reach: a first nudge soon, each in its turn.
		machine["nudge_in"] = 0.3 + 0.12 * MACHINE_SPOTS.keys().find(machine_id)
	machine["affordable"] = affordable
	machine["price"].affordable = affordable


## The exit key lies on the counter until the player buys it.
func set_key_on_counter(shown: bool) -> void:
	_key.visible = shown


## A party at `at` (someone's feet): confetti from the ceiling, a ring of
## sparkles, the robots jumping for joy and the lamps set swinging.
func celebrate(at: Vector2) -> void:
	var confetti: CPUParticles2D = CPUParticles2D.new()
	confetti.position = Vector2(at.x, WALL_TOP + CORNICE_HEIGHT)
	confetti.z_as_relative = false
	confetti.z_index = Sprites.Z_EFFECT
	confetti.amount = CONFETTI_AMOUNT
	confetti.lifetime = CONFETTI_TIME
	confetti.one_shot = true
	confetti.explosiveness = 0.7
	confetti.emission_shape = CPUParticles2D.EMISSION_SHAPE_RECTANGLE
	confetti.emission_rect_extents = Vector2(CONFETTI_SPREAD, 2.0)
	confetti.direction = Vector2.DOWN
	confetti.spread = 35.0
	confetti.gravity = Vector2(0.0, CONFETTI_FALL)
	confetti.initial_velocity_min = 10.0
	confetti.initial_velocity_max = 55.0
	# Square paper bits of two or three world pixels, in the store's colours.
	confetti.scale_amount_min = 2.0
	confetti.scale_amount_max = 3.0
	var colors: Gradient = Gradient.new()
	colors.interpolation_mode = Gradient.GRADIENT_INTERPOLATE_CONSTANT
	var stops: PackedFloat32Array = PackedFloat32Array()
	var tones: PackedColorArray = PackedColorArray()
	for index in range(CONFETTI_COLORS.size()):
		stops.append(float(index) / CONFETTI_COLORS.size())
		tones.append(Color(CONFETTI_COLORS[index]))
	colors.offsets = stops
	colors.colors = tones
	confetti.color_initial_ramp = colors
	add_child(confetti)
	confetti.emitting = true
	confetti.finished.connect(confetti.queue_free)
	var ring: Tween = create_tween()
	for index in range(CELEBRATION_SPARKLES):
		var angle: float = TAU * index / CELEBRATION_SPARKLES
		var spot: Vector2 = at + CELEBRATION_CENTRE + Vector2(cos(angle) * CELEBRATION_RING.x, sin(angle) * CELEBRATION_RING.y)
		ring.tween_callback(_sparkle.bind(spot.round()))
		ring.tween_interval(CELEBRATION_STEP)
	var order: int = 0
	for machine_id in machines:
		for robot in machines[machine_id]["robots"]:
			if robot.visible:
				_hop(robot, robot.get_meta("rest_y"), ROBOT_CHEER_HOP, ROBOT_CHEER_HOPS, 0.05 * order)
				order += 1
	for lamp in _lamps:
		if absf(lamp["x"] - at.x) < CONFETTI_SPREAD * 2.0:
			lamp["swing"].kick(LAMP_CHEER_KICK if lamp["x"] >= at.x else -LAMP_CHEER_KICK)


func _sparkle(at: Vector2) -> void:
	Sprites.burst(self, "sparkle", at, Vector2i(16, 16))


## `rate` is spins per second for the whole team; 0 means the robots are idle.
func set_robots(machine_id: String, count: int, rate: float) -> void:
	var robots: Array = machines[machine_id]["robots"]
	machines[machine_id]["robot_rate"] = rate if count > 0 else 0.0
	var cycle: float = maxf(Sprites.animation_length("robot_work"), 0.1)
	for index in range(robots.size()):
		var robot: AnimatedSprite2D = robots[index]
		robot.visible = index < count
		robot.get_meta("shadow").visible = robot.visible
		if not robot.visible:
			continue
		var wanted: String = "robot_work" if rate > 0.0 else "robot_idle"
		var pace: float = ROBOT_PACES[index % ROBOT_PACES.size()]
		robot.speed_scale = (clampf(rate * cycle, 0.5, 2.5) if rate > 0.0 else 1.0) * pace
		if robot.animation != wanted or not robot.is_playing():
			robot.play(wanted)
			# Team mates do not hop in step.
			robot.frame = ROBOT_FRAME_OFFSETS[index % ROBOT_FRAME_OFFSETS.size()] % maxi(robot.sprite_frames.get_frame_count(wanted), 1)


## Shows every figure in the gallery. `figures` is an ordered Array of
## {id, discovered, rarity_id}. A discovered figure stands on the base of its
## rarity and plays its idle loop; an undiscovered one is its still picture as
## a dark silhouette with no base at all, so nothing gives its rarity away.
func set_display(figures: Array) -> void:
	for index in range(figures.size()):
		var figure: Dictionary = figures[index]
		var figure_id: String = figure["id"]
		var foot: Vector2 = gallery_spot(index)
		# The whole cabinet hangs on the wall, behind everything on the floor.
		var layer: int = Z_WALL + 2
		var fresh: bool = not gallery.has(figure_id)
		if fresh:
			var sprite: AnimatedSprite2D = Sprites.figure_sprite(figure_id)
			sprite.scale = Vector2(GALLERY_ART_SCALE, GALLERY_ART_SCALE)
			sprite.z_index = layer + 1
			add_child(sprite)
			gallery[figure_id] = {"figure": sprite, "base": null, "discovered": false, "foot": foot, "rest": foot, "near": false}
		var entry: Dictionary = gallery[figure_id]
		var discovered: bool = bool(figure["discovered"])
		var base: AnimatedSprite2D = entry["base"]
		if discovered and base == null:
			base = Sprites.base_sprite(str(figure.get("rarity_id", "common")))
			base.position = foot - Vector2(Sprites.BASE_SIZE.x / 2.0, Sprites.BASE_SIZE.y) * GALLERY_ART_SCALE
			base.scale = Vector2(GALLERY_ART_SCALE, GALLERY_ART_SCALE)
			base.z_index = layer
			# Neighbours of one rarity do not glint in step.
			base.frame = index % maxi(base.sprite_frames.get_frame_count(base.animation), 1)
			add_child(base)
			entry["base"] = base
		if base != null:
			base.visible = discovered
		var sprite_now: AnimatedSprite2D = entry["figure"]
		if discovered:
			entry["rest"] = foot + Vector2(0.0, (Sprites.BASE_STAND.y - Sprites.BASE_SIZE.y) * GALLERY_ART_SCALE)
			sprite_now.modulate = Color.WHITE
			if sprite_now.animation != Sprites.FIGURE_IDLE or not sprite_now.is_playing():
				sprite_now.play(Sprites.FIGURE_IDLE)
				sprite_now.frame = index * GALLERY_FRAME_STRIDE % maxi(sprite_now.sprite_frames.get_frame_count(Sprites.FIGURE_IDLE), 1)
				sprite_now.speed_scale = GALLERY_PACES[index % GALLERY_PACES.size()]
		else:
			entry["rest"] = foot - Vector2(0.0, GALLERY_SILHOUETTE_LIFT)
			sprite_now.modulate = SILHOUETTE
			sprite_now.stop()
			sprite_now.animation = Sprites.FIGURE_STILL
			sprite_now.frame = 0
		sprite_now.position = entry["rest"]
		if discovered and not entry["discovered"] and not fresh:
			# A figure joining the collection twinkles on its shelf.
			_sparkle(sprite_now.position + Vector2(0.0, -6.0))
		entry["discovered"] = discovered


## Plays the machine's prize animation. The returned tween finishes when the
## capsule is in the tray; the prize itself was decided before this started.
## `lead_in` seconds pass first, while the player's hand reaches the machine.
func play_prize_animation(machine_id: String, slot: int, speed: float, lead_in: float = 0.0) -> Tween:
	var machine: Dictionary = machines[machine_id]
	_rest_machine(machine)
	_set_machine_awake(machine, true, false)
	var capsule: Sprite2D = machine["capsule"]
	last_capsule_color = CAPSULE_COLORS[_rng.randi_range(0, CAPSULE_COLORS.size() - 1)]
	capsule.texture = _capsule_texture(last_capsule_color)
	machine["speed"] = maxf(speed, 0.1)
	var tween: Tween = create_tween()
	tween.set_speed_scale(machine["speed"])
	if lead_in > 0.0:
		_toss_coin(machine, lead_in)
		tween.tween_interval(lead_in)
	match machine["type"]:
		"claw":
			_animate_claw(tween, machine)
		"plinko":
			_animate_plinko(tween, machine, slot)
		_:
			_animate_crank(tween, machine, lead_in)
	machine["busy"] = true
	tween.finished.connect(func() -> void: machine["busy"] = false)
	return tween


## The door swings open and daylight spills across the floor.
func play_door_open() -> void:
	if _door_tween != null:
		_door_tween.kill()
	Sprites.set_standing_texture(_door_sprite, Sprites.texture("props/door_open", DOOR_SIZE, C_CREAM))
	_door_glow.visible = true
	_door_glow.modulate.a = 0.0
	_door_glow.scale = Vector2(0.35, 1.0)
	_door_tween = create_tween()
	_door_tween.tween_property(_door_glow, "modulate:a", DOOR_GLOW_ALPHA, DOOR_OPEN_TIME * 0.5).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
	_door_tween.parallel().tween_property(_door_glow, "scale:x", 1.0, DOOR_OPEN_TIME).set_trans(Tween.TRANS_CUBIC).set_ease(Tween.EASE_OUT)
	# Dust motes catch the light, one after another.
	for index in range(DOOR_MOTES.size()):
		_door_tween.parallel().tween_callback(_door_mote.bind(DOOR_MOTES[index])).set_delay(DOOR_OPEN_TIME * (0.25 + 0.15 * index))


func _door_mote(offset: Vector2) -> void:
	Sprites.burst(self, "sparkle", Vector2(DOOR_X, 0.0) + offset, Vector2i(16, 16))


func reset_door() -> void:
	if _door_tween != null:
		_door_tween.kill()
		_door_tween = null
	Sprites.set_standing_texture(_door_sprite, Sprites.texture("props/door_closed", DOOR_SIZE, Color("#1f3a8a")))
	_door_glow.visible = false


# --- Machine anchors ---------------------------------------------------------

func _load_anchors() -> void:
	if not FileAccess.file_exists(ANCHORS_FILE):
		return
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(ANCHORS_FILE))
	if parsed is Dictionary:
		_anchors = parsed


## One anchor value of a machine, from the art's file or the defaults.
func _anchor(machine_id: String, kind: String, key: String) -> Variant:
	var own: Variant = _anchors.get(machine_id, {})
	if own is Dictionary and own.has(key):
		return own[key]
	return DEFAULT_ANCHORS[kind][key]


## A point of the machine's sprite, relative to its bottom centre. Anchors are
## measured on the picture, in sprite pixels; `canvas` and every result are in
## world pixels.
func _anchor_point(machine_id: String, kind: String, key: String, canvas: Vector2i) -> Vector2:
	var raw: Variant = _anchor(machine_id, kind, key)
	if not raw is Array or raw.size() < 2:
		raw = DEFAULT_ANCHORS[kind][key]
	return Vector2(Sprites.to_world(float(raw[0])) - canvas.x / 2.0, Sprites.to_world(float(raw[1])) - canvas.y)


func _anchor_x(machine_id: String, kind: String, key: String, canvas: Vector2i) -> float:
	return Sprites.to_world(float(_anchor(machine_id, kind, key))) - canvas.x / 2.0


func _anchor_y(machine_id: String, kind: String, key: String, canvas: Vector2i) -> float:
	return Sprites.to_world(float(_anchor(machine_id, kind, key))) - canvas.y


## A distance measured on the machine's picture, in world pixels.
func _anchor_length(machine_id: String, kind: String, key: String) -> float:
	return Sprites.to_world(float(_anchor(machine_id, kind, key)))


func _capsule_texture(color_name: String) -> Texture2D:
	return Sprites.texture("machines/capsule_%s" % color_name, CAPSULE_SIZE, Color(CAPSULE_FALLBACKS.get(color_name, "#e2231a")))


# --- Machine animations -------------------------------------------------------

## Shows the machine alive (powered) or as its sleeping, powered-off picture.
func _set_machine_awake(machine: Dictionary, awake: bool, animate: bool) -> void:
	var off: Sprite2D = machine["off"]
	var anim: AnimatedSprite2D = machine["anim"]
	if awake and anim.visible:
		return
	off.visible = not awake
	anim.visible = awake
	machine["robot_clock"] = 0.0
	if not awake:
		anim.stop()
		return
	if animate:
		_play_machine(machine, "wake")
	else:
		_idle_machine(machine)


## Plays one of the machine's one-shot animations (wake, play, react); it falls
## back to idle when it ends, or at once when the art is missing.
func _play_machine(machine: Dictionary, action: String) -> void:
	var anim: AnimatedSprite2D = machine["anim"]
	var anim_name: String = "%s_%s" % [machine["id"], action]
	if not anim.visible:
		return
	if not anim.sprite_frames.has_animation(anim_name) or not Sprites.has_animation(anim_name):
		_idle_machine(machine)
		return
	anim.speed_scale = 1.0 if action == "wake" else machine["speed"] * machine["play_pace"]
	anim.play(anim_name)
	anim.frame = 0


func _idle_machine(machine: Dictionary) -> void:
	var anim: AnimatedSprite2D = machine["anim"]
	if not anim.visible:
		return
	anim.speed_scale = machine["idle_pace"]
	anim.play("%s_idle" % machine["id"])


func _has_machine_animation(machine: Dictionary, action: String) -> bool:
	return Sprites.has_animation("%s_%s" % [machine["id"], action])


## A coin is tossed into the slot and lands as the hand arrives.
func _toss_coin(machine: Dictionary, lead_in: float) -> void:
	var length: float = Sprites.animation_length("coin_flip")
	if length <= 0.0:
		return
	var root: Node2D = machine["root"]
	var coin: AnimatedSprite2D = Sprites.burst(self, "coin_flip", machine["at"] + COIN_SLOTS[machine["type"]] + Vector2(0.0, -14.0), Vector2i(12, 28))
	if coin != null:
		coin.speed_scale = machine["speed"] * maxf(length / lead_in, 1.0)
		coin.z_as_relative = false
		coin.z_index = root.z_index + 1


## The machine cranks itself, a clunk, then the capsule drops into the tray.
func _animate_crank(tween: Tween, machine: Dictionary, lead_in: float) -> void:
	var root: Node2D = machine["root"]
	var rest: Vector2 = machine["at"]
	var chute: Vector2 = machine["chute"]
	var crank_time: float = CRANK_DEFAULT_TIME
	var drawn: bool = _has_machine_animation(machine, "play")
	if drawn:
		crank_time = Sprites.animation_length("%s_play" % machine["id"])
	var drawn_time: float = crank_time
	# Whatever the art's length, the capsule is in the tray within the budget.
	# A crank drawn longer than the room left is played faster, so the machine
	# has finished turning before the capsule drops.
	var room: float = GACHA_BUDGET - lead_in - CRANK_CLUNK_TIME - CHUTE_DROP_TIME - CRANK_MARGIN
	crank_time = clampf(crank_time, CRANK_MIN_TIME, maxf(room, CRANK_MIN_TIME))
	var pace: float = maxf(drawn_time / crank_time, 1.0) if drawn else 1.0
	tween.tween_callback(func() -> void:
		machine["play_pace"] = pace
		_play_machine(machine, "play")
		_rattle_surroundings(machine))
	if drawn:
		tween.tween_interval(crank_time)
	else:
		# No drawn crank: the cabinet rattles instead.
		tween.tween_method(_rattle.bind(root, rest), 0.0, 1.0, crank_time)
	tween.tween_callback(func() -> void: root.position = rest)
	# The capsule lands inside: the whole cabinet hops one pixel.
	tween.tween_property(root, "position:y", rest.y - 1.0, CRANK_CLUNK_TIME * 0.5)
	tween.tween_property(root, "position:y", rest.y, CRANK_CLUNK_TIME * 0.5)
	_tween_chute_drop(tween, machine, chute)


## Whole-pixel shake that dies out before the turn ends.
func _rattle(progress: float, root: Node2D, rest: Vector2) -> void:
	var side: float = 1.0 if int(progress * RATTLE_STEPS) % 2 == 0 else -1.0
	root.position.x = rest.x + (side if progress < 0.8 else 0.0)


## Travel with the claw swinging behind, lower, grab, lift, carry, release.
func _animate_claw(tween: Tween, machine: Dictionary) -> void:
	var claw: Sprite2D = machine["claw"]
	var capsule: Sprite2D = machine["capsule"]
	var root: Node2D = machine["root"]
	var rest: Vector2 = machine["at"]
	var speed: float = machine["speed"]
	var rail_y: float = machine["claw_rail_y"]
	var grab_y: float = machine["claw_grab_y"]
	var drop_x: float = machine["claw_drop_x"]
	var rest_x: float = machine["claw_rest_x"]
	var pick_max: float = maxf(minf(machine["claw_max_x"], drop_x - CLAW_PICK_MARGIN), machine["claw_min_x"])
	var target_x: float = roundf(_rng.randf_range(machine["claw_min_x"], pick_max))
	var open: Texture2D = Sprites.texture("machines/claw_open", CLAW_SIZE, C_INK)
	var closed: Texture2D = Sprites.texture("machines/claw_closed", CLAW_SIZE, C_INK)
	# Out to the prize: the claw lags behind the carriage, then settles.
	tween.tween_property(claw, "position:x", target_x, CLAW_MOVE_TIME).set_trans(Tween.TRANS_SINE)
	tween.parallel().tween_method(_sway.bind(claw, CLAW_SWAY, 1.5), 0.0, 1.0, CLAW_MOVE_TIME + CLAW_SETTLE_TIME)
	tween.tween_property(claw, "position:y", grab_y, CLAW_LOWER_TIME).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_IN)
	# Grab: the claw snaps shut, dips into the pile and the cabinet shudders.
	tween.tween_callback(func() -> void:
		claw.texture = closed
		machine["held"] = true
		capsule.rotation = 0.0
		capsule.position = claw.position + CLAW_HOLD
		capsule.visible = true
		shaken.emit(GRAB_SHAKE, GRAB_SHAKE_TIME)
		_rattle_surroundings(machine))
	tween.tween_property(claw, "position:y", grab_y + 1.0, CLAW_GRAB_TIME * 0.3)
	tween.tween_property(claw, "position:y", grab_y, CLAW_GRAB_TIME * 0.3)
	tween.parallel().tween_method(_rattle.bind(root, rest), 0.5, 1.0, CLAW_GRAB_TIME * 0.7)
	tween.tween_property(claw, "position:y", rail_y, CLAW_LIFT_TIME).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
	tween.parallel().tween_method(_sway.bind(claw, CLAW_SWAY * 0.4, 1.0), 0.0, 1.0, CLAW_LIFT_TIME)
	# Carry to the prize hole, swinging with the weight.
	tween.tween_property(claw, "position:x", drop_x, CLAW_CARRY_TIME).set_trans(Tween.TRANS_SINE)
	tween.parallel().tween_method(_sway.bind(claw, CLAW_SWAY, 1.5), 0.0, 1.0, CLAW_CARRY_TIME + CLAW_SETTLE_TIME)
	# Release: the capsule falls into the hole, the cabinet bounces for joy,
	# the claw kicks back and goes home.
	tween.tween_callback(func() -> void:
		claw.texture = open
		machine["held"] = false
		capsule.position = Vector2(drop_x, rail_y) + CLAW_HOLD
		_play_machine(machine, "react")
		var home: Tween = create_tween()
		home.set_speed_scale(speed)
		home.tween_method(_sway.bind(claw, -CLAW_SWAY * 0.6, 1.0), 0.0, 1.0, CLAW_RELEASE_TIME)
		home.tween_property(claw, "position:x", rest_x, CLAW_RETURN_TIME).set_trans(Tween.TRANS_SINE)
		home.parallel().tween_method(_sway.bind(claw, -CLAW_SWAY * 0.5, 1.5), 0.0, 1.0, CLAW_RETURN_TIME + CLAW_SETTLE_TIME)
		machine["aux"] = home)
	tween.tween_property(capsule, "position:y", machine["claw_drop_y"], CLAW_RELEASE_TIME).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_IN)
	_tween_chute_drop(tween, machine, machine["chute"])


## A damped pendulum swing of the claw around its hanging point. A positive
## amplitude starts by trailing to the left (the claw is moving right).
func _sway(progress: float, claw: Sprite2D, amplitude: float, swings: float) -> void:
	claw.rotation = amplitude * sin(progress * TAU * swings) * (1.0 - progress)


## The ball drops onto the top peg, hops down row by row and lights its slot.
func _animate_plinko(tween: Tween, machine: Dictionary, slot: int) -> void:
	var ball: Sprite2D = machine["ball"]
	var lamp: Polygon2D = machine["slot_lamp"]
	var root: Node2D = machine["root"]
	var slots: Array = machine["slots"]
	var rows: int = machine["rows"]
	var column_step: float = machine["column_step"]
	var row_step: float = machine["row_step"]
	var top: Vector2 = machine["ball_start"]
	var final_slot: int = clampi(slot, 0, slots.size() - 1)
	var slot_at: Vector2 = slots[final_slot]
	# Each row moves the ball one column step; the mix of lefts and rights
	# decides the slot it ends above.
	var columns: int = int(roundf((slot_at.x - top.x) / maxf(column_step, 1.0)))
	var rights: int = clampi((rows + columns) / 2, 0, rows)
	var steps: Array = []
	for index in range(rows):
		steps.append(1.0 if index < rights else -1.0)
	var widest_allowed: float = PLINKO_MAX_COLUMNS * column_step
	# Shuffle until the path stays on the pegs of the board.
	for attempt in range(40):
		for index in range(steps.size() - 1, 0, -1):
			var other: int = _rng.randi_range(0, index)
			var kept: float = steps[index]
			steps[index] = steps[other]
			steps[other] = kept
		var offset: float = 0.0
		var widest: float = 0.0
		for step in steps:
			offset += step * column_step
			widest = maxf(widest, absf(offset))
		if widest <= widest_allowed:
			break
	var at: Vector2 = top
	var hop_time: float = PLINKO_HOPS_TIME / maxi(rows, 1)
	tween.tween_callback(func() -> void:
		ball.position = top + Vector2(0.0, -4.0)
		ball.visible = true)
	tween.tween_property(ball, "position", at, PLINKO_DROP_TIME).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_IN)
	for step in steps:
		var from: Vector2 = at
		at += Vector2(step * column_step, row_step)
		tween.tween_callback(_peg_hit.bind(root, from))
		tween.tween_method(_pose_hop.bind(ball, from, at), 0.0, 1.0, hop_time)
	tween.tween_property(ball, "position", slot_at, PLINKO_SLOT_TIME).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_IN)
	tween.tween_callback(func() -> void:
		lamp.position = slot_at
		_play_machine(machine, "react"))
	tween.tween_method(_blink.bind(lamp), 0.0, 1.0, PLINKO_HOLD_TIME)
	tween.tween_callback(func() -> void:
		ball.visible = false
		lamp.visible = false)
	_tween_chute_drop(tween, machine, machine["chute"])


## The ball strikes the peg it rests on: a sound and a glint on the peg.
func _peg_hit(root: Node2D, ball_at: Vector2) -> void:
	plinko_bounced.emit()
	_flash(root, ball_at + Vector2(-1.0, 2.0), Vector2(2.0, 2.0), PEG_FLASH_TIME)


## A bounce off a peg: straight across, up and over under gravity.
func _pose_hop(progress: float, ball: Sprite2D, from: Vector2, to: Vector2) -> void:
	var at: Vector2 = from.lerp(to, progress)
	at.y = from.y + (to.y - from.y) * progress * progress - sin(progress * PI) * PLINKO_HOP_HEIGHT
	ball.position = at.round()


func _blink(progress: float, lamp: Polygon2D) -> void:
	lamp.visible = int(progress * PLINKO_BLINKS * 2.0) % 2 == 0


## A small square of light that fades out, e.g. a peg struck by the ball.
func _flash(parent: Node2D, at: Vector2, flash_size: Vector2, seconds: float) -> void:
	var flash: ColorRect = ColorRect.new()
	flash.color = Color(1.0, 1.0, 0.85, 0.95)
	flash.position = at
	flash.size = flash_size
	flash.mouse_filter = Control.MOUSE_FILTER_IGNORE
	parent.add_child(flash)
	var fade: Tween = flash.create_tween()
	fade.tween_property(flash, "color:a", 0.0, seconds)
	fade.tween_callback(flash.queue_free)


## The capsule drops out of the chute, bounces twice while it rolls a quarter
## turn per bounce, and a sparkle marks it in the tray.
func _tween_chute_drop(tween: Tween, machine: Dictionary, to: Vector2) -> void:
	var capsule: Sprite2D = machine["capsule"]
	var from: Vector2 = to + Vector2(0.0, -CHUTE_DROP_HEIGHT)
	tween.tween_callback(func() -> void:
		capsule.position = from
		capsule.rotation = 0.0
		capsule.visible = true)
	tween.tween_property(capsule, "position", to, CHUTE_DROP_TIME * 0.4).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_IN)
	tween.tween_callback(func() -> void: capsule.rotation = PI / 2.0)
	tween.tween_property(capsule, "position", to + Vector2(0.0, -3.0), CHUTE_DROP_TIME * 0.2).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
	tween.tween_property(capsule, "position", to, CHUTE_DROP_TIME * 0.2).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_IN)
	tween.tween_callback(func() -> void: capsule.rotation = PI)
	tween.tween_property(capsule, "position", to + Vector2(0.0, -1.0), CHUTE_DROP_TIME * 0.1)
	tween.tween_property(capsule, "position", to, CHUTE_DROP_TIME * 0.1)
	tween.tween_callback(_tray_sparkle.bind(machine, to))


## The capsule has come to rest: it flattens for a moment and twinkles. The
## squash runs by itself, so it adds nothing to the animation's length.
func _tray_sparkle(machine: Dictionary, tray: Vector2) -> void:
	_sparkle(machine["at"] + tray + Vector2(5.0, -6.0))
	var capsule: Sprite2D = machine["capsule"]
	var squash: Tween = capsule.create_tween()
	for step in SQUASH_STEPS:
		# On top of the scale every sprite is drawn at.
		squash.tween_callback(capsule.set_scale.bind(step * Sprites.DRAW_SCALE))
		squash.tween_interval(SQUASH_STEP_TIME)


## A machine at work shakes its price sign and the lamps hanging near it.
func _rattle_surroundings(machine: Dictionary) -> void:
	machine["sign_swing"].kick(SIGN_RATTLE_KICK)
	var x: float = machine["at"].x
	for lamp in _lamps:
		if absf(lamp["x"] - x) <= RATTLE_REACH:
			lamp["swing"].kick(LAMP_RATTLE_KICK if lamp["x"] >= x else -LAMP_RATTLE_KICK)


## Puts the moving parts back before a new animation.
func _rest_machine(machine: Dictionary) -> void:
	if machine["aux"] != null and machine["aux"].is_valid():
		machine["aux"].kill()
	machine["aux"] = null
	if machine["hop"] != null and machine["hop"].is_valid():
		machine["hop"].kill()
	machine["hop"] = null
	machine["play_pace"] = 1.0
	machine["held"] = false
	machine["root"].position = machine["at"]
	machine["capsule"].visible = false
	machine["capsule"].rotation = 0.0
	machine["capsule"].scale = Sprites.DRAW_SCALE
	match machine["type"]:
		"claw":
			machine["claw"].position = Vector2(machine["claw_rest_x"], machine["claw_rail_y"])
			machine["claw"].rotation = 0.0
			machine["claw"].texture = Sprites.texture("machines/claw_open", CLAW_SIZE, C_INK)
		"plinko":
			machine["ball"].visible = false
			machine["slot_lamp"].visible = false


func _on_machine_animation_finished(machine: Dictionary) -> void:
	if machine["anim"].visible:
		_idle_machine(machine)


# --- Power --------------------------------------------------------------------

## The lever flips under the player's hand, the lamps flicker on from the
## switch outwards while the room brightens, then the machines wake one by one.
func _play_power_on() -> void:
	_power_tween = create_tween()
	_power_tween.tween_interval(POWER_LEAD_TIME)
	_power_tween.tween_callback(_set_switch.bind(true))
	var order: Array = _lamps.duplicate()
	order.sort_custom(func(a: Dictionary, b: Dictionary) -> bool:
		return absf(a["x"] - SWITCH_X) < absf(b["x"] - SWITCH_X))
	var lit: int = 0
	for lamp in order:
		lit += 1
		var level: float = float(lit) / order.size()
		_power_tween.tween_callback(_flicker_lamp.bind(lamp))
		_power_tween.tween_property(_modulate, "color", DARK.lerp(Color.WHITE, level), POWER_LAMP_STEP)
	_power_tween.tween_callback(func() -> void:
		_set_computer(true)
		_set_gallery_lights(true)
		ambient.set_power(true))
	for machine_id in machines:
		_power_tween.tween_callback(_wake_machine.bind(machines[machine_id]))
		_power_tween.tween_interval(POWER_MACHINE_STEP)


## Power reaches one machine: a click, its eyes pop open, a twinkle.
func _wake_machine(machine: Dictionary) -> void:
	machine_lit.emit()
	if machine["anim"].visible:
		return
	_set_machine_awake(machine, true, true)
	var canvas: Vector2i = machine["canvas"]
	_sparkle(machine["at"] + Vector2(_rng.randf_range(-8.0, 8.0), -canvas.y + 10.0))
	machine["sign_swing"].kick(SIGN_GREET_KICK)


func _set_switch(is_on: bool) -> void:
	Sprites.set_standing_texture(_switch_sprite, Sprites.texture("props/power_switch_%s" % ("on" if is_on else "off"), Vector2i(20, 28), C_MUSTARD if is_on else Color("#4a5160")))


## A lamp stutters on: the shade and its light blink a few times, then stay.
func _flicker_lamp(lamp: Dictionary) -> void:
	var flicker: Tween = create_tween()
	for step in LAMP_FLICKER:
		flicker.tween_callback(_set_lamp.bind(lamp, step[0]))
		if step[1] > 0.0:
			flicker.tween_interval(step[1])
	_flicker_tweens.append(flicker)


func _set_lamp(lamp: Dictionary, is_on: bool) -> void:
	lamp["sprite"].texture = Sprites.texture("props/lamp_%s" % ("on" if is_on else "off"), LAMP_SIZE, C_MUSTARD if is_on else Color("#4a5160"))
	lamp["glow"].visible = is_on
	lamp["on"] = is_on


func _set_gallery_lights(is_on: bool) -> void:
	for light in _gallery_lights:
		light.visible = is_on


func _set_computer(is_on: bool) -> void:
	Sprites.set_standing_texture(_computer, Sprites.texture("props/computer_%s" % ("on" if is_on else "off"), Vector2i(30, 30), Color("#2e9e4f") if is_on else C_INK))


# --- Rooms --------------------------------------------------------------------

func _build_bathroom() -> void:
	_floor_prop("props/toilet", TOILET_AT, Vector2i(30, 40), 18.0)
	_floor_prop("props/sink", SINK_AT, Vector2i(30, 50), 10.0)
	furniture["sink"] = SINK_AT
	for index in range(COIN_SPOTS.size()):
		var spot: Vector2 = COIN_SPOTS[index]
		var coin: Node2D = _interactable("Coin%d" % index, spot, COIN_REACH)
		coin.z_index = floor_z(spot.y)
		coin.set_meta("coin_index", index)
		var shadow: Polygon2D = _shadow(spot + Vector2(0.0, -1.0), Vector2(5.0, 1.5))
		coin.set_meta("shadow", shadow)
		var spin: AnimatedSprite2D = Sprites.animated(["coin_spin"], COIN_SIZE, C_MUSTARD)
		spin.play("coin_spin")
		spin.frame = index * 2 % maxi(spin.sprite_frames.get_frame_count("coin_spin"), 1)
		coin.add_child(spin)
		coin.set_meta("spin", spin)
		coins.append(coin)


func _build_corridor() -> void:
	power_switch = _interactable("PowerSwitch", Vector2(SWITCH_X, 0.0), WALL_USE_REACH)
	power_switch.use_offset = WALL_USE_OFFSET
	power_switch.z_index = Z_WALL
	_switch_sprite = Sprites.standing("props/power_switch_off", Vector2i(20, 28), Color("#4a5160"))
	_switch_sprite.position = Vector2(0.0, SWITCH_Y)
	power_switch.add_child(_switch_sprite)


func _build_hall() -> void:
	_wall_prop("props/sign_gacha", Vector2(366.0, WALL_TOP + 28.0), Vector2i(110, 28)).z_index = Z_HANGING
	for machine_id in MACHINE_SPOTS:
		_build_machine(machine_id)


func _build_machine(machine_id: String) -> void:
	var at: Vector2 = MACHINE_SPOTS[machine_id]
	var index: int = MACHINE_SPOTS.keys().find(machine_id)
	var kind: String = "gacha"
	if machine_id == "machine_005":
		kind = "claw"
	elif machine_id == "machine_006":
		kind = "plinko"
	var canvas: Vector2i = GACHA_SIZE if kind == "gacha" else BIG_SIZE
	var fallback: Color = Color(MACHINE_FALLBACKS[index % MACHINE_FALLBACKS.size()])
	_shadow(at + Vector2(0.0, -1.0), Vector2(canvas.x / 2.0, 4.0))
	var root: Node2D = Node2D.new()
	root.name = machine_id
	root.position = at
	root.z_index = floor_z(at.y)
	add_child(root)
	_solid(at, canvas.x - FOOTPRINT_INSET, at.y)
	# Asleep: the powered-off picture. Awake: the animated character. A missing
	# animation falls back to the still picture, so there is always a machine.
	var off: Sprite2D = Sprites.standing("machines/%s" % machine_id, canvas, fallback.darkened(0.35))
	root.add_child(off)
	var action: String = "play" if kind == "gacha" else "react"
	var names: Array = ["%s_idle" % machine_id, "%s_wake" % machine_id, "%s_%s" % [machine_id, action]]
	var still: Texture2D = off.texture if Sprites.has_texture("machines/%s" % machine_id) else Sprites.placeholder(Sprites.art_size(canvas), fallback)
	var anim: AnimatedSprite2D = Sprites.animated(names, canvas, fallback, still)
	for one_shot in [names[1], names[2]]:
		anim.sprite_frames.set_animation_loop(one_shot, false)
	anim.visible = false
	root.add_child(anim)
	var machine: Dictionary = {
		"id": machine_id, "root": root, "at": at, "type": kind, "canvas": canvas, "off": off, "anim": anim,
		"robots": [], "busy": false, "held": false, "aux": null, "robot_rate": 0.0, "robot_clock": 0.0, "speed": 1.0,
		"play_pace": 1.0, "hop": null, "near": false, "affordable": false, "nudge_in": 0.0, "sign_swing": Swing.new(),
		"idle_pace": MACHINE_IDLE_PACES[index % MACHINE_IDLE_PACES.size()],
		"chute": _anchor_point(machine_id, kind, "chute", canvas),
	}
	anim.animation_finished.connect(_on_machine_animation_finished.bind(machine))
	match kind:
		"claw":
			machine["claw_rail_y"] = _anchor_y(machine_id, kind, "claw_rail_y", canvas)
			machine["claw_grab_y"] = _anchor_y(machine_id, kind, "grab_y", canvas)
			machine["claw_drop_y"] = _anchor_y(machine_id, kind, "drop_y", canvas)
			machine["claw_min_x"] = _anchor_x(machine_id, kind, "claw_min_x", canvas)
			machine["claw_max_x"] = _anchor_x(machine_id, kind, "claw_max_x", canvas)
			machine["claw_rest_x"] = _anchor_x(machine_id, kind, "claw_rest_x", canvas)
			machine["claw_drop_x"] = _anchor_x(machine_id, kind, "drop_x", canvas)
			var rope: Line2D = Line2D.new()
			rope.width = 1.0
			rope.default_color = C_INK
			rope.points = PackedVector2Array([Vector2.ZERO, Vector2.ZERO])
			root.add_child(rope)
			# The claw hangs from the top centre of its picture.
			var claw: Sprite2D = Sprites.hanging("machines/claw_open", CLAW_SIZE, C_INK)
			claw.position = Vector2(machine["claw_rest_x"], machine["claw_rail_y"])
			root.add_child(claw)
			machine["claw"] = claw
			machine["rope"] = rope
		"plinko":
			var top: Vector2 = _anchor_point(machine_id, kind, "ball_start", canvas)
			machine["ball_start"] = top
			machine["rows"] = maxi(int(_anchor(machine_id, kind, "rows")), 1)
			machine["row_step"] = _anchor_length(machine_id, kind, "row_step")
			machine["column_step"] = _anchor_length(machine_id, kind, "column_step")
			var slot_y: float = _anchor_y(machine_id, kind, "slot_y", canvas)
			var slot_xs: Variant = _anchor(machine_id, kind, "slot_xs")
			if not slot_xs is Array or slot_xs.is_empty():
				slot_xs = DEFAULT_ANCHORS[kind]["slot_xs"]
			var slots: Array = []
			for slot_x in slot_xs:
				slots.append(Vector2(Sprites.to_world(float(slot_x)) - canvas.x / 2.0, slot_y))
			machine["slots"] = slots
			var lamp: Polygon2D = Polygon2D.new()
			lamp.polygon = PackedVector2Array([Vector2(-4, -4), Vector2(4, -4), Vector2(4, 4), Vector2(-4, 4)])
			lamp.color = Color(1.0, 0.95, 0.6, 0.7)
			lamp.visible = false
			root.add_child(lamp)
			var ball: Sprite2D = Sprites.part("machines/plinko_ball", Vector2i(6, 6), C_CREAM)
			ball.visible = false
			root.add_child(ball)
			machine["ball"] = ball
			machine["slot_lamp"] = lamp
	var capsule: Sprite2D = Sprites.part("machines/capsule_red", CAPSULE_SIZE, Color(CAPSULE_FALLBACKS["red"]))
	capsule.visible = false
	root.add_child(capsule)
	machine["capsule"] = capsule
	var price: Node2D = PriceSign.new()
	price.name = "Price_%s" % machine_id
	price.position = at + Vector2(0.0, SIGN_SEAT[kind] - canvas.y)
	# Just behind the machine: a cap that stretches up covers the sign's feet.
	price.z_index = root.z_index - 1
	add_child(price)
	price.affordable = false
	machine["price"] = price
	var offsets: Array = ROBOT_OFFSETS_GACHA if kind == "gacha" else ROBOT_OFFSETS_BIG
	for robot_index in range(MAX_ROBOT_SPRITES):
		var robot: AnimatedSprite2D = Sprites.animated(["robot_idle", "robot_work"], ROBOT_SIZE)
		robot.position = at + offsets[robot_index % offsets.size()]
		robot.flip_h = ROBOT_FLIPS[robot_index % ROBOT_FLIPS.size()]
		robot.z_index = floor_z(robot.position.y)
		robot.visible = false
		robot.set_meta("rest_y", robot.position.y)
		add_child(robot)
		var shadow: Polygon2D = _shadow(robot.position + Vector2(0.0, -1.0), ROBOT_SHADOW)
		shadow.visible = false
		robot.set_meta("shadow", shadow)
		machine["robots"].append(robot)
	var body: Node2D = _interactable("Use_%s" % machine_id, at, MACHINE_REACH)
	body.use_offset = MACHINE_USE_OFFSET
	machine["body"] = body
	machines[machine_id] = machine


func _process(delta: float) -> void:
	_time += delta
	_breeze_from = _breeze_to
	_breeze_to = player_at.x
	for machine_id in machines:
		var machine: Dictionary = machines[machine_id]
		if machine["type"] == "claw":
			# The rope follows the claw, and a held capsule swings with it.
			var claw: Sprite2D = machine["claw"]
			machine["rope"].points = PackedVector2Array([Vector2(claw.position.x, machine["claw_rail_y"]), claw.position])
			if machine["held"]:
				machine["capsule"].position = (claw.position + CLAW_HOLD.rotated(claw.rotation)).round()
		_robots_work_machine(machine, delta)
		_machine_life(machine, delta)
	_animate_coins()
	for lamp in _lamps:
		var push: float = breeze(lamp["x"])
		if push != 0.0:
			lamp["swing"].kick(push * LAMP_BREEZE_KICK)
		# Cords sway a little, each lamp in its own time, plus whatever stirred it.
		lamp["sprite"].rotation = sin(_time * LAMP_SWAY_SPEED + lamp["phase"]) * LAMP_SWAY + lamp["swing"].step(delta)
	_gallery_life()
	_computer_life()


## The small things a machine does by itself: its price sign wobbles, it hops
## to greet a player who walks up, and it calls for attention while the player
## could pay for it.
func _machine_life(machine: Dictionary, delta: float) -> void:
	var price: Node2D = machine["price"]
	var swing: RefCounted = machine["sign_swing"]
	price.rotation = swing.step(delta) * SIGN_WOBBLE
	# The sign rides on the machine's head through every hop and rattle.
	price.position = machine["root"].position + Vector2(0.0, SIGN_SEAT[machine["type"]] - machine["canvas"].y)
	if not _power_on or not machine["anim"].visible:
		machine["near"] = false
		return
	var at: Vector2 = machine["at"]
	var near: bool = absf(player_at.x - at.x) < NOTICE_HALF_WIDTH and player_at.y < at.y + NOTICE_DEPTH
	if near and not machine["near"] and not machine["busy"]:
		_hop_machine(machine, GREET_HOP)
		swing.kick(SIGN_GREET_KICK)
		if machine["affordable"]:
			_sparkle(price.coin_point())
		else:
			# Too dear for now: the machine wonders about this customer.
			var canvas: Vector2i = machine["canvas"]
			_bubble(at + Vector2(0.0, -canvas.y) + BUBBLE_OFFSETS[machine["type"]])
	machine["near"] = near
	if machine["affordable"] and not near and not machine["busy"]:
		machine["nudge_in"] -= delta
		if machine["nudge_in"] <= 0.0:
			machine["nudge_in"] = _rng.randf_range(NUDGE_EVERY.x, NUDGE_EVERY.y)
			_hop_machine(machine, NUDGE_HOP)
			swing.kick(SIGN_NUDGE_KICK)
			_sparkle(price.coin_point())


## The whole machine hops by whole pixels; never during a prize animation,
## which moves the cabinet itself.
func _hop_machine(machine: Dictionary, height: float) -> void:
	if machine["busy"]:
		return
	if machine["hop"] != null and machine["hop"].is_valid():
		machine["hop"].kill()
	var root: Node2D = machine["root"]
	root.position = machine["at"]
	machine["hop"] = _hop(root, machine["at"].y, height)


## `hops` little jumps of a node above its resting y, after `delay` seconds.
func _hop(node: Node2D, rest_y: float, height: float, hops: int = 1, delay: float = 0.0) -> Tween:
	var hop: Tween = node.create_tween()
	if delay > 0.0:
		hop.tween_interval(delay)
	for index in range(hops):
		hop.tween_property(node, "position:y", rest_y - height, HOP_UP_TIME).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
		hop.tween_property(node, "position:y", rest_y, HOP_DOWN_TIME).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_IN)
	return hop


## A "thinking" bubble of bouncing dots for a moment; `at` is its bottom centre.
func _bubble(at: Vector2) -> void:
	if not Sprites.has_animation("speech_dots"):
		return
	var bubble: AnimatedSprite2D = Sprites.animated(["speech_dots"], BUBBLE_SIZE)
	bubble.position = at
	bubble.z_index = Z_LABEL
	add_child(bubble)
	bubble.play("speech_dots")
	var life: Tween = bubble.create_tween()
	life.tween_interval(BUBBLE_TIME)
	life.tween_callback(bubble.queue_free)


## Discovered figures hop on their bases as the player walks by.
func _gallery_life() -> void:
	var room: Vector2 = room_range("gallery")
	var inside: bool = player_at.x >= room.x and player_at.x <= room.y
	var moving: bool = absf(player_velocity.x) > 1.0
	for figure_id in gallery:
		var entry: Dictionary = gallery[figure_id]
		if not entry["discovered"]:
			continue
		var near: bool = inside and absf(player_at.x - entry["foot"].x) < GALLERY_HOP_REACH
		if near and not entry["near"] and moving:
			_hop(entry["figure"], entry["rest"].y, GALLERY_HOP)
		entry["near"] = near


## The salesman's terminal hops and "thinks" as the player steps to the counter.
func _computer_life() -> void:
	var near: bool = _power_on and player_at.distance_to(COUNTER_AT + COUNTER_USE_OFFSET) <= COUNTER_REACH
	if near and not _computer_near:
		_hop(_computer, COMPUTER_OFFSET.y, COMPUTER_HOP, 2)
		_bubble(COUNTER_AT + COMPUTER_OFFSET + COMPUTER_BUBBLE)
	_computer_near = near


## Between the player's own turns, a machine worked by robots acts by itself
## in time with their spins.
func _robots_work_machine(machine: Dictionary, delta: float) -> void:
	var rate: float = machine["robot_rate"]
	if rate <= 0.0 or machine["busy"] or not machine["anim"].visible:
		return
	var action: String = "play" if machine["type"] == "gacha" else "react"
	if not _has_machine_animation(machine, action):
		return
	machine["robot_clock"] += delta
	var every: float = maxf(1.0 / rate, Sprites.animation_length("%s_%s" % [machine["id"], action]) + ROBOT_PLAY_GAP)
	if machine["robot_clock"] >= every:
		machine["robot_clock"] = 0.0
		machine["speed"] = 1.0
		_play_machine(machine, action)


## Floor coins bob by a pixel, out of step, and one of them twinkles now and
## then so they can be found in the dark.
func _animate_coins() -> void:
	var waiting: Array = []
	for index in range(coins.size()):
		var coin: Node2D = coins[index]
		if not coin.visible:
			continue
		waiting.append(coin)
		var spin: Node2D = coin.get_meta("spin")
		spin.position.y = roundf(sin(_time * COIN_BOB_SPEED + index * 1.9)) - 1.0
	if _time >= _next_twinkle:
		_next_twinkle = _time + COIN_TWINKLE_EVERY * _rng.randf_range(0.7, 1.3)
		if not waiting.is_empty():
			var lucky: Node2D = waiting[_rng.randi_range(0, waiting.size() - 1)]
			Sprites.burst(self, "sparkle", lucky.position + Vector2(_rng.randf_range(-3.0, 3.0), -9.0), Vector2i(16, 16))


## The gallery: wall shelves for the upper row and a long display bench on the
## floor for the lower one, each washed by a light from behind; `set_display`
## stands the figures on them. A poster and keepsakes fill the gaps.
func _build_gallery() -> void:
	# The cabinet: a dark back board in an ink frame, and one plank per shelf.
	var frame: ColorRect = ColorRect.new()
	frame.color = C_INK
	frame.position = GALLERY_CABINET.position - Vector2(2.0, 2.0)
	frame.size = GALLERY_CABINET.size + Vector2(4.0, 2.0)
	frame.mouse_filter = Control.MOUSE_FILTER_IGNORE
	frame.z_index = Z_WALL
	add_child(frame)
	var board: ColorRect = ColorRect.new()
	board.color = GALLERY_BOARD_COLOR
	board.position = GALLERY_CABINET.position
	board.size = GALLERY_CABINET.size
	board.mouse_filter = Control.MOUSE_FILTER_IGNORE
	board.z_index = Z_WALL
	add_child(board)
	for row_y in GALLERY_ROW_YS:
		# Thin planks: the miniatures are only a few pixels tall.
		var plank: ColorRect = ColorRect.new()
		plank.color = Color("#b9743f")
		plank.position = Vector2(GALLERY_CABINET.position.x, row_y)
		plank.size = Vector2(GALLERY_CABINET.size.x, 2.0)
		plank.mouse_filter = Control.MOUSE_FILTER_IGNORE
		plank.z_index = Z_WALL + 1
		add_child(plank)


func _build_reception() -> void:
	# The glass door is part of the back wall; daylight falls from it over the floor.
	door = _interactable("FrontDoor", Vector2(DOOR_X, 0.0), WALL_USE_REACH)
	door.use_offset = WALL_USE_OFFSET
	door.z_index = Z_WALL
	_door_sprite = Sprites.standing("props/door_closed", DOOR_SIZE, Color("#1f3a8a"))
	door.add_child(_door_sprite)
	furniture["door"] = Vector2(DOOR_X, 0.0)
	var left: float = DOOR_OPENING.position.x
	var right: float = DOOR_OPENING.end.x
	# Daylight on the floor only, and under everything that stands on it: the
	# open door's own picture shows the sky, and nobody is washed out by fog.
	_door_glow = Polygon2D.new()
	_door_glow.polygon = PackedVector2Array([Vector2(left, 0.0), Vector2(right, 0.0), Vector2(right + DOOR_LIGHT_SPREAD, FLOOR_DEPTH), Vector2(left - DOOR_LIGHT_SPREAD, FLOOR_DEPTH)])
	# Bright at the doorway, fading out across the floor.
	var bright: Color = Color(1.0, 0.97, 0.85, 1.0)
	var faded: Color = Color(1.0, 0.95, 0.75, 0.15)
	_door_glow.color = Color.WHITE
	_door_glow.vertex_colors = PackedColorArray([bright, bright, faded, faded])
	_door_glow.position = Vector2(DOOR_X, 0.0)
	_door_glow.z_index = Z_DECAL + 1
	_door_glow.visible = false
	add_child(_door_glow)
	reception = _interactable("Reception", COUNTER_AT, COUNTER_REACH)
	reception.use_offset = COUNTER_USE_OFFSET
	reception.z_index = floor_z(COUNTER_AT.y)
	_shadow(COUNTER_AT + Vector2(0.0, -1.0), Vector2(COUNTER_SIZE.x / 2.0 + 2.0, 4.0))
	_solid(COUNTER_AT, COUNTER_SIZE.x - FOOTPRINT_INSET, COUNTER_DEPTH)
	reception.add_child(Sprites.standing("props/counter", COUNTER_SIZE, Color("#9c1420")))
	_computer = Sprites.standing("props/computer_off", Vector2i(30, 30), C_INK)
	_computer.position = COMPUTER_OFFSET
	reception.add_child(_computer)
	_key = Sprites.standing("props/key", Vector2i(14, 10), C_MUSTARD)
	_key.position = KEY_OFFSET
	reception.add_child(_key)
	furniture["counter"] = COUNTER_AT


func _build_staff_room() -> void:
	_floor_prop("props/locker", LOCKER_AT, Vector2i(30, 74), 5.0)
	sofa = _interactable("Sofa", SOFA_AT, SOFA_REACH)
	sofa.use_offset = SOFA_USE_OFFSET
	sofa.z_index = floor_z(SOFA_AT.y)
	_shadow(SOFA_AT + Vector2(0.0, -1.0), Vector2(SOFA_SIZE.x / 2.0 + 2.0, 4.0))
	_solid(SOFA_AT, SOFA_SIZE.x - FOOTPRINT_INSET, SOFA_DEPTH)
	sofa.add_child(Sprites.standing("props/sofa", SOFA_SIZE, Color("#9c1420")))
	_floor_prop("props/table", TABLE_AT, Vector2i(46, 32), 12.0)
	furniture["table"] = TABLE_AT
	_wall_prop("props/poster_b", POSTER_B_AT, Vector2i(28, 36))


## Pendant lamps along the top of the wall, each with a cone and a pool of
## light that only show while it is lit.
func _build_lamps() -> void:
	for x in LAMP_XS:
		_build_lamp(x, LAMP_CONE_BOTTOM)
	for x in GALLERY_GAP_XS:
		_build_lamp(x, GALLERY_CONE_BOTTOM)


## One lamp at world x `x`; its beam is `cone_bottom` wide (half) at the floor.
func _build_lamp(x: float, cone_bottom: float) -> void:
	var index: int = _lamps.size()
	var glow: Node2D = Node2D.new()
	glow.position = Vector2(x, WALL_TOP + LAMP_BULB_Y)
	glow.z_index = Z_GLOW
	var additive: CanvasItemMaterial = CanvasItemMaterial.new()
	additive.blend_mode = CanvasItemMaterial.BLEND_MODE_ADD
	var cone: Polygon2D = Polygon2D.new()
	var reach: float = LAMP_POOL_Y - glow.position.y
	cone.polygon = PackedVector2Array([Vector2(-LAMP_CONE_TOP, 0.0), Vector2(LAMP_CONE_TOP, 0.0), Vector2(cone_bottom, reach), Vector2(-cone_bottom, reach)])
	# A soft cone: brightest under the shade, gone at the floor.
	var bright: Color = Color(LAMP_GLOW_COLOR, LAMP_GLOW_ALPHA)
	var faded: Color = Color(LAMP_GLOW_COLOR, 0.0)
	cone.color = Color.WHITE
	cone.vertex_colors = PackedColorArray([bright, bright, faded, faded])
	cone.material = additive
	glow.add_child(cone)
	var pool: Polygon2D = Sprites.ellipse(LAMP_POOL_RADIUS, Color(LAMP_GLOW_COLOR, LAMP_POOL_ALPHA), 20)
	pool.position = Vector2(0.0, reach)
	pool.material = additive
	glow.add_child(pool)
	# Dust drifts in the beam of a lit lamp, where the beam is wide enough.
	if Sprites.has_animation("amb_dust_motes") and cone_bottom >= MOTES_SIZE.x / 2.0:
		var motes: AnimatedSprite2D = Sprites.animated(["amb_dust_motes"], MOTES_SIZE)
		motes.position = Vector2(0.0, MOTES_SIZE.y + 6.0)
		motes.material = additive
		motes.play("amb_dust_motes")
		motes.frame = index * 3 % maxi(motes.sprite_frames.get_frame_count("amb_dust_motes"), 1)
		glow.add_child(motes)
	add_child(glow)
	var sprite: Sprite2D = Sprites.hanging("props/lamp_off", LAMP_SIZE, Color("#4a5160"))
	sprite.position = Vector2(x, WALL_TOP)
	sprite.z_index = Z_HANGING
	add_child(sprite)
	_lamps.append({"x": x, "sprite": sprite, "glow": glow, "on": false, "phase": index * 1.7, "swing": Swing.new()})


## World x of every lamp, for the life that gathers around them.
func lamp_points() -> Array:
	var points: Array = []
	for lamp in _lamps:
		points.append(Vector2(lamp["x"], WALL_TOP + LAMP_BULB_Y))
	return points


# --- Helpers ------------------------------------------------------------------

## A thing standing on the floor, sorted by its floor line. `depth` > 0 makes
## its footprint solid and gives it a drop shadow.
func _floor_prop(path: String, at: Vector2, fallback_size: Vector2i, depth: float = 0.0) -> Sprite2D:
	var sprite: Sprite2D = Sprites.standing(path, fallback_size)
	sprite.position = at
	sprite.z_index = floor_z(at.y)
	add_child(sprite)
	if depth > 0.0:
		var width: float = fallback_size.x
		_shadow(at + Vector2(0.0, -1.0), Vector2(width / 2.0 + 1.0, 3.5))
		_solid(at, width - FOOTPRINT_INSET, depth)
	return sprite


## A thing on the back wall; `at` is its bottom centre.
func _wall_prop(path: String, at: Vector2, fallback_size: Vector2i) -> Sprite2D:
	var sprite: Sprite2D = Sprites.standing(path, fallback_size)
	sprite.position = at
	sprite.z_index = Z_WALL
	add_child(sprite)
	return sprite


## Something lying flat on the floor, under everything that stands.
func _decal(path: String, at: Vector2, fallback_size: Vector2i) -> Sprite2D:
	var sprite: Sprite2D = Sprites.standing(path, fallback_size, Color("#9c1420"))
	sprite.position = at
	sprite.z_index = Z_DECAL
	add_child(sprite)
	return sprite


## A soft drop shadow on the floor.
func _shadow(at: Vector2, radius: Vector2) -> Polygon2D:
	var shadow: Polygon2D = Sprites.ellipse(radius, SHADOW_COLOR)
	shadow.position = at
	shadow.z_index = Z_SHADOW
	add_child(shadow)
	return shadow


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
