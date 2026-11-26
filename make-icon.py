from PIL import Image, ImageDraw

grid_size = 64
canvas = Image.new("RGBA", (grid_size, grid_size), (0, 0, 0, 0))
px = canvas.load()

BG = (22, 24, 28, 255)          # Тёмный фон (#16181c)
BORDER = (255, 190, 11, 255)    # Ярко-золотая круглая обводка
ORANGE = (255, 162, 0, 255)     # Яркий рыжий
DARK_OR = (255, 115, 0, 255)    # Полоски
LIGHT_OR = (255, 209, 102, 255) # Светлые ушки
WHITE = (255, 255, 255, 255)    # Мордочка
EYE = (30, 30, 38, 255)         # Глазки и улыбка
NOSE = (255, 77, 136, 255)      # Носик
BLUSH = (255, 112, 166, 255)    # Румянец

draw_small = ImageDraw.Draw(canvas)

# 1. Идеальный круг 64x64 для аватарки GitHub
draw_small.ellipse([1, 1, 62, 62], fill=BG, outline=BORDER, width=2)

# 2. Голова кота
draw_small.rounded_rectangle([13, 21, 50, 51], radius=9, fill=ORANGE)

# 3. Острые ушки
for i in range(11):
    draw_small.line([13, 24 - i, 13 + (10 - i), 24 - i], fill=ORANGE)
    if 1 < i < 8:
        draw_small.line([15, 23 - i, 15 + (6 - i), 23 - i], fill=LIGHT_OR)
    draw_small.line([50 - (10 - i), 24 - i, 50, 24 - i], fill=ORANGE)
    if 1 < i < 8:
        draw_small.line([48 - (6 - i), 23 - i, 48, 23 - i], fill=LIGHT_OR)

# 4. Полоски на лбу и щёчках
draw_small.rectangle([25, 22, 27, 26], fill=DARK_OR)
draw_small.rectangle([31, 22, 32, 28], fill=DARK_OR)
draw_small.rectangle([36, 22, 38, 26], fill=DARK_OR)
draw_small.rectangle([14, 34, 17, 36], fill=DARK_OR)
draw_small.rectangle([46, 34, 49, 36], fill=DARK_OR)

# 5. Довольные прищуренные глазки (^ ^)
left_eye = [(18, 34), (19, 33), (20, 32), (21, 31), (22, 31), (23, 32), (24, 33), (25, 34),
            (19, 34), (20, 33), (21, 32), (22, 32), (23, 33), (24, 34)]
right_eye = [(38, 34), (39, 33), (40, 32), (41, 31), (42, 31), (43, 32), (44, 33), (45, 34),
             (39, 34), (40, 33), (41, 32), (42, 32), (43, 33), (44, 34)]
for x, y in left_eye + right_eye:
    px[x, y] = EYE

# 6. Румянец
draw_small.rectangle([18, 36, 22, 38], fill=BLUSH)
draw_small.rectangle([41, 36, 45, 38], fill=BLUSH)

# 7. Белая мордочка
draw_small.rounded_rectangle([23, 37, 40, 48], radius=5, fill=WHITE)

# 8. Розовый носик
draw_small.rectangle([30, 39, 33, 41], fill=NOSE)

# 9. Довольная улыбка (w)
smile = [
    (31, 42), (32, 42), (31, 43), (32, 43),
    (26, 44), (27, 45), (28, 46), (29, 46), (30, 45), (31, 44),
    (32, 44), (33, 45), (34, 46), (35, 46), (36, 45), (37, 44)
]
for x, y in smile:
    px[x, y] = EYE

final_github = canvas.resize((512, 512), resample=Image.NEAREST)
final_github.save("github_avatar.png")
print("Готово! Круглая аватарка сохранена в github_avatar.png")
