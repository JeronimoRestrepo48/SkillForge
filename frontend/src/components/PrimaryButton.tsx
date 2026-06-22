import React from 'react';
import { motion } from 'framer-motion';

interface PrimaryButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  children: React.ReactNode;
  className?: string;
}

export const PrimaryButton: React.FC<PrimaryButtonProps> = ({
  children,
  className = '',
  ...props
}) => {
  return (
    <motion.button
      whileTap={{ scale: 0.96 }}
      transition={{ type: 'spring', stiffness: 400, damping: 25 }}
      className={`px-6 py-2.5 bg-primary hover:bg-primary-dark text-black font-semibold rounded-xl text-sm disabled:opacity-50 transition ${className}`}
      {...(props as any)}
    >
      {children}
    </motion.button>
  );
};

export default PrimaryButton;
