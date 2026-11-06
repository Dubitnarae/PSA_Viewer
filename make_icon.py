"""앱 아이콘(icon.ico) 생성: python make_icon.py — 파란 둥근 사각형 + 흰 빈도 분포(종 모양) + 누적 곡선(S자)."""
import math

from PIL import Image, ImageDraw

N = 1024  # 크게 그린 뒤 줄여서 가장자리를 부드럽게


def stroke(d, pts, w, fill):
    """둥근 붓으로 선 긋기 — PIL line은 급한 기울기에서 굵기가 들쭉날쭉해서 점을 촘촘히 찍는다."""
    r = w / 2
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        n = max(1, int(math.hypot(bx - ax, by - ay) / 2))
        for k in range(n + 1):
            x, y = ax + (bx - ax) * k / n, ay + (by - ay) * k / n
            d.ellipse([x - r, y - r, x + r, y + r], fill=fill)


def draw() -> Image.Image:
    img = Image.new("RGBA", (N, N), (0, 0, 0, 0))
    # 위→아래로 밝은 파랑에서 화면 강조색(#0071e3)으로
    grad = Image.new("RGBA", (N, N))
    gd = ImageDraw.Draw(grad)
    for y in range(N):
        t = y / (N - 1)
        gd.line([(0, y), (N, y)], fill=(int(40 + (0 - 40) * t), int(150 + (113 - 150) * t), int(255 + (227 - 255) * t), 255))
    mask = Image.new("L", (N, N), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, N - 1, N - 1], radius=int(N * 0.22), fill=255)
    img.paste(grad, (0, 0), mask)

    d = ImageDraw.Draw(img)
    x0, x1, base, top = N * 0.16, N * 0.84, N * 0.78, N * 0.22
    xs = [x0 + (x1 - x0) * i / 400 for i in range(401)]
    # 빈도 분포: 가우스 종 모양(반투명 채움 + 흰 윤곽)
    bell = [(x, base - (base - top) * 0.78 * math.exp(-((i / 400 - 0.42) / 0.17) ** 2)) for i, x in enumerate(xs)]
    over = Image.new("RGBA", (N, N), (0, 0, 0, 0))
    ImageDraw.Draw(over).polygon([(x0, base), *bell, (x1, base)], fill=(255, 255, 255, 80))
    img.alpha_composite(over)
    stroke(d, bell, N * 0.04, "white")
    # 누적 곡선: S자 (로지스틱)
    cum = [(x, base - (base - top) / (1 + math.exp(-(i / 400 - 0.42) / 0.08))) for i, x in enumerate(xs)]
    stroke(d, cum, N * 0.055, (255, 214, 102, 255))  # 누적은 노란색으로 구분
    # 바닥 축
    stroke(d, [(x0, base), (x1, base)], N * 0.03, "white")
    return img


if __name__ == "__main__":
    big = draw()
    big.resize((256, 256), Image.LANCZOS).save("icon.ico", sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
