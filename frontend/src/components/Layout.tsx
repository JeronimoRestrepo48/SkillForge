import React, { Suspense } from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { AnimatePresence, motion } from 'framer-motion';
import Navbar from './Navbar';
import { PageLoader } from './PageLoader';

const PageWrapper = ({ children }: { children: React.ReactNode }) => (
  <motion.div
    initial={{ opacity: 0, y: 16 }}
    animate={{ opacity: 1, y: 0 }}
    exit={{ opacity: 0, y: -8 }}
    transition={{ duration: 0.25, ease: 'easeOut' }}
  >
    {children}
  </motion.div>
);

export const Layout: React.FC = () => {
  const location = useLocation();
  const { t } = useTranslation();

  return (
    <div className="min-h-screen bg-background-deep text-text-primary flex flex-col font-sans">
      <Navbar />
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 py-8">
        <Suspense fallback={<PageLoader />}>
          <AnimatePresence mode="wait">
            <PageWrapper key={location.pathname}>
              <Outlet />
            </PageWrapper>
          </AnimatePresence>
        </Suspense>
      </main>
      <footer className="border-t border-zinc-800/50 py-6 text-center text-xs text-text-muted mt-auto">
        &copy; {new Date().getFullYear()} SkillForge. {t('common.rights')}
      </footer>
    </div>
  );
};

export default Layout;
