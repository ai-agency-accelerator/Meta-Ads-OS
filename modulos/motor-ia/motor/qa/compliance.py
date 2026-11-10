"""Cumplimiento publicitario determinista: lo que se dice o se ve tiene que estar respaldado por la marca.

Comprueba guion, texto en pantalla, CTA y el texto REAL de las pantallas de producto que se muestran (OCR):
  - cifras, precios, porcentajes y ahorros que no aparecen en las afirmaciones aprobadas / pruebas del producto;
  - superlativos y absolutos («el mejor», «garantizado», «100 %») sin respaldo;
  - temas vetados por las reglas «no» de la marca (p. ej. salud, pérdida de peso).
No reescribe nada por sí mismo: el guionista recibe los avisos y reescribe; lo que queda va a «revisar antes de publicar».
"""

from __future__ import annotations

import re
from typing import Any

from ..models import BrandKit, Product, Project

NUM = re.compile(r"(\d+(?:[.,]\d+)?)\s*(€|euros?|\$|dólares|%|por ciento|minutos|min|kcal|calor[ií]as|kg|kilos)?", re.I)
SUPERLATIVES = [r"\bel mejor\b", r"\bla mejor\b", r"\bn[ºo°]\s?1\b", r"\bnúmero uno\b", r"\bgarantizad[oa]s?\b", r"\b100 ?%",
                r"\bcura\b", r"\bmilagro", r"\bsin esfuerzo\b", r"\bpara siempre\b", r"\bthe best\b", r"\bguaranteed\b"]
TOPIC_WORDS = {
    "salud": ["salud", "saludable", "kcal", "caloría", "calorías", "proteína", "dieta", "adelgaz", "nutri"],
    "peso": ["adelgaz", "pérdida de peso", "perder peso", "bajar de peso", "quema grasa", "lose weight"],
    "ahorro": ["ahorr", "€", "euros", "barato"],
    "precio": ["€", "euros", "precio", "gratis"],
}


def _backed(token: str, sources: str) -> bool:
    return token.replace(",", ".") in sources.replace(",", ".")


def check_text(text: str, brand: BrandKit, product: Product, *, where: str) -> list[str]:
    """Avisos para un texto concreto (guion, rótulo, CTA u OCR de una pantalla)."""
    issues: list[str] = []
    low = text.lower()
    backing = " ".join(brand.approved_claims + product.benefits + product.proof_points + brand.ctas).lower()
    screen = where.startswith("pantalla")
    for m in NUM.finditer(text):
        num, unit = m.group(1), (m.group(2) or "").lower()
        if screen and unit not in ("€", "euro", "euros", "$", "dólares", "%", "por ciento"):
            continue  # en una pantalla real, cantidades de receta o lista no son afirmaciones; dinero y % sí
        if not unit and len(num) < 2:
            continue  # «2 minutos» sí cuenta; un «3» suelto no es una afirmación
        if not _backed(num, backing):
            issues.append(f"{where}: cifra «{m.group(0).strip()}» sin respaldo en las afirmaciones aprobadas")
    for pat in SUPERLATIVES:
        mm = re.search(pat, low)
        if mm and not re.search(pat, backing):
            issues.append(f"{where}: absoluto/superlativo «{mm.group(0)}» sin respaldo")
    for rule in brand.dont_rules:
        r = rule.lower()
        for topic, words in TOPIC_WORDS.items():
            if topic in r:
                hit = next((w for w in words if w in low), None)
                if hit and not ("salvo" in r and where.startswith("pantalla")):
                    issues.append(f"{where}: toca «{topic}» («{hit}») y la marca dice: «{rule}»")
    return sorted(set(issues))


def check_project(p: Project, brand: BrandKit, product: Product, *, screens: bool = True) -> list[str]:
    issues: list[str] = []
    if p.script:
        for seg in p.script.segments:
            issues += check_text(seg.text, brand, product, where=f"guion [{seg.role}]")
            if seg.on_screen_text:
                issues += check_text(seg.on_screen_text, brand, product, where=f"rótulo [{seg.role}]")
        if p.script.cta:
            issues += check_text(p.script.cta, brand, product, where="CTA")
    if screens and product.screenshot_asset_ids:
        from ..pipeline.product import screen_text
        from ..store import ctx

        shown = {a for s in p.shots if s.shot_type == "app_screen" for a in s.constraints.get("screens", [])} or set(
            product.screenshot_asset_ids)
        for aid in shown:
            try:
                txt = screen_text(ctx().db.get_asset(aid))
            except KeyError:
                continue
            issues += check_text(" ".join(txt.split()), brand, product, where=f"pantalla {aid[:6]}")
    return sorted(set(issues))


def summary(issues: list[str]) -> dict[str, Any]:
    return {"issues": issues, "count": len(issues)}
