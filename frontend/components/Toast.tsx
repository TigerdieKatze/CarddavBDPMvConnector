import React from 'react';
import { X } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

type ToastProps = {
  message: string;
  type: 'success' | 'error';
  onClose: () => void;
};

export const Toast: React.FC<ToastProps> = ({ message, type, onClose }) => {
  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0, y: 50 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: 50 }}
        transition={{ duration: 0.3 }}
        className={`fixed bottom-4 right-4 p-4 rounded-md shadow-md ${type === 'success' ? 'bg-green-500' : 'bg-red-500'} text-white flex items-center justify-between z-50`}
      >
        <span>{message}</span>
        <button onClick={onClose} className="ml-4 text-white hover:text-gray-200 transition-colors duration-200">
          <X size={18} />
        </button>
      </motion.div>
    </AnimatePresence>
  );
};