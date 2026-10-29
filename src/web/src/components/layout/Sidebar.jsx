import { useState } from "react";
import {
  Activity,
  Brain,
  ChevronDown,
  ChevronUp,
  ChevronsLeft,
  ChevronsRight,
  FolderTree,
  Sparkles,
  User,
  X,
} from "lucide-react";
import { getSchoolDisplayName } from "../common/schoolText";
import { StatusPill } from "../common/StatusPill";
import { getCourseStatusText } from "../common/statusText";
import { useLocale } from "../../i18n";

function getCourseTone(status) {
  if (status === "active") return "active";
  if (status === "completed") return "success";
  if (status === "archived") return "neutral";
  return "warning";
}

export function Sidebar({
  sidebarOpen,
  sidebarCollapsed,
  onClose,
  onToggleCollapse,
  currentSchool,
  currentCourse,
  courses,
  onSelectCourse,
  onOpenSchoolModal,
  onOpenAuthModal,
  user,
}) {
  const { t, locale } = useLocale();
  const [coursePanelOpen, setCoursePanelOpen] = useState(true);
  const desktopCollapsed = Boolean(sidebarCollapsed);

  return (
    <aside
      className={`fixed inset-y-0 left-0 z-50 w-72 transform border-r border-slate-200 bg-white transition-all duration-300 ease-in-out md:relative md:translate-x-0 ${
        desktopCollapsed ? "md:w-20" : "md:w-72"
      } ${sidebarOpen ? "translate-x-0" : "-translate-x-full"} flex flex-col`}
    >
      <div className="flex items-center justify-between border-b border-slate-200 p-5">
        <div className={`flex items-center gap-2 ${desktopCollapsed ? "md:justify-center" : ""}`}>
          <div className="rounded-lg bg-teal-50 p-2 text-teal-600">
            <Brain className="h-5 w-5" />
          </div>
          <div className={desktopCollapsed ? "block md:hidden" : "block"}>
            <p className="text-sm font-semibold text-slate-800">PsicoIA</p>
            <p className="text-xs text-slate-500">{locale === "en" ? "Conversation workspace" : "Espaço de conversa"}</p>
          </div>
        </div>

        <div className="flex items-center gap-1">
          <button
            type="button"
            className="hidden rounded-md p-1 text-slate-500 hover:bg-slate-100 md:inline-flex"
            onClick={onToggleCollapse}
            aria-label={desktopCollapsed ? (locale === "en" ? "Expand sidebar" : "Expandir barra lateral") : (locale === "en" ? "Collapse sidebar" : "Recolher barra lateral")}
            title={desktopCollapsed ? (locale === "en" ? "Expand sidebar" : "Expandir barra lateral") : (locale === "en" ? "Collapse sidebar" : "Recolher barra lateral")}
          >
            {desktopCollapsed ? <ChevronsRight className="h-4 w-4" /> : <ChevronsLeft className="h-4 w-4" />}
          </button>

          <button type="button" className="md:hidden" onClick={onClose}>
            <X className="h-5 w-5 text-slate-500" />
          </button>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-4">
        {desktopCollapsed ? (
          <div className="hidden md:flex md:flex-col md:items-center md:gap-3">
            <button
              type="button"
              onClick={onOpenSchoolModal}
              className="inline-flex h-10 w-10 items-center justify-center rounded-lg border border-slate-200 bg-slate-50 text-slate-700 hover:bg-slate-100"
              title={t("切换")}
            >
              <Activity className="h-4 w-4" />
            </button>
          </div>
        ) : null}

        <div className={desktopCollapsed ? "space-y-5 md:hidden" : "space-y-5"}>
          {currentSchool ? (
            <section className="rounded-xl border border-slate-200 bg-slate-50 p-4">
              <div className="mb-2 flex items-center justify-between">
                <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">{t("当前咨询流派")}</p>
                <button
                  type="button"
                  onClick={onOpenSchoolModal}
                  className="text-xs font-medium text-teal-600 hover:text-teal-700"
                >
                  {t("切换")}
                </button>
              </div>

              <div className="flex items-start gap-3">
                <div className={`rounded-lg p-2 text-white ${currentSchool.color}`}>
                  <Activity className="h-4 w-4" />
                </div>
                <div>
                  <p className="text-sm font-semibold text-slate-800">{getSchoolDisplayName(currentSchool)}</p>
                  <p className="mt-1 text-xs leading-5 text-slate-600">
                    {locale === "en" ? "Current stage: " : "Etapa atual: "}{currentCourse?.current_stage?.label || t("未开始")}
                  </p>
                </div>
              </div>
            </section>
          ) : (
            <section className="rounded-xl border border-dashed border-slate-300 bg-slate-50 p-4 text-sm text-slate-600">
              <p>{locale === "en" ? "Choose an approach before creating a course." : "Selecione uma abordagem antes de criar um percurso."}</p>
              <button
                type="button"
                onClick={onOpenSchoolModal}
                className="mt-3 text-xs font-medium text-teal-600 hover:text-teal-700"
              >
                {locale === "en" ? "Choose approach" : "Escolher abordagem"}
              </button>
            </section>
          )}

          <section>
            <div className="mb-2 flex items-center justify-between">
              <h2 className="text-sm font-semibold text-slate-800">{t("疗程列表")}</h2>
              <div className="flex items-center gap-1">
                <FolderTree className="h-4 w-4 text-slate-400" />
                <button
                  type="button"
                  onClick={() => setCoursePanelOpen((prev) => !prev)}
                  className="inline-flex items-center gap-1 rounded-md px-2 py-1 text-xs font-medium text-slate-600 hover:bg-slate-100"
                  aria-label={coursePanelOpen ? (locale === "en" ? "Collapse course list" : "Recolher percursos") : (locale === "en" ? "Expand course list" : "Expandir percursos")}
                >
                  {coursePanelOpen ? (
                    <>
                      {locale === "en" ? "Collapse" : "Recolher"}
                      <ChevronUp className="h-3.5 w-3.5" />
                    </>
                  ) : (
                    <>
                      {locale === "en" ? "Expand" : "Expandir"}
                      <ChevronDown className="h-3.5 w-3.5" />
                    </>
                  )}
                </button>
              </div>
            </div>

            {coursePanelOpen ? (
              <div className="space-y-2">
                {courses.map((course) => (
                  <button
                    key={course.course_id}
                    type="button"
                    onClick={() => onSelectCourse(course.course_id)}
                    className={`w-full rounded-xl border bg-white p-3 text-left transition ${
                      currentCourse?.course_id === course.course_id
                        ? "border-teal-300 ring-2 ring-teal-100"
                        : "border-slate-200 hover:border-teal-200"
                    }`}
                  >
                    <div className="flex items-start justify-between gap-2">
                      <p className="text-sm font-semibold text-slate-800">{course.title || t("未命名疗程")}</p>
                      <StatusPill text={getCourseStatusText(course.status)} tone={getCourseTone(course.status)} />
                    </div>

                    <div className="mt-2 space-y-1 text-xs text-slate-600">
                      <p>{locale === "en" ? "Current stage: " : "Etapa atual: "}{course.current_stage?.label || t("未开始")}</p>
                      <p>{locale === "en" ? "Sessions completed: " : "Sessões realizadas: "}{course.latest_visit_no || 0}</p>
                      <p className="inline-flex items-center gap-1 text-slate-500">
                        <Sparkles className="h-3.5 w-3.5" />
                        {course.active_visit_id ? (locale === "en" ? "Session in progress" : "Há uma sessão em andamento") : (locale === "en" ? "No session in progress" : "Nenhuma sessão em andamento")}
                      </p>
                    </div>
                  </button>
                ))}

                {courses.length === 0 ? (
                  <div className="rounded-lg border border-dashed border-slate-300 bg-slate-50 p-3 text-xs leading-5 text-slate-600">
                    {locale === "en" ? "No courses for this approach yet. Select ‘New course’ to begin." : "Ainda não há percursos nesta abordagem. Selecione ‘Novo percurso’ para começar."}
                  </div>
                ) : null}
              </div>
            ) : (
              <div className="rounded-lg border border-dashed border-slate-300 bg-slate-50 p-3 text-xs leading-5 text-slate-600">
                {currentCourse
                  ? `${locale === "en" ? "Selected: " : "Selecionado: "}${currentCourse.title || t("未命名疗程")}`
                  : (locale === "en" ? "Course list collapsed. Select ‘Expand’ to view all courses." : "A lista está recolhida. Selecione ‘Expandir’ para ver todos os percursos.")}
              </div>
            )}
          </section>
        </div>
      </div>

      <div className="border-t border-slate-200 bg-slate-50 p-3">
        <button
          type="button"
          onClick={onOpenAuthModal}
          className={`flex w-full items-center gap-2 rounded-lg p-2 text-sm text-slate-700 hover:bg-slate-100 ${
            desktopCollapsed ? "md:hidden" : ""
          }`}
        >
          <User className="h-4 w-4" />
          <span>{user ? `${locale === "en" ? "Signed in: " : "Conectado: "}${user.username}` : (locale === "en" ? "Sign in / Register" : "Entrar / Criar conta")}</span>
        </button>
      </div>
    </aside>
  );
}
