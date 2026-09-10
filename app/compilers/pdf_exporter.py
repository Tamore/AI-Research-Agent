import os
import logging
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from app.models.schemas import ResearchReport

logger = logging.getLogger("pdf_exporter")

class PDFExporter:
    """PDF compiler using ReportLab to export premium academic paper drafts."""

    @staticmethod
    def compile_pdf(report: ResearchReport, output_filepath: str = "ieee_paper_draft.pdf") -> str:
        """Compile ResearchReport data into a beautiful IEEE/Academic style PDF file."""
        try:
            doc = SimpleDocTemplate(
                output_filepath,
                pagesize=letter,
                rightMargin=40,
                leftMargin=40,
                topMargin=40,
                bottomMargin=40
            )

            styles = getSampleStyleSheet()

            # Palette Definition
            PRIMARY_COLOR = colors.HexColor("#0f172a")    # Deep Slate / Navy
            SECONDARY_COLOR = colors.HexColor("#2563eb")  # Royal Accent Blue
            NEUTRAL_DARK = colors.HexColor("#334155")     # Charcoal Text
            BG_LIGHT = colors.HexColor("#f8fafc")         # Soft Ice Background
            BORDER_COLOR = colors.HexColor("#e2e8f0")     # Subtle Border

            # Custom Typography Styles
            title_style = ParagraphStyle(
                'DocTitle',
                parent=styles['Heading1'],
                fontName='Helvetica-Bold',
                fontSize=20,
                leading=24,
                textColor=PRIMARY_COLOR,
                alignment=1, # Center
                spaceAfter=8
            )

            subtitle_style = ParagraphStyle(
                'DocSubtitle',
                parent=styles['Normal'],
                fontName='Helvetica',
                fontSize=10,
                leading=14,
                textColor=SECONDARY_COLOR,
                alignment=1, # Center
                spaceAfter=14
            )

            author_style = ParagraphStyle(
                'AuthorBlock',
                parent=styles['Normal'],
                fontName='Helvetica-Bold',
                fontSize=9.5,
                leading=14,
                textColor=NEUTRAL_DARK,
                alignment=1, # Center
                spaceAfter=16
            )

            h2_style = ParagraphStyle(
                'SectionHeading',
                parent=styles['Heading2'],
                fontName='Helvetica-Bold',
                fontSize=12,
                leading=16,
                textColor=PRIMARY_COLOR,
                spaceBefore=14,
                spaceAfter=8
            )

            body_style = ParagraphStyle(
                'BodyText',
                parent=styles['Normal'],
                fontName='Helvetica',
                fontSize=9.5,
                leading=14,
                textColor=NEUTRAL_DARK,
                spaceAfter=8
            )

            code_style = ParagraphStyle(
                'CodeBlock',
                parent=styles['Normal'],
                fontName='Courier',
                fontSize=8,
                leading=11,
                textColor=colors.HexColor("#0f172a"),
                backColor=BG_LIGHT,
                borderColor=BORDER_COLOR,
                borderWidth=0.5,
                borderPadding=6,
                spaceAfter=8
            )

            elements = []

            # 1. Header & Title Block
            elements.append(Paragraph(f"<b>{report.topic}</b>", title_style))
            elements.append(Paragraph("<b>AUTONOMOUS ACADEMIC LITERATURE REVIEW & RESEARCH SYNTHESIS</b>", subtitle_style))
            elements.append(Paragraph("<b>Author: Nirmiti R. Tamore</b> &nbsp;|&nbsp; <i>Synthesized by AI Academic Research Agent</i>", author_style))
            
            elements.append(HRFlowable(width="100%", thickness=1.5, color=SECONDARY_COLOR, spaceAfter=14))

            # 2. Executive Literature Summary
            elements.append(Paragraph("1. Executive Literature Summary", h2_style))
            summary_clean = report.summary_markdown.replace("#", "").replace("*", "")
            for para in summary_clean.split("\n\n"):
                if para.strip():
                    elements.append(Paragraph(para.strip(), body_style))

            elements.append(Spacer(1, 10))

            # 3. Comparative Literature Table
            elements.append(Paragraph("2. Analyzed Academic Publications", h2_style))
            table_data = [["#", "Paper Title", "Year", "Authors & Categories"]]
            
            for idx, p in enumerate(report.analyzed_papers, start=1):
                authors_str = ", ".join(p.authors[:2]) + (" et al." if len(p.authors) > 2 else "")
                cats = f"({', '.join(p.categories[:2])})" if p.categories else ""
                table_data.append([str(idx), p.title[:50] + "...", str(p.year), f"{authors_str} {cats}"])

            t = Table(table_data, colWidths=[24, 230, 45, 233])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), PRIMARY_COLOR),
                ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                ('ALIGN', (0,0), (-1,-1), 'LEFT'),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('FONTSIZE', (0,0), (-1,-1), 8.5),
                ('BOTTOMPADDING', (0,0), (-1,0), 6),
                ('TOPPADDING', (0,0), (-1,0), 6),
                ('BACKGROUND', (0,1), (-1,-1), BG_LIGHT),
                ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
            ]))
            elements.append(t)
            elements.append(Spacer(1, 14))

            # 4. Faculty & Lab Radar (If available)
            if report.faculty_radar:
                elements.append(Paragraph("3. Target Faculty & Laboratory Discovery Radar", h2_style))
                fac_table_data = [["Faculty / PI", "Institution / Lab", "Target Focus", "Alignment"]]
                for f in report.faculty_radar:
                    fac_table_data.append([f.name, f.university_or_lab, f.primary_research_focus, f"{int(f.alignment_score * 100)}%"])

                ft = Table(fac_table_data, colWidths=[120, 160, 200, 52])
                ft.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,0), SECONDARY_COLOR),
                    ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                    ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0,0), (-1,-1), 8.5),
                    ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
                ]))
                elements.append(ft)
                elements.append(Spacer(1, 14))

            # 5. BibTeX References Section
            elements.append(Paragraph("4. BibTeX Citation References", h2_style))
            bib_clean = report.bibtex_citations.replace("\n", "<br/>")
            elements.append(Paragraph(bib_clean, code_style))

            # Build Document
            doc.build(elements)
            logger.info(f"Successfully compiled beautiful PDF report to {output_filepath}")
            return output_filepath

        except Exception as e:
            logger.error(f"Error compiling PDF with ReportLab: {e}")
            raise e
