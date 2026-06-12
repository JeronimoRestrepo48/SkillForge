import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { certificatesApi } from '../api/certificates';
import { CertificateVerifyResult } from '../types/certificates';

export const CertificateVerify: React.FC = () => {
  const { uuid } = useParams<{ uuid: string }>();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [cert, setCert] = useState<CertificateVerifyResult | null>(null);

  useEffect(() => {
    if (!uuid) {
      setError('Código de verificación no especificado.');
      setLoading(false);
      return;
    }

    const fetchVerification = async () => {
      try {
        setLoading(true);
        setError(null);
        const result = await certificatesApi.verifyCertificate(uuid);
        setCert(result);
      } catch (err: any) {
        console.error('Error verifying certificate:', err);
        setError(
          err.response?.data?.detail || 
          'No se pudo verificar el certificado. Código inválido o error en el servidor.'
        );
      } finally {
        setLoading(false);
      }
    };

    fetchVerification();
  }, [uuid]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[70vh] bg-background-deep text-text-primary">
        <div className="flex flex-col items-center">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary mb-4"></div>
          <p className="text-text-secondary font-medium">Validando firma criptográfica del certificado...</p>
        </div>
      </div>
    );
  }

  if (error || !cert) {
    return (
      <div className="flex items-center justify-center min-h-[70vh] p-4 text-center">
        <div className="w-full max-w-2xl p-8 md:p-12 rounded-3xl glass-effect border border-zinc-800 shadow-2xl relative">
          <div className="absolute top-0 left-1/2 -translate-x-1/2 w-64 h-64 bg-red-900/10 rounded-full blur-3xl -z-10"></div>
          <div className="space-y-6">
            <div className="mx-auto w-20 h-20 rounded-full bg-red-900/20 border border-red-500/40 flex items-center justify-center text-4xl animate-pulse">
              ⚠️
            </div>
            <div className="space-y-2">
              <h2 className="text-3xl font-extrabold tracking-tight text-white">Certificado No Acreditado</h2>
              <p className="text-text-secondary text-base">
                {error || 'El código de verificación proporcionado no coincide con ningún registro oficial.'}
              </p>
            </div>
            <div className="pt-4 border-t border-zinc-900">
              <Link
                to="/"
                className="px-6 py-2.5 bg-zinc-900 border border-zinc-800 hover:border-zinc-700 text-xs font-semibold rounded-xl text-text-secondary hover:text-white transition"
              >
                Volver al Home
              </Link>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex items-center justify-center min-h-[70vh] p-4 text-center">
      <div className="w-full max-w-2xl p-8 md:p-12 rounded-3xl glass-effect border border-zinc-800 shadow-2xl relative">
        {/* Glow */}
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-64 h-64 bg-primary/10 rounded-full blur-3xl -z-10"></div>

        <div className="space-y-8">
          {/* Cabecera */}
          <div className="space-y-2">
            <span className="text-[10px] font-mono font-bold text-emerald-400 bg-emerald-950/20 px-3 py-1 rounded-full border border-emerald-500/20">
              🛡️ Criptografía Válida
            </span>
            <h2 className="text-3xl font-extrabold tracking-tight text-white mt-4">Verificación de Certificado</h2>
            <p className="text-xs text-text-muted font-mono truncate max-w-md mx-auto">
              Código de verificación: {cert.verification_code}
            </p>
          </div>

          {/* Ficha técnica del Certificado */}
          <div className="border border-zinc-800 bg-background-dark/50 rounded-2xl p-6 text-left space-y-4 max-w-md mx-auto">
            <div className="flex justify-between border-b border-zinc-850 pb-2.5 text-xs text-text-secondary">
              <span>Estudiante</span>
              <strong className="text-white">{cert.student_name}</strong>
            </div>

            <div className="flex justify-between border-b border-zinc-850 pb-2.5 text-xs text-text-secondary">
              <span>Curso acreditado</span>
              <strong className="text-white">{cert.course_title}</strong>
            </div>

            <div className="flex justify-between border-b border-zinc-850 pb-2.5 text-xs text-text-secondary">
              <span>Fecha de egreso</span>
              <strong className="text-white">{cert.completion_date}</strong>
            </div>

            <div className="flex justify-between border-b border-zinc-850 pb-2.5 text-xs text-text-secondary">
              <span>Entidad emisora</span>
              <strong className="text-white">{cert.issuer}</strong>
            </div>

            <div className="flex justify-between text-xs text-text-secondary pt-2">
              <span>Estado</span>
              <strong className="text-emerald-400 font-bold">✅ {cert.status}</strong>
            </div>
          </div>

          <p className="text-xs text-text-muted max-w-sm mx-auto">
            Este certificado fue emitido tras completar todas las evaluaciones académicas requeridas en SkillForge. La firma digital ha sido validada contra nuestra base de datos oficial.
          </p>

          <div className="flex flex-col sm:flex-row justify-center gap-3 pt-4 border-t border-zinc-900">
            {cert.pdf_url && (
              <a
                href={cert.pdf_url}
                target="_blank"
                rel="noopener noreferrer"
                className="px-6 py-2.5 bg-primary hover:bg-primary-dark text-xs font-semibold rounded-xl text-white transition text-center"
              >
                📄 Descargar Certificado (PDF)
              </a>
            )}
            <Link
              to="/"
              className="px-6 py-2.5 bg-zinc-900 border border-zinc-800 hover:border-zinc-700 text-xs font-semibold rounded-xl text-text-secondary hover:text-white transition text-center"
            >
              Ir al Portal de SkillForge
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CertificateVerify;
