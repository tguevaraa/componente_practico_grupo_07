import tempfile

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    HRFlowable,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
)


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
    # Story builder
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
        caso = eq.get('caso', 0)
        raices = eq.get('raices', {})
        timestamp = eq.get('timestamp', '')
        caso_color = {1: '#2e7d32', 2: '#1565c0', 3: '#6a1b9a'}.get(caso, '#424242')

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
            Paragraph(self._fmt_equation(eq.get('ecuacion_str', '')), st['math']),
            Paragraph('<b>Ra&#237;ces:</b>', st['label']),
            Paragraph(self._fmt_roots(caso, raices), st['math']),
            Paragraph('<b>Soluci&#243;n general:</b>', st['label']),
            Paragraph(self._fmt_solution(caso, raices), st['math']),
        ]
        return block

    # ------------------------------------------------------------------
    # Math formatting (Latin-1 safe + reportlab markup)
    # ------------------------------------------------------------------

    def _fmt_equation(self, ec_str: str) -> str:
        # Replace ASCII '' / ' with unicode prime characters (Latin-1 range U+00xx covered)
        # y'' -> y" (double prime U+2033 is NOT Latin-1, use two apostrophes as-is)
        return ec_str  # already ASCII-safe from obtener_representacion()

    def _fmt_roots(self, caso: int, raices: dict) -> str:
        if caso == 1:
            r1, r2 = raices.get('r1', 0), raices.get('r2', 0)
            return (f'r<sub>1</sub> = {r1:.4g}'
                    f'&nbsp;&nbsp;&nbsp;&nbsp;'
                    f'r<sub>2</sub> = {r2:.4g}')
        if caso == 2:
            r = raices.get('r', 0)
            return f'r = {r:.4g}  (ra&#237;z doble)'
        if caso == 3:
            real = raices.get('real', 0)
            imag = raices.get('imag', 0)
            return f'r = {real:.4g} &#177; {imag:.4g}i'
        return ''

    def _fmt_solution(self, caso: int, raices: dict) -> str:
        def e(v: float) -> str:
            if v == 0: return '0'
            if v == 1: return ''
            if v == -1: return '-'
            return str(int(v)) if v == int(v) else f'{v:.4g}'

        if caso == 1:
            r1, r2 = raices.get('r1', 0), raices.get('r2', 0)
            return (f'y(x) = C<sub>1</sub> e<super>({e(r1)}x)</super>'
                    f' + C<sub>2</sub> e<super>({e(r2)}x)</super>')
        if caso == 2:
            r = raices.get('r', 0)
            return (f'y(x) = (C<sub>1</sub> + C<sub>2</sub> x)'
                    f' e<super>({e(r)}x)</super>')
        if caso == 3:
            real = raices.get('real', 0)
            imag = raices.get('imag', 0)
            b = f'{imag:.4g}'
            if real == 0:
                return (f'y(x) = C<sub>1</sub> cos({b}x)'
                        f' + C<sub>2</sub> sin({b}x)')
            return (f'y(x) = e<super>({e(real)}x)</super>'
                    f' [ C<sub>1</sub> cos({b}x) + C<sub>2</sub> sin({b}x) ]')
        return ''

    # ------------------------------------------------------------------
    # Styles
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
            'math': ParagraphStyle(
                'pdf_math', parent=base['Normal'],
                fontSize=11, fontName='Courier',
                spaceAfter=2, leading=17, leftIndent=0.5 * cm,
            ),
        }
