import React, { useEffect, useState } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import { transactionsApi } from '../api/transactions';
import axios from 'axios';

export const PaymentConfirmation: React.FC = () => {
  const [searchParams] = useSearchParams();
  const transactionId = searchParams.get('id');
  const envParam = searchParams.get('env');
  
  // Para compatibilidad/fallback
  const statusParam = searchParams.get('status');
  const orderParam = searchParams.get('order') || 'SF-XXXX';

  const [loading, setLoading] = useState(!!transactionId);
  const [pollingStatus, setPollingStatus] = useState<string>('Verificando tu pago con Wompi...');
  const [isSuccess, setIsSuccess] = useState<boolean>(statusParam === 'success');
  const [orderNumber, setOrderNumber] = useState<string>(orderParam);
  const [errorDetails, setErrorDetails] = useState<string | null>(null);

  useEffect(() => {
    if (!transactionId) {
      return;
    }

    let isMounted = true;
    let pollInterval: any;

    const checkTransactionStatus = async () => {
      try {
        const wompiBaseUrl = envParam === 'prod' 
          ? 'https://production.wompi.co/v1' 
          : 'https://sandbox.wompi.co/v1';
          
        const response = await axios.get(`${wompiBaseUrl}/transactions/${transactionId}`);
        const transaction = response.data?.data;

        if (!transaction) {
          throw new Error('No se recibió información de la transacción.');
        }

        const { status, reference } = transaction;
        if (reference) {
          setOrderNumber(reference);
        }

        if (status === 'APPROVED') {
          clearInterval(pollInterval);
          if (isMounted) {
            setPollingStatus('¡Pago aprobado! Sincronizando tu matrícula...');
          }
          
          try {
            // Confirmar en el backend para crear inscripciones
            await transactionsApi.returnCheckout({
              order_number: reference,
              result: 'success',
            });
            if (isMounted) {
              setIsSuccess(true);
              setLoading(false);
            }
          } catch (err: any) {
            console.error('Error al sincronizar con el backend:', err);
            if (isMounted) {
              setErrorDetails('El pago fue aprobado por Wompi, pero tuvimos un problema al activar tu curso. Contacta a soporte.');
              setIsSuccess(false);
              setLoading(false);
            }
          }
        } else if (status === 'DECLINED' || status === 'VOIDED' || status === 'ERROR') {
          clearInterval(pollInterval);
          if (isMounted) {
            setPollingStatus('La transacción fue rechazada o cancelada.');
          }
          
          try {
            await transactionsApi.returnCheckout({
              order_number: reference,
              result: 'fail',
            });
          } catch (err) {
            console.error('Error al notificar rechazo al backend:', err);
          }

          if (isMounted) {
            setIsSuccess(false);
            setLoading(false);
          }
        } else if (status === 'PENDING') {
          if (isMounted) {
            setPollingStatus('Tu pago está en proceso de verificación por la pasarela...');
          }
        }
      } catch (error: any) {
        console.error('Error al consultar Wompi:', error);
        clearInterval(pollInterval);
        if (isMounted) {
          setErrorDetails('Error al conectar con la pasarela de pagos.');
          setIsSuccess(false);
          setLoading(false);
        }
      }
    };

    // Consultar inmediatamente y luego cada 2 segundos
    checkTransactionStatus();
    pollInterval = setInterval(checkTransactionStatus, 2000);

    return () => {
      isMounted = false;
      clearInterval(pollInterval);
    };
  }, [transactionId]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[70vh] bg-background-deep text-text-primary">
        <div className="flex flex-col items-center">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary mb-4"></div>
          <p className="text-text-secondary font-medium">{pollingStatus}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex items-center justify-center min-h-[70vh] p-4 text-center">
      <div className="w-full max-w-lg p-8 md:p-12 rounded-3xl glass-effect border border-zinc-800 shadow-2xl relative overflow-hidden">
        {/* Glow de Fondo Púrpura */}
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-64 h-64 bg-primary/10 rounded-full blur-3xl -z-10"></div>

        {isSuccess ? (
          <div className="space-y-6">
            <div className="mx-auto w-20 h-20 rounded-full bg-primary/20 border border-primary/40 flex items-center justify-center text-4xl animate-bounce">
              🎉
            </div>
            
            <div className="space-y-2">
              <h2 className="text-3xl font-extrabold tracking-tight text-white">¡Pago Confirmado!</h2>
              <p className="text-text-secondary text-base">
                Tu orden <span className="font-mono text-primary-light font-bold">{orderNumber}</span> ha sido procesada con éxito.
              </p>
            </div>

            <p className="text-sm text-text-muted max-w-sm mx-auto">
              Tus cursos ya están activos en tu cuenta. Ya puedes acceder al contenido e interactuar con los módulos de aprendizaje.
            </p>

            <div className="flex flex-col sm:flex-row gap-3 justify-center pt-6 border-t border-zinc-900">
              <Link
                to="/dashboard"
                className="px-6 py-3 bg-primary hover:bg-primary-dark text-white font-semibold rounded-xl transition duration-200 text-sm"
              >
                Ir a Mis Cursos
              </Link>
              <Link
                to="/courses"
                className="px-6 py-3 bg-zinc-900 border border-zinc-800 hover:border-zinc-700 text-text-secondary hover:text-white font-semibold rounded-xl transition duration-200 text-sm"
              >
                Seguir Explorando
              </Link>
            </div>
          </div>
        ) : (
          <div className="space-y-6">
            <div className="mx-auto w-20 h-20 rounded-full bg-red-900/20 border border-red-500/40 flex items-center justify-center text-4xl animate-pulse">
              ❌
            </div>
            
            <div className="space-y-2">
              <h2 className="text-3xl font-extrabold tracking-tight text-white">El Pago no pudo procesarse</h2>
              <p className="text-text-secondary text-base">
                {errorDetails || 'La pasarela de pago reportó un error al intentar procesar la transacción.'}
              </p>
            </div>

            <p className="text-sm text-text-muted max-w-sm mx-auto">
              Por favor revisa que tengas fondos disponibles o intenta con otro método de pago.
            </p>

            <div className="flex flex-col sm:flex-row gap-3 justify-center pt-6 border-t border-zinc-900">
              <Link
                to="/cart"
                className="px-6 py-3 bg-primary hover:bg-primary-dark text-white font-semibold rounded-xl transition duration-200 text-sm"
              >
                Reintentar Pago
              </Link>
              <Link
                to="/"
                className="px-6 py-3 bg-zinc-900 border border-zinc-800 hover:border-zinc-700 text-text-secondary hover:text-white font-semibold rounded-xl transition duration-200 text-sm"
              >
                Volver al Home
              </Link>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default PaymentConfirmation;
