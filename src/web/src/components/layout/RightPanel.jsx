import { Activity, ShieldAlert, Target } from "lucide-react";
import { t } from "../../i18n";

const SESSION_FOCUS_DEFAULT = [
  "Establish rapport and the counseling framework",
  "Gather relevant background information",
  "Understand current concerns and recent changes",
  "Clarify the client's motivations and expectations",
  "Assess well-being and daily functioning",
  "Identify potential risks and available resources",
  "Summarize the session and provide collaborative feedback",
];

function Section({ title, icon: Icon, children }) {
  return (
    <section className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
      <div className="mb-2 flex items-center gap-2 text-slate-800">
        <Icon className="h-4 w-4" />
        <h3 className="text-sm font-semibold">{title}</h3>
      </div>
      <div className="text-xs leading-6 text-slate-600">{children}</div>
    </section>
  );
}

function buildPromptSessionFocus(currentVisit) {
  const focus = [];
  const appendUnique = (rawValue) => {
    const text = String(rawValue ?? "").trim();
    if (!text || focus.includes(text)) return;
    focus.push(text);
  };

  (currentVisit?.psych_context?.session_focus || []).forEach(appendUnique);
  if (focus.length === 0) {
    SESSION_FOCUS_DEFAULT.forEach(appendUnique);
  }
  return focus.slice(0, 8);
}

export function RightPanel({ currentCourse, currentVisit, locale = "en", embedded = false }) {
  const stage = currentVisit?.stage || currentCourse?.current_stage;
  const sessionFocus = buildPromptSessionFocus(currentVisit);

  const wrapperClassName = embedded
    ? "space-y-4"
    : "hidden shrink-0 xl:block xl:w-64 2xl:w-72 border-l border-slate-200 bg-slate-50/70 p-4 overflow-y-auto";

  return (
    <aside className={wrapperClassName}>
      <Section title={t("Current stage", locale)} icon={Activity}>
        {currentCourse ? (
          <div className="space-y-1">
            <p className="font-semibold text-slate-800">{t(stage?.label || "Not started", locale)}</p>
            <p>{t("Session {number}.", locale, { number: currentVisit?.visit_no || currentCourse?.latest_visit_no || 0 })}</p>
          </div>
        ) : (
          <p>{t("Select a course to view its current stage and progress.", locale)}</p>
        )}
      </Section>

      <Section title={t("Session goals", locale)} icon={Target}>
        {currentCourse ? (
          sessionFocus.length > 0 ? (
            <ul className="space-y-1">
              {sessionFocus.map((focusItem, index) => (
                <li key={`${index}-${focusItem}`} className="flex items-start gap-2">
                  <span className="mt-2 h-1.5 w-1.5 rounded-full bg-teal-500" />
                  <span>{t(focusItem, locale)}</span>
                </li>
              ))}
            </ul>
          ) : (
            <p>{t("There are no goal details for this session yet.", locale)}</p>
          )
        ) : (
          <p>{t("Create a course to view and manage counseling goals here.", locale)}</p>
        )}
      </Section>

      <Section title={t("Support and reminders", locale)} icon={ShieldAlert}>
        <ul className="space-y-1">
          <li>{t("AI content is for informational purposes only and does not replace professional medical advice.", locale)}</li>
          <li>{t("In a mental health emergency, contact local emergency services or a qualified professional.", locale)}</li>
          <li>{t("This area is reserved for future post-session tasks and at-home exercises.", locale)}</li>
        </ul>
      </Section>
    </aside>
  );
}
