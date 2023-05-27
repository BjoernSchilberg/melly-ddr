import pew
from pew import K_LEFT, K_RIGHT, K_UP, K_DOWN

import random

screen = pew.Pix()
note_bars = [set()] * 8


def new_round():
    which_button = random.randint(1, 6)
    if which_button == 1:
        new_bar = {K_LEFT}
    elif which_button == 2:
        new_bar = {K_DOWN}
    elif which_button == 3:
        new_bar = {K_UP}
    elif which_button == 4:
        new_bar = {K_RIGHT}
    else:
        new_bar = set()
    note_bars.pop(0)
    note_bars.append(new_bar)


async def splash_screen(text):
    screen.box(0, 0, 0, 8, 8)
    for dx in range(-8, text.width):
        screen.blit(text, -dx, 1)
        pew.show(screen)
        await pew.tick(1 / 12)


def show_points(points, x, width):
    screen.box(0, x, 0, width, 8)
    bar_y = 8 - int(points / 3)
    rem_y = points % 3
    if bar_y < 8:
        screen.box(3, x, bar_y, width, 8)
    if rem_y:
        screen.box(rem_y, x, bar_y - 1, width, 1)


def show_note_bars(keys):
    screen.box(1, 0, 6, 6, 1)
    line = 7
    for bar in note_bars:
        if line == 6:
            white = 3
            black1 = black2 = black3 = black4 = 2 if keys else 1
        else:
            white = 2
            black1 = 1 if keys & K_LEFT else 0
            black2 = 1 if keys & K_DOWN else 0
            black3 = 1 if keys & K_UP else 0
            black4 = 1 if keys & K_RIGHT else 0
        screen.pixel(1, line, white if K_LEFT in bar else black1)
        screen.pixel(2, line, white if K_DOWN in bar else black2)
        screen.pixel(3, line, white if K_UP in bar else black3)
        screen.pixel(4, line, white if K_RIGHT in bar else black4)
        line -= 1  # line = line - 1
    screen.pixel(0, 6, 2 if keys else 1)
    screen.pixel(5, 6, 2 if keys else 1)


async def main():
    try:
        await inner_main()
    except Exception as exc:
        import traceback

        err = Element("pewpew")
        err.element.setAttribute(
            "style",
            "color: red; font-family: monospace; font-size: 0.5em",
        )

        lines = ["<pre>\n"]
        lines.extend(traceback.format_exception(exc))
        lines.append("</pre>\n")
        err.write("".join(lines))


async def inner_main():
    pew.init()

    text = pew.Pix.from_text("Konami ")
    await splash_screen(text)

    speed = 0
    buttonpressed = False
    points = 0
    ticks = 0
    while True:
        pew.brightness(speed)
        keys = await pew.keys()
        if ticks % (7 - speed) == 0:
            new_round()
            if points == 24:
                if speed == 3:
                    text = pew.Pix.from_text("YOU WON :] ")
                    pew.brightness(0)
                    await splash_screen(text)
                    break
                speed += 1
                points = 0
        if keys == 0 or not buttonpressed:
            if keys & pew.K_LEFT:
                if K_LEFT in note_bars[1]:
                    points += 1
                buttonpressed = True
            if keys & pew.K_RIGHT:
                if K_RIGHT in note_bars[1]:
                    points += 1
                buttonpressed = True
            if keys & pew.K_DOWN:
                if K_DOWN in note_bars[1]:
                    points += 1
                buttonpressed = True
            if keys & pew.K_UP:
                if K_UP in note_bars[1]:
                    points += 1
                buttonpressed = True
            if keys == 0:
                buttonpressed = False
        show_points(points, x=6, width=2)
        show_note_bars(keys)
        pew.show(screen)
        await pew.tick(1 / 15)
        ticks += 1
