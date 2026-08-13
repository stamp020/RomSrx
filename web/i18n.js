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

  /* -- playlists -- */
  "All games": "Todos os jogos",
  "Playlist": "Lista",
  "New playlist": "Nova lista",
  "New playlist…": "Nova lista…",
  "Playlist name": "Nome da lista",
  "Rename playlist": "Mudar o nome da lista",
  "Rename": "Mudar o nome",
  "Delete playlist": "Eliminar lista",
  "Create": "Criar",
  "Add to…": "Adicionar a…",
  "Add {n} games to…": "Adicionar {n} jogos a…",
  "Add to playlist": "Adicionar à lista",
  "Add to playlist…": "Adicionar à lista…",
  "Remove from playlist": "Remover da lista",
  "Remove from {name}": "Remover de {name}",
  "Remove from download list": "Remover da lista de transferências",
  "Add to the download list or a playlist": "Adicionar à lista de transferências ou a uma lista",
  "In your download list — click to change where this goes": "Na sua lista de transferências — clique para mudar o destino",
  "In a playlist — click to change where this goes": "Numa lista — clique para mudar o destino",
  "Not downloaded": "Não transferido",
  "not downloaded": "por transferir",
  "Download missing": "Transferir em falta",
  "Add missing to list": "Adicionar em falta à lista",
  "This playlist is empty": "Esta lista está vazia",
  "Nothing on this playlist yet — use the + button on any game, in the search or in your library.": "Ainda não há nada nesta lista — use o botão + em qualquer jogo, na pesquisa ou na sua biblioteca.",
  "Added to {name}.": "Adicionado a {name}.",
  "Taken off {name}.": "Removido de {name}.",
  "{n} taken off {name}.": "{n} removidos de {name}.",
  "{n} added to your download list.": "{n} adicionados à sua lista de transferências.",
  "They are all on your download list already.": "Já estão todos na sua lista de transferências.",
  "That file": "Esse ficheiro",
  "Your playlists could not be saved — is RomSrx still running? Changes made now will be lost when this window is closed.": "Não foi possível guardar as suas listas — o RomSrx ainda está em execução? As alterações feitas agora perder-se-ão ao fechar esta janela.",
  "Your download list could not be saved — is RomSrx still running? Changes made now will be lost when this window is closed.": "Não foi possível guardar a sua lista de transferências — o RomSrx ainda está em execução? As alterações feitas agora perder-se-ão ao fechar esta janela.",
  "Delete the playlist \"{name}\"?\n\nOnly the list goes — the {n} games on it are left exactly as they are, downloaded or not.": "Eliminar a lista \"{name}\"?\n\nApenas a lista desaparece — os {n} jogos que contém ficam exatamente como estão, transferidos ou não.",

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
  "Tell me when a download finishes": "Avisar quando uma transferência terminar",
  "Download finished": "Transferência concluída",
  "Downloaded {name}": "Transferido {name}",
  "Downloaded {name} and {n} more": "Transferido {name} e mais {n}",
  "Pick a console, or search for a game.": "Escolha uma consola ou procure um jogo.",
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
  "Backup": "Cópia de segurança",
  "Save a backup…": "Guardar uma cópia…",
  "Restore from a backup…": "Restaurar a partir de uma cópia…",
  "Restore": "Restaurar",
  "Get covers automatically": "Obter capas automaticamente",
  "Fetch the box art as each game for this console finishes downloading":
    "Obter a capa assim que cada jogo desta consola acabar de transferir",
  "Detect console folders": "Detetar pastas das consolas",
  "Looking…": "A procurar…",
  "Looks inside the main folder for one named after each console and links it. Nothing is moved or deleted.":
    "Procura na pasta principal uma pasta com o nome de cada consola e associa-a. Nada é movido nem eliminado.",
  "Nothing to change.\n\n{kept} consoles already point at a folder that is still there, and no folder named after any of the others turned up in:\n\n{roots}":
    "Nada a alterar.\n\n{kept} consolas já apontam para uma pasta que continua a existir, e não apareceu nenhuma pasta com o nome das restantes em:\n\n{roots}",
  "Linked {n}: {list}": "Associadas {n}: {list}",
  "Re-pointed {n} whose folder had moved: {list}":
    "Reapontadas {n} cuja pasta tinha mudado: {list}",
  "Left {n} already-working ones alone.": "Mantidas {n} que já funcionavam.",
  "Press Refresh in the library to see them sorted.":
    "Carregue em Atualizar na biblioteca para as ver organizadas.",
  "Take off this list and keep the files": "Retirar desta lista e manter os ficheiros",
  "Emulator": "Emulador",
  "Settings": "Definições",
  "All": "Tudo",
  "Look and language": "Aspeto e idioma",
  "Downloads/Paths": "Transferências/Pastas",
  "Paths": "Pastas",
  "Choose console…": "Escolher consola…",
  "Choose a console": "Escolher uma consola",
  "Games folder": "Pasta dos jogos",
  "Core": "Core",
  "Arguments": "Argumentos",
  "Delete covers with the game": "Eliminar as capas com o jogo",
  "When you remove a game from your PC through this app, its cover in the folder above goes too. Off, the image is left alone. Nothing else in that folder is ever touched.":
    "Quando remove um jogo do PC através desta aplicação, a capa na pasta acima também é eliminada. Desligado, a imagem fica intacta. Mais nada nessa pasta é alterado.",
  "As each game for this console finishes downloading, its box art is fetched and saved into the covers folder above. Needs that folder set.":
    "À medida que cada jogo desta consola acaba de transferir, a capa é obtida e guardada na pasta de capas acima. É preciso definir essa pasta.",
  "The program that plays this console's games.":
    "O programa que abre os jogos desta consola.",
  "RetroArch cannot open anything without a core. Pick the one for this console. Every other emulator leaves this blank.":
    "O RetroArch não abre nada sem um core. Escolha o desta consola. Todos os outros emuladores deixam isto em branco.",
  "Anything else the program wants, typed as you would type it. The game is added at the end unless you write {game} yourself.":
    "Tudo o resto que o programa precise, tal como o escreveria. O jogo é acrescentado no fim, a menos que escreva {game}.",
  "Each console downloads to its own subfolder of the folder above. Pick a console to override that, and to choose where its covers are saved and what plays the games.":
    "Cada consola transfere para a sua própria subpasta da pasta acima. Escolha uma consola para alterar isso e para definir onde as capas são guardadas e o que abre os jogos.",
  "Every console downloads to the folder above. Pick a console to give it a folder of its own, and to choose where its covers are saved and what plays the games.":
    "Todas as consolas transferem para a pasta acima. Escolha uma consola para lhe dar uma pasta própria e para definir onde as capas são guardadas e o que abre os jogos.",
  "Mute the download-finished sound": "Silenciar o som de transferência concluída",
  "Download sound is off — click to turn it on":
    "O som das transferências está desligado — clique para ligar",
  "Mute sound": "Silenciar",
  "Clear the folders, covers and emulators set for all {n} consoles?\n\nOnly the settings are cleared — no files are moved or deleted.":
    "Limpar as pastas, capas e emuladores definidos para as {n} consolas?\n\nSó as definições são limpas — nenhum ficheiro é movido ou eliminado.",
  "extra arguments, if the program needs any": "argumentos adicionais, se o programa precisar",
  "core — only RetroArch needs one": "core — só o RetroArch precisa de um",
  "Choose a core": "Escolher um core",
  "RetroArch cannot open anything without a core. Pick the one for this console.":
    "O RetroArch não abre nada sem um core. Escolha o desta consola.",
  "Extra arguments. The game is added at the end unless you write {game} yourself.":
    "Argumentos adicionais. O jogo é acrescentado no fim, a menos que escreva {game}.",
  "none": "nenhum",
  "Choose a program": "Escolher um programa",
  "Games for this console open in this program":
    "Os jogos desta consola abrem neste programa",
  "Play": "Jogar",
  "Continue playing": "Continuar a jogar",
  "Only games launched from this app are listed. This PC is not recording when files are read, so games opened straight from an emulator cannot be spotted. Turn it back on with: fsutil behavior set DisableLastAccess 2":
    "Só são listados os jogos abertos a partir desta aplicação. Este PC não regista quando os ficheiros são lidos, por isso não é possível detetar jogos abertos diretamente num emulador. Reative com: fsutil behavior set DisableLastAccess 2",
  "Delete cover file": "Eliminar ficheiro da capa",
  "No emulator is set for {console}.\n\nOpen Settings → Folders and emulators and choose one in the Emulator column, then try again.":
    "Não está definido nenhum emulador para {console}.\n\nAbra Definições → Pastas e emuladores e escolha um na coluna Emulador, depois tente novamente.",
  "Delete the cover file \"{name}\" from your PC?\n\nThis removes the image saved in this console's cover folder. The game itself is not touched.":
    "Eliminar o ficheiro da capa \"{name}\" do seu PC?\n\nIsto remove a imagem guardada na pasta de capas desta consola. O jogo em si não é afetado.",
  "There is no cover file to delete at {path}.": "Não existe nenhum ficheiro de capa para eliminar em {path}.",
  "Cover file deleted: {path}": "Ficheiro da capa eliminado: {path}",
  "Could not reach the app.": "Não foi possível contactar a aplicação.",
  "Each console downloads to its own subfolder of the folder above. Override any of it here, and choose where covers are saved and what plays the games.":
    "Cada consola transfere para a sua própria subpasta da pasta acima. Altere o que quiser aqui e escolha onde são guardadas as capas e o que abre os jogos.",
  "Every console downloads to the folder above. Give one a folder of its own here, and choose where covers are saved and what plays the games.":
    "Todas as consolas transferem para a pasta acima. Dê aqui uma pasta própria a uma delas e escolha onde são guardadas as capas e o que abre os jogos.",

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
  "Update available": "Atualização disponível",
  "Later": "Mais tarde",
  "Open release page": "Abrir a página da versão",
  "Check for updates": "Procurar atualizações",
  "Checking…": "A procurar…",
  "No notes for this release.": "Sem notas para esta versão.",

  /* -- messages ----------------------------------------------------------
     Whole sentences, with {placeholders} for the numbers and names. Split
     into fragments they could not be reordered, and Portuguese does not put
     its words where English does. */
  "Cover saved to {path}": "Capa guardada em {path}",
  "That game is no longer in your library.": "Esse jogo já não está na sua biblioteca.",
  "Delete {n} games from your PC?\n\nThe files are removed from disk, not just the list.\n\nThis can't be undone.":
    "Eliminar {n} jogos do seu PC?\n\nOs ficheiros são removidos do disco, não apenas da lista.\n\nIsto não pode ser anulado.",
  "Removed {done}. Could not remove {failed}:":
    "Removidos {done}. Não foi possível remover {failed}:",
  "Deleted {n} games and their covers.": "Eliminados {n} jogos e as respetivas capas.",
  "Deleted the game and its cover.": "Jogo e respetiva capa eliminados.",
  "Delete \"{name}\" from your PC?\n\nThe files are removed from disk, not just the list.":
    "Eliminar \"{name}\" do seu PC?\n\nOs ficheiros são removidos do disco, não apenas da lista.",
  "Delete \"{name}\" from your PC?\n\nThe file is removed from disk, along with any part-download. This can't be undone.":
    "Eliminar \"{name}\" do seu PC?\n\nO ficheiro é removido do disco, juntamente com qualquer transferência parcial. Isto não pode ser anulado.",
  "Remove all {n} downloads and delete their files from your PC?\n\nFinished files and part-downloads are both deleted.":
    "Remover todas as {n} transferências e eliminar os seus ficheiros do PC?\n\nSão eliminados tanto os ficheiros concluídos como as transferências parciais.",
  "{n} downloads need an archive.org account, so they have been paused.\n\nNothing is lost — sign back in and resume, and they pick up from where they stopped.":
    "{n} transferências precisam de uma conta archive.org, por isso foram colocadas em pausa.\n\nNada se perde — inicie sessão novamente e retome, e continuam de onde pararam.",
  "Could not reach GitHub to check for updates.": "Não foi possível contactar o GitHub para procurar atualizações.",
  "Could not check for updates - no connection.": "Não foi possível procurar atualizações — sem ligação.",
  "You're up to date. RomSrx {version} is the latest.":
    "Está atualizado. O RomSrx {version} é a versão mais recente.",
  "Could not reach GitHub to fetch the release notes.":
    "Não foi possível contactar o GitHub para obter as notas da versão.",

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
 *  makes partial translation safe.
 *
 *  `vars` fills `{name}` placeholders. Sentences are translated whole rather
 *  than glued together from pieces, because word order is not the same in
 *  every language and a sentence assembled in English order stops being a
 *  sentence anywhere else. */
function t(text, vars) {
  const table = TRANSLATIONS[uiLang];
  let out = (table && table[text]) ?? text;
  if (vars) {
    for (const [name, value] of Object.entries(vars)) {
      out = out.split(`{${name}}`).join(value);
    }
  }
  return out;
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
