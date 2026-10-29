import { Send } from "lucide-react";
import { useLocale } from "../../i18n";

export function ChatInput({ currentCourse, currentVisit, input, isTyping, onInputChange, onSend }) {
  const { locale } = useLocale();
  const nextVisitNo = (currentCourse?.latest_visit_no || 0) + 1;

  if (!currentVisit) {
    if (!currentCourse) return null;
    return (
      <div className="mb-20 border-t border-slate-200 bg-white p-4 text-center text-sm text-slate-600 lg:mb-0">
        {locale === "en" ? `No session has started for this course. Select “Start session ${nextVisitNo}”.` : `Ainda não há sessão neste percurso. Selecione “Iniciar sessão ${nextVisitNo}”.`}
      </div>
    );
  }

  if (currentVisit.status !== "open") {
    return (
      <div className="mb-20 border-t border-slate-200 bg-white p-4 text-center text-sm text-slate-600 lg:mb-0">
        {locale === "en" ? "This session has ended. You can start the next one." : "Esta sessão foi encerrada. Você pode iniciar a próxima."}
      </div>
    );
  }

  return (
    <div className="mb-20 border-t border-slate-200 bg-white p-4 lg:mb-0">
      <div className="relative mx-auto max-w-4xl">
        <textarea
          value={input}
          onChange={(event) => onInputChange(event.target.value)}
          onKeyDown={(event) => {
            if (event.key === "Enter" && !event.shiftKey) {
              event.preventDefault();
              onSend();
            }
          }}
          placeholder={locale === "en" ? "Write a message. Enter to send; Shift + Enter for a new line." : "Escreva sua mensagem. Enter envia; Shift + Enter quebra a linha."}
          className="min-h-[56px] w-full max-h-32 resize-none rounded-xl border border-slate-200 bg-slate-50 py-3 pl-4 pr-12 text-sm focus:border-teal-500 focus:outline-none focus:ring-2 focus:ring-teal-500/20 md:text-base"
          rows={1}
        />

        <button
          type="button"
          onClick={onSend}
          disabled={!input.trim() || isTyping}
          className="absolute right-2 top-1/2 flex -translate-y-1/2 items-center justify-center rounded-lg bg-teal-600 p-2 text-white transition-all hover:bg-teal-700 disabled:cursor-not-allowed disabled:opacity-50"
        >
          <Send className="h-4 w-4" />
        </button>
      </div>

      <p className="mt-2 text-center text-xs leading-5 text-slate-600">
        {locale === "en" ? "AI responses are informational and do not replace professional advice. In an emergency, contact local services." : "As respostas de IA são informativas e não substituem orientação profissional. Em emergências, procure os serviços locais."}
      </p>
    </div>
  );
}
