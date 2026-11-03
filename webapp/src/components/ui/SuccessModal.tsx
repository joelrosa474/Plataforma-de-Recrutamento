"use client";

import { CheckCircle2, X } from "lucide-react";

interface SuccessModalProps {
  isOpen: boolean;
  title: string;
  message: string;
  submessage?: string;
  onClose: () => void;
  actionLabel?: string;
  onAction?: () => void;
}

export function SuccessModal({
  isOpen,
  title,
  message,
  submessage,
  onClose,
  actionLabel,
  onAction,
}: SuccessModalProps) {
  if (!isOpen) return null;

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-label={title}
      className="fixed inset-0 z-[9999] flex items-center justify-center bg-black/50 backdrop-blur-sm"
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
    >
      <div className="relative flex w-full max-w-sm flex-col items-center gap-5 rounded-2xl bg-white px-8 py-10 shadow-2xl">
        {/* Close button */}
        <button
          onClick={onClose}
          aria-label="Fechar"
          className="absolute right-4 top-4 rounded-full p-1.5 text-slate-400 transition hover:bg-slate-100 hover:text-slate-700"
        >
          <X className="h-4 w-4" />
        </button>

        {/* Icon */}
        <div className="flex h-16 w-16 items-center justify-center rounded-full bg-emerald-100">
          <CheckCircle2 className="h-9 w-9 text-emerald-600" />
        </div>

        {/* Content */}
        <div className="text-center">
          <h2 className="text-xl font-bold text-slate-900">{title}</h2>
          <p className="mt-2 text-sm leading-relaxed text-slate-600">{message}</p>
          {submessage && (
            <p className="mt-2 rounded-lg bg-sky-50 border border-sky-100 px-4 py-2 text-xs font-medium text-sky-700">
              {submessage}
            </p>
          )}
        </div>

        {/* Actions */}
        <div className="flex w-full flex-col gap-2">
          {actionLabel && onAction && (
            <button
              onClick={onAction}
              className="w-full rounded-xl bg-sky-600 py-2.5 text-sm font-bold text-white transition hover:bg-sky-700"
            >
              {actionLabel}
            </button>
          )}
          <button
            onClick={onClose}
            className="w-full rounded-xl border border-slate-200 bg-white py-2.5 text-sm font-semibold text-slate-700 transition hover:bg-slate-50"
          >
            Fechar
          </button>
        </div>
      </div>
    </div>
  );
}

