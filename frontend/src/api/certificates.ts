import api from './axios';
import { Certificate, CertificateVerifyResult } from '../types/certificates';

const _realCertificatesApi = {
  // Obtener los certificados del estudiante logueado
  getMyCertificates: async (): Promise<Certificate[]> => {
    const response = await api.get<Certificate[]>('/certificates/my-certificates');
    return response.data;
  },

  // Verificar un certificado públicamente usando su código
  verifyCertificate: async (code: string): Promise<CertificateVerifyResult> => {
    const response = await api.get<CertificateVerifyResult>(`/certificates/verify/${code}`);
    return response.data;
  },

  // Generar o forzar emisión manual si es necesario
  checkAndIssue: async (payload: { user_id: number; course_id: number }): Promise<Certificate> => {
    const response = await api.post<Certificate>('/certificates/check-and-issue', payload);
    return response.data;
  }
};

// ── Demo mode switch ──────────────────────────────────────────────────────────
import { mockCertificatesApi } from './mock/mockCertificates';
const isDemo = import.meta.env.VITE_DEMO_MODE === 'true';
export const certificatesApi = isDemo ? mockCertificatesApi : _realCertificatesApi;
