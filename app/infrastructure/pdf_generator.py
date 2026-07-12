import io
import tempfile

import matplotlib
matplotlib.use('Agg')  # backend sin pantalla
import matplotlib.pyplot as plt
from matplotlib import rcParams

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    HRFlowable,
    Image,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
)

rcParams['mathtext.fontset'] = 'cm'   # Computer Modern — igual que LaTeX/MathJax


def _fmt_int(v: float) -> str:
    """Formatea un float redondeando al entero más cercano (igual que el dominio)."""
    r = round(v)
    return str(r) if r != 0 else '1'


def _render_latex(expr: str, font_size: float = 14) -> Image:
    """
    Convierte una expresión LaTeX a una imagen PNG en memoria
    y la devuelve como un flowable Image de ReportLab.
    """
    fig, ax = plt.subplots(figsize=(0.01, 0.01))
    ax.axis('off')
    text = ax.text(
        0.5, 0.5, f'${expr}$',
        fontsize=font_size,
        ha='center', va='center',
        transform=fig.transFigure,
    )

    # Ajustar el canvas al tamaño real del texto
    fig.canvas.draw()
    bbox = text.get_window_extent(renderer=fig.canvas.get_renderer())
    pad = 4
    fig.set_size_inches(
        (bbox.width + pad * 2) / fig.dpi,
        (bbox.height + pad * 2) / fig.dpi,
    )

    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=150, bbox_inches='tight',
                transparent=True, pad_inches=0.04)
    plt.close(fig)
    buf.seek(0)

    img = Image(buf)
    # Escalar para que encaje bien en la página
    max_width = 12 * cm
    if img.drawWidth > max_width:
        scale = max_width / img.drawWidth
        img.drawWidth  *= scale
        img.drawHeight *= scale
    return img


class GeneradorPDF:
    """Genera el historial de ecuaciones guardadas como PDF con notación matemática."""

    def generar(self, ecuaciones: list) -> str:
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        tmp.close()

        doc = SimpleDocTemplate(
            tmp.name,
            pagesize=A4,
            topMargin=2 * cm,
            bottomMargin=2 * cm,
            leftMargin=2.5 * cm,
            rightMargin=2.5 * cm,
            title='Historial de Ecuaciones Diferenciales',
        )
        doc.build(self._build_story(ecuaciones))
        return tmp.name

    # ------------------------------------------------------------------

    def _build_story(self, ecuaciones: list) -> list:
        st = self._styles()
        story = []

        story.append(Paragraph('Historial de Ecuaciones Diferenciales', st['title']))
        story.append(Paragraph(
            'Ecuaciones Homog&#233;neas de Segundo Orden &mdash; ay&#8243; + by&#8242; + cy = 0',
            st['subtitle'],
        ))
        story.append(HRFlowable(width='100%', thickness=2, color=colors.HexColor('#1a237e')))
        story.append(Spacer(1, 0.5 * cm))

        for i, eq in enumerate(ecuaciones, 1):
            story.extend(self._eq_block(eq, i, st))
            if i < len(ecuaciones):
                story.append(Spacer(1, 0.3 * cm))
                story.append(HRFlowable(width='100%', thickness=0.5,
                                        color=colors.HexColor('#bdbdbd')))
                story.append(Spacer(1, 0.3 * cm))

        return story

    def _eq_block(self, eq: dict, num: int, st: dict) -> list:
        caso       = eq.get('caso', 0)
        timestamp  = eq.get('timestamp', '')
        caso_color = {1: '#2e7d32', 2: '#1565c0', 3: '#6a1b9a'}.get(caso, '#424242')

        # Expresiones LaTeX ya calculadas por el dominio
        ec_latex  = eq.get('ecuacion_latex', eq.get('ecuacion_str', ''))
        r_latex   = eq.get('raices_latex', self._fallback_roots(caso, eq.get('raices', {})))
        sol_latex = eq.get('solucion_latex', '')

        block = [
            Paragraph(
                f'Ecuaci&#243;n #{num}'
                f'&nbsp;&nbsp;<font color="#9e9e9e" size="9">{timestamp}</font>',
                st['eq_header'],
            ),
            Paragraph(
                f'<font color="{caso_color}"><b>Caso {caso}:</b></font>'
                f' {eq.get("tipo", "")}',
                st['normal'],
            ),
            Spacer(1, 0.2 * cm),
            Paragraph('<b>Ecuaci&#243;n:</b>', st['label']),
            _render_latex(ec_latex, font_size=13),
            Spacer(1, 0.1 * cm),
            Paragraph('<b>Ra&#237;ces:</b>', st['label']),
            _render_latex(r_latex, font_size=13),
            Spacer(1, 0.1 * cm),
            Paragraph('<b>Soluci&#243;n general:</b>', st['label']),
            _render_latex(sol_latex, font_size=13),
        ]
        return block

    def _fallback_roots(self, caso: int, raices: dict) -> str:
        """Genera LaTeX de raíces con valores redondeados si el dict no trae raices_latex."""
        if caso == 1:
            r1 = _fmt_int(raices.get('r1', 0))
            r2 = _fmt_int(raices.get('r2', 0))
            return fr'r_1 = {r1},\quad r_2 = {r2}'
        if caso == 2:
            r = _fmt_int(raices.get('r', 0))
            return fr'r = {r}\;(\text{{raíz doble}})'
        if caso == 3:
            real = _fmt_int(raices.get('real', 0))
            imag = _fmt_int(raices.get('imag', 0))
            return fr'r = {real} \pm {imag}\,i'
        return ''

    # ------------------------------------------------------------------

    def _styles(self) -> dict:
        base = getSampleStyleSheet()
        return {
            'title': ParagraphStyle(
                'pdf_title', parent=base['Title'],
                fontSize=17, textColor=colors.HexColor('#1a237e'),
                spaceAfter=4, alignment=TA_CENTER,
            ),
            'subtitle': ParagraphStyle(
                'pdf_subtitle', parent=base['Normal'],
                fontSize=9, textColor=colors.HexColor('#546e7a'),
                spaceAfter=10, alignment=TA_CENTER,
            ),
            'eq_header': ParagraphStyle(
                'pdf_eq_header', parent=base['Normal'],
                fontSize=13, fontName='Helvetica-Bold',
                textColor=colors.HexColor('#1a237e'), spaceAfter=4,
            ),
            'normal': ParagraphStyle(
                'pdf_normal', parent=base['Normal'],
                fontSize=10, spaceAfter=4, leading=14,
            ),
            'label': ParagraphStyle(
                'pdf_label', parent=base['Normal'],
                fontSize=8, textColor=colors.HexColor('#757575'),
                spaceBefore=6, spaceAfter=2,
            ),
        }
