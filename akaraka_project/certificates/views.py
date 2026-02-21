from django.shortcuts import render, get_object_or_404
from django.views.generic import View, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import FileResponse, HttpResponse
from django.template.loader import render_to_string
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
import uuid
from .models import Certificate, CertificateTemplate
from courses.models import Course


class MyCertificatesView(LoginRequiredMixin, ListView):
    """User's earned certificates"""
    model = Certificate
    template_name = 'certificates/my_certificates.html'
    context_object_name = 'certificates'
    paginate_by = 10
    
    def get_queryset(self):
        return Certificate.objects.filter(user=self.request.user).select_related('course')


class CertificateDetailView(LoginRequiredMixin, View):
    """View certificate details"""
    def get(self, request, certificate_id):
        certificate = get_object_or_404(Certificate, id=certificate_id, user=request.user)
        context = {
            'certificate': certificate,
            'verification_url': certificate.get_verification_url(),
        }
        return render(request, 'certificates/certificate_detail.html', context)


class DownloadCertificateView(LoginRequiredMixin, View):
    """Download certificate as PDF"""
    def get(self, request, certificate_id):
        certificate = get_object_or_404(Certificate, id=certificate_id, user=request.user)
        
        if certificate.pdf_file:
            return FileResponse(certificate.pdf_file.open('rb'), as_attachment=True, filename=f'{certificate.certificate_number}.pdf')
        
        # Generate PDF if not exists
        return self.generate_pdf(certificate)
    
    def generate_pdf(self, certificate):
        """Generate PDF certificate"""
        from io import BytesIO
        from reportlab.lib.units import inch
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib import colors
        from datetime import datetime
        
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=1*inch, bottomMargin=1*inch)
        elements = []
        
        # Title
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=36,
            textColor=colors.HexColor('#1e40af'),
            spaceAfter=30,
            alignment=1,
        )
        
        elements.append(Paragraph("Certificate of Completion", title_style))
        elements.append(Spacer(1, 0.2*inch))
        
        # Body
        body_text = f"""
        This is to certify that<br/>
        <b>{certificate.user.get_full_name()}</b><br/>
        has successfully completed the<br/>
        <b>{certificate.course.title}</b> course<br/>
        on {certificate.issue_date.strftime('%B %d, %Y')}<br/>
        <br/>
        Certificate Number: {certificate.certificate_number}
        """
        
        elements.append(Paragraph(body_text, styles['Normal']))
        elements.append(Spacer(1, 0.5*inch))
        
        # Build PDF
        doc.build(elements)
        buffer.seek(0)
        
        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{certificate.certificate_number}.pdf"'
        return response


class VerifyCertificateView(View):
    """Verify certificate authenticity"""
    def get(self, request, verification_code):
        certificate = get_object_or_404(Certificate, verification_code=verification_code)
        context = {
            'certificate': certificate,
            'user': certificate.user,
            'is_valid': True,
        }
        return render(request, 'certificates/verify_certificate.html', context)


class GenerateCertificateView(LoginRequiredMixin, View):
    """Generate certificate on course completion"""
    def post(self, request, course_id):
        course = get_object_or_404(Course, id=course_id)
        user = request.user
        
        # Check if user completed the course
        lesson_progress = user.lesson_progress.filter(lesson__course=course, is_completed=True)
        total_lessons = course.lessons.count()
        
        if lesson_progress.count() < total_lessons:
            return HttpResponse('Course not completed yet', status=400)
        
        # Generate certificate
        certificate, created = Certificate.objects.get_or_create(
            user=user,
            course=course,
            defaults={
                'certificate_number': f'CERT-{uuid.uuid4().hex[:8].upper()}',
                'verification_code': uuid.uuid4().hex,
                'score': 100,
            }
        )
        
        return redirect('certificates:download', certificate_id=certificate.id)
