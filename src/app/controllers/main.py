from flask import Blueprint, render_template, redirect, url_for, g, request, flash, send_file, send_from_directory, current_app
from src.app import db
from src.app.models import Exam, Subject, Question, Result, Center
from .auth import login_required

import io
import os
import random
import uuid

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors

bp = Blueprint('main', __name__)

@bp.route('/uploads/<path:filename>')
@login_required
def uploads(filename):
    return send_from_directory(current_app.instance_path, filename)

@bp.route('/dashboard')
@login_required
def dashboard():
    exams = Exam.query.all()
    history = Result.query.filter_by(user_id=g.user.id).order_by(Result.created_at.desc()).all()
    return render_template('student/dashboard.html', exams=exams, history=history)

@bp.route('/setup/<int:exam_id>')
@login_required
def exam_setup(exam_id):
    exam = Exam.query.get_or_404(exam_id)
    subjects = Subject.query.filter_by(exam_id=exam.id).all()
    return render_template('student/setup.html', exam=exam, subjects=subjects)

@bp.route('/take-exam', methods=['POST'])
@login_required
def take_exam():
    exam_id = request.form.get('exam_id')
    selected_ids = request.form.getlist('subjects')

    exam = Exam.query.get_or_404(exam_id)

    if not selected_ids:
        flash("Please select subjects.", "warning")
        return redirect(url_for('main.exam_setup', exam_id=exam.id))

    # Enforce EXACT subject count (JAMB = 4, etc.)
    try:
        required = int(getattr(exam, "required_subjects", 1) or 1)
    except Exception:
        required = 1

    if len(selected_ids) != required:
        flash(f"Select exactly {required} subjects to start.", "warning")
        return redirect(url_for('main.exam_setup', exam_id=exam.id))

    g.user.is_writing = True
    db.session.commit()

    exam_data = {}
    for sid in selected_ids:
        sub = Subject.query.get_or_404(int(sid))

        qs = Question.query.filter_by(subject_id=sub.id).all()

        # Apply per-subject question limit
        try:
            limit = int(getattr(sub, 'question_limit', 50) or 50)
        except Exception:
            limit = 50
        if limit < 1:
            limit = 1

        random.shuffle(qs)
        qs = qs[:min(len(qs), limit)]

        sub_items = []
        for q in qs:
            opts = [
                {'key': 'A', 'text': q.option_a},
                {'key': 'B', 'text': q.option_b},
                {'key': 'C', 'text': q.option_c},
                {'key': 'D', 'text': q.option_d},
            ]
            random.shuffle(opts)
            sub_items.append({'q': q, 'opts': opts})
        exam_data[sub.name] = sub_items

    return render_template('student/war_room.html', exam_data=exam_data, exam=exam)

@bp.route('/submit-exam', methods=['POST'])
@login_required
def submit_exam():
    # Grade ALL questions displayed (including skipped ones => 0 mark)
    score = 0
    total = 0
    results_list = []

    # war_room.html now sends all shown question ids using hidden inputs all_q_ids
    all_q_ids = request.form.getlist('all_q_ids')

    # Fallback: old behavior (counts only answered) if hidden list is missing
    if not all_q_ids:
        for key, value in request.form.items():
            if key.startswith('q_'):
                q_id = int(key.split('_')[1])
                all_q_ids.append(str(q_id))

    # Deduplicate while keeping order
    seen = set()
    ordered_ids = []
    for x in all_q_ids:
        if x and x not in seen:
            seen.add(x)
            ordered_ids.append(x)

    for qid_str in ordered_ids:
        try:
            q_id = int(qid_str)
        except Exception:
            continue

        q = Question.query.get(q_id)
        if not q:
            continue

        total += 1
        user_answer = request.form.get(f"q_{q_id}")  # None means skipped
        is_correct = (user_answer is not None) and (q.correct_option == user_answer)

        if is_correct:
            score += 1

        results_list.append({
            'question_text': q.text,
            'user_answer': user_answer or "-",   # show '-' for skipped
            'correct_answer': q.correct_option,
            'is_correct': is_correct,
            'explanation': q.explanation
        })

    # Save result
    exam_name = request.form.get('exam_name') or "Exam"
    new_result = Result(
        user_id=g.user.id,
        center_id=g.user.center_id,
        exam_name=exam_name,
        score=float(score),
        total_questions=int(total)
    )

    g.user.is_writing = False
    db.session.add(new_result)
    db.session.commit()

    results_data = {
        'id': new_result.id,
        'score': score,
        'total_questions': total,
        'subject_name': exam_name,
        'results_list': results_list
    }
    return render_template('student/results.html', results=results_data)

@bp.route('/download-result/<int:result_id>')
@login_required
def download_result(result_id):
    """
    If the result has attempt_id, we generate a multi-subject slip (JAMB style).
    Otherwise fallback to single row slip.
    """
    result = Result.query.get_or_404(result_id)
    if result.user_id != g.user.id and g.user.role not in ['superadmin', 'centeradmin']:
        return "Unauthorized", 403

    # center name best-effort
    center_name = "N/A"
    try:
        if result.center_id:
            c = Center.query.get(result.center_id)
            if c and getattr(c, "name", ""):
                center_name = c.name
    except Exception:
        pass

    rows = [result]
    if result.attempt_id:
        rows = Result.query.filter_by(user_id=result.user_id, attempt_id=result.attempt_id).all()
        rows.sort(key=lambda r: (r.subject_name or ""))

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Header
    p.setFont("Helvetica-Bold", 20)
    p.drawString(50, height - 50, "EXAM ARENA - RESULT SLIP")

    p.setFont("Helvetica", 11)
    p.drawString(50, height - 78, f"Candidate: {result.user.username}")
    p.drawString(50, height - 95, f"Center: {center_name}")
    p.drawString(50, height - 112, f"Exam: {result.exam_name or 'N/A'}")
    p.drawString(50, height - 129, f"Date: {result.created_at.strftime('%Y-%m-%d %H:%M')}")

    # Table
    y = height - 165
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y, "Subject")
    p.drawString(320, y, "Score")
    p.line(50, y - 4, width - 50, y - 4)
    y -= 22

    total_score = 0
    total_q = 0

    p.setFont("Helvetica", 12)
    for r in rows:
        sname = r.subject_name or "N/A"
        sc = int(r.score or 0)
        tq = int(r.total_questions or 0)
        total_score += sc
        total_q += tq
        p.drawString(50, y, sname)
        p.drawString(320, y, f"{sc} / {tq}")
        y -= 18
        if y < 90:
            p.showPage()
            y = height - 80

    y -= 8
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y, "TOTAL")
    p.drawString(320, y, f"{total_score} / {total_q}")

    # Pass/Fail
    y -= 45
    pct = (total_score / total_q * 100) if total_q else 0
    p.setFont("Helvetica-Bold", 34)
    if pct >= 50:
        p.setFillColor(colors.green)
        p.drawString(50, y, "PASSED")
    else:
        p.setFillColor(colors.red)
        p.drawString(50, y, "FAILED")

    p.setFillColor(colors.black)
    p.setFont("Helvetica", 9)
    p.drawString(50, 45, "Generated by Exam Arena CBT Practice (Offline). For practice use only.")

    p.showPage()
    p.save()
    buffer.seek(0)

    return send_file(buffer, as_attachment=True, download_name=f"Result_{result.user.username}_{result.id}.pdf", mimetype='application/pdf')
