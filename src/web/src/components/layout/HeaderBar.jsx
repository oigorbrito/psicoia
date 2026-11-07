import { CalendarPlus2, CheckCircle2, PlayCircle, PlusCircle, XCircle } from "lucide-react";
import { getCourseStatusText, getVisitStatusText } from "../common/statusText";
import { getSchoolDisplayName } from "../common/schoolText";
import { t } from "../../i18n";

export function HeaderBar({
  currentSchool,
  currentCourse,
  currentVisit,
  locale,
  onLocaleChange,
  selectedSchoolId,
  token,
  canCreateCourse,
  canStartNextVisit,
  canCompleteCourse,
  onOpenCreateCourseModal,
  onStartNextVisit,
  onContinueVisit,
  onCloseVisit,
  onOpenCompleteCourseModal,
}) {
  const hasOpenVisit = currentVisit?.status === "open" || Boolean(currentCourse?.active_visit_id);
  const nextVisitNo = (currentCourse?.latest_visit_no || 0) + 1;

  const primaryAction = !currentCourse || currentCourse.status !== "active"
    ? {
        label: t("Create course", locale),
        icon: PlusCircle,
        onClick: onOpenCreateCourseModal,
        disabled: !canCreateCourse || !selectedSchoolId || !token,
      }
    : hasOpenVisit
    ? {
        label: t("Continue session", locale),
        icon: PlayCircle,
        onClick: onContinueVisit,
        disabled: false,
      }
    : {
        label: t("Start session {number}", locale, { number: nextVisitNo }),
        icon: CalendarPlus2,
        onClick: onStartNextVisit,
        disabled: !canStartNextVisit,
      };

  const PrimaryIcon = primaryAction.icon;

  return (
    <header className="border-b border-slate-200 bg-white/90 px-5 py-3 backdrop-blur-sm sm:px-6">
      <div className="flex items-center justify-between gap-4">
        <div className="ml-10 md:ml-0">
          <h1 className="text-base font-semibold text-slate-900">
            {currentSchool ? `${getSchoolDisplayName(currentSchool, locale)} ${t("Counseling Workspace", locale)}` : t("Counseling Workspace", locale)}
          </h1>
          <p className="mt-1 text-xs text-slate-600">
            {!currentCourse
              ? t("Create a course to get started.", locale)
              : `${t("Course status: {status}", locale, { status: getCourseStatusText(currentCourse.status, locale) })}${
                  currentVisit ? ` · ${t("Session status: {status}", locale, { status: getVisitStatusText(currentVisit.status, locale) })}` : ""
                }`}
          </p>
        </div>

        <div className="flex items-center gap-2">
          <select
            aria-label={t("Language", locale)}
            value={locale}
            onChange={(event) => onLocaleChange(event.target.value)}
            className="rounded-lg border border-slate-200 bg-white px-2 py-2 text-xs text-slate-700"
          >
            <option value="en">English</option>
            <option value="pt-BR">Português (Brasil)</option>
          </select>
          <div className="hidden items-center gap-2 lg:flex">
          <button
            type="button"
            onClick={primaryAction.onClick}
            disabled={primaryAction.disabled}
            className="inline-flex items-center gap-1 rounded-lg bg-teal-600 px-3 py-2 text-xs font-semibold text-white hover:bg-teal-700 disabled:cursor-not-allowed disabled:opacity-50"
          >
            <PrimaryIcon className="h-3.5 w-3.5" />
            {primaryAction.label}
          </button>

          {hasOpenVisit ? (
            <button
              type="button"
              onClick={onCloseVisit}
              className="inline-flex items-center gap-1 rounded-lg bg-rose-50 px-3 py-2 text-xs font-semibold text-rose-700 hover:bg-rose-100"
            >
              <XCircle className="h-3.5 w-3.5" />
              {t("End session", locale)}
            </button>
          ) : null}

          {canCompleteCourse ? (
            <button
              type="button"
              onClick={onOpenCompleteCourseModal}
              className="inline-flex items-center gap-1 rounded-lg bg-emerald-50 px-3 py-2 text-xs font-semibold text-emerald-700 hover:bg-emerald-100"
            >
              <CheckCircle2 className="h-3.5 w-3.5" />
              {t("Complete course", locale)}
            </button>
          ) : null}
          </div>
        </div>
      </div>
    </header>
  );
}
