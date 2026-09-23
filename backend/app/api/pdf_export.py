from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session
from fpdf import FPDF
from app.database.database import get_db
from app.models.patient import Patient
from app.models.screening import Screening, ModelPrediction, DecisionRecord
from datetime import datetime

router = APIRouter(prefix="/api/patients", tags=["pdf_export"])

class PDFReport(FPDF):
    def header(self):
        self.set_font('helvetica', 'B', 15)
        self.cell(0, 10, 'Drusti: AI-Assisted Diabetic Retinopathy Screening', 0, 1, 'C')
        self.set_font('helvetica', 'I', 10)
        self.cell(0, 10, 'Patient Screening History Report', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('helvetica', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')


@router.get("/{patient_id}/pdf")
def export_patient_pdf(patient_id: int, db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    screenings = db.query(Screening).filter(Screening.patient_id == patient_id).order_by(Screening.created_at.desc()).all()

    pdf = PDFReport()
    pdf.add_page()
    
    # Patient Details
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(0, 10, "Patient Details", 0, 1)
    
    pdf.set_font("helvetica", "", 10)
    pdf.cell(50, 8, f"Name: {patient.name}", 0, 0)
    pdf.cell(50, 8, f"Code: {patient.patient_code}", 0, 1)
    pdf.cell(50, 8, f"Age: {patient.age or 'N/A'}", 0, 0)
    pdf.cell(50, 8, f"Sex: {patient.sex or 'N/A'}", 0, 1)
    pdf.cell(100, 8, f"Diabetes Status: {patient.diabetes_status or 'N/A'}", 0, 1)
    pdf.ln(10)

    # Screening History Table
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(0, 10, "Screening History", 0, 1)
    
    if not screenings:
        pdf.set_font("helvetica", "I", 10)
        pdf.cell(0, 10, "No screenings recorded.", 0, 1)
    else:
        # Table Header
        pdf.set_font("helvetica", "B", 10)
        pdf.cell(40, 10, "Date", 1, 0, "C")
        pdf.cell(30, 10, "Eye", 1, 0, "C")
        pdf.cell(60, 10, "Prediction", 1, 0, "C")
        pdf.cell(40, 10, "Decision", 1, 1, "C")
        
        # Table Content
        pdf.set_font("helvetica", "", 9)
        for s in screenings:
            date_str = s.created_at.strftime("%Y-%m-%d %H:%M") if s.created_at else "N/A"
            eye = s.eye_side.capitalize() if s.eye_side else "Unknown"
            
            pred = db.query(ModelPrediction).filter(ModelPrediction.screening_id == s.id).first()
            pred_label = pred.predicted_label if pred else "Pending"
            
            dec = db.query(DecisionRecord).filter(DecisionRecord.screening_id == s.id).first()
            dec_label = dec.decision.capitalize() if dec else "Pending"
            
            pdf.cell(40, 10, date_str, 1, 0, "C")
            pdf.cell(30, 10, eye, 1, 0, "C")
            pdf.cell(60, 10, pred_label, 1, 0, "C")
            pdf.cell(40, 10, dec_label, 1, 1, "C")

    # FPDF2 output() without arguments returns a bytearray
    pdf_bytes = bytes(pdf.output())
    
    filename = f"Drusti_Report_{patient.patient_code}.pdf"
    
    return Response(
        content=pdf_bytes, 
        media_type="application/pdf", 
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
