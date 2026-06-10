from framework.contracts.base_controller import BaseController
class HomeController(BaseController):
    def index(self, app, request):
        return app.templates.TemplateResponse(request, "welcome.html")

    def mergepdf(self, app, request):
        return app.templates.TemplateResponse(request, "merge-pdf.html")

    def splitpdf(self, app, request):
        return app.templates.TemplateResponse(request, "split-pdf.html")

    def compresspdf(self, app, request):
        return app.templates.TemplateResponse(request, "compress-pdf.html")

    def wordtopdf(self, app, request):
        return app.templates.TemplateResponse(request, "word-to-pdf.html")

    def wordtopdf_job(self, app, request, job_id):
        return app.templates.TemplateResponse(request, "jobs/word_to_pdf.html", {"job_id": job_id})

    def pdftoword(self, app, request):
        return app.templates.TemplateResponse(request, "pdf-to-word.html")

    def pdftoword_job(self, app, request, job_id):
        return app.templates.TemplateResponse(request, "jobs/pdf-to-word.html", {"job_id": job_id})

    def pdftojpg_job(self, app, request, job_id):
        return app.templates.TemplateResponse(request, "jobs/pdf-to-jpg.html", {"job_id": job_id})

    def pdftoppt(self, app, request):
        return app.templates.TemplateResponse(request, "pdf-to-ppt.html")

    def pdftoppt_job(self, app, request, job_id):
        return app.templates.TemplateResponse(request, "jobs/pdf-to-ppt.html", {"job_id": job_id})

    def pdftoexcel(self, app, request):
        return app.templates.TemplateResponse(request, "pdf-to-excel.html")

    def pdftoexcel_job(self, app, request, job_id):
        return app.templates.TemplateResponse(request, "jobs/pdf-to-excel.html", {"job_id": job_id})

    def jpgtopdf_job(self, app, request, job_id):
        return app.templates.TemplateResponse(request, "jobs/jpg-to-pdf.html", {"job_id": job_id})

    def ppttopdf(self, app, request):
        return app.templates.TemplateResponse(request, "ppt-to-pdf.html")

    def ppttopdf_job(self, app, request, job_id):
        return app.templates.TemplateResponse(request, "jobs/ppt-to-pdf.html", {"job_id": job_id})

    def exceltopdf(self, app, request):
        return app.templates.TemplateResponse(request, "excel-to-pdf.html")

    def exceltopdf_job(self, app, request, job_id):
        return app.templates.TemplateResponse(request, "jobs/excel-to-pdf.html", {"job_id": job_id})

    def redactpdf(self, app, request):
        return app.templates.TemplateResponse(request, "redact-pdf.html")

    def signpdf(self, app, request):
        return app.templates.TemplateResponse(request, "sign-pdf.html")

    def watermark(self, app, request):
        return app.templates.TemplateResponse(request, "watermark.html")

    def protectpdf(self, app, request):
        return app.templates.TemplateResponse(request, "protect-pdf.html")

    def unlockpdf(self, app, request):
        return app.templates.TemplateResponse(request, "unlock-pdf.html")

    def aisummerizer(self, app, request):
        return app.templates.TemplateResponse(request, "ai-summerizer.html")

    def pagenumber(self, app, request):
        return app.templates.TemplateResponse(request, "page-number.html")

    def jpgtopdf(self, app, request):
        return app.templates.TemplateResponse(request, "jpg-to-pdf.html")

    def pdftojpg(self, app, request):
        return app.templates.TemplateResponse(request, "pdf-to-jpg.html")

    def rotatepdf(self, app, request):
        return app.templates.TemplateResponse(request, "rotate-pdf.html")
    def editpdf(self, app, request):
        return app.templates.TemplateResponse(request, "edit-pdf.html")
    def comparepdf(self, app, request):
        return app.templates.TemplateResponse(request, "compare-pdf.html")
    def organizepdf(self, app, request):
        return app.templates.TemplateResponse(request, "organize-pdf.html")

    def scanpdf(self, app, request):
        return app.templates.TemplateResponse(request, "scan-pdf.html")

    def ocrpdf(self, app, request):
        return app.templates.TemplateResponse(request, "ocr-pdf.html")

    def croppdf(self, app, request):
        return app.templates.TemplateResponse(request, "crop-pdf.html")
