import { User, X } from "lucide-react";
import { t } from "../../i18n";

export function AuthModal({
  open,
  locale = "en",
  user,
  authMode,
  authForm,
  onClose,
  onChangeMode,
  onChangeForm,
  onSubmit,
  onLogout,
}) {
  if (!open) return null;

  return (
    <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center z-[70] p-4">
      <div className="bg-white border border-slate-200 shadow-2xl rounded-2xl w-full max-w-md p-6 space-y-4 relative">
        <button className="absolute top-3 right-3 text-slate-400 hover:text-slate-600" onClick={onClose}>
          <X className="w-5 h-5" />
        </button>

        <div className="text-center space-y-1">
          <h2 className="text-xl font-bold text-slate-800">{t("Account", locale)}</h2>
          <p className="text-sm text-slate-500">
            {user ? t("Signed in as: {username}", locale, { username: user.username }) : t("Enter your username and password, or create a new account.", locale)}
          </p>
        </div>

        {!user && (
          <div className="space-y-3">
            <input
              className="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm"
              placeholder={t("Username", locale)}
              value={authForm.username}
              onChange={(event) => onChangeForm({ ...authForm, username: event.target.value })}
            />

            <input
              className="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm"
              placeholder={t("Password", locale)}
              type="password"
              value={authForm.password}
              onChange={(event) => onChangeForm({ ...authForm, password: event.target.value })}
            />

            <div className="flex items-center justify-between text-xs text-slate-500">
              <div>{t("Mode: {mode}", locale, { mode: t(authMode === "login" ? "Sign in" : "Sign up", locale) })}</div>
              <button
                className="text-teal-600 hover:text-teal-700"
                onClick={() => onChangeMode(authMode === "login" ? "register" : "login")}
              >
                {t("Switch to {mode}", locale, { mode: t(authMode === "login" ? "Sign up" : "Sign in", locale).toLowerCase() })}
              </button>
            </div>

            <button
              className="w-full bg-teal-600 text-white rounded-lg py-2 text-sm font-semibold hover:bg-teal-700 transition"
              onClick={() => onSubmit(authMode)}
            >
              {t(authMode === "login" ? "Sign in" : "Sign up", locale)}
            </button>
          </div>
        )}

        {user && (
          <div className="space-y-3 text-sm text-slate-600">
            <div className="flex items-center gap-2">
              <User className="w-4 h-4 text-slate-500" />
              <span>{user.username}</span>
            </div>

            <button
              className="w-full bg-slate-800 text-white rounded-lg py-2 text-sm font-semibold hover:bg-slate-900 transition"
              onClick={onLogout}
            >
              {t("Sign out", locale)}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
