#!/usr/bin/env python3
"""Genera los recursos de marca de Asalith a partir de una sola definicion.

Salidas:
  assets/asalith-badge.svg  Insignia completa (escena + logotipo).
  assets/favicon.svg        Version reducida, sin texto, legible a 32 px.
  assets/og-asalith.png     Tarjeta 1200x630 para enlaces en Discord y redes.

La geometria (colinas, coniferas, arcos del atardecer) se define una sola vez
como listas de puntos, y de ahi salen tanto el SVG como los PNG. Asi el dibujo
vectorial y el rasterizado no se desincronizan.

Uso:
  python scripts/build_brand_assets.py            genera los recursos
  python scripts/build_brand_assets.py --preview  ademas rasteriza la insignia
                                                  para revisarla a ojo
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"

# --- Paleta, tomada del logotipo ------------------------------------------

VERDE_BORDE = "#2b3823"
CREMA = "#f2ebdc"
ROJO_TIERRA = "#8f2a1c"

# Bandas del atardecer, de fuera hacia dentro.
BANDAS = [
    (270, "#a94219"),
    (228, "#c25a1e"),
    (190, "#d9762a"),
    (156, "#e9a878"),
    (126, "#e0897a"),
    (98, "#eecfae"),
]
SOL = (58, "#ec8b2d")

COLINA_FONDO = "#33452a"
COLINA_FRENTE = "#1e2a18"
ARBOL_FONDO = "#24321c"
ARBOL_FRENTE = "#161f11"

# --- Geometria de la escena (lienzo de referencia 520x520) -----------------

CENTRO = (260.0, 260.0)
R_EXTERIOR = 256.0
R_CREMA = 248.0
R_INTERIOR_BORDE = 236.0
R_ESCENA = 228.0
HORIZONTE = (260.0, 300.0)

# Alturas de las dos colinas en el lienzo de referencia. La colina delantera
# queda justo por encima del logotipo: el texto se apoya en verde solido y la
# linea de coniferas se recorta contra el cielo, como en el logotipo original.
Y_COLINA_FONDO = 318.0
Y_COLINA_FRENTE = 334.0


def colina(y_base: float, amplitud: float, fase: float,
           x0: float = -10.0, x1: float = 530.0, pasos: int = 44) -> list[tuple[float, float]]:
    """Perfil ondulado de una colina, muestreado como lista de puntos."""
    pts = []
    for i in range(pasos + 1):
        x = x0 + (x1 - x0) * i / pasos
        y = y_base + amplitud * math.sin(fase + x / 96.0) + amplitud * 0.45 * math.sin(x / 41.0)
        pts.append((x, y))
    return pts


def cerrar(pts: list[tuple[float, float]], y_fondo: float = 540.0) -> list[tuple[float, float]]:
    """Cierra un perfil por abajo para poder rellenarlo."""
    return pts + [(pts[-1][0], y_fondo), (pts[0][0], y_fondo)]


def altura_colina(pts: list[tuple[float, float]], x: float) -> float:
    """Altura de la colina en una x concreta, para plantar arboles sobre ella."""
    for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
        if x1 <= x <= x2:
            t = (x - x1) / (x2 - x1) if x2 != x1 else 0.0
            return y1 + (y2 - y1) * t
    return pts[-1][1]


def conifera(cx: float, base_y: float, alto: float, ancho: float) -> list[tuple[float, float]]:
    """Silueta de conifera en tres pisos, desde la punta y en sentido horario."""
    a1, a2, a3 = ancho * 0.30, ancho * 0.40, ancho * 0.50
    y1, y2 = base_y - alto * 0.58, base_y - alto * 0.30
    return [
        (cx, base_y - alto),
        (cx + a1, y1), (cx + a1 * 0.55, y1),
        (cx + a2, y2), (cx + a2 * 0.60, y2),
        (cx + a3, base_y),
        (cx - a3, base_y),
        (cx - a2 * 0.60, y2), (cx - a2, y2),
        (cx - a1 * 0.55, y1), (cx - a1, y1),
    ]


COLINA_A = colina(Y_COLINA_FONDO, 7.0, 0.6)
COLINA_B = colina(Y_COLINA_FRENTE, 9.0, 2.4)

# (x, alto, ancho) — la base se calcula sobre la colina correspondiente.
# El centro se deja despejado para que el sol se vea entero entre los arboles.
CONIFERAS_FONDO = [
    (40, 70, 36), (68, 96, 46), (96, 62, 32), (124, 84, 40), (152, 58, 30),
    (180, 76, 38), (208, 64, 32), (312, 68, 34), (340, 90, 44), (368, 60, 30),
    (396, 82, 40), (424, 66, 34), (452, 94, 46), (480, 72, 36),
]
CONIFERAS_FRENTE = [
    (26, 104, 52), (58, 132, 64), (92, 92, 46),
    (428, 96, 48), (462, 134, 66), (494, 106, 52),
]

PAJAROS = [(196, 150, 13), (232, 134, 10), (266, 154, 11), (318, 142, 12)]


def arboles_plantados(specs, perfil, subir=2.0):
    """Coloca cada conifera con la base justo sobre el perfil de la colina."""
    salida = []
    for x, alto, ancho in specs:
        base = altura_colina(perfil, x) + subir
        salida.append(conifera(x, base, alto, ancho))
    return salida


# --- SVG -------------------------------------------------------------------

def pts_svg(pts) -> str:
    return " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)


def pajaro_svg(x: float, y: float, s: float) -> str:
    return (
        f'<path d="M {x - s:.1f},{y:.1f} q {s * 0.5:.1f},{-s * 0.6:.1f} {s:.1f},0 '
        f'q {s * 0.5:.1f},{-s * 0.6:.1f} {s:.1f},0" fill="none" '
        f'stroke="{ARBOL_FRENTE}" stroke-width="{s * 0.2:.1f}" stroke-linecap="round"/>'
    )


def escena_svg(con_texto: bool) -> str:
    p: list[str] = []
    cx, cy = CENTRO
    hx, hy = HORIZONTE

    p.append(f'<circle cx="{cx}" cy="{cy}" r="{R_EXTERIOR}" fill="{VERDE_BORDE}"/>')
    p.append(f'<circle cx="{cx}" cy="{cy}" r="{R_CREMA}" fill="{CREMA}"/>')
    p.append(f'<circle cx="{cx}" cy="{cy}" r="{R_INTERIOR_BORDE}" fill="{VERDE_BORDE}"/>')
    p.append('<g clip-path="url(#recorte-escena)">')

    for radio, color in BANDAS:
        p.append(f'<circle cx="{hx}" cy="{hy}" r="{radio}" fill="{color}"/>')
    p.append(f'<circle class="sol" cx="{hx}" cy="{hy}" r="{SOL[0]}" fill="{SOL[1]}"/>')

    for x, y, s in PAJAROS:
        p.append(pajaro_svg(x, y, s))

    p.append(f'<polygon points="{pts_svg(cerrar(COLINA_A))}" fill="{COLINA_FONDO}"/>')
    for arbol in arboles_plantados(CONIFERAS_FONDO, COLINA_A):
        p.append(f'<polygon points="{pts_svg(arbol)}" fill="{ARBOL_FONDO}"/>')

    p.append(f'<polygon points="{pts_svg(cerrar(COLINA_B))}" fill="{COLINA_FRENTE}"/>')
    for arbol in arboles_plantados(CONIFERAS_FRENTE, COLINA_B):
        p.append(f'<polygon points="{pts_svg(arbol)}" fill="{ARBOL_FRENTE}"/>')

    if con_texto:
        p.append(
            f'<text x="260" y="392" text-anchor="middle" fill="{CREMA}" '
            "font-family=\"'Archivo Black','Arial Black',Arial,sans-serif\" "
            'font-size="76" letter-spacing="1">ASALITH</text>'
        )
        p.append(
            f'<text x="260" y="438" text-anchor="middle" fill="{ROJO_TIERRA}" '
            "font-family=\"'Archivo Black','Arial Black',Arial,sans-serif\" "
            'font-size="37" letter-spacing="12">FIELDS</text>'
        )
    p.append("</g>")
    return "\n  ".join(p)


def construir_svg(con_texto: bool, titulo: str) -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 520 520" role="img" aria-label="{titulo}">
  <title>{titulo}</title>
  <defs>
    <clipPath id="recorte-escena">
      <circle cx="{CENTRO[0]}" cy="{CENTRO[1]}" r="{R_ESCENA}"/>
    </clipPath>
  </defs>
  {escena_svg(con_texto)}
</svg>
"""


# --- Rasterizado -----------------------------------------------------------

def _fuente(tam: int):
    from PIL import ImageFont
    for ruta in (
        "C:/Windows/Fonts/ariblk.ttf",
        "C:/Windows/Fonts/segoeuib.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ):
        if Path(ruta).exists():
            return ImageFont.truetype(ruta, tam)
    return ImageFont.load_default()


def _centrar(d, texto, f, y, color, ancho_total, espaciado=0):
    if espaciado:
        anchos = [d.textlength(c, font=f) for c in texto]
        total = sum(anchos) + espaciado * (len(texto) - 1)
        x = (ancho_total - total) / 2
        for c, w in zip(texto, anchos):
            d.text((x, y), c, font=f, fill=color)
            x += w + espaciado
    else:
        w = d.textlength(texto, font=f)
        d.text(((ancho_total - w) / 2, y), texto, font=f, fill=color)


def construir_preview_badge() -> None:
    """Rasteriza la insignia para poder revisarla; no se publica."""
    from PIL import Image, ImageDraw

    S = 3
    L = int(520 * S)
    img = Image.new("RGB", (L, L), VERDE_BORDE)
    d = ImageDraw.Draw(img)

    def circulo(cx, cy, r, color, dib=d):
        dib.ellipse([(cx - r) * S, (cy - r) * S, (cx + r) * S, (cy + r) * S], fill=color)

    circulo(*CENTRO, R_EXTERIOR, VERDE_BORDE)
    circulo(*CENTRO, R_CREMA, CREMA)
    circulo(*CENTRO, R_INTERIOR_BORDE, VERDE_BORDE)

    capa = Image.new("RGB", (L, L), VERDE_BORDE)
    dc = ImageDraw.Draw(capa)
    for radio, color in BANDAS:
        circulo(*HORIZONTE, radio, color, dc)
    circulo(*HORIZONTE, SOL[0], SOL[1], dc)

    for bx, by, bs in PAJAROS:
        for lado in (-1, 1):
            dc.arc(
                [(bx + lado * bs * 0.5 - bs * 0.5) * S, (by - bs * 0.5) * S,
                 (bx + lado * bs * 0.5 + bs * 0.5) * S, (by + bs * 0.5) * S],
                200, 340, fill=ARBOL_FRENTE, width=int(bs * 0.22 * S),
            )

    dc.polygon([(x * S, y * S) for x, y in cerrar(COLINA_A)], fill=COLINA_FONDO)
    for arbol in arboles_plantados(CONIFERAS_FONDO, COLINA_A):
        dc.polygon([(x * S, y * S) for x, y in arbol], fill=ARBOL_FONDO)
    dc.polygon([(x * S, y * S) for x, y in cerrar(COLINA_B)], fill=COLINA_FRENTE)
    for arbol in arboles_plantados(CONIFERAS_FRENTE, COLINA_B):
        dc.polygon([(x * S, y * S) for x, y in arbol], fill=ARBOL_FRENTE)

    _centrar(dc, "ASALITH", _fuente(int(76 * S)), int(330 * S), CREMA, L)
    _centrar(dc, "FIELDS", _fuente(int(37 * S)), int(404 * S), ROJO_TIERRA, L, espaciado=int(12 * S))

    mascara = Image.new("L", (L, L), 0)
    ImageDraw.Draw(mascara).ellipse(
        [(CENTRO[0] - R_ESCENA) * S, (CENTRO[1] - R_ESCENA) * S,
         (CENTRO[0] + R_ESCENA) * S, (CENTRO[1] + R_ESCENA) * S], fill=255)
    img.paste(capa, (0, 0), mascara)

    img.resize((520, 520), Image.LANCZOS).save(ASSETS / "preview-badge.png")
    print("Vista previa: assets/preview-badge.png")


def construir_og() -> None:
    """Tarjeta apaisada 1200x630. El texto vive por encima de la linea de arboles."""
    from PIL import Image, ImageDraw

    W, H, S = 1200, 630, 3
    img = Image.new("RGB", (W * S, H * S), VERDE_BORDE)
    d = ImageDraw.Draw(img)

    # El horizonte queda bajo, con los arcos abriendose sobre todo el ancho.
    hx, hy = W * S * 0.5, H * S * 0.80
    k = (W * S) / 520 * 0.92
    for radio, color in BANDAS:
        r = radio * k
        d.ellipse([hx - r, hy - r, hx + r, hy + r], fill=color)
    r = SOL[0] * k * 1.15
    d.ellipse([hx - r, hy - r, hx + r, hy + r], fill=SOL[1])

    # Colinas propias del formato apaisado, en las mismas proporciones.
    sx = (W * S) / 520
    perfil_a = colina(0.0, 7.0, 0.6)
    perfil_b = colina(0.0, 9.0, 2.4)
    base_a, base_b = H * S * 0.72, H * S * 0.865

    poli_a = [(x * sx, base_a + y * S) for x, y in perfil_a]
    d.polygon(poli_a + [(W * S, H * S), (0, H * S)], fill=COLINA_FONDO)
    for x, alto, ancho in CONIFERAS_FONDO:
        y_base = base_a + altura_colina(perfil_a, x) * S + 2 * S
        pts = conifera(x * sx / S, y_base / S, alto * 0.92, ancho)
        d.polygon([(px * S * (sx / S), py * S) for px, py in pts], fill=ARBOL_FONDO)

    poli_b = [(x * sx, base_b + y * S) for x, y in perfil_b]
    d.polygon(poli_b + [(W * S, H * S), (0, H * S)], fill=COLINA_FRENTE)
    for x, alto, ancho in CONIFERAS_FRENTE:
        y_base = base_b + altura_colina(perfil_b, x) * S + 2 * S
        pts = conifera(x * sx / S, y_base / S, alto * 1.05, ancho * 1.05)
        d.polygon([(px * S * (sx / S), py * S) for px, py in pts], fill=ARBOL_FRENTE)

    _centrar(d, "ASALITH", _fuente(int(158 * S)), int(120 * S), CREMA, W * S)
    _centrar(d, "FIELDS", _fuente(int(64 * S)), int(300 * S), ROJO_TIERRA, W * S, espaciado=int(24 * S))
    _centrar(d, "MINECRAFT 1.20.1  ·  FORGE", _fuente(int(30 * S)), int(400 * S), CREMA, W * S,
             espaciado=int(3 * S))

    img.resize((W, H), Image.LANCZOS).save(ASSETS / "og-asalith.png", optimize=True)


def main() -> None:
    ASSETS.mkdir(exist_ok=True)
    (ASSETS / "asalith-badge.svg").write_text(construir_svg(True, "Asalith Fields"), encoding="utf-8")
    (ASSETS / "favicon.svg").write_text(construir_svg(False, "Asalith"), encoding="utf-8")
    construir_og()
    print("Recursos generados: asalith-badge.svg, favicon.svg, og-asalith.png")
    if "--preview" in sys.argv:
        construir_preview_badge()


if __name__ == "__main__":
    main()
