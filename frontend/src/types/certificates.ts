export interface Certificate {
  id: number;
  user_id: number;
  course_id: number;
  course_title: string;
  student_name: string;
  numero_certificado: string;
  codigo_verificacion: string;
  fecha_emision: string;
  pdf_url?: string;
  plantilla: string;
}

export interface CertificateVerifyResult {
  valid: boolean;
  student_name: string;
  course_title: string;
  completion_date: string;
  issuer: string;
  verification_code: string;
  status: string;
  pdf_url?: string;
}
