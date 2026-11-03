"use client";

interface LoadingModalProps {
  isOpen: boolean;
  message?: string;
  submessage?: string;
}

export function LoadingModal({
  isOpen,
  message = "A processar…",
  submessage,
}: LoadingModalProps) {
  if (!isOpen) return null;

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-label={message}
      className="fixed inset-0 z-[9999] flex items-center justify-center bg-black/50 backdrop-blur-sm"
    >
      <div className="flex w-full max-w-xs flex-col items-center gap-5 rounded-2xl bg-white px-8 py-10 shadow-2xl">
        {/* Spinner */}
        <div className="relative flex h-16 w-16 items-center justify-center">
          {/* Outer ring */}
          <div className="absolute inset-0 animate-spin rounded-full border-4 border-sky-100 border-t-sky-500" />
          {/* Inner dot */}
          <div className="h-5 w-5 rounded-full bg-sky-500 animate-pulse" />
        </div>

        {/* Text */}
        <div className="text-center">
          <p className="text-base font-bold text-slate-800">{message}</p>
          {submessage && (
            <p className="mt-1 text-xs text-slate-500">{submessage}</p>
          )}
        </div>
      </div>
    </div>
  );
}
