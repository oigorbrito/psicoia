import { Clock3, MessageSquarePlus, Milestone } from "lucide-react";
import { EmptyState } from "../common/EmptyState";
import { StatusPill } from "../common/StatusPill";
import { formatVisitLabel, getVisitStatusText } from "../common/statusText";
import { t } from "../../i18n";

function getVisitTone(status) {
  if (status === "open") return "active";
  if (status === "closed") return "neutral";
  return "warning";
}

export function VisitTimeline({
  currentCourse,
  visits,
  currentVisit,
  locale = "en",
  canStartNextVisit,
  onStartNextVisit,
  onSelectVisit,
}) {
  const nextVisitNo = (currentCourse?.latest_visit_no || 0) + 1;

  return (
    <aside className="hidden shrink-0 lg:flex lg:w-64 xl:w-72 border-r border-slate-200 bg-slate-50/80 flex-col">
      <div className="border-b border-slate-200 p-4">
        <h2 className="text-sm font-semibold text-slate-800">{t("Session timeline", locale)}</h2>
        <p className="mt-1 text-xs leading-5 text-slate-600">
          {currentCourse
            ? t("Review each session in {title}.", locale, { title: currentCourse.title })
            : t("Select a course to view its session timeline.", locale)}
        </p>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {!currentCourse ? (
          <EmptyState
            icon={Milestone}
            title={t("No course selected", locale)}
            description={t("Select a course on the left to view session progress.", locale)}
          />
        ) : visits.length === 0 ? (
          <EmptyState
            icon={Clock3}
            title={t("No sessions yet", locale)}
            description={t("The first session starts automatically when you create a course. You can also start one later.", locale)}
            action={
              canStartNextVisit ? (
                <button
                  type="button"
                  className="inline-flex items-center rounded-lg bg-teal-600 px-3 py-2 text-xs font-semibold text-white hover:bg-teal-700"
                  onClick={onStartNextVisit}
                >
                  {t("Start session {number}", locale, { number: nextVisitNo })}
                </button>
              ) : null
            }
          />
        ) : (
          visits.map((visit) => (
            <button
              key={visit.visit_id}
              type="button"
              onClick={() => onSelectVisit?.(visit.visit_id)}
              className={`w-full rounded-xl border bg-white p-3 text-left transition ${
                currentVisit?.visit_id === visit.visit_id
                  ? "border-teal-300 ring-2 ring-teal-100"
                  : "border-slate-200 hover:border-teal-200"
              }`}
            >
              <div className="flex items-start justify-between gap-2">
                <div>
                  <p className="text-sm font-semibold text-slate-800">{formatVisitLabel(visit.visit_no, locale)}</p>
                  <p className="mt-1 text-xs text-slate-600">{t("Current stage: {stage}", locale, { stage: t(visit.stage?.label || "Not started", locale) })}</p>
                </div>
                <StatusPill text={getVisitStatusText(visit.status, locale)} tone={getVisitTone(visit.status)} />
              </div>

              <div className="mt-3 flex items-center justify-between text-xs text-slate-600">
                <span className="inline-flex items-center gap-1">
                  <MessageSquarePlus className="h-3.5 w-3.5" />
                  {t("{number} messages", locale, { number: visit.message_count || 0 })}
                </span>
                <span>{t(visit.ended_at ? "Ended" : "In progress", locale)}</span>
              </div>
            </button>
          ))
        )}
      </div>
    </aside>
  );
}
