import { createContext, useContext, useEffect, useMemo, useState } from "react";
import { containsSourceLanguageText } from "./locale.js";

const STRINGS = {
  "zh-CN": {
    "心理咨询工作台": ["Espaço de conversa", "Counseling workspace"],
    "心理咨询师工作台": ["Espaço de conversa", "Counseling workspace"],
    "选择咨询流派": ["Escolha uma abordagem", "Choose an approach"],
    "选择后会自动切换疗程列表。当前：": ["A lista de percursos será atualizada. Atual: ", "The course list will update. Current: "],
    "请选择流派": ["Selecione uma abordagem", "Select an approach"],
    "请先登录后再切换流派。": ["Entre para trocar de abordagem.", "Sign in to switch approaches."],
    "关闭": ["Fechar", "Close"],
    "新建疗程": ["Novo percurso", "New course"],
    "填写疗程标题后将自动创建第一次会谈。": ["A primeira sessão será criada automaticamente após informar o título.", "The first session will be created automatically after you enter a title."],
    "疗程标题": ["Título do percurso", "Course title"],
    "例如：焦虑管理与认知重建": ["Ex.: manejo da ansiedade e reavaliação cognitiva", "Example: anxiety management and cognitive reframing"],
    "取消": ["Cancelar", "Cancel"],
    "创建中...": ["Criando...", "Creating..."],
    "创建疗程": ["Criar percurso", "Create course"],
    "完成疗程": ["Concluir percurso", "Complete course"],
    "将把当前疗程标记为已完成。疗程：": ["Este percurso será marcado como concluído. Percurso: ", "This course will be marked as complete. Course: "],
    "处理中...": ["Processando...", "Processing..."],
    "确认完成": ["Confirmar conclusão", "Confirm completion"],
    "账户": ["Conta", "Account"],
    "请输入用户名和密码，或注册新账号。": ["Informe seu nome de usuário e senha ou crie uma conta.", "Enter your username and password, or create an account."],
    "用户名": ["Nome de usuário", "Username"],
    "密码": ["Senha", "Password"],
    "当前模式：": ["Modo atual: ", "Current mode: "],
    "登录": ["Entrar", "Sign in"],
    "注册": ["Criar conta", "Register"],
    "切换到": ["Mudar para ", "Switch to "],
    "退出登录": ["Sair", "Sign out"],
    "当前阶段": ["Etapa atual", "Current stage"],
    "咨询目标": ["Foco da sessão", "Session focus"],
    "支持与提醒": ["Informações e lembretes", "Information and reminders"],
    "未开始": ["Não iniciada", "Not started"],
    "选择疗程后可查看当前阶段与进度。": ["Selecione um percurso para ver a etapa e o progresso.", "Select a course to see its stage and progress."],
    "当前会谈暂无目标信息。": ["Não há foco registrado para esta sessão.", "No focus is recorded for this session."],
    "创建疗程后可在此查看和维护咨询目标。": ["Após criar um percurso, você poderá consultar e atualizar o foco aqui.", "After creating a course, you can view and update its focus here."],
    "AI 内容仅供参考，不替代专业医疗建议。": ["O conteúdo gerado por IA é apenas informativo e não substitui orientação profissional de saúde.", "AI-generated content is informational and does not replace professional healthcare advice."],
    "如遇紧急心理危机，请尽快联系当地急救资源或专业机构。": ["Em uma emergência, procure os serviços de emergência locais ou uma instituição especializada.", "In an emergency, contact local emergency services or a qualified organization."],
    "登录后即可开始咨询": ["Entre para começar", "Sign in to get started"],
    "请先登录账号，再选择咨询流派并创建疗程。": ["Entre, escolha uma abordagem e crie um percurso.", "Sign in, choose an approach, and create a course."],
    "先选择或创建疗程": ["Selecione ou crie um percurso", "Select or create a course"],
    "建议先在左侧选择流派并新建疗程，系统会自动创建第一次会谈。": ["Escolha uma abordagem e crie um percurso. A primeira sessão será criada automaticamente.", "Choose an approach and create a course. The first session will be created automatically."],
    "当前疗程还没有会谈内容": ["Ainda não há sessões neste percurso", "There are no sessions in this course yet"],
    "点击“开始第 N 次会谈”后，即可在此查看完整对话记录。": ["Selecione “Iniciar sessão N” para consultar a conversa completa.", "Select “Start session N” to view the full conversation."],
    "未命名疗程": ["Percurso sem título", "Untitled course"],
    "未选择": ["Não selecionada", "Not selected"],
    "未知阶段": ["Etapa desconhecida", "Unknown stage"],
    "进行中": ["Em andamento", "In progress"],
    "已完成": ["Concluído", "Completed"],
    "已归档": ["Arquivado", "Archived"],
    "已结束": ["Encerrada", "Ended"],
    "未知状态": ["Status desconhecido", "Unknown status"],
    "新建": ["Criar", "Create"],
    "继续当前会谈": ["Continuar sessão", "Continue session"],
    "结束本次会谈": ["Encerrar sessão", "End session"],
    "先创建疗程，再进入会谈流程。": ["Crie um percurso para iniciar as sessões.", "Create a course to begin sessions."],
    "疗程状态：": ["Percurso: ", "Course: "],
    "会谈状态：": ["Sessão: ", "Session: "],
    "请选择咨询流派": ["Selecione uma abordagem", "Select an approach"],
    "当前咨询流派": ["Abordagem atual", "Current approach"],
    "切换": ["Trocar", "Switch"],
    "请先选择咨询流派，再创建疗程。": ["Selecione uma abordagem antes de criar um percurso.", "Select an approach before creating a course."],
    "打开流派选择": ["Escolher abordagem", "Choose an approach"],
    "疗程列表": ["Percursos", "Courses"],
    "收起": ["Recolher", "Collapse"],
    "展开": ["Expandir", "Expand"],
    "当前阶段：": ["Etapa atual: ", "Current stage: "],
    "已进行会谈：": ["Sessões realizadas: ", "Sessions completed: "],
    "有进行中的会谈": ["Há uma sessão em andamento", "A session is in progress"],
    "暂无进行中的会谈": ["Nenhuma sessão em andamento", "No session in progress"],
    "当前流派下还没有疗程，请点击“新建疗程”开始。": ["Ainda não há percursos nesta abordagem. Selecione “Novo percurso” para começar.", "There are no courses for this approach yet. Select “New course” to begin."],
    "当前已选：": ["Selecionado: ", "Selected: "],
    "疗程列表已收起，点击“展开”查看全部疗程。": ["A lista está recolhida. Selecione “Expandir” para ver todos os percursos.", "The list is collapsed. Select “Expand” to view all courses."],
    "已登录：": ["Conectado: ", "Signed in: "],
    "登录 / 注册": ["Entrar / Criar conta", "Sign in / Register"],
    "开始第 ": ["Iniciar sessão ", "Start session "],
    " 次会谈": ["", ""],
    "当前没有进行中的会谈。": ["Não há sessão em andamento.", "There is no session in progress."],
    "当前会谈已结束，可开始下一次会谈。": ["Esta sessão foi encerrada. Você pode iniciar a próxima.", "This session has ended. You can start the next one."],
    "当前疗程尚未开始会谈，请点击“开始第 ": ["Ainda não há sessão neste percurso. Selecione “Iniciar sessão ", "No session has started for this course. Select “Start session "],
    " 次会谈”。": ["”.", "”."],
    "输入你的想法，按 Enter 发送，Shift + Enter 换行。": ["Escreva sua mensagem. Enter envia; Shift + Enter quebra a linha.", "Type your message. Enter sends; Shift + Enter adds a line break."],
    "AI 回答仅供参考，不替代专业医疗建议。如有紧急情况，请立即联系当地急救资源。": ["As respostas de IA são informativas e não substituem orientação profissional. Em emergências, procure os serviços locais.", "AI responses are informational and do not replace professional advice. In emergencies, contact local services."],
    "会谈时间线": ["Linha do tempo", "Session timeline"],
    "还未选择疗程": ["Nenhum percurso selecionado", "No course selected"],
    "还没有会谈记录": ["Ainda não há sessões", "No sessions yet"],
    "开始第 N 次会谈": ["Iniciar sessão N", "Start session N"],
    "信息": ["Informações", "Information"],
    "查看疗程信息": ["Ver informações do percurso", "View course information"],
    "第 ": ["Sessão ", "Session "],
    "条消息": [" mensagens", " messages"],
    "从“流派 -&gt; 疗程 -&gt; 会谈 -&gt; 消息”开始：先选择流派并创建疗程。": ["Para começar: escolha uma abordagem, crie um percurso e inicie uma sessão.", "To begin: choose an approach, create a course, and start a session."],
    "登录已过期，请重新登录后继续操作。": ["Sua sessão expirou. Entre novamente para continuar.", "Your session expired. Sign in again to continue."],
    "无法加载流派列表。": ["Não foi possível carregar as abordagens.", "Unable to load approaches."],
    "无法加载疗程列表。": ["Não foi possível carregar os percursos.", "Unable to load courses."],
    "无法加载疗程信息。": ["Não foi possível carregar as informações do percurso.", "Unable to load course information."],
    "无法加载会谈列表。": ["Não foi possível carregar a lista de sessões.", "Unable to load sessions."],
    "无法加载会谈。": ["Não foi possível carregar a sessão.", "Unable to load the session."],
    "请先登录。": ["Entre para continuar.", "Sign in to continue."],
    "请先选择咨询流派。": ["Selecione uma abordagem primeiro.", "Select an approach first."],
    "疗程创建成功，已自动创建第一次会谈。": ["Percurso criado; a primeira sessão foi iniciada automaticamente.", "Course created; the first session was started automatically."],
    "创建疗程失败。": ["Não foi possível criar o percurso.", "Unable to create the course."],
    "请先选择一个疗程。": ["Selecione um percurso primeiro.", "Select a course first."],
    "只有进行中的疗程才能开始新会谈。": ["Só é possível iniciar uma sessão em um percurso em andamento.", "A new session can only be started in an active course."],
    "当前疗程已有进行中的会谈。": ["Este percurso já tem uma sessão em andamento.", "This course already has a session in progress."],
    "已开始第 ": ["Sessão ", "Session "],
    " 次会谈。": [" iniciada.", " started."],
    "创建会谈失败。": ["Não foi possível iniciar a sessão.", "Unable to start the session."],
    "发送失败。": ["Não foi possível enviar a mensagem.", "Unable to send the message."],
    "当前会谈已结束。": ["Esta sessão foi encerrada.", "This session has ended."],
    "结束本次会谈失败。": ["Não foi possível encerrar a sessão.", "Unable to end the session."],
    "只有进行中的疗程才能完成。": ["Só é possível concluir um percurso em andamento.", "Only an active course can be completed."],
    "请先结束当前会谈，再完成疗程。": ["Encerre a sessão atual antes de concluir o percurso.", "End the current session before completing the course."],
    "疗程已完成。": ["Percurso concluído.", "Course completed."],
    "完成疗程失败。": ["Não foi possível concluir o percurso.", "Unable to complete the course."],
    "请输入用户名和密码。": ["Informe o nome de usuário e a senha.", "Enter a username and password."],
    "注册成功，已自动登录。": ["Conta criada e acesso iniciado.", "Account created and signed in."],
    "登录成功。": ["Acesso iniciado.", "Signed in."],
    "认证失败。": ["Não foi possível autenticar.", "Authentication failed."],
    "已退出登录。": ["Você saiu da conta.", "You have signed out."],
    "未知": ["Não informado", "Unknown"],
    "待澄清": ["A esclarecer", "To be clarified"],
    "当前困扰": ["Questão atual", "Current concern"],
    "来访者": ["Pessoa usuária", "Client"],
    "咨询师": ["Profissional", "Counselor"],
    "用户已存在": ["Este nome de usuário já existe.", "This username already exists."],
    "用户名或密码错误": ["Nome de usuário ou senha incorretos.", "Incorrect username or password."],
    "当前会谈已结束，无法继续发送消息": ["Esta sessão foi encerrada e não aceita novas mensagens.", "This session has ended and cannot receive new messages."],
    "当前疗程已有未结束的会谈": ["Este percurso já tem uma sessão não encerrada.", "This course already has an unfinished session."],
    "创建疗程失败，请稍后重试。": ["Não foi possível criar o percurso. Tente novamente mais tarde.", "Unable to create the course. Try again later."],
    "只有已完成的疗程才能归档": ["Somente percursos concluídos podem ser arquivados.", "Only completed courses can be archived."],
    "只有进行中的疗程才能开始新会谈": ["Só é possível iniciar uma sessão em um percurso em andamento.", "A new session can only be started in an active course."],
    "当前会谈已结束，进度已保存": ["Sessão encerrada; progresso salvo.", "Session ended; progress saved."],
    "会谈开场生成失败，请稍后重试": ["Não foi possível preparar a abertura da sessão. Tente novamente mais tarde.", "Unable to prepare the session opening. Try again later."],
    "大模型调用失败，请稍后重试": ["Não foi possível acessar o modelo. Tente novamente mais tarde.", "Unable to reach the model. Try again later."],
    "大模型返回为空，请稍后重试": ["O modelo retornou uma resposta vazia. Tente novamente mais tarde.", "The model returned an empty response. Try again later."],
    "Não foi possível conectar à API local. Verifique se o backend está em execução.": ["Não foi possível conectar à API local. Verifique se o backend está em execução.", "Could not connect to the local API. Check that the backend is running."],
    "Token de acesso não informado.": ["Token de acesso não informado.", "Access token was not provided."],
    "Token de acesso inválido.": ["Token de acesso inválido.", "Invalid access token."],
    "Usuário não encontrado.": ["Usuário não encontrado.", "User not found."],
    "Este nome de usuário já está em uso.": ["Este nome de usuário já está em uso.", "This username is already in use."],
    "Nome de usuário ou senha incorretos.": ["Nome de usuário ou senha incorretos.", "Incorrect username or password."],
    "Percurso não encontrado.": ["Percurso não encontrado.", "Course not found."],
    "Sessão não encontrada.": ["Sessão não encontrada.", "Session not found."],
    "Acesso não autorizado.": ["Acesso não autorizado.", "Access is not authorized."],
    "Abordagem não encontrada.": ["Abordagem não encontrada.", "Approach not found."],
    "A abordagem selecionada não está disponível.": ["A abordagem selecionada não está disponível.", "The selected approach is unavailable."],
    "Não foi possível criar o percurso. Tente novamente.": ["Não foi possível criar o percurso. Tente novamente.", "Unable to create the course. Try again."],
    "Encerre a sessão atual antes de concluir o percurso.": ["Encerre a sessão atual antes de concluir o percurso.", "End the current session before completing the course."],
    "Somente percursos concluídos podem ser arquivados.": ["Somente percursos concluídos podem ser arquivados.", "Only completed courses can be archived."],
    "Só é possível iniciar uma sessão em um percurso em andamento.": ["Só é possível iniciar uma sessão em um percurso em andamento.", "A session can only be started in an active course."],
    "Este percurso já tem uma sessão em andamento.": ["Este percurso já tem uma sessão em andamento.", "This course already has a session in progress."],
    "Esta sessão já foi encerrada.": ["Esta sessão já foi encerrada.", "This session has already ended."],
    "Esta sessão foi encerrada e não aceita novas mensagens.": ["Esta sessão foi encerrada e não aceita novas mensagens.", "This session has ended and cannot accept new messages."],
    "Não foi possível preparar a abertura da sessão. Tente novamente.": ["Não foi possível preparar a abertura da sessão. Tente novamente.", "Unable to prepare the session opening. Try again."],
    "Não foi possível gerar uma resposta. Tente novamente.": ["Não foi possível gerar uma resposta. Tente novamente.", "Unable to generate a response. Try again."],
    "O serviço de geração retornou uma resposta vazia. Tente novamente.": ["O serviço de geração retornou uma resposta vazia. Tente novamente.", "The generation service returned an empty response. Try again."],
    "Este campo é obrigatório.": ["Este campo é obrigatório.", "This field is required."],
    "Os dados informados são inválidos.": ["Os dados informados são inválidos.", "The provided data is invalid."],
    "O tipo de dado informado não é válido.": ["O tipo de dado informado não é válido.", "The provided data type is invalid."],
    "O valor informado é menor que o mínimo permitido.": ["O valor informado é menor que o mínimo permitido.", "The value is below the minimum allowed."],
    "O valor informado excede o limite permitido.": ["O valor informado excede o limite permitido.", "The value exceeds the allowed limit."],
    "O valor informado está fora do intervalo permitido.": ["O valor informado está fora do intervalo permitido.", "The value is outside the allowed range."],
    "O valor informado não corresponde a uma opção válida.": ["O valor informado não corresponde a uma opção válida.", "The value does not match a valid option."],
    "O corpo da solicitação contém JSON inválido.": ["O corpo da solicitação contém JSON inválido.", "The request body contains invalid JSON."],
  },
};

const LocaleContext = createContext(null);

export function LocaleProvider({ children }) {
  const [locale, setLocaleState] = useState(() => localStorage.getItem("psicoia-locale") || "pt-BR");
  const setLocale = (value) => {
    const next = value === "en" ? "en" : "pt-BR";
    localStorage.setItem("psicoia-locale", next);
    setLocaleState(next);
  };
  useEffect(() => {
    document.documentElement.lang = locale === "en" ? "en" : "pt-BR";
  }, [locale]);
  const value = useMemo(() => ({
    locale,
    setLocale,
    t: (source) => {
      const text = String(source ?? "");
      const known = STRINGS["zh-CN"][text];
      if (known) return known[locale === "en" ? 1 : 0];
      if (locale === "en") {
        const requestFailure = text.match(/^Falha na solicitação \(status (\d+)\)\.$/);
        if (requestFailure) return `Request failed (status ${requestFailure[1]}).`;
      }
      if (containsSourceLanguageText(text)) {
        return locale === "en"
          ? `Untranslated source-language text: ${text}`
          : `Texto não traduzido no idioma de origem: ${text}`;
      }
      return text;
    },
  }), [locale]);
  return <LocaleContext.Provider value={value}>{children}</LocaleContext.Provider>;
}

export function useLocale() {
  const value = useContext(LocaleContext);
  if (!value) throw new Error("useLocale must be used within LocaleProvider");
  return value;
}
