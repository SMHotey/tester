#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF generator for test results.
Requires: reportlab library (pip install reportlab)
"""

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
    from reportlab.lib import colors
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
except ImportError:
    raise ImportError("Please install reportlab: pip install reportlab")

import os
from pathlib import Path
from datetime import datetime


def generate_pdf(result, reglament):
    """Generate PDF report from test results."""
    # Setup paths
    output_dir = Path(__file__).parent / "results"
    output_dir.mkdir(exist_ok=True)

    # Create filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"test_result_{result['last_name']}_{result['first_name']}_{timestamp}.pdf"
    filepath = output_dir / filename

    # Create PDF document
    doc = SimpleDocTemplate(
        str(filepath),
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )

    # Styles
    styles = getSampleStyleSheet()

    # Custom styles for Russian text
    # Try to use a Unicode font that supports Cyrillic
    try:
        # Try to register Arial font
        pdfmetrics.registerFont(TTFont('Arial', 'C:\\Windows\\Fonts\\arial.ttf'))
        pdfmetrics.registerFont(TTFont('Arial-Bold', 'C:\\Windows\\Fonts\\arialbd.ttf'))
        font_name = 'Arial'
        bold_font = 'Arial-Bold'
    except:
        # Fallback to built-in fonts
        font_name = 'Helvetica'
        bold_font = 'Helvetica-Bold'

    # Create custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontName=bold_font,
        fontSize=16,
        alignment=TA_CENTER,
        spaceAfter=20,
    )

    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontName=bold_font,
        fontSize=12,
        spaceAfter=10,
    )

    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=10,
        spaceAfter=6,
    )

    # Build content
    story = []

    # Title
    story.append(Paragraph("РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ", title_style))
    story.append(Spacer(1, 0.5*cm))

    # Test info table
    test_info = [
        ["ФИО тестируемого:", f"{result['last_name']} {result['first_name']}"],
        ["Дата тестирования:", datetime.fromisoformat(result['start_time']).strftime("%d.%m.%Y")],
        ["Время начала:", datetime.fromisoformat(result['start_time']).strftime("%H:%M:%S")],
        ["Время завершения:", datetime.fromisoformat(result['end_time']).strftime("%H:%M:%S")],
        ["Длительность:", f"{int(result['duration_seconds'] // 60)} мин. {int(result['duration_seconds'] % 60)} сек."],
    ]

    info_table = Table(test_info, colWidths=[6*cm, 10*cm])
    info_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), font_name),
        ('FONTNAME', (0, 0), (0, -1), bold_font),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 0.5*cm))

    # Results summary
    story.append(Paragraph("ИТОГОВЫЙ РЕЗУЛЬТАТ", heading_style))

    # Score table
    score_data = [
        ["Всего вопросов:", f"{result['total_questions']}"],
        ["Правильных ответов:", f"{result['correct_count']}"],
        ["Неправильных ответов:", f"{result['incorrect_count']}"],
        ["Процент успеха:", f"{(result['correct_count'] / result['total_questions'] * 100):.1f}%"],
    ]

    score_table = Table(score_data, colWidths=[6*cm, 10*cm])
    score_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), font_name),
        ('FONTNAME', (0, 0), (0, -1), bold_font),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.lightgrey, colors.white]),
    ]))

    # Color code the score
    if result['correct_count'] == result['total_questions']:
        score_color = colors.green
    elif result['correct_count'] / result['total_questions'] >= 0.7:
        score_color = colors.orange
    else:
        score_color = colors.red

    story.append(score_table)
    story.append(Spacer(1, 0.5*cm))

    # Detailed results
    story.append(Paragraph("ДЕТАЛИЗАЦИЯ ПО ВОПРОСАМ", heading_style))

    # Add each question result
    for i, detail in enumerate(result['details'], 1):
        # Question header
        status = "✓ Верно" if detail['correct'] else "✗ Неверно"
        status_color = colors.green if detail['correct'] else colors.red

        question_text = f"Вопрос {i}: {status}"
        story.append(Paragraph(question_text, normal_style))

        # Question text
        story.append(Paragraph(detail['question'], normal_style))

        # User answer
        user_answer = format_answer_for_pdf(detail)
        story.append(Paragraph(f"<b>Ваш ответ:</b> {user_answer}", normal_style))

        # Correct answer if wrong
        if not detail['correct']:
            correct_answer = format_correct_answer_for_pdf(detail)
            story.append(Paragraph(f"<b>Правильный ответ:</b> {correct_answer}", normal_style))

            # Explanation
            explanation = detail.get('explanation', '')
            if explanation:
                story.append(Paragraph(f"<b>Объяснение:</b> {explanation}", normal_style))

        story.append(Spacer(1, 0.3*cm))

    # Footer
    story.append(Spacer(1, 1*cm))
    story.append(Paragraph(f"Документ сгенерирован: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}", normal_style))

    # Build PDF
    doc.build(story)

    return str(filepath)


def format_answer_for_pdf(detail):
    """Format user answer for PDF display."""
    question_type = detail.get('type')
    user_answer = detail.get('user_answer')

    if question_type == 'single_choice':
        return f"Вариант {int(user_answer) + 1 if user_answer else 'нет'}"
    elif question_type == 'multiple_choice':
        if isinstance(user_answer, list):
            return f"Варианты: {', '.join(str(int(x) + 1) for x in user_answer)}"
        return "Нет ответа"
    elif question_type == 'ordering':
        if isinstance(user_answer, list):
            return f"Порядок: {', '.join(str(int(x) + 1) for x in user_answer)}"
        return "Нет ответа"
    elif question_type == 'true_false':
        if user_answer == 'true':
            return "Верно"
        elif user_answer == 'false':
            return "Неверно"
        return "Нет ответа"

    return str(user_answer)


def format_correct_answer_for_pdf(detail):
    """Format correct answer for PDF display."""
    question_type = detail.get('type')
    correct_answer = detail.get('correct_answer')

    if question_type == 'single_choice':
        return f"Вариант {int(correct_answer[0]) + 1 if correct_answer else 'нет'}"
    elif question_type == 'multiple_choice':
        if isinstance(correct_answer, list):
            return f"Варианты: {', '.join(str(int(x) + 1) for x in correct_answer)}"
        return "Нет ответа"
    elif question_type == 'ordering':
        if isinstance(correct_answer, list):
            return f"Порядок: {', '.join(str(int(x) + 1) for x in correct_answer)}"
        return "Нет ответа"
    elif question_type == 'true_false':
        if correct_answer == True:
            return "Верно"
        elif correct_answer == False:
            return "Неверно"
        return "Нет ответа"

    return str(correct_answer)
