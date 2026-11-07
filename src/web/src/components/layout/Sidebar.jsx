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
import { t } from "../../i18n";

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
  locale,
  courses,
  onSelectCourse,
  onOpenSchoolModal,
  onOpenAuthModal,
  user,
}) {
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
            <p className="text-sm font-semibold text-slate-800">{t("Counseling Workspace", locale)}</p>
            <p className="text-xs text-slate-500">MindSpace</p>
          </div>
        </div>

        <div className="flex items-center gap-1">
          <button
            type="button"
            className="hidden rounded-md p-1 text-slate-500 hover:bg-slate-100 md:inline-flex"
            onClick={onToggleCollapse}
            aria-label={t(desktopCollapsed ? "Expand sidebar" : "Collapse sidebar", locale)}
            title={t(desktopCollapsed ? "Expand sidebar" : "Collapse sidebar", locale)}
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
              title={t("Change approach", locale)}
            >
              <Activity className="h-4 w-4" />
            </button>
          </div>
        ) : null}

        <div className={desktopCollapsed ? "space-y-5 md:hidden" : "space-y-5"}>
          {currentSchool ? (
            <section className="rounded-xl border border-slate-200 bg-slate-50 p-4">
              <div className="mb-2 flex items-center justify-between">
                <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">{t("Current approach", locale)}</p>
                <button
                  type="button"
                  onClick={onOpenSchoolModal}
                  className="text-xs font-medium text-teal-600 hover:text-teal-700"
                >
                  {t("Change", locale)}
                </button>
              </div>

              <div className="flex items-start gap-3">
                <div className={`rounded-lg p-2 text-white ${currentSchool.color}`}>
                  <Activity className="h-4 w-4" />
                </div>
                <div>
                  <p className="text-sm font-semibold text-slate-800">{getSchoolDisplayName(currentSchool, locale)}</p>
                  <p className="mt-1 text-xs leading-5 text-slate-600">
                    {t("Current stage: {stage}", locale, { stage: t(currentCourse?.current_stage?.label || "Not started", locale) })}
                  </p>
                </div>
              </div>
            </section>
          ) : (
            <section className="rounded-xl border border-dashed border-slate-300 bg-slate-50 p-4 text-sm text-slate-600">
              <p>{t("Choose an approach before creating a course.", locale)}</p>
              <button
                type="button"
                onClick={onOpenSchoolModal}
                className="mt-3 text-xs font-medium text-teal-600 hover:text-teal-700"
              >
                {t("Choose an approach", locale)}
              </button>
            </section>
          )}

          <section>
            <div className="mb-2 flex items-center justify-between">
              <h2 className="text-sm font-semibold text-slate-800">{t("Courses", locale)}</h2>
              <div className="flex items-center gap-1">
                <FolderTree className="h-4 w-4 text-slate-400" />
                <button
                  type="button"
                  onClick={() => setCoursePanelOpen((prev) => !prev)}
                  className="inline-flex items-center gap-1 rounded-md px-2 py-1 text-xs font-medium text-slate-600 hover:bg-slate-100"
                  aria-label={t(coursePanelOpen ? "Collapse course list" : "Expand course list", locale)}
                >
                  {coursePanelOpen ? (
                    <>
                      {t("Collapse", locale)}
                      <ChevronUp className="h-3.5 w-3.5" />
                    </>
                  ) : (
                    <>
                      {t("Expand", locale)}
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
                      <p className="text-sm font-semibold text-slate-800">{course.title || t("Untitled course", locale)}</p>
                      <StatusPill text={getCourseStatusText(course.status, locale)} tone={getCourseTone(course.status)} />
                    </div>

                    <div className="mt-2 space-y-1 text-xs text-slate-600">
                      <p>{t("Current stage: {stage}", locale, { stage: t(course.current_stage?.label || "Not started", locale) })}</p>
                      <p>{t("Sessions completed: {number}", locale, { number: course.latest_visit_no || 0 })}</p>
                      <p className="inline-flex items-center gap-1 text-slate-500">
                        <Sparkles className="h-3.5 w-3.5" />
                        {t(course.active_visit_id ? "Active session" : "No active session", locale)}
                      </p>
                    </div>
                  </button>
                ))}

                {courses.length === 0 ? (
                  <div className="rounded-lg border border-dashed border-slate-300 bg-slate-50 p-3 text-xs leading-5 text-slate-600">
                    {t("There are no courses for this approach yet. Select “Create course” to get started.", locale)}
                  </div>
                ) : null}
              </div>
            ) : (
              <div className="rounded-lg border border-dashed border-slate-300 bg-slate-50 p-3 text-xs leading-5 text-slate-600">
                {currentCourse
                  ? t("Selected: {title}", locale, { title: currentCourse.title || t("Untitled course", locale) })
                  : t("The course list is collapsed. Select “Expand” to view all courses.", locale)}
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
          <span>{user ? t("Signed in: {username}", locale, { username: user.username }) : t("Sign in / Sign up", locale)}</span>
        </button>
      </div>
    </aside>
  );
}
