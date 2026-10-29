import { Clock3, MessageSquarePlus, Milestone } from "lucide-react";
import { EmptyState } from "../common/EmptyState";
import { StatusPill } from "../common/StatusPill";
import { formatVisitLabel, getVisitStatusText } from "../common/statusText";
import { useLocale } from "../../i18n";

function getVisitTone(status) {
  if (status === "open") return "active";
  if (status === "closed") return "neutral";
  return "warning";
}

export function VisitTimeline({
  currentCourse,
  visits,
  currentVisit,
  canStartNextVisit,
  onStartNextVisit,
  onSelectVisit,
}) {
  const { locale } = useLocale();
  const nextVisitNo = (currentCourse?.latest_visit_no || 0) + 1;

  return (
    <aside className="hidden shrink-0 lg:flex lg:w-64 xl:w-72 border-r border-slate-200 bg-slate-50/80 flex-col">
      <div className="border-b border-slate-200 p-4">
        <h2 className="text-sm font-semibold text-slate-800">{locale === "en" ? "Session timeline" : "Linha do tempo das sessões"}</h2>
        <p className="mt-1 text-xs leading-5 text-slate-600">
          {currentCourse
            ? (locale === "en" ? `Review sessions in ${currentCourse.title} by date.` : `Revise as sessões de ${currentCourse.title} por data.`)
            : (locale === "en" ? "Select a course to view its session timeline." : "Selecione um percurso para consultar as sessões.")}
        </p>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {!currentCourse ? (
          <EmptyState
            icon={Milestone}
            title={locale === "en" ? "No course selected" : "Nenhum percurso selecionado"}
            description={locale === "en" ? "Select a course from the sidebar to view session progress." : "Selecione um percurso na barra lateral para consultar o andamento."}
          />
        ) : visits.length === 0 ? (
          <EmptyState
            icon={Clock3}
            title={locale === "en" ? "No sessions yet" : "Ainda não há sessões"}
            description={locale === "en" ? "The first session starts automatically when you create a course." : "A primeira sessão começa automaticamente ao criar um percurso."}
            action={
              canStartNextVisit ? (
                <button
                  type="button"
                  className="inline-flex items-center rounded-lg bg-teal-600 px-3 py-2 text-xs font-semibold text-white hover:bg-teal-700"
                  onClick={onStartNextVisit}
                >
                  {locale === "en" ? `Start session ${nextVisitNo}` : `Iniciar sessão ${nextVisitNo}`}
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
                  <p className="mt-1 text-xs text-slate-600">{locale === "en" ? "Stage: " : "Etapa: "}{visit.stage?.label || (locale === "en" ? "Not started" : "Não iniciada")}</p>
                </div>
                <StatusPill text={getVisitStatusText(visit.status)} tone={getVisitTone(visit.status)} />
              </div>

              <div className="mt-3 flex items-center justify-between text-xs text-slate-600">
                <span className="inline-flex items-center gap-1">
                  <MessageSquarePlus className="h-3.5 w-3.5" />
                  {visit.message_count || 0}{locale === "en" ? " messages" : " mensagens"}
                </span>
                <span>{visit.ended_at ? (locale === "en" ? "Ended" : "Encerrada") : (locale === "en" ? "In progress" : "Em andamento")}</span>
              </div>
            </button>
          ))
        )}
      </div>
    </aside>
  );
}
