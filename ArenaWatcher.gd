extends Node3D

@export var state_file_path: String = "res://arena_state.json"
@export var poll_interval: float = 1.5

@onready var forge_mesh: MeshInstance3D = $Buildings/Forge
@onready var library_mesh: MeshInstance3D = $Buildings/Library
@onready var observatory_mesh: MeshInstance3D = $Buildings/Observatory
@onready var neon_sign_mesh: MeshInstance3D = $Signs/NeonSign
@onready var log_label: Label = $CanvasLayer/UI/ScrollContainer/VBoxContainer/LogLabel
@onready var status_label: Label = $CanvasLayer/UI/StatusLabel

var last_chronicle_count: int = 0
var poll_timer: Timer

func _ready() -> void:
	poll_timer = Timer.new()
	poll_timer.wait_time = poll_interval
	poll_timer.autostart = true
	poll_timer.timeout.connect(_on_poll_timeout)
	add_child(poll_timer)
	_on_poll_timeout()

func _on_poll_timeout() -> void:
	if not FileAccess.file_exists(state_file_path):
		return
	
	var file = FileAccess.open(state_file_path, FileAccess.READ)
	if file == null:
		return
	var text = file.get_as_text()
	var json = JSON.new()
	var error = json.parse(text)
	if error != OK:
		return
	
	var data = json.data
	if typeof(data) != TYPE_DICTIONARY:
		return
	
	var chronicle = data.get("chronicle", [])
	var town = data.get("town", {})
	var ridewire = data.get("ridewire", {})
	
	if chronicle.size() > last_chronicle_count:
		last_chronicle_count = chronicle.size()
		var latest = chronicle[-1]
		_update_display(latest, town, ridewire, chronicle.size())

func _update_display(entry: Dictionary, town: Dictionary, ridewire: Dictionary, total_count: int) -> void:
	var citizen = entry.get("citizen", "Citizen")
	var attempt = entry.get("attempt", "")
	var learned = entry.get("learned", "")
	var discovered = entry.get("discovered", "")
	var logic_state = entry.get("logic_state", "GENESIS")
	
	if log_label:
		var formatted = "✦ [%s] (13-Logic: %s)\n   Attempt: %s\n   Found: %s\n   Lore: %s\n\n%s" % [
			citizen, logic_state, attempt, discovered, learned, log_label.text
		]
		log_label.text = formatted
	
	if status_label:
		var entropy = ridewire.get("spatial_entropy", town.get("total_entropy_H", 0.0))
		var dom_state = ridewire.get("dominant_13_logic", logic_state)
		var credits = town.get("treasury_credits", 1000.0)
		var sign_text = town.get("active_sign", "WELCOME TO THE ARENA")
		status_label.text = "ROUTE 66 ARENA | MILE %d | 13-LOGIC: %s | H=%.3f | TREASURY: %.0f CR | SIGN: '%s'" % [
			total_count,
			dom_state,
			entropy,
			credits,
			sign_text
		]
	
	# Visually scale buildings to reflect construction milestones
	var forge_lvl = town.get("forge_level", 1)
	if forge_mesh:
		forge_mesh.scale = Vector3.ONE * (1.0 + min(forge_lvl * 0.05, 2.2))
	
	var lib_lvl = town.get("library_level", 1)
	if library_mesh:
		library_mesh.scale = Vector3.ONE * (1.0 + min(lib_lvl * 0.05, 2.2))
		
	var obs_lvl = town.get("observatory_level", 1)
	if observatory_mesh:
		observatory_mesh.scale = Vector3.ONE * (1.0 + min(obs_lvl * 0.05, 2.2))
	
	# Update glowing neon sign
	if neon_sign_mesh:
		var mat = neon_sign_mesh.get_surface_override_material(0)
		if mat is StandardMaterial3D:
			mat.emission_energy_multiplier = float(town.get("neon_intensity", 1.2))
