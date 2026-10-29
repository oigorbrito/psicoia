import { X } from "lucide-react";
import { getSchoolDisplayName } from "../common/schoolText";
import { useLocale } from "../../i18n";

export function SchoolModal({
  open,
  token,
  schools,
  selectedSchoolId,
  currentSchool,
  onClose,
  onSelectSchool,
}) {
  const { locale } = useLocale();
  if (!open) return null;

  return (
    <div className="fixed inset-0 z-[70] flex items-center justify-center bg-slate-900/60 p-4 backdrop-blur-sm">
      <div className="relative w-full max-w-md space-y-4 rounded-2xl border border-slate-200 bg-white p-6 shadow-2xl">
        <button type="button" className="absolute right-3 top-3 text-slate-400 hover:text-slate-600" onClick={onClose}>
          <X className="h-5 w-5" />
        </button>

        <div>
          <h3 className="text-lg font-bold text-slate-800">{locale === "en" ? "Choose an approach" : "Escolha uma abordagem"}</h3>
          <p className="mt-1 text-sm text-slate-600">
            {locale === "en" ? "The course list updates when you switch. Current: " : "A lista de percursos será atualizada. Atual: "}{getSchoolDisplayName(currentSchool, locale)}
          </p>
        </div>

        <select
          className="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm"
          value={selectedSchoolId}
          onChange={(event) => onSelectSchool(event.target.value)}
          disabled={!token}
        >
          <option value="" disabled>
            {locale === "en" ? "Select an approach" : "Selecione uma abordagem"}
          </option>
          {schools.map((school) => (
            <option key={school.id} value={school.id}>
              {getSchoolDisplayName(school, locale)}
            </option>
          ))}
        </select>

        {!token ? <p className="text-xs text-amber-600">{locale === "en" ? "Sign in before switching approaches." : "Entre para trocar de abordagem."}</p> : null}

        <button
          type="button"
          className="w-full rounded-lg bg-slate-100 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-200"
          onClick={onClose}
        >
          {locale === "en" ? "Close" : "Fechar"}
        </button>
      </div>
    </div>
  );
}
