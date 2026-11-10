"""Tests de herramientas/notificar.py. Sin red: Telegram y Slack con urlopen simulado, email con SMTP simulado."""
from __future__ import annotations

import io
import json
import os
import re
import smtplib
import stat
import subprocess
import sys
import urllib.error

import pytest

TOKEN = "123456789:AAH" + "x" * 32
CHAT = "987654321"
WEBHOOK = "https://hooks.slack.com/services/T000/B000/" + "y" * 24
VARIABLES = ["TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID", "SLACK_WEBHOOK_URL", "SMTP_HOST", "SMTP_PORT",
             "SMTP_USUARIO", "SMTP_CLAVE", "EMAIL_DESTINO", "META_TOKEN"]

BRIEF = """---
fecha: 2026-11-10
semaforo: rojo
---
# Brief diario · 2026-11-10 · 🔴 1 · 🟢 1

🔴 **Clínica Sonrisa** — Lead a 0 en el dataset desde ayer (navegador y servidor). CPA < 40 € & CTR > 1 %.
→ Revisa el formulario y Events Manager.

🟢 **Acme Automations** — En ritmo (91 %), 9 Lead (banda 4–17).

- No toques `BROAD-A+_LEAD` ni act_000000000000000: cambió el 2026-11-06.
"""


class _Respuesta:
    def __init__(self, cuerpo: bytes, status: int = 200):
        self._cuerpo, self.status = cuerpo, status

    def read(self, *_):
        return self._cuerpo

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False


class Red:
    """Sustituye urllib.request.urlopen. Responde con la cola `respuestas` [(estado, cuerpo)] o con un ok."""

    def __init__(self, respuestas=None, por_defecto=(200, {"ok": True, "result": {"message_id": 1}})):
        self.respuestas = list(respuestas or [])
        self.por_defecto = por_defecto
        self.peticiones: list[dict] = []

    def __call__(self, req, timeout=None):
        url = req.full_url
        datos = json.loads(req.data) if req.data else None
        self.peticiones.append({"url": url, "metodo": req.get_method(), "json": datos})
        r = self.respuestas.pop(0) if self.respuestas else self.por_defecto
        if isinstance(r, Exception):
            raise r
        estado, cuerpo = r
        crudo = cuerpo.encode() if isinstance(cuerpo, str) else json.dumps(cuerpo).encode()
        if estado >= 400:
            raise urllib.error.HTTPError(url, estado, "error", {}, io.BytesIO(crudo))
        return _Respuesta(crudo, estado)


@pytest.fixture
def nt(instancia, monkeypatch):
    """notificar con la instancia de prueba, sin credenciales del entorno real y sin esperas."""
    for v in VARIABLES:  # setenv + delenv: pytest restaura «no existe» aunque cargar_entorno la cree después
        monkeypatch.setenv(v, "x")
        monkeypatch.delenv(v)
    import notificar
    dormidas: list[float] = []
    monkeypatch.setattr(notificar, "_dormir", dormidas.append)
    notificar.dormidas = dormidas
    return notificar


@pytest.fixture
def red(monkeypatch):
    r = Red()
    monkeypatch.setattr(urllib.request, "urlopen", r)
    return r


def _brief(raiz, texto=BRIEF, ruta="informes/diario/2026-11-10.md"):
    f = raiz / ruta
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(texto, encoding="utf-8")
    return ruta


def _telegram(monkeypatch):
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", TOKEN)
    monkeypatch.setenv("TELEGRAM_CHAT_ID", CHAT)


def _preferencias(raiz, canal):
    (raiz / "contexto" / "preferencias.md").write_text(
        f'---\nnivel: principiante\nestilo: profesor\nbrief:\n  canal: {canal}\n  hora: "08:00"\n  clientes: todos\n'
        '  programado_con: ""\n---\n', encoding="utf-8")


def _salida(capsys) -> str:
    c = capsys.readouterr()
    return c.out + c.err


def _entidades_correctas(t: str) -> bool:
    return re.search(r"&(?!(?:amp|lt|gt|quot|#\d+|#x[0-9a-fA-F]+);)", t) is None


def _etiquetas_equilibradas(t: str) -> bool:
    return all(t.count(f"<{e}>") + t.count(f"<{e} ") == t.count(f"</{e}>") for e in ("b", "i", "s", "code", "pre",
                                                                                    "blockquote", "a"))


# ------------------------------------------------------------------------------------------------ formato
def test_html_de_telegram_escapa_y_formatea(nt):
    md = ("# Brief · 2026-11-10\n\n**CPA < 40 € & CTR > 1 %**\n- `act_000` con *cursiva* y ~~tachado~~\n"
          "[Ads Manager](https://example.com/a?b=1&c=2)\n\n| Bloque | Estado | Dato |\n|---|---|---|\n"
          "| Gasto | 🟢 | 91 % |\n\n> cita\n\n2 * 3 * 4 y BROAD-A+_LEAD_v2")
    t = "\n".join(nt.render_telegram(md))
    assert "<b>Brief · 2026-11-10</b>" in t
    assert "<b>CPA &lt; 40 € &amp; CTR &gt; 1 %</b>" in t
    assert "• <code>act_000</code> con <i>cursiva</i> y <s>tachado</s>" in t
    assert '<a href="https://example.com/a?b=1&amp;c=2">Ads Manager</a>' in t
    assert "<b>Gasto</b> · 🟢 · 91 %" in t and "Bloque" not in t  # la cabecera de la tabla sobra en el móvil
    assert "<blockquote>cita</blockquote>" in t
    assert "2 * 3 * 4 y BROAD-A+_LEAD_v2" in t  # ni el asterisco suelto ni los guiones bajos son formato
    assert _entidades_correctas(t) and _etiquetas_equilibradas(t)


def test_la_cabecera_yaml_no_se_envia(nt):
    t = "\n".join(nt.render_telegram(BRIEF))
    assert "semaforo" not in t and t.startswith("<b>Brief diario")


def test_trocear_a_4096_con_etiquetas_cerradas(nt):
    lineas = [f"- **Cliente {n}** — gasto 🟢 & CTR <1 % · [detalle](https://example.com/{n})" for n in range(400)]
    trozos = nt.trocear_telegram("# Brief largo\n\n" + "\n".join(lineas))
    assert len(trozos) > 1
    for i, t in enumerate(trozos, start=1):
        assert nt.longitud_telegram(t) <= 4096
        assert _etiquetas_equilibradas(t) and _entidades_correctas(t)
        assert t.endswith(f"<i>({i}/{len(trozos)})</i>")
    plano = nt.a_texto_plano("\n".join(trozos))
    posiciones = [plano.index(f"Cliente {n} ") for n in range(400)]
    assert posiciones == sorted(posiciones)  # nada se pierde ni se desordena


def test_emoji_cuenta_doble_en_telegram(nt):
    assert nt.longitud_telegram("🟢") == 2 and nt.longitud_telegram("é") == 1
    trozos = nt.trocear_telegram("🟢" * 5000)
    assert len(trozos) >= 3 and all(nt.longitud_telegram(t) <= 4096 for t in trozos)


def test_linea_gigante_se_parte_sin_romper_entidades(nt):
    md = " ".join(["A&B <x>"] * 2500)
    trozos = nt.trocear_telegram(md)
    assert len(trozos) > 1
    assert all(nt.longitud_telegram(t) <= 4096 and _entidades_correctas(t) for t in trozos)
    assert nt.a_texto_plano("".join(t.rsplit("\n", 1)[0] for t in trozos)).count("A&B") == 2500


def test_bloque_de_codigo_largo_se_reparte_en_varios_pre(nt):
    md = "```\n" + "\n".join(f"linea {n} <tag> & más" for n in range(400)) + "\n```"
    trozos = nt.trocear_telegram(md)
    assert len(trozos) > 1
    assert all(t.startswith("<pre>") and _etiquetas_equilibradas(t) and nt.longitud_telegram(t) <= 4096
               for t in trozos)


def test_slack_mrkdwn_y_troceo(nt):
    t = "\n".join(nt.render_slack("# Título\n**negrita** y *cursiva* [web](https://e.com) a < b & c\n- punto\n> cita"))
    assert "*Título*" in t and "*negrita* y _cursiva_" in t and "<https://e.com|web>" in t
    assert "a &lt; b &amp; c" in t and "• punto" in t and "> cita" in t
    trozos = nt.trocear_slack("\n".join(f"- **Cliente {n}** gasto & CTR" for n in range(500)))
    assert len(trozos) > 1 and all(len(x) <= 4000 for x in trozos)


# ------------------------------------------------------------------------------------------------ Telegram
def test_enviar_por_telegram(nt, red, instancia, monkeypatch, capsys):
    _telegram(monkeypatch)
    ruta = _brief(instancia)
    assert nt.main(["enviar", "--archivo", ruta, "--canal", "telegram"]) == 0
    assert len(red.peticiones) == 1
    p = red.peticiones[0]
    assert p["metodo"] == "POST" and p["url"].endswith("/sendMessage")
    assert p["json"]["chat_id"] == CHAT and p["json"]["parse_mode"] == "HTML"
    assert p["json"]["link_preview_options"] == {"is_disabled": True}
    assert "<b>Clínica Sonrisa</b>" in p["json"]["text"] and "CPA &lt; 40 € &amp; CTR &gt; 1 %" in p["json"]["text"]
    salida = _salida(capsys)
    assert "Enviado por telegram: 1 mensaje" in salida and TOKEN not in salida
    log = (instancia / "logs" / "notificaciones.jsonl").read_text(encoding="utf-8")
    assert '"archivo": "informes/diario/2026-11-10.md", "ok": true' in log  # lo busca brief.sh
    assert TOKEN not in log and CHAT not in log and "Clínica" not in log


def test_informe_largo_se_envia_en_varios_mensajes_con_pausa(nt, red, instancia, monkeypatch):
    _telegram(monkeypatch)
    ruta = _brief(instancia, "# Brief\n\n" + "\n".join(f"- **Cliente {n}** — todo en orden" for n in range(300)))
    assert nt.main(["enviar", "--archivo", ruta, "--canal", "telegram"]) == 0
    assert len(red.peticiones) > 1
    assert nt.dormidas.count(1) == len(red.peticiones) - 1  # ~1 mensaje por segundo


def test_html_rechazado_se_reenvia_como_texto_plano(nt, monkeypatch, instancia):
    _telegram(monkeypatch)
    red = Red([(400, {"ok": False, "error_code": 400,
                      "description": "Bad Request: can't parse entities: unexpected end tag"})])
    monkeypatch.setattr(urllib.request, "urlopen", red)
    assert nt.main(["enviar", "--archivo", _brief(instancia), "--canal", "telegram"]) == 0
    segundo = red.peticiones[1]["json"]
    assert "parse_mode" not in segundo and "<b>" not in segundo["text"] and "CPA < 40 € & CTR" in segundo["text"]


def test_429_espera_lo_que_pide_telegram(nt, monkeypatch, instancia):
    _telegram(monkeypatch)
    red = Red([(429, {"ok": False, "error_code": 429, "description": "Too Many Requests",
                      "parameters": {"retry_after": 3}})])
    monkeypatch.setattr(urllib.request, "urlopen", red)
    assert nt.main(["enviar", "--archivo", _brief(instancia), "--canal", "telegram"]) == 0
    assert 4 in nt.dormidas and len(red.peticiones) == 2


@pytest.mark.parametrize("estado,descripcion,texto", [
    (401, "Unauthorized", "TELEGRAM_BOT_TOKEN"),
    (400, "Bad Request: chat not found", "TELEGRAM_CHAT_ID"),
    (403, "Forbidden: bot was blocked by the user", "Iniciar"),
])
def test_errores_de_configuracion_de_telegram(nt, monkeypatch, instancia, capsys, estado, descripcion, texto):
    _telegram(monkeypatch)
    monkeypatch.setattr(urllib.request, "urlopen",
                        Red([(estado, {"ok": False, "error_code": estado, "description": descripcion})]))
    assert nt.main(["enviar", "--archivo", _brief(instancia), "--canal", "telegram"]) == 2
    salida = _salida(capsys)
    assert texto in salida and TOKEN not in salida and CHAT not in salida
    assert '"ok": false' in (instancia / "logs" / "notificaciones.jsonl").read_text(encoding="utf-8")


def test_grupo_convertido_en_supergrupo_da_el_chat_id_nuevo(nt, monkeypatch, instancia, capsys):
    _telegram(monkeypatch)
    red = Red([(400, {"ok": False, "error_code": 400,
                      "description": "Bad Request: group chat was upgraded to a supergroup chat",
                      "parameters": {"migrate_to_chat_id": -1001234567890}})])
    monkeypatch.setattr(urllib.request, "urlopen", red)
    assert nt.main(["enviar", "--archivo", _brief(instancia), "--canal", "telegram"]) == 2
    salida = _salida(capsys)
    assert "-1001234567890" in salida and "TELEGRAM_CHAT_ID" in salida and len(red.peticiones) == 1


def test_fallo_de_red_no_filtra_el_token(nt, monkeypatch, instancia, capsys):
    _telegram(monkeypatch)
    fallo = urllib.error.URLError(f"no se pudo abrir https://api.telegram.org/bot{TOKEN}/sendMessage")
    red = Red([fallo, fallo, fallo])
    monkeypatch.setattr(urllib.request, "urlopen", red)
    assert nt.main(["enviar", "--archivo", _brief(instancia), "--canal", "telegram"]) == 1
    salida = _salida(capsys)
    assert "api.telegram.org" in salida and TOKEN not in salida and TOKEN.split(":")[1] not in salida
    assert len(red.peticiones) == 3 and nt.dormidas  # reintenta con espera
    assert TOKEN not in (instancia / "logs" / "notificaciones.jsonl").read_text(encoding="utf-8")


def test_token_con_formato_raro_es_error_de_configuracion(nt, red, monkeypatch, instancia, capsys):
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "pegado-mal-123")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", CHAT)
    assert nt.main(["enviar", "--archivo", _brief(instancia), "--canal", "telegram"]) == 2
    assert not red.peticiones and "pegado-mal-123" not in _salida(capsys)


# ------------------------------------------------------------------------------------------- credenciales
@pytest.mark.parametrize("canal,puestas,falta", [
    ("telegram", {"TELEGRAM_CHAT_ID": "valor-secreto-chat"}, "TELEGRAM_BOT_TOKEN"),
    ("telegram", {"TELEGRAM_BOT_TOKEN": TOKEN}, "TELEGRAM_CHAT_ID"),
    ("slack", {}, "SLACK_WEBHOOK_URL"),
    ("email", {"SMTP_HOST": "smtp.ejemplo.test", "SMTP_PORT": "587", "SMTP_USUARIO": "valor-secreto-usuario",
               "EMAIL_DESTINO": "operador@ejemplo.test"}, "SMTP_CLAVE"),
])
def test_credencial_que_falta_sale_con_2_y_sin_valores(nt, red, monkeypatch, instancia, capsys, canal, puestas, falta):
    for k, v in puestas.items():
        monkeypatch.setenv(k, v)
    assert nt.main(["enviar", "--archivo", _brief(instancia), "--canal", canal]) == 2
    salida = _salida(capsys)
    assert falta in salida and "docs/guias/brief-diario.md" in salida
    for v in puestas.values():
        assert v not in salida
    assert not red.peticiones


def test_salida_json_en_error(nt, red, instancia, capsys):
    assert nt.main(["enviar", "--archivo", _brief(instancia), "--canal", "slack", "--json"]) == 2
    datos = json.loads(capsys.readouterr().out)
    assert datos["ok"] is False and datos["codigo"] == 2 and "SLACK_WEBHOOK_URL" in datos["error"]


# ------------------------------------------------------------------------------------------------ canal auto
def test_auto_usa_el_canal_de_las_preferencias(nt, red, monkeypatch, instancia):
    _telegram(monkeypatch)
    monkeypatch.setenv("SLACK_WEBHOOK_URL", WEBHOOK)
    _preferencias(instancia, "slack")
    red.por_defecto = (200, "ok")
    assert nt.main(["enviar", "--archivo", _brief(instancia)]) == 0
    assert [p["url"] for p in red.peticiones] == [WEBHOOK]
    assert "*Clínica Sonrisa*" in red.peticiones[0]["json"]["text"]


def test_auto_con_canal_ninguno_no_envia(nt, red, instancia, capsys):
    _preferencias(instancia, "ninguno")
    assert nt.main(["enviar", "--archivo", _brief(instancia)]) == 0
    assert not red.peticiones and "no se envía nada" in _salida(capsys)


def test_auto_sin_preferencias_usa_las_credenciales_que_haya(nt, red, monkeypatch, instancia):
    _telegram(monkeypatch)
    assert nt.main(["enviar", "--archivo", _brief(instancia)]) == 0
    assert red.peticiones[0]["url"].startswith("https://api.telegram.org/bot")


def test_auto_sin_preferencias_ni_credenciales_es_error_2(nt, red, instancia, capsys):
    assert nt.main(["enviar", "--archivo", _brief(instancia)]) == 2
    assert "/brief-diario programar" in _salida(capsys) and not red.peticiones


def test_canal_invalido_en_preferencias(nt, red, instancia):
    _preferencias(instancia, "whatsapp")
    assert nt.main(["enviar", "--archivo", _brief(instancia)]) == 2


# ---------------------------------------------------------------------------------------------- seguridad
@pytest.mark.parametrize("ruta", [".env", "contexto/operador.md", "clientes/acme/privado/leads.md",
                                  "clientes/acme/ficha.md", "../fuera/informes/x.md", "informes/diario/x.txt"])
def test_solo_se_envian_informes(nt, red, monkeypatch, instancia, capsys, ruta):
    _telegram(monkeypatch)
    assert nt.main(["enviar", "--archivo", ruta, "--canal", "telegram"]) == 1
    assert not red.peticiones and "informes/" in _salida(capsys)


def test_informe_de_cliente_si_se_puede_enviar(nt, red, monkeypatch, instancia):
    _telegram(monkeypatch)
    ruta = _brief(instancia, ruta="clientes/acme/informes/diario/2026-11-10.md")
    assert nt.main(["enviar", "--archivo", ruta, "--canal", "telegram"]) == 0


def test_archivo_inexistente_o_vacio(nt, red, monkeypatch, instancia):
    _telegram(monkeypatch)
    assert nt.main(["enviar", "--archivo", "informes/diario/2030-01-01.md", "--canal", "telegram"]) == 1
    assert nt.main(["enviar", "--archivo", _brief(instancia, "---\na: 1\n---\n\n"), "--canal", "telegram"]) == 1
    assert not red.peticiones


@pytest.mark.parametrize("secreto", ["EAA" + "B" * 40, "sk_live_" + "a" * 24, TOKEN, WEBHOOK,
                                     "-----BEGIN PRIVATE KEY-----"])
def test_informe_con_algo_que_parece_una_clave_no_se_envia(nt, red, monkeypatch, instancia, capsys, secreto):
    _telegram(monkeypatch)
    ruta = _brief(instancia, BRIEF + f"\nDato: {secreto}\n")
    assert nt.main(["enviar", "--archivo", ruta, "--canal", "telegram"]) == 1
    assert not red.peticiones and secreto not in _salida(capsys)


def test_informe_con_el_valor_de_una_variable_sensible_no_se_envia(nt, red, monkeypatch, instancia, capsys):
    _telegram(monkeypatch)
    monkeypatch.setenv("META_TOKEN", "valor-muy-secreto-del-token")
    ruta = _brief(instancia, BRIEF + "\nvalor-muy-secreto-del-token\n")
    assert nt.main(["enviar", "--archivo", ruta, "--canal", "telegram"]) == 1
    salida = _salida(capsys)
    assert "META_TOKEN" in salida and "valor-muy-secreto" not in salida and not red.peticiones


def test_los_emails_del_texto_se_anonimizan(nt, red, monkeypatch, instancia):
    _telegram(monkeypatch)
    ruta = _brief(instancia, BRIEF + "\nLead sin atender: ana.garcia@ejemplo.com\n")
    assert nt.main(["enviar", "--archivo", ruta, "--canal", "telegram"]) == 0
    texto = red.peticiones[0]["json"]["text"]
    assert "ejemplo.com" not in texto and "Lead sin atender: ***" in texto


# --------------------------------------------------------------------------------------------------- Slack
def test_slack_url_que_no_es_webhook(nt, red, monkeypatch, instancia):
    monkeypatch.setenv("SLACK_WEBHOOK_URL", "https://ejemplo.test/recoge")
    assert nt.main(["enviar", "--archivo", _brief(instancia), "--canal", "slack"]) == 2
    assert not red.peticiones


def test_slack_webhook_revocado(nt, monkeypatch, instancia, capsys):
    monkeypatch.setenv("SLACK_WEBHOOK_URL", WEBHOOK)
    monkeypatch.setattr(urllib.request, "urlopen", Red([(404, "no_service")]))
    assert nt.main(["enviar", "--archivo", _brief(instancia), "--canal", "slack"]) == 2
    assert WEBHOOK not in _salida(capsys)


def test_slack_payload_invalido(nt, monkeypatch, instancia):
    monkeypatch.setenv("SLACK_WEBHOOK_URL", WEBHOOK)
    monkeypatch.setattr(urllib.request, "urlopen", Red([(400, "invalid_payload")]))
    assert nt.main(["enviar", "--archivo", _brief(instancia), "--canal", "slack"]) == 1


# --------------------------------------------------------------------------------------------------- Email
class SMTPFalso:
    instancias: list["SMTPFalso"] = []
    ssl = False

    def __init__(self, host, port, timeout=None, context=None):
        self.host, self.port, self.llamadas, self.mensajes = host, port, [], []
        self.extensiones = {"starttls"}
        self.fallo_login = None
        type(self).instancias.append(self)

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False

    def ehlo(self):
        self.llamadas.append("ehlo")

    def has_extn(self, nombre):
        return nombre in self.extensiones

    def starttls(self, context=None):
        self.llamadas.append("starttls")

    def login(self, usuario, clave):
        self.llamadas.append("login")
        if SMTPFalso.fallo_login:
            raise SMTPFalso.fallo_login

    def send_message(self, msg):
        self.mensajes.append(msg)


class SMTPSSLFalso(SMTPFalso):
    instancias: list[SMTPFalso] = []


@pytest.fixture
def smtp(nt, monkeypatch):
    SMTPFalso.instancias, SMTPSSLFalso.instancias, SMTPFalso.fallo_login = [], [], None
    monkeypatch.setattr(smtplib, "SMTP", SMTPFalso)
    monkeypatch.setattr(smtplib, "SMTP_SSL", SMTPSSLFalso)
    for k, v in {"SMTP_HOST": "smtp.ejemplo.test", "SMTP_PORT": "587", "SMTP_USUARIO": "operador@ejemplo.test",
                 "SMTP_CLAVE": "clave-de-aplicacion-xyz", "EMAIL_DESTINO": "operador@ejemplo.test"}.items():
        monkeypatch.setenv(k, v)
    return SMTPFalso


def test_email_por_587_con_starttls(nt, smtp, instancia):
    assert nt.main(["enviar", "--archivo", _brief(instancia, BRIEF + "\n| Bloque | Dato |\n|---|---|\n| Gasto | 91 % |\n"),
                    "--canal", "email"]) == 0
    s = SMTPFalso.instancias[0]
    assert s.port == 587 and s.llamadas.index("starttls") < s.llamadas.index("login")
    msg = s.mensajes[0]
    assert msg["To"] == "operador@ejemplo.test" and msg["Subject"] == "Brief diario · 2026-11-10 · 🔴 1 · 🟢 1"
    plano = msg.get_body(("plain",)).get_content()
    html_parte = msg.get_body(("html",)).get_content()
    assert "semaforo" not in plano and "**Clínica Sonrisa**" in plano
    assert "<table" in html_parte and "<b>Clínica Sonrisa</b>" in html_parte and "CPA &lt; 40 €" in html_parte


def test_email_por_465_usa_ssl_y_asunto_propio(nt, smtp, monkeypatch, instancia):
    monkeypatch.setenv("SMTP_PORT", "465")
    assert nt.main(["enviar", "--archivo", _brief(instancia), "--canal", "email", "--asunto", "Brief de prueba"]) == 0
    assert not SMTPFalso.instancias and SMTPSSLFalso.instancias[0].mensajes[0]["Subject"] == "Brief de prueba"


def test_email_sin_starttls_no_manda_la_clave(nt, smtp, monkeypatch, instancia, capsys):
    real_init = SMTPFalso.__init__

    def sin_tls(self, *a, **k):
        real_init(self, *a, **k)
        self.extensiones = set()
    monkeypatch.setattr(SMTPFalso, "__init__", sin_tls)
    assert nt.main(["enviar", "--archivo", _brief(instancia), "--canal", "email"]) == 2
    assert "login" not in SMTPFalso.instancias[0].llamadas and "465" in _salida(capsys)


def test_email_con_clave_mala(nt, smtp, instancia, capsys):
    SMTPFalso.fallo_login = smtplib.SMTPAuthenticationError(535, b"5.7.8 Username and Password not accepted")
    assert nt.main(["enviar", "--archivo", _brief(instancia), "--canal", "email"]) == 2
    salida = _salida(capsys)
    assert "SMTP_CLAVE" in salida and "clave-de-aplicacion-xyz" not in salida


# ------------------------------------------------------------------------------------- probar y chat_id
def test_probar(nt, red, monkeypatch, instancia, capsys):
    _telegram(monkeypatch)
    assert nt.main(["probar", "--canal", "telegram"]) == 0
    assert "prueba del brief diario" in red.peticiones[0]["json"]["text"]
    assert "Comprueba que te ha llegado" in _salida(capsys)
    assert '"detalle": "prueba"' in (instancia / "logs" / "notificaciones.jsonl").read_text(encoding="utf-8")


def test_probar_con_canal_ninguno_es_error_2(nt, red, instancia):
    _preferencias(instancia, "ninguno")
    assert nt.main(["probar"]) == 2 and not red.peticiones


ACTUALIZACIONES = {"ok": True, "result": [
    {"update_id": 1, "message": {"message_id": 1, "text": "hola",
                                 "chat": {"id": int(CHAT), "type": "private", "first_name": "Operador"}}},
    {"update_id": 2, "message": {"message_id": 2, "text": "otra vez",
                                 "chat": {"id": int(CHAT), "type": "private", "first_name": "Operador"}}},
]}


def test_telegram_chat_id(nt, monkeypatch, instancia, capsys):
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", TOKEN)
    red = Red([(200, ACTUALIZACIONES)])
    monkeypatch.setattr(urllib.request, "urlopen", red)
    assert nt.main(["telegram-chat-id"]) == 0
    assert red.peticiones[0]["metodo"] == "GET" and red.peticiones[0]["url"].endswith("/getUpdates")
    salida = _salida(capsys)
    assert CHAT in salida and "conversación privada" in salida and "Operador" not in salida and TOKEN not in salida
    assert not (instancia / ".env").exists()


def test_telegram_chat_id_guardar_crea_env_con_600(nt, monkeypatch, instancia):
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", TOKEN)
    monkeypatch.setattr(urllib.request, "urlopen", Red([(200, ACTUALIZACIONES)]))
    assert nt.main(["telegram-chat-id", "--guardar"]) == 0
    env = instancia / ".env"
    assert env.read_text(encoding="utf-8") == f"TELEGRAM_CHAT_ID={CHAT}\n"
    assert stat.S_IMODE(env.stat().st_mode) == 0o600


def test_telegram_chat_id_guardar_respeta_lo_que_hay(nt, monkeypatch, instancia):
    env = instancia / ".env"
    env.write_text(f"TELEGRAM_BOT_TOKEN={TOKEN}", encoding="utf-8")  # sin salto de línea final
    monkeypatch.setattr(urllib.request, "urlopen", Red([(200, ACTUALIZACIONES)]))
    assert nt.main(["telegram-chat-id", "--guardar"]) == 0
    assert env.read_text(encoding="utf-8") == f"TELEGRAM_BOT_TOKEN={TOKEN}\nTELEGRAM_CHAT_ID={CHAT}\n"


def test_telegram_chat_id_no_sobrescribe_otro(nt, monkeypatch, instancia):
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", TOKEN)
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "111")
    monkeypatch.setattr(urllib.request, "urlopen", Red([(200, ACTUALIZACIONES)]))
    assert nt.main(["telegram-chat-id", "--guardar"]) == 1
    assert not (instancia / ".env").exists()


def test_telegram_chat_id_sin_mensajes_o_con_webhook(nt, monkeypatch, instancia, capsys):
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", TOKEN)
    monkeypatch.setattr(urllib.request, "urlopen", Red([(200, {"ok": True, "result": []})]))
    assert nt.main(["telegram-chat-id"]) == 1 and "Iniciar" in _salida(capsys)
    monkeypatch.setattr(urllib.request, "urlopen", Red([(409, {"ok": False, "error_code": 409,
                                                               "description": "Conflict: webhook is active"})]))
    assert nt.main(["telegram-chat-id"]) == 2 and "webhook" in _salida(capsys)


# ------------------------------------------------------------------------------------------------------ CLI
def test_errores_de_argumentos_salen_con_1(nt):
    with pytest.raises(SystemExit) as e:
        nt.main(["enviar"])
    assert e.value.code == 1


def test_cli_real_con_python_aislado(instancia):
    """`python3 -I` no añade herramientas/ al path: el script lo hace solo. Sin credenciales → 2, sin red."""
    raiz_producto = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    _brief(instancia)
    entorno = {k: v for k, v in os.environ.items() if k not in VARIABLES}
    entorno["META_ADS_OS_RAIZ"] = str(instancia)
    r = subprocess.run([sys.executable, "-I", os.path.join(raiz_producto, "herramientas", "notificar.py"), "enviar",
                        "--archivo", "informes/diario/2026-11-10.md", "--canal", "telegram"],
                       capture_output=True, text=True, env=entorno, timeout=60)
    assert r.returncode == 2, r.stderr
    assert "TELEGRAM_BOT_TOKEN" in r.stderr


# ------------------------------------------------------------------- programación (.claude/skills/brief-diario)
import pathlib  # noqa: E402
import plistlib  # noqa: E402
import shutil  # noqa: E402
from datetime import date  # noqa: E402

PRODUCTO = pathlib.Path(__file__).resolve().parents[2]
SKILL = PRODUCTO / ".claude" / "skills" / "brief-diario"
PROGRAMACION = SKILL / "programacion"


def _reglas(nombre: str) -> list[str]:
    lineas = (PROGRAMACION / nombre).read_text(encoding="utf-8").splitlines()
    return [x.strip() for x in lineas if x.strip() and not x.strip().startswith("#")]


def test_la_lista_permitida_solo_lee_y_escribe_informes():
    permitidas = _reglas("herramientas-permitidas.txt")
    assert [r for r in permitidas if r.startswith(("Edit(", "Write(", "MultiEdit", "NotebookEdit"))] == [
        "Edit(informes/diario/**)", "Edit(clientes/*/informes/diario/**)",
        "Write(informes/diario/**)", "Write(clientes/*/informes/diario/**)"]
    assert "Edit" not in permitidas and "Write" not in permitidas  # nunca sin ruta
    escrituras = re.compile(r"_(create|update|delete|activate|boost)|pixel_event|catalog|experiment")
    assert not [r for r in permitidas if r.startswith("mcp__") and escrituras.search(r)]
    assert not [r for r in permitidas if r.startswith(("mcp__ghl", "mcp__stripe", "WebFetch", "WebSearch"))]
    for r in [r for r in permitidas if r.startswith("Bash(")]:
        assert r.startswith(("Bash(date ", "Bash(python3 -I herramientas/")), r
        assert not re.search(r"\b(crear|activar|pausar|presupuesto|probar|telegram-chat-id|capi\.py)\b", r), r
    denegadas = _reglas("herramientas-denegadas.txt")
    assert "Read(./.env)" in denegadas and "mcp__meta-ads__ads_update_*" in denegadas
    assert not set(permitidas) & set(denegadas)


def test_allowed_tools_de_la_skill_estan_en_la_lista_programada():
    texto = (SKILL / "SKILL.md").read_text(encoding="utf-8")
    cabecera = texto.split("---", 2)[1]
    bloque = cabecera.split("allowed-tools:", 1)[1]
    de_la_skill = [x.strip()[2:] for x in bloque.splitlines() if x.strip().startswith("- ")]
    assert de_la_skill and set(de_la_skill) <= set(_reglas("herramientas-permitidas.txt"))
    descripcion = re.search(r'^description: "(.*)"$', cabecera, re.M).group(1)
    assert len(descripcion) <= 350
    assert "disable-model-invocation" not in cabecera  # una tarea programada no podría lanzarla


def test_plantilla_de_launchd_valida_al_rellenarla(tmp_path):
    t = (PROGRAMACION / "com.meta-ads-os.brief-diario.plist").read_text(encoding="utf-8")
    for k, v in {"__RAIZ__": "/ruta con espacios & cosas/meta-ads-os", "__HORA__": "08:30", "__H__": "8",
                 "__M__": "30", "__CLAUDE_BIN__": "/opt/claude", "__PYTHON_BIN__": "/usr/bin/python3",
                 "__PATH__": "/usr/bin:/bin"}.items():
        t = t.replace(k, html_escape(v))
    datos = plistlib.loads(t.encode("utf-8"))
    assert datos["StartCalendarInterval"] == {"Hour": 8, "Minute": 30} and datos["RunAtLoad"] is True
    assert datos["ProgramArguments"][1:] == [
        "/ruta con espacios & cosas/meta-ads-os/.claude/skills/brief-diario/programacion/brief.sh", "--si-falta",
        "08:30"]


def html_escape(v: str) -> str:
    import html as _html
    return _html.escape(v, quote=False)


CLAUDE_FALSO = """#!/bin/bash
printf '%s\\n' "$@" > "$RAIZ_PRUEBA/args.txt"
if [ -n "${CLAUDE_CODE_OAUTH_TOKEN:-}" ]; then echo token-presente > "$RAIZ_PRUEBA/token.txt"; fi
echo "salida del claude falso"
if [ "$MODO_FALSO" = "envia" ]; then
  "$PYTHON_BIN" -I -c "import sys; sys.path.insert(0, 'herramientas'); import notificar; \
notificar._registrar('telegram', 'informes/diario/$(date +%Y-%m-%d).md', True, 1)"
fi
exit ${CODIGO_FALSO:-0}
"""


@pytest.fixture
def lanzador(tmp_path):
    if shutil.which("bash") is None or sys.platform.startswith("win"):
        pytest.skip("brief.sh necesita bash (Mac o Linux)")
    raiz = tmp_path / "instancia"
    destino = raiz / ".claude" / "skills" / "brief-diario" / "programacion"
    shutil.copytree(PROGRAMACION, destino)
    (raiz / "herramientas").mkdir(parents=True)
    for f in ("notificar.py", "_comun.py"):
        shutil.copy(PRODUCTO / "herramientas" / f, raiz / "herramientas" / f)
    falso = tmp_path / "bin" / "claude"
    falso.parent.mkdir()
    falso.write_text(CLAUDE_FALSO, encoding="utf-8")
    falso.chmod(0o755)
    entorno = {"HOME": str(tmp_path / "casa"), "PATH": "/usr/bin:/bin", "CLAUDE_BIN": str(falso),
               "PYTHON_BIN": sys.executable, "RAIZ_PRUEBA": str(raiz), "MODO_FALSO": "envia", "LANG": "C.UTF-8"}

    def correr(*args, **extra):
        e = dict(entorno, **extra)
        return subprocess.run(["bash", str(destino / "brief.sh"), *args], env=e, capture_output=True, text=True,
                              timeout=60)
    correr.raiz = raiz
    return correr


def test_brief_sh_lanza_claude_en_dontask_con_la_lista_cerrada(lanzador):
    r = lanzador()
    assert r.returncode == 0, r.stderr
    args = (lanzador.raiz / "args.txt").read_text(encoding="utf-8").splitlines()
    assert args[:2] == ["-p", "/brief-diario todos"]
    assert args[args.index("--permission-mode") + 1] == "dontAsk"
    i, j = args.index("--allowedTools"), args.index("--disallowedTools")
    assert args[i + 1:j] == _reglas("herramientas-permitidas.txt")  # cada regla llega entera, con sus espacios
    assert args[j + 1:] == _reglas("herramientas-denegadas.txt")
    hoy = date.today().isoformat()
    log = (lanzador.raiz / "logs" / f"brief-diario-{hoy[:7]}.log").read_text(encoding="utf-8")
    assert "salida del claude falso" in log and "brief enviado" in log
    assert not (lanzador.raiz / "informes" / "diario" / f"{hoy}-aviso.md").exists()


def test_brief_sh_avisa_si_no_hay_brief(lanzador):
    r = lanzador(MODO_FALSO="nada", CODIGO_FALSO="1")
    assert r.returncode == 1
    hoy = date.today().isoformat()
    aviso = (lanzador.raiz / "informes" / "diario" / f"{hoy}-aviso.md").read_text(encoding="utf-8")
    assert aviso.startswith(f"# ⚠️ Brief diario · {hoy} · no se ha generado") and "código 1" in aviso
    log = (lanzador.raiz / "logs" / f"brief-diario-{hoy[:7]}.log").read_text(encoding="utf-8")
    assert "No hay canal configurado" in log  # notificar.py lo intentó y, sin credenciales, no salió a la red


def test_brief_sh_si_falta_una_vez_al_dia(lanzador):
    assert lanzador("--si-falta", "00:00").returncode == 0
    (lanzador.raiz / "args.txt").unlink()
    assert lanzador("--si-falta", "00:00").returncode == 0  # hoy ya se intentó: no vuelve a lanzar claude
    assert not (lanzador.raiz / "args.txt").exists()
    (lanzador.raiz / "logs" / "brief-diario.ultimo").write_text("forzar\n", encoding="utf-8")
    assert lanzador("--si-falta", "23:59").returncode == 0  # «forzar» (instalar --probar) salta hora y marca
    assert (lanzador.raiz / "args.txt").exists()
    assert lanzador("--si-falta", "8:00").returncode == 1  # hora mal escrita


def test_brief_sh_usa_el_token_de_env_sin_mostrarlo(lanzador):
    (lanzador.raiz / ".env").write_text('OTRA=1\nCLAUDE_CODE_OAUTH_TOKEN="sk-ant-oat01-secreto-de-prueba"\n',
                                        encoding="utf-8")
    r = lanzador()
    assert r.returncode == 0
    assert (lanzador.raiz / "token.txt").read_text(encoding="utf-8").strip() == "token-presente"
    log = (lanzador.raiz / "logs" / f"brief-diario-{date.today().isoformat()[:7]}.log").read_text(encoding="utf-8")
    assert "secreto-de-prueba" not in log + r.stdout + r.stderr
