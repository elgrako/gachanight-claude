extends RefCounted
## Number formatting for player-facing text (English).

const SUFFIXES: Array = ["", "K", "M", "B", "T", "Qa", "Qi"]


## 950 -> "950", 1500 -> "1.5K", 25000000 -> "25M".
static func number(value: int) -> String:
	if value < 10000:
		return str(value)
	var scaled: float = float(value)
	var index: int = 0
	while scaled >= 1000.0 and index < SUFFIXES.size() - 1:
		scaled /= 1000.0
		index += 1
	var text: String = "%.2f" % scaled if scaled < 10.0 else ("%.1f" % scaled if scaled < 100.0 else "%.0f" % scaled)
	if text.contains("."):
		text = text.rstrip("0").rstrip(".")
	return text + SUFFIXES[index]


static func coins(value: int) -> String:
	return "%s %s" % [number(value), "coin" if value == 1 else "coins"]


static func duration(seconds: float) -> String:
	var total: int = int(seconds)
	return "%d:%02d:%02d" % [total / 3600, (total / 60) % 60, total % 60]
