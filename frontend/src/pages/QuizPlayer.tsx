import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { catalogApi } from '../api/catalog';
import { certificatesApi } from '../api/certificates';
import { QuizAttemptSubmit, QuizAttemptSubmitItem, QuizAttemptResultOut, QuizDetailOut } from '../types/catalog';
import { useAuth } from '../context/AuthContext';
import { useCourseProgressQuery } from '../hooks/useCourses';

export const QuizPlayer: React.FC = () => {
  const { t } = useTranslation();
  const { courseId, lessonId } = useParams<{ courseId: string; lessonId: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { user } = useAuth();
  
  useCourseProgressQuery(Number(courseId));

  // Load Quiz Details
  const {
    data: quizData,
    isLoading: isQuizLoading,
    error: quizError,
  } = useQuery<QuizDetailOut>({
    queryKey: ['quiz', lessonId],
    queryFn: () => catalogApi.getQuizDetails(Number(lessonId)),
    retry: false,
  });

  // Load Previous Attempts
  const {
    data: previousAttempts,
    isLoading: isAttemptsLoading,
    refetch: refetchAttempts,
  } = useQuery<QuizAttemptResultOut[]>({
    queryKey: ['quizAttempts', quizData?.id],
    queryFn: () => catalogApi.getQuizAttempts(quizData!.id),
    enabled: !!quizData?.id,
    retry: false,
  });

  const [answers, setAnswers] = useState<Record<number, QuizAttemptSubmitItem>>({});
  const [currentResult, setCurrentResult] = useState<QuizAttemptResultOut | null>(null);
  const [attemptError, setAttemptError] = useState<string | null>(null);

  const submitMutation = useMutation({
    mutationFn: (submitData: QuizAttemptSubmit) => catalogApi.submitQuizAttempt(quizData!.id, submitData),
    onSuccess: (result) => {
      setCurrentResult(result);
      refetchAttempts();
      setAttemptError(null);
      
      // Invalidate course progress to refresh it
      queryClient.invalidateQueries({ queryKey: ['courseProgress', Number(courseId)] }).then(() => {
        // After invalidating, fetch the new progress manually to see if it's 100%
        catalogApi.getCourseProgress(Number(courseId)).then((newProgress) => {
          if (newProgress.completed && user?.id) {
            certificatesApi.checkAndIssue({ user_id: user.id, course_id: Number(courseId) })
              .catch(err => console.error('Error generating certificate:', err));
          }
        });
      });
    },
    onError: (err: any) => {
      if (err.response?.status === 403) {
        setAttemptError(t('quiz.locked'));
      } else {
        setAttemptError(err.response?.data?.detail || 'Ocurrió un error al enviar las respuestas.');
      }
    },
  });

  if (isQuizLoading || isAttemptsLoading) {
    return (
      <div className="flex items-center justify-center min-h-[50vh]">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (quizError || !quizData) {
    return (
      <div className="max-w-3xl mx-auto mt-12 p-8 text-center bg-[#111111] rounded-3xl border border-zinc-800 shadow-2xl glass-effect">
        <h2 className="text-2xl font-bold text-red-500 mb-2">Error</h2>
        <p className="text-text-secondary">
          No se pudo cargar el quiz. {(quizError as any)?.response?.data?.detail}
        </p>
        <button
          onClick={() => navigate(`/courses/${courseId}`)}
          className="mt-6 inline-block px-6 py-3 bg-zinc-800 hover:bg-zinc-700 text-white rounded-xl font-semibold transition"
        >
          {t('quiz.back_to_course')}
        </button>
      </div>
    );
  }

  const handleOptionChange = (questionId: number, optionId: number) => {
    setAnswers((prev) => ({
      ...prev,
      [questionId]: { question_id: questionId, selected_option_id: optionId },
    }));
  };

  const handleTextChange = (questionId: number, text: string) => {
    setAnswers((prev) => ({
      ...prev,
      [questionId]: { question_id: questionId, respuesta_texto: text },
    }));
  };

  const isFormComplete = quizData.questions.every(
    (q) => answers[q.id] && (answers[q.id].selected_option_id !== undefined || !!answers[q.id].respuesta_texto?.trim())
  );

  const handleSubmit = () => {
    const submitData: QuizAttemptSubmit = {
      respuestas: Object.values(answers),
    };
    submitMutation.mutate(submitData);
  };

  if (attemptError && attemptError.includes('aprobar el examen del módulo anterior')) {
    return (
      <div className="max-w-3xl mx-auto mt-12 p-8 text-center bg-red-950/20 rounded-3xl border border-red-900/50 shadow-2xl">
        <div className="text-5xl mb-4">🔒</div>
        <h2 className="text-2xl font-bold text-red-400 mb-2">Módulo Bloqueado</h2>
        <p className="text-red-200/80 mb-6">{attemptError}</p>
        <button
          onClick={() => navigate(`/courses/${courseId}`)}
          className="px-6 py-3 bg-zinc-800 hover:bg-zinc-700 text-white rounded-xl font-semibold transition"
        >
          {t('quiz.back_to_course')}
        </button>
      </div>
    );
  }

  if (currentResult) {
    const isApproved = currentResult.aprobado;
    return (
      <div className="max-w-4xl mx-auto mt-8 mb-16 space-y-8 px-4">
        <div className="bg-[#111111] rounded-3xl border border-zinc-800 shadow-2xl overflow-hidden glass-effect p-8">
          <div className="text-center space-y-4 mb-8">
            <h1 className="text-3xl font-extrabold text-white">Resultados del Quiz</h1>
            <div className={`text-2xl font-bold ${isApproved ? 'text-primary' : 'text-red-500'}`}>
              {isApproved ? `✅ ${t('quiz.approved')}` : `❌ ${t('quiz.failed')}`}
            </div>
            <p className="text-lg text-text-secondary">
              Obtuviste <span className="font-bold text-white">{currentResult.puntaje_obtenido}</span> de {currentResult.puntaje_maximo} puntos ({currentResult.porcentaje}%)
            </p>
          </div>

          <div className="space-y-6">
            {currentResult.answers.map((ans) => {
              const question = quizData.questions.find((q) => q.id === ans.question_id);
              if (!question) return null;

              if (question.tipo === 'OPCION_MULTIPLE') {
                const isCorrect = ans.puntaje_obtenido > 0;
                return (
                  <div key={ans.question_id} className={`p-4 rounded-xl border ${isCorrect ? 'border-primary/50 bg-primary/10' : 'border-red-500/50 bg-red-500/10'}`}>
                    <p className="text-white font-medium mb-2">{question.enunciado}</p>
                    <div className="flex items-center gap-2">
                      <span className="text-xl">{isCorrect ? '✅' : '❌'}</span>
                      <span className="text-sm text-text-secondary">
                        {isCorrect ? t('quiz.correct') : t('quiz.incorrect')}
                      </span>
                    </div>
                  </div>
                );
              } else {
                let badgeColor = 'bg-red-500/20 text-red-400 border-red-500/30';
                let label = t('quiz.incorrect');
                const similitud = ans.similitud || 0;
                if (similitud >= 75) {
                  badgeColor = 'bg-primary/20 text-primary border-primary/30';
                  label = t('quiz.correct');
                } else if (similitud >= 60) {
                  badgeColor = 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30';
                  label = t('quiz.partial');
                }

                return (
                  <div key={ans.question_id} className="p-4 rounded-xl border border-zinc-800 bg-zinc-900/50">
                    <p className="text-white font-medium mb-2">{question.enunciado}</p>
                    <div className="text-sm text-text-secondary italic mb-3">
                      Tu respuesta: "{ans.respuesta_texto}"
                    </div>
                    <div className="flex items-center gap-3">
                      <span className={`px-3 py-1 text-xs font-bold rounded-full border ${badgeColor}`}>
                        {label}
                      </span>
                      <span className="text-sm font-mono text-text-muted">{t('quiz.similarity')}: {similitud}%</span>
                    </div>
                  </div>
                );
              }
            })}
          </div>

          <div className="mt-8 flex justify-end gap-4">
            <button
              onClick={() => {
                setCurrentResult(null);
                setAnswers({});
              }}
              className="px-6 py-2 bg-zinc-800 hover:bg-zinc-700 text-white rounded-xl text-sm font-semibold transition"
            >
              {t('quiz.retry')}
            </button>
            <button
              onClick={() => navigate(`/courses/${courseId}`)}
              className="px-6 py-2 bg-primary hover:bg-primary-dark text-white rounded-xl text-sm font-semibold transition"
            >
              {t('quiz.back_to_course')}
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto mt-8 mb-16 space-y-8 px-4">
      {/* Quiz Form */}
      <div className="bg-[#111111] rounded-3xl border border-zinc-800 shadow-2xl overflow-hidden glass-effect p-8">
        <h1 className="text-3xl font-extrabold text-white mb-2">{quizData.titulo}</h1>
        <p className="text-text-secondary mb-8">Puntaje mínimo para aprobar: <span className="font-bold text-white">{quizData.puntaje_minimo_aprobacion}%</span></p>

        {attemptError && (
          <div className="mb-6 p-4 bg-red-950/50 border border-red-900 rounded-xl text-red-200">
            {attemptError}
          </div>
        )}

        <div className="space-y-8">
          {quizData.questions.map((question, index) => (
            <div key={question.id} className="space-y-4">
              <h3 className="text-lg font-bold text-white">
                <span className="text-primary-light mr-2">{index + 1}.</span>
                {question.enunciado}
              </h3>

              {question.tipo === 'OPCION_MULTIPLE' ? (
                <div className="space-y-2 pl-6">
                  {question.options?.map((opt) => (
                    <label key={opt.id} className="flex items-center gap-3 text-text-secondary hover:text-white cursor-pointer group">
                      <div className={`w-5 h-5 rounded-full border-2 flex items-center justify-center transition-colors ${answers[question.id]?.selected_option_id === opt.id ? 'border-primary' : 'border-zinc-600 group-hover:border-zinc-400'}`}>
                        {answers[question.id]?.selected_option_id === opt.id && <div className="w-2.5 h-2.5 rounded-full bg-primary" />}
                      </div>
                      <input
                        type="radio"
                        name={`question-${question.id}`}
                        className="hidden"
                        checked={answers[question.id]?.selected_option_id === opt.id}
                        onChange={() => handleOptionChange(question.id, opt.id)}
                      />
                      <span>{opt.texto}</span>
                    </label>
                  ))}
                </div>
              ) : (
                <div className="pl-6">
                  <textarea
                    rows={4}
                    className="w-full bg-zinc-900/50 border border-zinc-800 rounded-xl p-4 text-white focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition resize-none placeholder-zinc-600"
                    placeholder="Escribe tu respuesta aquí..."
                    value={answers[question.id]?.respuesta_texto || ''}
                    onChange={(e) => handleTextChange(question.id, e.target.value)}
                  />
                </div>
              )}
            </div>
          ))}
        </div>

        <div className="mt-10 flex justify-between items-center border-t border-zinc-800/50 pt-6">
          <button
            onClick={() => navigate(`/courses/${courseId}`)}
            className="px-6 py-3 bg-zinc-800 hover:bg-zinc-700 text-white rounded-xl text-sm font-semibold transition"
          >
            {t('quiz.back_to_course')}
          </button>
          
          <button
            onClick={handleSubmit}
            disabled={!isFormComplete || submitMutation.isPending}
            className="px-8 py-3 bg-primary hover:bg-primary-dark text-white rounded-xl text-sm font-semibold transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
          >
            {submitMutation.isPending ? 'Enviando...' : t('quiz.submit')}
          </button>
        </div>
      </div>

      {/* History */}
      {previousAttempts && previousAttempts.length > 0 && (
        <div className="bg-[#111111] rounded-2xl border border-zinc-800 p-6 shadow-xl">
          <h3 className="text-xl font-bold text-white mb-4">{t('quiz.history')}</h3>
          <div className="space-y-3">
            {previousAttempts.map((attempt, index) => (
              <div key={attempt.id} className="flex justify-between items-center p-4 bg-zinc-900/50 rounded-xl border border-zinc-800">
                <div>
                  <span className="font-bold text-white">Intento {previousAttempts.length - index}</span>
                  <span className="text-text-muted text-sm ml-2">({new Date(attempt.created_at).toLocaleDateString()})</span>
                </div>
                <div className="flex items-center gap-4">
                  <span className="font-mono text-sm text-text-secondary">{attempt.porcentaje}%</span>
                  <span className={`px-2 py-1 text-xs font-bold rounded-md ${attempt.aprobado ? 'bg-primary/20 text-primary' : 'bg-zinc-800 text-zinc-400'}`}>
                    {attempt.aprobado ? t('quiz.approved') : t('quiz.failed')}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default QuizPlayer;
