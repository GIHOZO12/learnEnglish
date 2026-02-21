from django.urls import path
from .views import (
    MyCertificatesView, CertificateDetailView, DownloadCertificateView,
    VerifyCertificateView, GenerateCertificateView
)

app_name = 'certificates'

urlpatterns = [
    path('my-certificates/', MyCertificatesView.as_view(), name='my_certificates'),
    path('<int:certificate_id>/', CertificateDetailView.as_view(), name='certificate_detail'),
    path('<int:certificate_id>/download/', DownloadCertificateView.as_view(), name='download'),
    path('verify/<str:verification_code>/', VerifyCertificateView.as_view(), name='verify'),
    path('generate/<int:course_id>/', GenerateCertificateView.as_view(), name='generate'),
]
