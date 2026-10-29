import { User, X } from "lucide-react";
import { useLocale } from "../../i18n";

export function AuthModal({
  open,
  user,
  authMode,
  authForm,
  onClose,
  onChangeMode,
  onChangeForm,
  onSubmit,
  onLogout,
}) {
  const { locale } = useLocale();
  if (!open) return null;

  return (
    <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center z-[70] p-4">
      <div className="bg-white border border-slate-200 shadow-2xl rounded-2xl w-full max-w-md p-6 space-y-4 relative">
        <button className="absolute top-3 right-3 text-slate-400 hover:text-slate-600" onClick={onClose}>
          <X className="w-5 h-5" />
        </button>

        <div className="text-center space-y-1">
          <h2 className="text-xl font-bold text-slate-800">{locale === "en" ? "Account" : "Conta"}</h2>
          <p className="text-sm text-slate-500">
            {user ? `${locale === "en" ? "Signed in: " : "Conectado: "}${user.username}` : (locale === "en" ? "Enter your username and password, or create an account." : "Informe seu nome de usuário e senha ou crie uma conta.")}
          </p>
        </div>

        {!user && (
          <div className="space-y-3">
            <input
              className="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm"
              placeholder={locale === "en" ? "Username" : "Nome de usuário"}
              value={authForm.username}
              onChange={(event) => onChangeForm({ ...authForm, username: event.target.value })}
            />

            <input
              className="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm"
              placeholder={locale === "en" ? "Password" : "Senha"}
              type="password"
              value={authForm.password}
              onChange={(event) => onChangeForm({ ...authForm, password: event.target.value })}
            />

            <div className="flex items-center justify-between text-xs text-slate-500">
              <div>{locale === "en" ? "Mode: " : "Modo: "}{authMode === "login" ? (locale === "en" ? "Sign in" : "Entrar") : (locale === "en" ? "Register" : "Criar conta")}</div>
              <button
                className="text-teal-600 hover:text-teal-700"
                onClick={() => onChangeMode(authMode === "login" ? "register" : "login")}
              >
                {locale === "en" ? "Switch to " : "Mudar para "}{authMode === "login" ? (locale === "en" ? "Register" : "Criar conta") : (locale === "en" ? "Sign in" : "Entrar")}
              </button>
            </div>

            <button
              className="w-full bg-teal-600 text-white rounded-lg py-2 text-sm font-semibold hover:bg-teal-700 transition"
              onClick={() => onSubmit(authMode)}
            >
              {authMode === "login" ? (locale === "en" ? "Sign in" : "Entrar") : (locale === "en" ? "Register" : "Criar conta")}
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
              {locale === "en" ? "Sign out" : "Sair"}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
