"""LED matrix drawing: colours, shapes, a digit font, bars and rainbows.

Pure Python - no numpy, no sense_hat import. Every function returns a flat
64-element list of (r, g, b) tuples ready for SenseHat.set_pixels(), which
means all of it is testable without hardware.

The shapes come from sensehat_config.py (which existed as three identical
copies). The digit font is rescued verbatim from _archive; its author packed
each numeral into 4x4, where 8 is necessarily a solid block - the data is kept
as designed rather than second-guessed.
"""

GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
PINK = (255, 105, 180)
OFF = (0, 0, 0)

COLORS = {
    "green": GREEN, "blue": BLUE, "red": RED, "white": WHITE,
    "yellow": YELLOW, "pink": PINK, "off": OFF,
}

# --- shapes ---------------------------------------------------------------
# Each is an 8x8 grid of keys into a palette, so one bitmap can be recoloured.
_SHAPE_GRIDS = {
    "heart": [
        "........",
        ".PP.PP..",
        "PPPPPPP.",
        "PPPPPPP.",
        ".PPPPP..",
        "..PPP...",
        "...P....",
        "........",
    ],
    "plus": [
        "........",
        "...PP...",
        "...PP...",
        ".PPPPPP.",
        ".PPPPPP.",
        "...PP...",
        "...PP...",
        "........",
    ],
    "equals": [
        "........",
        ".PPPPPP.",
        ".PPPPPP.",
        "........",
        "........",
        ".PPPPPP.",
        ".PPPPPP.",
        "........",
    ],
    "raspi_logo": [
        ".GG..GG.",
        "..GGGG..",
        "..RRRR..",
        ".RRRRRR.",
        "RRRRRRRR",
        "RRRRRRRR",
        ".RRRRRR.",
        "..RRRR..",
    ],
    "trinket_logo": [
        "........",
        ".YYYBG..",
        "YYYYYBG.",
        "YYYYYBG.",
        "YYYYYBG.",
        "YYYYYBG.",
        ".YYYBG..",
        "........",
    ],
}

_PALETTE = {"G": GREEN, "R": RED, "Y": YELLOW, "B": BLUE, ".": OFF}


def shape(name, colour=BLUE):
    """An 8x8 shape as 64 (r, g, b) tuples. `colour` fills the 'P' pixels."""
    if name not in _SHAPE_GRIDS:
        raise KeyError("unknown shape {!r}; have: {}".format(
            name, ", ".join(sorted(_SHAPE_GRIDS))))
    palette = dict(_PALETTE)
    palette["P"] = colour
    return [palette[ch] for row in _SHAPE_GRIDS[name] for ch in row]


SHAPES = tuple(sorted(_SHAPE_GRIDS))

# --- digit font -----------------------------------------------------------
# Ten 4x4 numerals, row-major, 16 entries each.
DIGITS = [
    # 0
    [
        0, 1, 1, 1,
        0, 1, 0, 1,
        0, 1, 0, 1,
        0, 1, 1, 1,
    ],
    # 1
    [
        0, 0, 1, 0,
        0, 1, 1, 0,
        0, 0, 1, 0,
        0, 1, 1, 1,
    ],
    # 2
    [
        0, 1, 1, 1,
        0, 0, 1, 1,
        0, 1, 1, 0,
        0, 1, 1, 1,
    ],
    # 3
    [
        0, 1, 1, 1,
        0, 0, 1, 1,
        0, 0, 1, 1,
        0, 1, 1, 1,
    ],
    # 4
    [
        0, 1, 0, 1,
        0, 1, 1, 1,
        0, 0, 0, 1,
        0, 0, 0, 1,
    ],
    # 5
    [
        0, 1, 1, 1,
        0, 1, 1, 0,
        0, 0, 1, 1,
        0, 1, 1, 1,
    ],
    # 6
    [
        0, 1, 0, 0,
        0, 1, 1, 1,
        0, 1, 0, 1,
        0, 1, 1, 1,
    ],
    # 7
    [
        0, 1, 1, 1,
        0, 0, 0, 1,
        0, 0, 1, 0,
        0, 1, 0, 0,
    ],
    # 8
    [
        0, 1, 1, 1,
        0, 1, 1, 1,
        0, 1, 1, 1,
        0, 1, 1, 1,
    ],
    # 9
    [
        0, 1, 1, 1,
        0, 1, 0, 1,
        0, 1, 1, 1,
        0, 0, 0, 1,
    ],
]


def digit_pixels(value, colour=WHITE, background=OFF):
    """One digit (0-9) as a 4x4 grid of 16 tuples."""
    if not 0 <= value <= 9:
        raise ValueError("digit must be 0-9, got {}".format(value))
    return [colour if bit else background for bit in DIGITS[value]]


def clock_pixels(hour, minute, hour_colour=RED, minute_colour=(0, 255, 255)):
    """A 4-digit clock on the 8x8 grid: hour on top, minute below.

    Each row of the display is 8 wide, so two 4-wide digits sit side by side.
    """
    if not 0 <= hour <= 23 or not 0 <= minute <= 59:
        raise ValueError("bad time {}:{}".format(hour, minute))

    quads = [
        (hour // 10, hour_colour), (hour % 10, hour_colour),
        (minute // 10, minute_colour), (minute % 10, minute_colour),
    ]
    grids = [digit_pixels(v, c) for v, c in quads]

    pixels = []
    for half in (0, 1):                       # top pair, then bottom pair
        left, right = grids[half * 2], grids[half * 2 + 1]
        for row in range(4):
            pixels.extend(left[row * 4:(row + 1) * 4])
            pixels.extend(right[row * 4:(row + 1) * 4])
    return pixels


# --- bars -----------------------------------------------------------------

def clamp(value, min_value, max_value):
    """`value` limited to the inclusive range min_value..max_value."""
    return min(max_value, max(min_value, value))


def scale(value, from_min, from_max, to_min=0, to_max=8):
    """Rescale `value` from one inclusive range to another."""
    from_range = from_max - from_min
    if from_range == 0:
        return to_min
    return (((value - from_min) / from_range) * (to_max - to_min)) + to_min


def bar_pixels(bars, background=OFF):
    """Vertical bars on the 8x8 grid, drawn bottom-up.

    `bars` is a sequence of (x, width, height, colour). Height is in pixels,
    0-8. Anything off-grid is clipped rather than raising.
    """
    grid = [[background] * 8 for _ in range(8)]
    for x, width, height, colour in bars:
        height = int(round(clamp(height, 0, 8)))
        for col in range(x, min(x + width, 8)):
            if col < 0:
                continue
            for row in range(8 - height, 8):
                grid[row][col] = colour
    return [pixel for row in grid for pixel in row]


def reading_bars(specs):
    """Bars from (value, min, max, colour) tuples, evenly spaced across 8px.

    Three readings become three 2px bars with 1px gaps, the layout the
    archived bar-graph used for temperature / pressure / humidity.
    """
    positions = {1: [(3, 2)], 2: [(1, 2), (5, 2)], 3: [(0, 2), (3, 2), (6, 2)]}
    layout = positions.get(len(specs))
    if layout is None:
        raise ValueError("reading_bars handles 1-3 readings, got {}".format(len(specs)))
    bars = []
    for (value, low, high, colour), (x, width) in zip(specs, layout):
        bars.append((x, width, scale(clamp(value, low, high), low, high), colour))
    return bar_pixels(bars)


# --- animation ------------------------------------------------------------

def rainbow_frame(offset=0.0):
    """One frame of a rainbow sweep: 64 tuples, hue varying across the grid."""
    import colorsys
    pixels = []
    for index in range(64):
        hue = ((index / 64.0) + offset) % 1.0
        r, g, b = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
        pixels.append((int(r * 255), int(g * 255), int(b * 255)))
    return pixels
