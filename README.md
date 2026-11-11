# Curso de Manejo Administrativo de Piscinas — guía interactiva

Sitio de una sola página con **buscador integrado** sobre todo el contenido del curso
(Alfa Consultores Profesionales): normativa, los 8 módulos, la chuleta de datos, el glosario,
las 60 preguntas de los talleres y del examen final, y la **Circular 2026090000180** de la
Gobernación de Antioquia sobre la **Resolución 0234 de 2026**.

- `index.html` — el sitio (autocontenido, sin dependencias de servidor).
- `template.html` + `build.py` — generador: `PYTHONPATH=/tmp/mdpy python3 build.py`.
- `circular-0234-2026.pdf` — circular original adjunta.

Funciona abriendo `index.html` en cualquier navegador; el buscador ignora tildes, mayúsculas y
plurales, acepta preguntas completas y resalta los resultados.
