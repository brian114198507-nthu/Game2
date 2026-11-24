extends Node3D

const MAX_COINS := 6
const PALETTE := {
	"ink": Color("101629"),
	"panel": Color("151e34"),
	"panel_light": Color("202b45"),
	"paper": Color("f5efdf"),
	"muted": Color("b9c2d2"),
	"gold": Color("ffd174"),
	"teal": Color("74d7c4"),
	"rose": Color("ff9f9e"),
	"violet": Color("b6a5ff"),
}

var ui: Control
var page: VBoxContainer
var story_panel: PanelContainer
var scroll: ScrollContainer
var header_hint: Label
var lantern_light: OmniLight3D
var score_text: Label
var key_text: Label
var hint_text: Label
var state := "title"
var level_scores := [0, 0]
var keys_found := [false, false]
var attempts := 0
var level_started := 0.0
var level_one_completed := false
var level_two_completed := false
var stage_two_values := [2, 2, 2]
var last_level_one_answer := -1
var level_two_observation := ""


func _ready() -> void:
	_build_world()
	_build_interface()
	_show_title()


func _build_world() -> void:
	var environment := WorldEnvironment.new()
	environment.name = "DreamEnvironment"
	var env := Environment.new()
	env.background_mode = Environment.BG_COLOR
	env.background_color = Color("080d18")
	env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.ambient_light_color = Color("7189b6")
	env.ambient_light_energy = 0.48
	env.tonemap_mode = Environment.TONE_MAPPER_FILMIC
	env.glow_enabled = true
	env.glow_intensity = 0.38
	env.glow_strength = 0.72
	env.fog_enabled = true
	env.fog_light_color = Color("18243a")
	env.fog_density = 0.012
	environment.environment = env
	add_child(environment)

	var camera := Camera3D.new()
	camera.name = "DreamCamera"
	camera.position = Vector3(0.0, 3.8, 13.5)
	camera.fov = 36.0
	camera.look_at_from_position(camera.position, Vector3(0.0, 1.0, 0.0))
	add_child(camera)
	camera.current = true

	var sun := DirectionalLight3D.new()
	sun.rotation_degrees = Vector3(-37.0, -24.0, 0.0)
	sun.light_color = Color("a8c6ff")
	sun.light_energy = 0.82
	sun.shadow_enabled = true
	sun.directional_shadow_max_distance = 28.0
	add_child(sun)
	var set_path := "res://assets/models/moon_archive.glb"
	if ResourceLoader.exists(set_path):
		var set_scene := load(set_path) as PackedScene
		if set_scene != null:
			var archive := set_scene.instantiate()
			archive.name = "MoonArchiveSet"
			add_child(archive)

	# Cool moonlight and warm practical lights carve the room into readable depth.
	_add_world_light("WindowMoonFill", Vector3(5.5, 3.3, -4.1), Color("87baff"), 1.55, 9.0)
	_add_world_light("ArchiveLanternGlow", Vector3(-1.6, 2.2, -4.0), Color("ffb75b"), 1.8, 6.0)
	_add_world_light("DreamTreeGlow", Vector3(5.8, 2.2, -1.8), Color("f7ce81"), 1.35, 5.5)
	_add_world_light("AruLanternLight", Vector3(3.75, 0.95, -1.5), Color("ffc36a"), 1.2, 4.0)
	lantern_light = OmniLight3D.new()
	lantern_light.name = "LanternLight"
	lantern_light.position = Vector3(3.75, 0.95, -1.5)
	lantern_light.light_color = Color("ffd487")
	lantern_light.light_energy = 1.05
	lantern_light.omni_range = 4.2
	add_child(lantern_light)


func _add_world_light(label: String, at: Vector3, tint: Color, strength: float, radius: float) -> void:
	var light := OmniLight3D.new()
	light.name = label
	light.position = at
	light.light_color = tint
	light.light_energy = strength
	light.omni_range = radius
	add_child(light)


func _add_mesh(label: String, mesh: Mesh, at: Vector3, tint: Color) -> MeshInstance3D:
	var item := MeshInstance3D.new()
	item.name = label
	item.mesh = mesh
	item.position = at
	var material := StandardMaterial3D.new()
	material.albedo_color = tint
	material.roughness = 0.84
	item.material_override = material
	add_child(item)
	return item


func _add_box(label: String, dimensions: Vector3, at: Vector3, tint: Color) -> MeshInstance3D:
	var mesh := BoxMesh.new()
	mesh.size = dimensions
	return _add_mesh(label, mesh, at, tint)


func _add_sphere(label: String, radius: float, at: Vector3, tint: Color) -> MeshInstance3D:
	var mesh := SphereMesh.new()
	mesh.radius = radius
	mesh.height = radius * 2.0
	mesh.radial_segments = 12
	mesh.rings = 8
	return _add_mesh(label, mesh, at, tint)


func _add_cylinder(label: String, radius: float, height: float, at: Vector3, tint: Color) -> MeshInstance3D:
	var mesh := CylinderMesh.new()
	mesh.top_radius = radius
	mesh.bottom_radius = radius * 1.35
	mesh.height = height
	mesh.radial_segments = 9
	return _add_mesh(label, mesh, at, tint)


func _build_interface() -> void:
	var layer := CanvasLayer.new()
	layer.layer = 2
	add_child(layer)
	ui = Control.new()
	ui.name = "Interface"
	ui.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	layer.add_child(ui)
	var cjk_font := load("res://assets/fonts/NotoSansTC.ttf") as FontFile
	if cjk_font != null:
		var game_theme := Theme.new()
		game_theme.default_font = cjk_font
		game_theme.default_font_size = 16
		ui.theme = game_theme

	var brand := Label.new()
	brand.text = "✦  夢境存錢旅"
	brand.position = Vector2(44, 22)
	brand.add_theme_font_size_override("font_size", 19)
	brand.add_theme_color_override("font_color", PALETTE.gold)
	ui.add_child(brand)

	header_hint = Label.new()
	header_hint.text = "一段為明天留一點光的冒險"
	header_hint.position = Vector2(218, 24)
	header_hint.add_theme_font_size_override("font_size", 15)
	header_hint.add_theme_color_override("font_color", PALETTE.muted)
	ui.add_child(header_hint)

	key_text = Label.new()
	key_text.position = Vector2(920, 24)
	key_text.size = Vector2(300, 34)
	key_text.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	key_text.add_theme_font_size_override("font_size", 16)
	key_text.add_theme_color_override("font_color", PALETTE.gold)
	ui.add_child(key_text)

	score_text = Label.new()
	score_text.position = Vector2(920, 54)
	score_text.size = Vector2(300, 28)
	score_text.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	score_text.add_theme_font_size_override("font_size", 14)
	score_text.add_theme_color_override("font_color", PALETTE.paper)
	ui.add_child(score_text)

	story_panel = PanelContainer.new()
	story_panel.name = "StoryPanel"
	story_panel.position = Vector2(42, 82)
	story_panel.size = Vector2(762, 594)
	var panel_style := StyleBoxFlat.new()
	panel_style.bg_color = Color(0.075, 0.095, 0.15, 0.94)
	panel_style.border_color = Color(0.42, 0.47, 0.60, 0.64)
	panel_style.set_border_width_all(1)
	panel_style.set_corner_radius_all(18)
	panel_style.set_content_margin_all(26)
	story_panel.add_theme_stylebox_override("panel", panel_style)
	ui.add_child(story_panel)

	var margin := MarginContainer.new()
	margin.add_theme_constant_override("margin_left", 3)
	margin.add_theme_constant_override("margin_right", 3)
	margin.add_theme_constant_override("margin_top", 2)
	margin.add_theme_constant_override("margin_bottom", 2)
	story_panel.add_child(margin)
	scroll = ScrollContainer.new()
	scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	margin.add_child(scroll)
	page = VBoxContainer.new()
	page.add_theme_constant_override("separation", 14)
	page.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	scroll.add_child(page)

	hint_text = Label.new()
	hint_text.anchor_left = 0.02
	hint_text.anchor_right = 0.61
	hint_text.anchor_top = 0.93
	hint_text.anchor_bottom = 0.99
	hint_text.add_theme_font_size_override("font_size", 12)
	hint_text.add_theme_color_override("font_color", Color("bac2d4"))
	hint_text.text = "可用滑鼠、觸控或鍵盤 Tab / Enter 操作。"
	ui.add_child(hint_text)
	ui.resized.connect(_layout_interface)
	_layout_interface()
	_update_hud()


func _layout_interface() -> void:
	if ui == null or story_panel == null:
		return
	var width := ui.size.x
	var height := ui.size.y
	var narrow := width < 880.0
	story_panel.position = Vector2(16.0 if narrow else 42.0, 72.0 if narrow else 82.0)
	story_panel.size = Vector2(maxf(320.0, width - (32.0 if narrow else 518.0)), maxf(360.0, height - (108.0 if narrow else 126.0)))
	header_hint.visible = not narrow
	key_text.anchor_left = 1.0
	key_text.anchor_right = 1.0
	key_text.offset_left = -330.0
	key_text.offset_right = -22.0
	score_text.anchor_left = 1.0
	score_text.anchor_right = 1.0
	score_text.offset_left = -330.0
	score_text.offset_right = -22.0
	hint_text.visible = not narrow


func _update_hud() -> void:
	var key_count := int(keys_found[0]) + int(keys_found[1])
	key_text.text = "月光鑰匙  %d / 2" % key_count
	score_text.text = "第 1 關 %d 　·　 第 2 關 %d" % [level_scores[0], level_scores[1]]


func _clear_page() -> void:
	for child in page.get_children():
		child.queue_free()
	_update_hud()


func _label(text: String, size: int, tint: Color = PALETTE.paper) -> Label:
	var item := Label.new()
	item.text = text
	item.add_theme_font_size_override("font_size", size)
	item.add_theme_color_override("font_color", tint)
	item.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	return item


func _button(text: String, callback: Callable, prominent := false) -> Button:
	var button := Button.new()
	button.text = text
	button.custom_minimum_size = Vector2(0, 54)
	button.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	button.add_theme_font_size_override("font_size", 17)
	button.add_theme_color_override("font_color", Color("19202e") if prominent else PALETTE.paper)
	button.add_theme_color_override("font_hover_color", Color("19202e") if prominent else Color.WHITE)
	var normal := StyleBoxFlat.new()
	normal.bg_color = PALETTE.gold if prominent else PALETTE.panel_light
	normal.border_color = Color("ffe5ad") if prominent else Color("3b4964")
	normal.set_border_width_all(1)
	normal.set_corner_radius_all(12)
	normal.set_content_margin_all(12)
	var hover := normal.duplicate() as StyleBoxFlat
	hover.bg_color = Color("ffe0a0") if prominent else Color("2a3957")
	var pressed := normal.duplicate() as StyleBoxFlat
	pressed.bg_color = Color("e6b75e") if prominent else Color("37486a")
	button.add_theme_stylebox_override("normal", normal)
	button.add_theme_stylebox_override("hover", hover)
	button.add_theme_stylebox_override("pressed", pressed)
	button.add_theme_stylebox_override("focus", hover)
	button.pressed.connect(callback)
	return button


func _show_title() -> void:
	state = "title"
	_clear_page()
	page.add_child(_label("兩把鑰匙，兩個為明天做的選擇。", 18, PALETTE.teal))
	page.add_child(_label("月光\n存錢旅", 49, PALETTE.paper))
	page.add_child(_label("夜色裡，飛蛾旅人阿露要穿過沉睡的鐘樓。\n先安排好零用錢，再為遠一點的夢想留一盞燈。", 18, PALETTE.muted))
	var spacer := Control.new()
	spacer.custom_minimum_size.y = 6
	page.add_child(spacer)
	page.add_child(_label("2 個關卡　·　每關解題取得月光鑰匙　·　約 5 分鐘", 14, PALETTE.gold))
	page.add_child(_button("開始今晚的冒險  →", _start_game, true))
	page.add_child(_label("小提醒：這是學習用的虛構遊戲，不代表真實投資建議。", 13, PALETTE.muted))


func _start_game() -> void:
	level_scores = [0, 0]
	keys_found = [false, false]
	level_one_completed = false
	level_two_completed = false
	last_level_one_answer = -1
	stage_two_values = [2, 2, 2]
	attempts = 0
	_start_level_clock()
	_show_level_one("")


func _start_level_clock() -> void:
	attempts = 1
	level_started = Time.get_ticks_msec() / 1000.0


func _show_level_one(feedback: String) -> void:
	state = "level_one"
	_clear_page()
	page.add_child(_label("關卡 1  /  需求和願望", 14, PALETTE.teal))
	page.add_child(_label("雨夜的預算門", 33))
	page.add_child(_label("阿露有 10 枚星幣。下雨了，急需的雨衣要 4 枚。\n她還想在兩個夜晚後買一盞 8 枚的暖光燈。", 17, PALETTE.muted))
	page.add_child(_label("選一個安排，讓現在需要的東西和以後的目標都照顧到：", 16, PALETTE.paper))
	if not feedback.is_empty():
		page.add_child(_label(feedback, 14, PALETTE.rose))
	page.add_child(_button("A　買雨衣 4 枚，留下 6 枚繼續存", _answer_level_one.bind(0), true))
	page.add_child(_button("B　買點心 3 枚，留下 7 枚", _answer_level_one.bind(1)))
	page.add_child(_button("C　買收藏玩具 5 枚，留下 5 枚", _answer_level_one.bind(2)))
	page.add_child(_label("想一想：哪一項是現在的需要？留下來的錢能不能幫助以後的目標？", 13, PALETTE.gold))


func _answer_level_one(choice: int) -> void:
	last_level_one_answer = choice
	if choice == 0:
		level_scores[0] = _score_for_attempts()
		keys_found[0] = true
		level_one_completed = true
		_update_hud()
		_show_level_one_result()
	else:
		attempts += 1
		var reason := "點心是願望，不是此刻下雨時最需要的東西。" if choice == 1 else "收藏玩具會用掉太多星幣，留下的錢還不夠達成暖光燈目標。"
		_show_level_one(reason + " 先滿足需要，也替目標保留一部分，試試看其他安排。")


func _score_for_attempts() -> int:
	var elapsed := (Time.get_ticks_msec() / 1000.0) - level_started
	var accuracy_score := maxi(55, 100 - (attempts - 1) * 15)
	var small_speed_bonus := 5 if elapsed <= 25.0 else 0
	return mini(100, accuracy_score + small_speed_bonus)


func _show_level_one_result() -> void:
	state = "level_one_result"
	_clear_page()
	page.add_child(_label("✦  月光鑰匙 1 已取得", 15, PALETTE.gold))
	page.add_child(_label("你先照顧了雨天的需要，也替想要的燈留下存款。", 23))
	page.add_child(_label("關卡得分　%d / 100" % level_scores[0], 29, PALETTE.teal))
	page.add_child(_label("先分清需要和願望，再按目標安排錢，會比較容易走到想去的地方。", 16, PALETTE.muted))
	page.add_child(_button("走進鐘樓花園  →", _show_level_two_intro, true))


func _show_level_two_intro() -> void:
	state = "level_two_intro"
	_clear_page()
	page.add_child(_label("關卡 2  /  儲蓄和投資", 14, PALETTE.teal))
	page.add_child(_label("夢樹花園", 33))
	page.add_child(_label("阿露拿著 6 枚星幣，要在明天支付 2 枚車票，\n也想讓剩下的錢為更久以後的飛行夢想工作。", 17, PALETTE.muted))
	page.add_child(_label("存錢罐裡的錢比較穩定；夢樹可能長出果實，也可能遇到壞天氣。\n請先留下短期要用的錢，再把投資分散到兩株夢樹。", 16, PALETTE.paper))
	page.add_child(_label("虛構例子：投資有風險，結果不保證；不要把短期需要的錢拿去冒險。", 14, PALETTE.gold))
	page.add_child(_button("開始分配 6 枚星幣  →", _begin_level_two, true))


func _begin_level_two() -> void:
	state = "level_two"
	_start_level_clock()
	stage_two_values = [6, 0, 0]
	_show_level_two("")


func _show_level_two(feedback: String) -> void:
	state = "level_two"
	_clear_page()
	page.add_child(_label("關卡 2  /  分散長期夢想金", 14, PALETTE.teal))
	page.add_child(_label("6 枚星幣，要怎麼放？", 30))
	page.add_child(_label("明天的車票需要 2 枚。存錢罐不會減少；夢樹結果不一定。\n用 − / + 調整，總數必須剛好是 6。", 16, PALETTE.muted))
	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", 9)
	page.add_child(row)
	_add_allocation_card(row, "安全存錢罐", 0, "短期車票")
	_add_allocation_card(row, "北風夢樹", 1, "可能增減")
	_add_allocation_card(row, "雨滴夢樹", 2, "可能增減")
	var total: int = stage_two_values[0] + stage_two_values[1] + stage_two_values[2]
	var total_color: Color = PALETTE.teal if total == MAX_COINS else PALETTE.gold
	page.add_child(_label("已分配  %d / 6" % total, 16, total_color))
	if not feedback.is_empty():
		page.add_child(_label(feedback, 14, PALETTE.rose))
	page.add_child(_button("種下夢想，看看天氣  →", _resolve_level_two, true))
	page.add_child(_label("提示：先留夠明天要用的錢；長期投資不要全放在同一株。", 13, PALETTE.gold))


func _add_allocation_card(parent: HBoxContainer, title: String, index: int, note: String) -> void:
	var card := PanelContainer.new()
	card.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	var style := StyleBoxFlat.new()
	style.bg_color = Color("202b45")
	style.border_color = Color("3c4a66")
	style.set_border_width_all(1)
	style.set_corner_radius_all(12)
	style.set_content_margin_all(8)
	card.add_theme_stylebox_override("panel", style)
	parent.add_child(card)
	var box := VBoxContainer.new()
	box.add_theme_constant_override("separation", 5)
	card.add_child(box)
	box.add_child(_label(title, 14, PALETTE.paper))
	box.add_child(_label(note, 11, PALETTE.muted))
	var controls := HBoxContainer.new()
	controls.add_theme_constant_override("separation", 3)
	box.add_child(controls)
	var minus := _button("−", _change_allocation.bind(index, -1))
	minus.custom_minimum_size = Vector2(42, 42)
	minus.size_flags_horizontal = Control.SIZE_SHRINK_BEGIN
	controls.add_child(minus)
	var amount := _label("%d" % stage_two_values[index], 22, PALETTE.gold)
	amount.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	amount.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	controls.add_child(amount)
	var plus := _button("+", _change_allocation.bind(index, 1))
	plus.custom_minimum_size = Vector2(42, 42)
	plus.size_flags_horizontal = Control.SIZE_SHRINK_END
	controls.add_child(plus)


func _change_allocation(index: int, delta: int) -> void:
	var total: int = stage_two_values[0] + stage_two_values[1] + stage_two_values[2]
	if stage_two_values[index] + delta < 0:
		return
	if delta > 0 and total >= MAX_COINS:
		return
	stage_two_values[index] += delta
	_show_level_two("")


func _resolve_level_two() -> void:
	var total: int = stage_two_values[0] + stage_two_values[1] + stage_two_values[2]
	if total != MAX_COINS:
		attempts += 1
		_show_level_two("先把 6 枚星幣全部安排好，想一想哪些要安全留著。")
		return
	var has_reserve: bool = stage_two_values[0] >= 2
	var spread: bool = stage_two_values[1] > 0 and stage_two_values[2] > 0
	if has_reserve and spread:
		level_two_observation = "北風夢樹少了 1 枚，雨滴夢樹多了 2 枚；分開放置後，變化不會只來自一株。存錢罐中的車票錢仍在。"
		level_scores[1] = _score_for_attempts()
		keys_found[1] = true
		level_two_completed = true
		_update_hud()
		_show_level_two_result()
	else:
		attempts += 1
		var reason := "明天要搭車的 2 枚還沒有安全留下。" if not has_reserve else "把投資分開放在兩株夢樹，再觀察其中一株遇到壞天氣時會怎樣。"
		_show_level_two(reason + " 可以調整後再試；這裡的結果只是虛構例子。")


func _show_level_two_result() -> void:
	state = "level_two_result"
	_clear_page()
	page.add_child(_label("✦  月光鑰匙 2 已取得", 15, PALETTE.gold))
	page.add_child(_label("你留下明天要用的錢，也沒有把長期投資全放在一處。", 22))
	page.add_child(_label("關卡得分　%d / 100" % level_scores[1], 29, PALETTE.teal))
	page.add_child(_label(level_two_observation, 15, PALETTE.muted))
	page.add_child(_label("記住：投資可能增值，也可能減少；分散不能保證獲利，但能避免只依賴一項。", 14, PALETTE.gold))
	page.add_child(_button("看看今晚的進步成果  →", _show_final_results, true))


func _show_final_results() -> void:
	state = "results"
	_clear_page()
	var total: int = level_scores[0] + level_scores[1]
	page.add_child(_label("兩把鑰匙，兩個為明天做的選擇。", 15, PALETTE.gold))
	page.add_child(_label("今晚的冒險成果", 32))
	page.add_child(_label("總分  %d / 200" % total, 27, PALETTE.teal))
	page.add_child(_label("第 1 關　%3d / 100　·　需要優先、為目標儲蓄" % level_scores[0], 16))
	page.add_child(_label("第 2 關　%3d / 100　·　留下備用、分散並理解風險" % level_scores[1], 16))
	page.add_child(_label("這是本次遊戲中的決策表現，不等於正式學習測驗。", 13, PALETTE.muted))
	if level_one_completed:
		page.add_child(_label("✓ 先照顧現在的需要，再替更大的目標存錢", 14, PALETTE.gold))
	if level_two_completed:
		page.add_child(_label("✓ 投資結果不保證；短期要用的錢先安全留下", 14, PALETTE.gold))
	page.add_child(_button("再玩一次  ↻", _start_game, true))
	page.add_child(_label("阿露把星幣收好，鐘樓也亮起了一盞新的光。", 14, PALETTE.muted))


func _process(_delta: float) -> void:
	# A gentle lantern pulse makes the original model readable without relying on sound.
	var glow := 0.7 + 0.12 * sin(Time.get_ticks_msec() / 850.0)
	if is_instance_valid(lantern_light):
		lantern_light.light_energy = glow
