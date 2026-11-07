import { t } from "../../i18n";

export function StageBadge({ stage, locale = "en" }) {
  return (
    <span
      className={`text-xs font-semibold px-2 py-1 rounded ${
        stage?.color || "bg-slate-100 text-slate-600"
      }`}
    >
      {t(stage?.label || "Unknown stage", locale)}
    </span>
  );
}
