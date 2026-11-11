#!/usr/bin/env python3
# Genera el sitio interactivo (index.html) del curso de piscinas + circular 0234/2026.
# Uso: PYTHONPATH=/tmp/mdpy python3 build.py
import re, json, html, pathlib

ROOT = pathlib.Path(__file__).resolve().parent
MD = ROOT.parent / "CURSO-DE-MANEJO-ADMINISTRATIVO-DE-PISCINAS.md"
OUT = ROOT / "index.html"

import markdown

md = markdown.Markdown(extensions=["tables", "sane_lists", "attr_list"])

def to_html(text: str) -> str:
    md.reset()
    return md.convert(text)

def strip_md(s: str) -> str:
    s = re.sub(r"[`*_>#]", "", s)
    s = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", s)
    return re.sub(r"\s+", " ", s).strip()

# ---------------------------------------------------------------- contenido base
raw = MD.read_text(encoding="utf-8")
# fuera el bloque de índice
raw = re.sub(r"## Índice\n(?:\n|.+\n)*?\n---\n", "---\n", raw, count=1)
blocks = re.split(r"\n(?=## )", raw)

CATS = [
    ("general", "Generalidades"),
    ("normativa", "Normativa"),
    ("gestion", "Gestión"),
    ("contaminacion", "Contaminación"),
    ("inspecciones", "Inspecciones"),
    ("bps", "BPS"),
    ("seguridad", "Plan de seguridad"),
    ("sst", "Salud y seguridad"),
    ("circular", "Circular 0234/2026"),
    ("faq", "Preguntas"),
    ("referencia", "Referencia"),
]

TEMAS = {
    "Módulo 1": ("general", "Generalidades y tipos de piscina"),
    "Módulo 2": ("normativa", "Marco normativo"),
    "Módulo 3": ("gestion", "Gestión administrativa"),
    "Módulo 4": ("contaminacion", "Contaminación y respuesta"),
    "Módulo 5": ("inspecciones", "Inspecciones y sanciones"),
    "Módulo 6": ("bps", "Buenas prácticas sanitarias"),
    "Módulo 7": ("seguridad", "Plan de seguridad"),
    "Módulo 8": ("sst", "Salud y seguridad en el trabajo"),
}

def limpiar(texto: str) -> str:
    """Quita referencias al aula y suaviza el tono de curso."""
    texto = re.sub(r"> ✅ \*\*Ya legible\.\*\*.*?\n\n", "", texto, flags=re.S)
    pares = [
        ("El examen final, en cambio, marca «cada 4 horas» como frecuencia de recirculación para piscinas de uso público. Para el taller y el material del módulo 1 la respuesta es **6 a 8 horas**; para el examen, **cada 4 horas**. Conviene saber las dos versiones.",
         "Hay dos criterios en circulación: la referencia técnica fija **6 a 8 horas** para uso público y algunos protocolos de operación hablan de **cada 4 horas**. Confirma siempre con la autoridad sanitaria de tu municipio."),
        ("(Un **engranaje** NO es elemento de piscina: es la respuesta del taller.)",
         "(Un **engranaje** no es un elemento de piscina: es un error frecuente.)"),
        (" (respuesta correcta del taller)", ""),
        ("el taller marca como correcta la opción de **llamar al laboratorio para tomar muestra y verificar parámetros microbiológicos** antes de reabrir.",
         "lo recomendable es **llamar al laboratorio para tomar muestra y verificar los parámetros microbiológicos** antes de reabrir."),
        ("Esto explica la pregunta del taller: decía que el numeral **2.5** trataba de «duchas y vestidores», y la respuesta correcta era **FALSO** — ese contenido es el **2.3**; el 2.5 es el de drenajes y canaletas.",
         "Ojo con la numeración: **duchas y vestidores** es el numeral **2.3**; el **2.5** corresponde a drenajes y canaletas."),
        (" (así lo marca el taller)", ""),
        ("El módulo es el **Anexo B:", "La referencia es el **Anexo B:"),
        ("**Vigencia del curso de manejo administrativo de piscinas: 3 años.**",
         "**Vigencia de la certificación del administrador: 3 años.**"),
        ("**6. EL  curso de manejo administrativo de piscina tiene una vigencia de**",
         "**6. ¿Cada cuánto se renueva la certificación del administrador?**"),
        ("Puntos que evalúa el aula:", "Puntos clave:"),
        ("| Vigencia del curso | 3 años |", "| Vigencia de la certificación | 3 años |"),
        ("Las 60 preguntas que aparecieron en los talleres y en el examen final, con la respuesta que la plataforma marcó como correcta. Sirve para repasar y para responder consultas rápidas.",
         "Preguntas de consulta rápida, agrupadas por tema, con la respuesta correcta."),
        ("> **Notas sobre el examen:** la opción correcta de la pregunta 9 dice «flitro» (error de digitación del aula; es **filtro**). La pregunta 10 («cada 4 horas») contradice el periodo del módulo 1 (6–8 h para uso público): son dos versiones del mismo tema y conviene tener las dos presentes.",
         "> **Notas:** en la pregunta 9 la opción aparece escrita «flitro» (error de digitación; es **filtro**). La pregunta 10 («cada 4 horas») y el periodo de 6–8 h son dos versiones del mismo tema: conviene tener las dos presentes."),
    ]
    for a, c in pares:
        texto = texto.replace(a, c)
    return texto

def categoria(titulo: str):
    m = re.search(r"Módulo\s*(\d)", titulo)
    if m: return TEMAS["Módulo " + m.group(1)][0]
    t = titulo.lower()
    if "normativ" in t or "marco" in t: return "normativa"
    if "preguntas" in t: return "faq"
    if "chuleta" in t or "glosario" in t or "fuentes" in t: return "referencia"
    return "referencia"

sections = []
visto_marco = False
for b in blocks:
    b = b.strip()
    if not b.startswith("## "):
        continue
    lines = b.splitlines()
    titulo_md = lines[0][3:].strip()
    if titulo_md.lower().startswith("índice"):
        continue
    titulo = re.sub(r"^\d+\.\s*", "", titulo_md)
    if titulo.startswith("Módulo "):
        clave = titulo.split(" — ")[0]
        if clave in TEMAS:
            titulo = TEMAS[clave][1]
    if titulo == "Marco normativo" and not visto_marco:
        titulo = "Normas y artículos clave"
        visto_marco = True
    cuerpo = limpiar("\n".join(lines[1:]).strip())
    cat = categoria(titulo_md)

    # El banco de preguntas se parte por taller para que el buscador apunte fino
    if cat == "faq":
        partes = re.split(r"\n(?=### )", cuerpo)
        intro = [p for p in partes if not p.lstrip().startswith("### ")]
        if intro:
            sections.append({
                "id": "preguntas-intro", "cat": cat, "title": "Preguntas frecuentes",
                "html": to_html("\n".join(intro).strip()),
            })
        for p in partes:
            if not p.lstrip().startswith("### "):
                continue
            pt = p.splitlines()[0][4:].strip()
            pb = limpiar("\n".join(p.splitlines()[1:]).strip())
            mm = re.search(r"Taller módulo\s*(\d)", pt)
            if mm:
                pt = "Preguntas · " + TEMAS["Módulo " + mm.group(1)][1]
            elif pt.lower().startswith("examen"):
                pt = "Preguntas · casos y cálculos"
            slug = re.sub(r"[^a-z0-9]+", "-", pt.lower()).strip("-")
            sections.append({"id": "q-" + slug, "cat": cat, "title": pt, "html": to_html(pb)})
        continue

    if titulo.lower().startswith("fuentes"):
        cuerpo = """- **Normas citadas:** Ley 9 de 1979 · Ley 1209 de 2008 · Decreto 780 de 2016 · Decreto 554 de 2015 ·
  Decreto 1538 de 2005 · Ley 1801 de 2016 · Ley 1225 de 2008 · Resolución 1229 de 2013 · Resolución 1394 de
  2015 · Resolución 4113 de 2012 · Resolución 4198 de 2012 · Resolución 2018060366702 de 2018.
- **Circular 2026090000180** de la Gobernación de Antioquia (15/07/2026) sobre la Resolución 0234 de 2026.
- **Cifras y tablas:** contrastadas con los documentos técnicos de referencia del sector y con el
  formulario de inspección sanitaria (Anexo B, Antioquia).

> **Aviso:** esta guía resume y ordena información técnica y normativa para el trabajo diario del
> administrador y del piscinero. No sustituye el texto oficial de las normas, el acta de la autoridad
> sanitaria ni el concepto de un profesional competente."""
    slug = re.sub(r"[^a-z0-9]+", "-", titulo.lower()).strip("-")
    sections.append({"id": slug, "cat": cat, "title": titulo, "html": to_html(cuerpo)})

# ---------------------------------------------------------------- circular 0234
circular_md = """
📄 **[Descargar la circular original (PDF)](circular-0234-2026.pdf)**

**Radicado K 2026090000180 · 15/07/2026 · CIRCULAR** — Gobernación de Antioquia, Secretaría de Salud e
Inclusión Social. *Asunto:* consideraciones generales para la adopción e implementación de la
**Resolución 0234 de 2026** (Ministerio de Salud y Protección Social, 10 de febrero de 2026).

### Qué dice, en corto

| Punto | Contenido |
|---|---|
| **Base legal** | Ley 9 de 1979 (arts. 222, 229 y 230: calidad del agua, equipos de control y libro de registro diario) y Resolución 1229 de 2013 (art. 9: enfoque de riesgo en la inspección) |
| **El vacío** | El **Decreto 554 de 2015** (hoy en el Decreto 780 de 2016) derogó el Decreto 2171 de 2009 y sus resoluciones, dejando sin herramientas la verificación de estándares del agua y las BPS |
| **Lo que se venía aplicando** | **Resolución 2018060366702 del 02/11/2018**: adopta el modelo de IVC y la guía del Certificado de Cumplimiento. Ocho años de aplicación en los **125 municipios** de Antioquia hasta 2025 |
| **Parámetros** | Art. **2.8.7.1.2.3 del Decreto 780 de 2016**: el agua de los estanques debe ser limpia y sana; el Ministerio define los parámetros fisicoquímicos y microbiológicos |
| **Asistencia técnica** | Ministerio de Salud acompañó a las direcciones territoriales el **16 y 17 de abril de 2026** |
| **Compromisos del Ministerio** | Entregar la **caja de herramientas** de la Resolución 0234/2026: acta de inspección sanitaria, instructivo para diligenciarla y el **ABC** con las dudas resueltas |

### La decisión transitoria (lo más importante)

> Mientras el nivel nacional precisa la implementación de la **Resolución 0234 de 2026** y ajusta la caja
> de herramientas, **se continúa aplicando la Resolución 2018060366702 de 2018** y el acta de inspección
> vigente, cuyo contenido es concurrente con la nueva normativa.

En otras palabras: **no cambia el formulario todavía**. Lo que se viene haciendo en Antioquia sigue
vigente; la Resolución 0234/2026 se incorporará y armonizará al modelo de IVC departamental cuando el
Ministerio entregue las precisiones y los instrumentos ajustados.

### Quién firma

- **Alma Solano Sánchez** — Secretaria de Salud e Inclusión Social (firma).
- Proyectó: **John William Tabares Morales** — profesional universitario, componente Vigilancia de la
  Calidad del Agua para Consumo Humano y Uso Recreativo.
- Aprobó: **Juan David Berrio Vargas** — Director Técnico de Salud Ambiental y Factores de Riesgo.
- Revisó: **Erika Hernández Bolívar** — Directora de Asuntos Legales de Salud.

### Cómo se relaciona con esta guía

- Esta guía trabaja el modelo de IVC, las BPS, el IRAPI y los sellos con base en la **Resolución 1229 de
  2013** y el **Decreto 780 de 2016**, y usa el acta de inspección del Anexo B (Gobernación de Antioquia):
  exactamente la que la circular mantiene vigente de forma transitoria.
- Para efectos prácticos en Antioquia: **se sigue auditando con el modelo vigente**, y el día que el
  Ministerio publique la caja de herramientas de la Resolución 0234/2026, el acta y los criterios se
  actualizarán. Conviene manejar las dos referencias para no confundirlas.

### Respuestas rápidas

- **¿Ya cambió el acta de inspección?** No. Transitoriamente se usa la de la Resolución 2018060366702 de 2018.
- **¿La Resolución 0234 de 2026 aplica ya?** Debe incorporarse y armonizarse; el Ministerio aún precisa la
  implementación y ajusta la caja de herramientas.
- **¿Qué pasa con los parámetros del agua?** Siguen los del art. 2.8.7.1.2.3 del Decreto 780 de 2016 y los
  valores de referencia del modelo departamental.
- **¿A quién aplica la circular?** Autoridades sanitarias municipales, responsables de establecimientos de
  piscinas, laboratorios de agua, oferentes de capacitación a piscineros, salvavidas y administradores.
"""

sections.append({
    "id": "circular-0234-2026",
    "cat": "circular",
    "title": "Circular 2026090000180 · Resolución 0234 de 2026",
    "html": to_html(circular_md),
})
# ---------------------------------------------------------------- respuestas rápidas
rapidas_md = """
Las preguntas que más se hacen, con la respuesta corta. Toca una para ver el detalle completo.

| Pregunta | Respuesta |
|---|---|
| **¿Cuánto cloro debe tener el agua?** | **2 a 4 ppm** de cloro libre residual en operación normal |
| **¿Cada cuánto debe recircular el agua?** | **6 a 8 h** abierta al público · **4 a 6 h** uso restringido · **4 h** propiedad privada (algunos protocolos usan «cada 4 horas» para uso público) |
| **¿Cómo se calcula el volumen?** | Rectangular: **largo × ancho × profundidad media**. Circular: **π × r² × h** (0,785 × D² × h) |
| **¿Profundidad máxima?** | Infantil **0,60 m** · uso público y recreativo **1,50 m** |
| **¿Qué significa el sello?** | **0–16 verde** (favorable) · **16,1–49,5 amarillo** (favorable condicionado) · **≥ 49,6 rojo** (desfavorable) |
| **¿Dosis de choque por materia fecal?** | Sólida: **9 ppm**, 8 h de contacto, 24 h cerrada · Líquida: **20 ppm**, 13 h, 48 h cerrada |
| **¿De cuánto es la multa?** | **50 a 1.000 SMMLV** y cierre temporal hasta **5 días** en la primera falta |
| **¿Qué botiquín necesito?** | **A** si la superficie es < 2.000 m² · **B** entre 2.000 y 15.000 m² · **C** (dos tipo B) si supera 15.000 m² |
| **¿Cada cuánto se renueva la certificación?** | La certificación del administrador tiene **vigencia de 3 años** |
| **¿Ya cambió el acta por la Resolución 0234 de 2026?** | **Todavía no**: transitoriamente sigue la Resolución 2018060366702 de 2018 |
"""

sections.insert(0, {
    "id": "respuestas-rapidas",
    "cat": "referencia",
    "title": "Respuestas rápidas · las preguntas de siempre",
    "html": to_html(rapidas_md),
})

# la circular va arriba, después de normativa
orden = {"normativa": 0, "circular": 1}
sections.sort(key=lambda s: orden.get(s["cat"], 5))

# ---------------------------------------------------------------- datos para el buscador
data = []
for s in sections:
    texto = html.unescape(re.sub(r"<[^>]+>", " ", s["html"]))
    data.append({
        "id": s["id"], "cat": s["cat"], "title": s["title"],
        "html": s["html"], "text": re.sub(r"\s+", " ", texto).strip(),
    })

cards = []
for s in data:
    cat_label = dict(CATS).get(s["cat"], "Referencia")
    cards.append(f"""<article class="card" id="{s['id']}" data-cat="{s['cat']}" data-title="{html.escape(s['title'], quote=True)}">
  <div class="card-top">
    <button class="card-head" aria-expanded="false">
      <span class="badge b-{s['cat']}">{html.escape(cat_label)}</span>
      <h2>{html.escape(s['title'])}</h2>
      <span class="chev" aria-hidden="true">⌄</span>
    </button>
    <button class="linkbtn" title="Copiar enlace a esta sección" aria-label="Copiar enlace">
      <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M10 13a5 5 0 0 0 7.1 0l3-3a5 5 0 0 0-7.1-7.1L11.6 4.2"/><path d="M14 11a5 5 0 0 0-7.1 0l-3 3a5 5 0 0 0 7.1 7.1l1.4-1.4"/></svg>
    </button>
  </div>
  <div class="card-body">{s['html']}</div>
</article>""")

chips = "".join(
    f'<button class="chip" data-filter="{k}">{v}</button>' for k, v in CATS
)

tpl = (ROOT / "template.html").read_text(encoding="utf-8")
out = (tpl.replace("__CARDS__", "\n".join(cards))
          .replace("__CHIPS__", chips)
          .replace("__DATA__", json.dumps(data, ensure_ascii=False).replace("</", "<\\/")))
OUT.write_text(out, encoding="utf-8")
print(f"OK {OUT} · {len(data)} secciones · {len(out)/1024:.0f} KB")
