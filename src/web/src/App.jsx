import { useState } from "react";
import { Menu, X } from "lucide-react";
import { ChatInput } from "./components/chat/ChatInput";
import { ChatMessages } from "./components/chat/ChatMessages";
import { FeedbackBanner } from "./components/common/FeedbackBanner";
import { StatusPill } from "./components/common/StatusPill";
import { HeaderBar } from "./components/layout/HeaderBar";
import { MobileBottomSheet } from "./components/layout/MobileBottomSheet";
import { RightPanel } from "./components/layout/RightPanel";
import { Sidebar } from "./components/layout/Sidebar";
import { VisitTimeline } from "./components/layout/VisitTimeline";
import { AuthModal } from "./components/modals/AuthModal";
import { CompleteCourseModal } from "./components/modals/CompleteCourseModal";
import { CreateCourseModal } from "./components/modals/CreateCourseModal";
import { SchoolModal } from "./components/modals/SchoolModal";
import { getCourseStatusText, getVisitStatusText } from "./components/common/statusText";
import { getSchoolDisplayName } from "./components/common/schoolText";
import { useMindCareApp } from "./hooks/useMindCareApp";
import { getLocale, setLocale, t } from "./i18n";

function getCourseTone(status) {
  if (status === "active") return "active";
  if (status === "completed") return "success";
  if (status === "archived") return "neutral";
  return "warning";
}

function getVisitTone(status) {
  if (status === "open") return "active";
  if (status === "closed") return "neutral";
  return "warning";
}

export default function App() {
  const [locale, setLocaleState] = useState(getLocale);
  const app = useMindCareApp(locale);
  const handleLocaleChange = (nextLocale) => setLocaleState(setLocale(nextLocale));

  return (
    <div className="flex h-screen w-full bg-white font-sans text-slate-900 selection:bg-teal-100">
      <button
        type="button"
        className="fixed left-4 top-4 z-40 rounded-lg border border-slate-200 bg-white p-2 shadow-md md:hidden"
        onClick={() => app.setSidebarOpen(!app.sidebarOpen)}
      >
        {app.sidebarOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
      </button>

      <Sidebar
        sidebarOpen={app.sidebarOpen}
        sidebarCollapsed={app.sidebarCollapsed}
        onClose={() => app.setSidebarOpen(false)}
        onToggleCollapse={() => app.setSidebarCollapsed(!app.sidebarCollapsed)}
        currentSchool={app.currentSchool}
        currentCourse={app.currentCourse}
        locale={locale}
        courses={app.courses}
        onSelectCourse={app.selectCourse}
        onOpenSchoolModal={() => app.setShowSchoolModal(true)}
        onOpenAuthModal={() => app.setShowAuthModal(true)}
        user={app.user}
      />

      <div className="flex min-w-0 flex-1 flex-col">
        <HeaderBar
          currentSchool={app.currentSchool}
          currentCourse={app.currentCourse}
          currentVisit={app.currentVisit}
          locale={locale}
          onLocaleChange={handleLocaleChange}
          selectedSchoolId={app.selectedSchoolId}
          token={app.token}
          canCreateCourse={app.canCreateCourse}
          canStartNextVisit={app.canStartNextVisit}
          canCompleteCourse={app.canCompleteCourse}
          onOpenCreateCourseModal={() => app.setShowCreateCourseModal(true)}
          onStartNextVisit={app.startNextVisit}
          onContinueVisit={app.continueCurrentVisit}
          onCloseVisit={app.closeCurrentVisit}
          onOpenCompleteCourseModal={() => app.setShowCompleteCourseModal(true)}
        />

        <FeedbackBanner feedback={app.feedback} onClose={app.clearFeedback} locale={locale} />

        <div className="flex min-h-0 flex-1">
          <VisitTimeline
            currentCourse={app.currentCourse}
            locale={locale}
            visits={app.visits}
            currentVisit={app.currentVisit}
            canStartNextVisit={app.canStartNextVisit}
            onStartNextVisit={app.startNextVisit}
            onSelectVisit={app.selectVisit}
          />

          <main className="flex min-w-0 flex-1 flex-col">
            <div className="border-b border-slate-200 bg-white px-4 py-3 sm:px-6">
              {app.currentCourse ? (
                <div className="flex flex-wrap items-center gap-2 text-xs text-slate-700">
                  <span className="rounded-md bg-slate-100 px-2 py-1">
                    {t("Approach: {value}", locale, { value: getSchoolDisplayName(app.currentSchool, locale) })}
                  </span>
                  <span className="rounded-md bg-slate-100 px-2 py-1">
                    {t("Course: {value}", locale, { value: app.currentCourse.title || t("Untitled course", locale) })}
                  </span>
                  <span className="rounded-md bg-slate-100 px-2 py-1">
                    {t("Session: {value}", locale, { value: app.currentVisit ? `#${app.currentVisit.visit_no}` : t("Not started", locale) })}
                  </span>
                  <StatusPill
                    text={getCourseStatusText(app.currentCourse.status, locale)}
                    tone={getCourseTone(app.currentCourse.status)}
                  />
                  {app.currentVisit ? (
                    <StatusPill
                      text={getVisitStatusText(app.currentVisit.status, locale)}
                      tone={getVisitTone(app.currentVisit.status)}
                    />
                  ) : null}
                </div>
                ) : (
                  <p className="text-sm text-slate-600">
                    {t("Start with approach → course → session → messages: choose an approach and create a course.", locale)}
                  </p>
                )}
            </div>

            <ChatMessages
              currentCourse={app.currentCourse}
              currentVisit={app.currentVisit}
              currentSchool={app.currentSchool}
              locale={locale}
              isTyping={app.isTyping}
              chatEndRef={app.chatEndRef}
              hasToken={Boolean(app.token)}
            />

            <ChatInput
              currentCourse={app.currentCourse}
              currentVisit={app.currentVisit}
              locale={locale}
              input={app.input}
              isTyping={app.isTyping}
              onInputChange={app.setInput}
              onSend={app.sendMessage}
            />
          </main>

          <RightPanel currentCourse={app.currentCourse} currentVisit={app.currentVisit} locale={locale} />
        </div>
      </div>

      <MobileBottomSheet
        token={app.token}
        locale={locale}
        selectedSchoolId={app.selectedSchoolId}
        currentCourse={app.currentCourse}
        currentVisit={app.currentVisit}
        canCreateCourse={app.canCreateCourse}
        canStartNextVisit={app.canStartNextVisit}
        canCompleteCourse={app.canCompleteCourse}
        onOpenCreateCourseModal={() => app.setShowCreateCourseModal(true)}
        onStartNextVisit={app.startNextVisit}
        onContinueVisit={app.continueCurrentVisit}
        onCloseVisit={app.closeCurrentVisit}
        onOpenCompleteCourseModal={() => app.setShowCompleteCourseModal(true)}
      >
        <RightPanel currentCourse={app.currentCourse} currentVisit={app.currentVisit} locale={locale} embedded />
      </MobileBottomSheet>

      <AuthModal
        open={app.showAuthModal}
        locale={locale}
        user={app.user}
        authMode={app.authMode}
        authForm={app.authForm}
        onClose={() => app.setShowAuthModal(false)}
        onChangeMode={app.setAuthMode}
        onChangeForm={app.setAuthForm}
        onSubmit={app.handleAuth}
        onLogout={app.logout}
      />

      <SchoolModal
        open={app.showSchoolModal}
        locale={locale}
        token={app.token}
        schools={app.schools}
        selectedSchoolId={app.selectedSchoolId}
        currentSchool={app.currentSchool}
        onClose={() => app.setShowSchoolModal(false)}
        onSelectSchool={app.setSelectedSchoolId}
      />

      <CreateCourseModal
        open={app.showCreateCourseModal}
        locale={locale}
        currentSchool={app.currentSchool}
        onClose={() => app.setShowCreateCourseModal(false)}
        onSubmit={async (payload) => {
          const data = await app.createCourse(payload);
          if (data) {
            app.setShowCreateCourseModal(false);
            return true;
          }
          return false;
        }}
      />

      <CompleteCourseModal
        open={app.showCompleteCourseModal}
        locale={locale}
        currentCourse={app.currentCourse}
        onClose={() => app.setShowCompleteCourseModal(false)}
        onConfirm={app.completeCurrentCourse}
      />
    </div>
  );
}
