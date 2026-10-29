import { Activity, ShieldAlert, Target } from "lucide-react";
import { useLocale } from "../../i18n";

const SESSION_FOCUS_DEFAULT = [
  "建立初始关系与咨询框架",
  "收集稳定背景信息",
  "了解当前主要困扰与近期变化",
  "澄清来访动机与期待",
  "进行基础身心与功能评估",
  "识别潜在风险与可用资源",
  "会谈总结与协作性反馈",
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

export function RightPanel({ currentCourse, currentVisit, embedded = false }) {
  const { locale } = useLocale();
  const stage = currentVisit?.stage || currentCourse?.current_stage;
  const sessionFocus = buildPromptSessionFocus(currentVisit);

  const wrapperClassName = embedded
    ? "space-y-4"
    : "hidden shrink-0 xl:block xl:w-64 2xl:w-72 border-l border-slate-200 bg-slate-50/70 p-4 overflow-y-auto";

  return (
    <aside className={wrapperClassName}>
      <Section title={locale === "en" ? "Current stage" : "Etapa atual"} icon={Activity}>
        {currentCourse ? (
          <div className="space-y-1">
            <p className="font-semibold text-slate-800">{stage?.label || (locale === "en" ? "Not started" : "Não iniciada")}</p>
            <p>{locale === "en" ? `Session ${currentVisit?.visit_no || currentCourse?.latest_visit_no || 0}.` : `Sessão ${currentVisit?.visit_no || currentCourse?.latest_visit_no || 0}.`}</p>
          </div>
        ) : (
          <p>{locale === "en" ? "Select a course to see its stage and progress." : "Selecione um percurso para ver a etapa e o progresso."}</p>
        )}
      </Section>

      <Section title={locale === "en" ? "Session focus" : "Foco da sessão"} icon={Target}>
        {currentCourse ? (
          sessionFocus.length > 0 ? (
            <ul className="space-y-1">
              {sessionFocus.map((focusItem, index) => (
                <li key={`${index}-${focusItem}`} className="flex items-start gap-2">
                  <span className="mt-2 h-1.5 w-1.5 rounded-full bg-teal-500" />
                  <span>{focusItem}</span>
                </li>
              ))}
            </ul>
          ) : (
            <p>{locale === "en" ? "No focus is recorded for this session." : "Não há foco registrado para esta sessão."}</p>
          )
        ) : (
          <p>{locale === "en" ? "Create a course to view and maintain its focus here." : "Crie um percurso para consultar e atualizar o foco aqui."}</p>
        )}
      </Section>

      <Section title={locale === "en" ? "Information and reminders" : "Informações e lembretes"} icon={ShieldAlert}>
        <ul className="space-y-1">
          <li>{locale === "en" ? "AI-generated content is informational and does not replace professional healthcare advice." : "O conteúdo gerado por IA é apenas informativo e não substitui orientação profissional de saúde."}</li>
          <li>{locale === "en" ? "In an emergency, contact local emergency services or a qualified organization." : "Em uma emergência, procure os serviços de emergência locais ou uma instituição especializada."}</li>
          <li>{locale === "en" ? "Post-session tasks and exercises are not available in this interface." : "Tarefas e exercícios pós-sessão não estão disponíveis nesta interface."}</li>
        </ul>
      </Section>
    </aside>
  );
}
