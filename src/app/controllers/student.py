from flask import Blueprint, render_template, session, g, make_response, redirect, url_for
from src.app.models import Result, User, Exam
from src.app import db
import weasyprint

bp = Blueprint('student', __name__, url_prefix='/student')

@bp.before_request
def check_student_auth():
    if g.user is None:
        return redirect(url_for('auth.login'))

@bp.route('/dashboard')
def dashboard():
    return render_template('student/dashboard.html')

@bp.route('/result/download/<int:result_id>')
def download_result_slip(result_id):
    result = Result.query.get_or_404(result_id)
    student = User.query.get(result.user_id)
    exam = Exam.query.get(result.exam_id)
    
    html = render_template('pdf/result_slip.html', result=result, student=student, exam=exam)
    pdf = weasyprint.HTML(string=html).write_pdf()
    
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=Result_Slip_{student.username}.pdf'
    return response
