import asyncio
import js 


_BLUES = (
    (0x00, 0x11, 0x22),
    (0x11, 0x22, 0x40),
    (0x22, 0x46, 0x90),
    (0x46, 0x8c, 0xff),
)
_GREENS = (
    (0x00, 0x22, 0x11),
    (0x11, 0x40, 0x22),
    (0x22, 0x90, 0x46),
    (0x46, 0xff, 0x8c),
)
_YELLOWS = (
    (0x22, 0x22, 0x00),
    (0x40, 0x40, 0x11),
    (0x90, 0x90, 0x22),
    (0xff, 0xff, 0x44),
)
_REDS = (
    (0x33, 0x00, 0x00),
    (0x50, 0x11, 0x00),
    (0xa0, 0x22, 0x11),
    (0xff, 0x44, 0x22),
)

_FONT = (
    b'{{{{{{wws{w{HY{{{{YDYDY{sUtGUsH[wyH{uHgHE{ws{{{{vyxyv{g[K[g{{]f]{{{wDw{{'
    b'{{{wy{{{D{{{{{{{w{K_w}x{VHLHe{wuwww{`KfyD{UKgKU{w}XDK{DxTKT{VxUHU{D[wyx{'
    b'UHfHU{UHEKe{{w{w{{{w{wy{KwxwK{{D{D{{xwKwx{eKg{w{VIHyB{fYH@H{dHdHd{FyxyF{'
    b'`XHX`{DxtxD{Dxtxx{FyxIF{HHDHH{wwwww{KKKHU{HXpXH{xxxxD{Y@DLH{IL@LX{fYHYf{'
    b'`HH`x{fYHIF{`HH`H{UxUKU{Dwwww{HHHIR{HHH]w{HHLD@{HYsYH{HYbww{D[wyD{txxxt{'
    b'x}w_K{GKKKG{wLY{{{{{{{{Dxs{{{{{BIIB{x`XX`{{ByyB{KBIIB{{WIpF{OwUwww{`YB[`'
    b'x`XHH{w{vwc{K{OKHUxHpXH{vwws_{{dD@H{{`XHH{{fYYf{{`XX`x{bYIBK{Ipxx{{F}_d{'
    b'wUws_{{HHIV{{HH]s{{HLD@{{HbbH{{HHV[a{D_}D{Cw|wC{wwwwwwpwOwp{WKfxu{@YYY@{'
)
_SALT = 132
_PALETTE = _BLUES

K_X = 0x01
K_DOWN = 0x02
K_LEFT = 0x04
K_RIGHT = 0x08
K_UP = 0x10
K_O = 0x20
K_SPACE = 0x40

_KEYMAP = {
    "X": K_X,
    "Z": K_O,
    "UP": K_UP,
    "DOWN": K_DOWN,
    "LEFT": K_LEFT,
    "RIGHT": K_RIGHT,
    "SPACE": K_SPACE,
}


def init():
    global _PALETTE
    _PALETTE = _BLUES

    cells = '\n'.join(
        f'<div id="{elem(x, y)}" class="cell"></div>'
        for y in range(8)
        for x in range(8)
    )
    Element("pewpew").write(cells)


def brightness(level):
    global _PALETTE

    _PALETTE = _BLUES
    if level == 1:
        _PALETTE = _GREENS
    elif level == 2:
        _PALETTE = _YELLOWS
    elif level == 3:
        _PALETTE = _REDS


async def tick(delay):
    await asyncio.sleep(delay)


def show(pix):
    for y in range(8):
        for x in range(8):
            clr = _PALETTE[pix.pixel(x, y) & 0x03]
            color_code = f"#{clr[0]:0<2x}{clr[1]:0<2x}{clr[2]:0<2x}"
            element = Element(elem(x, y)).element
            element.setAttribute("style", f"background-color: {color_code}")


async def keys():
    input = js.window.input

    result = 0x00
    for key, mask in _KEYMAP.items():
        if input.isDown(key):
            result |= mask
    input.reset()
    
    return result


def elem(x, y):
    return f"c{x}x{y}"


class GameOver(Exception):
    pass


class Pix:
    def __init__(self, width=8, height=8, buffer=None):
        if buffer is None:
            buffer = bytearray(width * height)
        self.buffer = buffer
        self.width = width
        self.height = height

    @classmethod
    def from_text(cls, string, color=None, bgcolor=0, colors=None):
        pix = cls(4 * len(string), 6)
        font = memoryview(_FONT)
        if colors is None:
            if color is None:
                colors = (3, 2, bgcolor, bgcolor)
            else:
                colors = (color, color, bgcolor, bgcolor)
        x = 0
        for c in string:
            index = ord(c) - 0x20
            if not 0 <= index <= 95:
                continue
            row = 0
            for byte in font[index * 6:index * 6 + 6]:
                unsalted = byte ^ _SALT
                for col in range(4):
                    pix.pixel(x + col, row, colors[unsalted & 0x03])
                    unsalted >>= 2
                row += 1
            x += 4
        return pix

    @classmethod
    def from_iter(cls, lines):
        pix = cls(len(lines[0]), len(lines))
        y = 0
        for line in lines:
            x = 0
            for pixel in line:
                pix.pixel(x, y, pixel)
                x += 1
            y += 1
        return pix

    def pixel(self, x, y, color=None):
        if not 0 <= x < self.width or not 0 <= y < self.height:
            return 0
        if color is None:
            return self.buffer[x + y * self.width]
        self.buffer[x + y * self.width] = color

    def box(self, color, x=0, y=0, width=None, height=None):
        x = min(max(x, 0), self.width - 1)
        y = min(max(y, 0), self.height - 1)
        width = max(0, min(width or self.width, self.width - x))
        height = max(0, min(height or self.height, self.height - y))
        for y in range(y, y + height):
            xx = y * self.width + x
            for i in range(width):
                self.buffer[xx] = color
                xx += 1

    def blit(self, source, dx=0, dy=0, x=0, y=0,
             width=None, height=None, key=None):
        if dx < 0:
            x -= dx
            dx = 0
        if x < 0:
            dx -= x
            x = 0
        if dy < 0:
            y -= dy
            dy = 0
        if y < 0:
            dy -= y
            y = 0
        width = min(min(width or source.width, source.width - x),
                    self.width - dx)
        height = min(min(height or source.height, source.height - y),
                     self.height - dy)
        source_buffer = memoryview(source.buffer)
        self_buffer = self.buffer
        if key is None:
            for row in range(height):
                xx = y * source.width + x
                dxx = dy * self.width + dx
                self_buffer[dxx:dxx + width] = source_buffer[xx:xx + width]
                y += 1
                dy += 1
        else:
            for row in range(height):
                xx = y * source.width + x
                dxx = dy * self.width + dx
                for col in range(width):
                    color = source_buffer[xx]
                    if color != key:
                        self_buffer[dxx] = color
                    dxx += 1
                    xx += 1
                y += 1
                dy += 1

    def __str__(self):
        return "\n".join(
            "".join(
                ('.', '+', '*', '@')[self.pixel(x, y)]
                for x in range(self.width)
            )
            for y in range(self.height)
        )
