import React from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useTranslation } from 'react-i18next';
import { useQuery } from '@tanstack/react-query';
import { catalogApi } from '../api/catalog';
import { Trayectoria } from '../types/catalog';
import { FadeInSection } from '../components/FadeInSection';

const containerVariants = {
  hidden: {},
  show: {
    transition: { staggerChildren: 0.08 }
  }
};

const itemVariants = {
  hidden: { opacity: 0, y: 28 },
  show: { opacity: 1, y: 0, transition: { duration: 0.4, ease: 'easeOut' as const } }
};

export const Trayectorias: React.FC = () => {
  const { t } = useTranslation();
  const { data: trayectorias, isLoading, error } = useQuery<Trayectoria[]>({
    queryKey: ['trayectorias'],
    queryFn: () => catalogApi.getTrayectorias(),
  });

  if (isLoading) {
    return (
      <div className="space-y-8 mt-8">
        <div className="text-center space-y-4 max-w-2xl mx-auto animate-pulse">
          <div className="h-12 bg-zinc-800 rounded-xl w-3/4 mx-auto" />
          <div className="h-4 bg-zinc-800 rounded w-full" />
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <div key={i} className="h-48 bg-zinc-800 rounded-3xl animate-pulse" />
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center p-8 mt-12 bg-red-950/20 border border-red-900/50 rounded-2xl text-red-200">
        {t('trayectorias.error_loading')}
      </div>
    );
  }

  return (
    <div className="space-y-8 mt-8">
      <FadeInSection delay={0}>
        <div className="text-center space-y-4 max-w-2xl mx-auto">
          <h1 className="text-4xl md:text-5xl font-extrabold text-white tracking-tight">
            {t('trayectorias.title_prefix')} <span className="text-primary">{t('trayectorias.title_highlight')}</span>
          </h1>
          <p className="text-text-secondary text-lg">
            {t('trayectorias.subtitle')}
          </p>
        </div>
      </FadeInSection>

      {!trayectorias || trayectorias.length === 0 ? (
        <div className="text-center mt-12 text-text-muted">
          {t('trayectorias.no_available')}
        </div>
      ) : (
        <motion.div
          variants={containerVariants}
          initial="hidden"
          animate="show"
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
        >
          {trayectorias.map((tray) => (
            <motion.div key={tray.id} variants={itemVariants}>
              <motion.div
                whileHover={{ y: -5, boxShadow: '0 0 28px rgba(57,255,20,0.12)' }}
                whileTap={{ scale: 0.98 }}
                transition={{ type: 'spring', stiffness: 280, damping: 22 }}
              >
                <Link
                  to={`/trayectorias/${tray.id}`}
                  className="group block bg-[#111111] border border-zinc-800 rounded-3xl p-6 hover:border-primary/50 hover:shadow-[0_0_30px_-5px_rgba(57,255,20,0.15)] transition-all duration-300"
                >
                  <div className="h-12 w-12 bg-zinc-800 text-primary rounded-2xl flex items-center justify-center text-2xl mb-4 group-hover:scale-110 transition-transform">
                    🚀
                  </div>
                  {tray.categoria_general && (
                    <span className="text-xs font-mono text-primary-light bg-primary/10 px-2 py-1 rounded-md mb-3 inline-block">
                      {tray.categoria_general}
                    </span>
                  )}
                  <h3 className="text-xl font-bold text-white mb-2 group-hover:text-primary transition-colors">
                    {tray.nombre}
                  </h3>
                  <p className="text-text-secondary text-sm line-clamp-3">
                    {tray.descripcion || t('trayectorias.no_description')}
                  </p>
                </Link>
              </motion.div>
            </motion.div>
          ))}
        </motion.div>
      )}
    </div>
  );
};

export default Trayectorias;
