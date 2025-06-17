// .src/components/Modal.jsx
// Purpose: A reusable modal component for the UpNest application. Used for displaying alerts, confirmations, and other important messages.

import React from "react";

const Modal = ({ isOpen, title, children, onClose }) => {
  if (!isOpen) return null;
  return (
    <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
      <div className="bg-surface rounded-2xl shadow-lg p-6 w-full max-w-md">
        <div className="mb-4 text-lg font-bold">{title}</div>
        <div>{children}</div>
        <button onClick={onClose} className="mt-4 text-primary underline">Close</button>
      </div>
    </div>
  );
};

export default Modal;
// This Modal component provides a simple way to display modals in the application. It accepts props for controlling visibility, title, content, and a close handler.