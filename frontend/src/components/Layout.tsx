import React from 'react';
import { Outlet } from 'react-router-dom';
import Navbar from './Navbar';

export const Layout: React.FC = () => {
  return (
    <div className="min-h-screen bg-background-deep text-text-primary flex flex-col font-sans">
      <Navbar />
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 py-8">
        <Outlet />
      </main>
      <footer className="border-t border-zinc-800/50 py-6 text-center text-xs text-text-muted mt-auto">
        &copy; {new Date().getFullYear()} SkillForge. Todos los derechos reservados.
      </footer>
    </div>
  );
};

export default Layout;
