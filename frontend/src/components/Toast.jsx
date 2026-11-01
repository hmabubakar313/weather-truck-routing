import { useEffect } from "react";

const AUTO_DISMISS_MS = 6000;

export default function Toast({ message, type = "error", onClose }) {
  useEffect(() => {
    if (!message) return undefined;
    const timer = setTimeout(onClose, AUTO_DISMISS_MS);
    return () => clearTimeout(timer);
  }, [message, onClose]);

  if (!message) return null;

  return (
    <div className={`toast toast-${type}`} role="alert">
      <span>{message}</span>
      <button className="toast-close" onClick={onClose} aria-label="Dismiss">
        &times;
      </button>
    </div>
  );
}
