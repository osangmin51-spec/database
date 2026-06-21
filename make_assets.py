from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


BASE_DIR = Path(__file__).resolve().parent
ASSETS = BASE_DIR / "assets"
ASSETS.mkdir(exist_ok=True)


def font(size: int, bold: bool = False):
    path = Path(r"C:\Windows\Fonts\malgunbd.ttf" if bold else r"C:\Windows\Fonts\malgun.ttf")
    return ImageFont.truetype(str(path), size)


def make_ball(filename: str, title: str, colors: tuple[str, str], accent: str):
    width, height = 900, 460
    image = Image.new("RGB", (width, height), "#0C151D")
    draw = ImageDraw.Draw(image)

    # 볼링 레인 배경을 단순화해 실제 장비 사진처럼 공이 중심에 보이도록 구성한다.
    for x in range(0, width, 90):
        draw.line((x, 0, width // 2 + (x - width // 2) * 0.35, height), fill="#27333C", width=2)
    draw.rectangle((0, height - 86, width, height), fill="#111E27")

    glow = Image.new("RGBA", image.size, (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)
    glow_draw.ellipse((235, 20, 665, 450), fill=accent + "88")
    glow = glow.filter(ImageFilter.GaussianBlur(45))
    image = Image.alpha_composite(image.convert("RGBA"), glow)

    ball_layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    ball = ImageDraw.Draw(ball_layer)
    ball.ellipse((285, 55, 615, 385), fill=colors[0], outline="#DCE8EE", width=3)
    for offset in range(0, 180, 18):
        ball.arc((305 - offset // 4, 70 + offset, 610, 350 + offset // 5), 185, 350, fill=colors[1], width=14)
    ball.ellipse((405, 118, 442, 155), fill="#071016")
    ball.ellipse((456, 103, 493, 140), fill="#071016")
    ball.ellipse((468, 159, 507, 198), fill="#071016")
    image = Image.alpha_composite(image, ball_layer)

    draw = ImageDraw.Draw(image)
    draw.text((40, 32), "TWO-HAND GEAR", font=font(20, True), fill=accent)
    draw.text((40, 62), title, font=font(34, True), fill="#F5F7FA")
    draw.text((40, 108), "DB 이미지 경로 저장 · Flet Image 출력", font=font(15), fill="#9BABBA")
    image.convert("RGB").save(ASSETS / filename, quality=94)


if __name__ == "__main__":
    make_ball("ball_neon.png", "네온 임팩트", ("#25DF67", "#092F19"), "#42E06F")
    make_ball("ball_blue.png", "블루 궤도", ("#2179D5", "#071D38"), "#59B8FF")
    make_ball("ball_white.png", "스페어 화이트", ("#E9EEF2", "#A9B2BA"), "#F5F7FA")

