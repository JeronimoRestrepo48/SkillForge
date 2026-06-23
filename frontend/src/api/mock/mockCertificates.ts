// Mock implementation of certificatesApi for demo mode
import { DEMO_CERTIFICATES } from '../../data/mockData';
import type { Certificate, CertificateVerifyResult } from '../../types/certificates';

const delay = (ms = 300) => new Promise(r => setTimeout(r, ms));

export const mockCertificatesApi = {
  getMyCertificates: async (): Promise<Certificate[]> => {
    await delay(200);
    return DEMO_CERTIFICATES;
  },

  verifyCertificate: async (code: string): Promise<CertificateVerifyResult> => {
    await delay(300);
    const cert = DEMO_CERTIFICATES.find(c => c.codigo_verificacion === code);
    if (cert) {
      return {
        valid: true,
        student_name: cert.student_name,
        course_title: cert.course_title,
        completion_date: cert.fecha_emision,
        issuer: 'SkillForge Academy',
        verification_code: cert.codigo_verificacion,
        status: 'VALID',
        pdf_url: cert.pdf_url,
      };
    }
    return {
      valid: false,
      student_name: '',
      course_title: '',
      completion_date: '',
      issuer: 'SkillForge Academy',
      verification_code: code,
      status: 'NOT_FOUND',
    };
  },

  checkAndIssue: async (_payload: any): Promise<Certificate> => {
    await delay(500);
    return DEMO_CERTIFICATES[0];
  },
};
