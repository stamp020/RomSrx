/* ---------- languages ----------

   English is the source language and the keys are the English strings
   themselves. That is deliberate: a missing translation falls back to
   readable English rather than to a bare key like `cart.empty.hint`, so the
   app is never worse than untranslated, and adding a string to the interface
   costs nothing until someone gets round to translating it.

   Loaded before app.js so `t()` exists by the time anything renders. */

const PT = {
  /* -- header -- */
  "Search": "Procurar",
  "Library": "Biblioteca",
  "Download list": "Lista de transferências",
  "Downloads": "Transferências",
  "Theme": "Tema",
  "Theme and language": "Tema e idioma",
  "archive.org account": "Conta archive.org",
  "Account": "Conta",
  "Reindex": "Reindexar",
  "Re-fetch file lists from archive.org": "Voltar a obter as listas de ficheiros do archive.org",
  "What's new in this version": "Novidades desta versão",
  "loading index…": "a carregar o índice…",
  "no index yet": "ainda sem índice",

  /* -- footer -- */
  "sources indexed": "fontes indexadas",
  "failed": "falharam",
  "last updated": "atualizado em",

  /* -- search -- */
  "Search for a game…": "Procurar um jogo…",
  "Clear search": "Limpar a pesquisa",
  "Console": "Consola",
  "Region": "Região",
  "Type": "Tipo",
  "No matches.": "Sem resultados.",
  "searching…": "a procurar…",
  "Filter": "Filtrar",
  "game": "jogo", "games": "jogos",
  "file": "ficheiro", "files": "ficheiros",
  "source": "fonte", "sources": "fontes",
  "Try a shorter or differently spelled title.": "Tente um título mais curto ou escrito de outra forma.",
  "No matches": "Sem resultados",
  "Load more": "Carregar mais",
  "Download": "Transferir",
  "Download now": "Transferir agora",
  "Queued": "Em fila",
  "Already queued": "Já está em fila",
  "Failed": "Falhou",
  "Server unreachable": "Servidor inacessível",
  "Add to download list": "Adicionar à lista de transferências",
  "Remove from list": "Remover da lista",
  "In Library": "Na biblioteca",
  "Show only games from RetroAchievements sets": "Mostrar apenas jogos de conjuntos RetroAchievements",
  "Showing only RetroAchievements sets — click to show everything": "A mostrar apenas conjuntos RetroAchievements — clique para mostrar tudo",
  "login": "início de sessão",
  "archive.org serves this item only to signed-in accounts": "o archive.org só disponibiliza este item a contas com sessão iniciada",

  /* -- first run -- */
  "Nothing indexed yet": "Ainda não há nada indexado",
  "Build the index": "Construir o índice",

  /* -- library -- */
  "Find in library…": "Procurar na biblioteca…",
  "Search your library": "Procurar na sua biblioteca",
  "Clear": "Limpar",
  "Covers": "Capas",
  "List": "Lista",
  "Titles": "Títulos",
  "Show game names under the covers": "Mostrar os nomes dos jogos por baixo das capas",
  "Cover size": "Tamanho das capas",
  "Rescan your folders for new games": "Voltar a analisar as suas pastas à procura de jogos novos",
  "Refresh": "Atualizar",
  "All consoles": "Todas as consolas",
  "Filter by console": "Filtrar por consola",
  "Order within each console": "Ordenar dentro de cada consola",
  "Name A–Z": "Nome A–Z",
  "Name Z–A": "Nome Z–A",
  "Largest first": "Maiores primeiro",
  "Smallest first": "Menores primeiro",
  "Select": "Selecionar",
  "Done": "Concluído",
  "Remove": "Remover",
  "No games found": "Nenhum jogo encontrado",
  "No games for that console.": "Nenhum jogo para essa consola.",
  "Select all on this console": "Selecionar todos desta consola",
  "Save cover image…": "Guardar imagem da capa…",
  "Set cover image…": "Definir imagem da capa…",
  "Remove custom cover": "Remover capa personalizada",
  "Open folder": "Abrir pasta",
  "Delete game from PC": "Eliminar jogo do PC",
  "Select every game shown": "Selecionar todos os jogos visíveis",
  "Pin to the top": "Fixar no topo",
  "Unpin": "Desafixar",
  "Move up": "Mover para cima",
  "Move down": "Mover para baixo",
  "Select all": "Selecionar todos",

  /* -- download list -- */
  "Compact": "Compacto",
  "Show more entries at once": "Mostrar mais entradas de uma vez",
  "Back to full-size covers": "Voltar às capas em tamanho normal",
  "Order the list": "Ordenar a lista",
  "Alphabetical (A–Z)": "Alfabética (A–Z)",
  "Alphabetical (Z–A)": "Alfabética (Z–A)",
  "Last added": "Adicionados por último",
  "First added": "Adicionados primeiro",
  "Added": "Adicionado",
  "Size": "Tamanho",
  "Name": "Nome",
  "Remove when downloaded": "Remover quando transferido",
  "As each download finishes, take it off this list": "À medida que cada transferência termina, retirá-la desta lista",
  "Download all": "Transferir tudo",
  "Copy URLs": "Copiar URLs",
  "Copied": "Copiado",
  "Copy failed": "Falha ao copiar",
  "Save .txt": "Guardar .txt",
  "No entries for this console.": "Sem entradas para esta consola.",
  "Nothing here yet — use the + button on any file.": "Ainda não há nada aqui — use o botão + em qualquer ficheiro.",
  "Downloads run inside the app, with resume and retry.": "As transferências correm dentro da aplicação, com retoma e nova tentativa.",
  "Queueing…": "A colocar em fila…",
  "Deselect all": "Desselecionar todos",
  "Download selected": "Transferir selecionados",
  "Remove selected": "Remover selecionados",
  "Resume all": "Retomar tudo",

  /* -- downloads panel -- */
  "Save to": "Guardar em",
  "Browse…": "Procurar…",
  "Choosing…": "A escolher…",
  "Choose a folder": "Escolher uma pasta",
  "Folder per console": "Pasta por consola",
  "Folders per console": "Pastas por consola",
  "Set folders": "Definir pastas",
  "Extract files after download": "Extrair ficheiros após a transferência",
  "into a folder of its own": "para uma pasta própria",
  "straight into the download folder": "diretamente para a pasta de transferências",
  "Where the contents of an archive go": "Para onde vai o conteúdo de um arquivo",
  "Delete archive after extraction": "Eliminar o arquivo após a extração",
  "At once": "Em simultâneo",
  "Saved": "Guardado",
  "Pause all": "Pausar tudo",
  "Clear finished": "Limpar concluídas",
  "Remove all": "Remover tudo",
  "Removing…": "A remover…",
  "Nothing downloading. Add files from your list.": "Nada a transferir. Adicione ficheiros a partir da sua lista.",
  "Downloading": "A transferir",
  "running": "a transferir", "queued": "em fila", "finished": "concluídas",
  "Paused": "Em pausa",
  "Finished": "Concluído",
  "Cancelled": "Cancelado",
  "Extracting…": "A extrair…",
  "Pause": "Pausar",
  "Resume": "Retomar",
  "next up": "a seguir",
  "extracted": "extraído",
  "unknown error": "erro desconhecido",
  "already downloaded": "já transferido",
  "Open containing folder": "Abrir a pasta que o contém",
  "Delete this download and its files from your PC": "Eliminar esta transferência e os seus ficheiros do PC",
  "Send back to the queue and let the next one start": "Devolver à fila e deixar começar a seguinte",
  "Move to the front of the queue": "Mover para o início da fila",
  "sign in to resume": "inicie sessão para retomar",
  "ask every time": "perguntar sempre",
  "Covers for this console are saved here without asking": "As capas desta consola são guardadas aqui sem perguntar",
  "Use the default": "Usar a predefinição",
  "Clear all": "Limpar tudo",
  "Each console has its own subfolder. Give one a different path to send it elsewhere — a folder inside the main one is remembered relative to it, so it moves if you change the main folder.":
    "Cada consola tem a sua própria subpasta. Dê a uma delas um caminho diferente para a enviar para outro lado — uma pasta dentro da principal é guardada em relação a esta, por isso acompanha-a se mudar a pasta principal.",
  "Everything shares the main folder. Give a console its own path here to split it out.":
    "Tudo partilha a pasta principal. Dê aqui um caminho próprio a uma consola para a separar.",

  /* -- account -- */
  "Email": "Email",
  "Password": "Palavra-passe",
  "Sign in": "Iniciar sessão",
  "Signing in…": "A iniciar sessão…",
  "Sign out": "Terminar sessão",
  "Sign-in failed.": "Falha ao iniciar sessão.",
  "Could not reach the local server.": "Não foi possível contactar o servidor local.",
  "Create a free account": "Criar uma conta gratuita",
  "Sign in to unlock login-only sources": "Inicie sessão para desbloquear as fontes que exigem conta",

  /* -- theme -- */
  "Language": "Idioma",
  "Tone": "Tom",
  "Colour": "Cor",
  "Default": "Predefinido",
  "Dark": "Escuro",
  "Light": "Claro",
  "Blue": "Azul", "Cyan": "Ciano", "Teal": "Turquesa", "Green": "Verde",
  "Gold": "Dourado", "Orange": "Laranja", "Red": "Vermelho",
  "Pink": "Rosa", "Purple": "Roxo",

  /* -- reindex -- */
  "Reindexing from archive.org": "A reindexar a partir do archive.org",
  "starting…": "a começar…",
  "Indexing… (click to watch)": "A indexar… (clique para acompanhar)",

  /* -- updates -- */
  "What's new": "Novidades",
  "Later": "Mais tarde",
  "Open release page": "Abrir a página da versão",
  "Check for updates": "Procurar atualizações",
  "Checking…": "A procurar…",
  "No notes for this release.": "Sem notas para esta versão.",

  /* -- shared -- */
  "OK": "OK",
  "Cancel": "Cancelar",
  "Close": "Fechar",
  "Fill the window": "Preencher a janela",
  "Shrink back to a panel": "Voltar a um painel",
  "Delete": "Eliminar",
  "Move": "Mover",
  "Scroll": "Deslocar",
  "Keyboard": "Teclado",
  "Options": "Opções",
  "Header": "Cabeçalho",
  "Back": "Voltar",
  "Stick": "Manípulo",
};

const LANGUAGES = { en: "English", pt: "Português (PT)" };
const TRANSLATIONS = { pt: PT };

let uiLang = "en";

/** Translate one string. Unknown strings come back unchanged, which is what
 *  makes partial translation safe. */
function t(text) {
  const table = TRANSLATIONS[uiLang];
  if (!table) return text;
  return table[text] ?? text;
}

/* Elements are translated from the English already in the markup, so nothing
   needs a made-up key. The original is stashed the first time round because
   the second pass would otherwise be translating a translation. */
const I18N_ATTRS = ["title", "aria-label", "placeholder", "label"];

/** The element's own words, as a text node.
 *
 *  Rewriting `textContent` would be simpler and quite wrong: half the labels
 *  in this app wrap something - `<label><input> Titles</label>`, buttons with
 *  an SVG beside the text - and replacing the content would throw the
 *  checkbox or the icon away. Only the text itself is touched. */
function wordsOf(el) {
  for (const node of el.childNodes) {
    if (node.nodeType === Node.TEXT_NODE && node.data.trim()) return node;
  }
  return null;
}

// `aria-label` -> `i18nAriaLabel`, matching how dataset spells attributes.
const datasetKey = (attr) =>
  `i18n${attr.replace(/(^|-)([a-z])/g, (_, __, c) => c.toUpperCase())}`;

function translateElement(el) {
  const node = wordsOf(el);
  if (node) {
    if (el.dataset.i18nText === undefined) el.dataset.i18nText = node.data.trim();
    // Whatever spacing the markup had is put back, so inline text keeps the
    // gap between it and its checkbox.
    const [, before, , after] = node.data.match(/^(\s*)(.*?)(\s*)$/s);
    node.data = before + t(el.dataset.i18nText) + after;
  }

  for (const attr of I18N_ATTRS) {
    const key = datasetKey(attr);
    if (el.dataset[key] === undefined) {
      if (!el.hasAttribute(attr)) continue;
      el.dataset[key] = el.getAttribute(attr);
    }
    el.setAttribute(attr, t(el.dataset[key]));
  }
}

/** Re-draw every marked-up string in the chosen language. */
function applyLanguage(lang) {
  uiLang = (lang === "en" || TRANSLATIONS[lang]) ? lang : "en";
  document.documentElement.lang = uiLang === "pt" ? "pt-PT" : "en";
  for (const el of document.querySelectorAll("[data-i18n]")) translateElement(el);
}
