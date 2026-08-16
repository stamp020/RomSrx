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

  /* -- RetroAchievements -- */
  "Open on RetroAchievements": "Abrir no RetroAchievements",
  "Open RetroAchievements": "Abrir o RetroAchievements",
  "Patches & supported files": "Patches e ficheiros suportados",
  "Download patch": "Transferir patch",
  "Automatic Patch": "Patch automático",
  "Patch a game online": "Aplicar um patch online",
  "Replace the game with the patched version":
    "Substituir o jogo pela versão com patch",
  "Off, a patched copy is written next to the game and your file is kept. On, the patched version takes the game's name and the original is deleted.":
    "Desligado, é criada uma cópia com patch ao lado do jogo e o teu ficheiro é mantido. Ligado, a versão com patch fica com o nome do jogo e o original é apagado.",
  "Save patches to": "Guardar patches em",
  "Search index (large)": "Índice de pesquisa (grande)",
  "Emulator saves": "Saves dos emuladores",
  "Prefer copies from": "Preferir cópias de",
  "The copy listed first for every game, and the one a game card offers by default. Nothing is hidden — the other regions are still there underneath.":
    "A cópia listada em primeiro lugar para cada jogo, e a que o cartão do jogo oferece por omissão. Nada é escondido — as outras regiões continuam lá por baixo.",
  "Make a disc playlist (.m3u)": "Criar uma playlist de discos (.m3u)",
  "Made \"{name}\", listing {n} discs.\n\nPoint your emulator at that file instead of a single disc and it can swap them itself.":
    "Criado \"{name}\", com {n} discos.\n\nAponta o teu emulador para esse ficheiro em vez de um disco só e ele pode trocá-los sozinho.",
  "Could not make the playlist.": "Não foi possível criar a playlist.",
  "This game is not in several discs, or the other discs are not in the same folder.":
    "Este jogo não está em vários discos, ou os outros discos não estão na mesma pasta.",
  "Where your space has gone": "Para onde foi o teu espaço",
  "What to play next": "O que jogar a seguir",
  "to beat": "para terminar",
  "to master": "para dominar",
  "Fastest to beat": "Mais rápidos de terminar",
  "Order by": "Ordenar por",
  "Best match": "Melhor correspondência",
  "timing…": "a cronometrar…",
  "ranking the {total} games loaded so far":
    "a ordenar os {total} jogos carregados até agora",
  "ranking {n} of the {total} loaded — {left} still to time":
    "a ordenar {n} dos {total} carregados — faltam {left} por cronometrar",
  "could not time these": "não foi possível cronometrar estes",
  "{n} more still being timed — pick this sort again in a moment.":
    "Faltam {n} por cronometrar — escolhe esta ordem outra vez daqui a pouco.",
  "Fastest to master": "Mais rápidos de dominar",
  "Tidy up": "Arrumar",
  "{n} things still point at games that are no longer here — hand-picked covers, per-game emulators and recently played.":
    "{n} coisas ainda apontam para jogos que já não estão aqui — capas escolhidas à mão, emuladores por jogo e jogados recentemente.",
  "Removed {n}.": "Removidos {n}.",
  "Could not tidy those away.": "Não foi possível arrumar isso.",
  "What next": "A seguir",
  "Games you have never started. Times are how long RetroAchievements' players actually took, in hardcore.":
    "Jogos que nunca começaste. Os tempos são o que os jogadores do RetroAchievements demoraram mesmo, em hardcore.",
  /* The same window asked of a playlist, where a game you have not downloaded
     is as good an answer as one you have. */
  "Games on “{name}” you have never started, the ones you have not downloaded included. Times are how long RetroAchievements' players actually took, in hardcore.":
    "Jogos em “{name}” que nunca começaste, incluindo os que ainda não transferiste. Os tempos são o que os jogadores do RetroAchievements demoraram mesmo, em hardcore.",
  "Looking these up…": "A procurar…",
  "Nothing to suggest — either everything on the shelf has been started, or RetroAchievements has no times for the ones that haven't.":
    "Nada a sugerir — ou já começaste tudo o que tens, ou o RetroAchievements não tem tempos para o que falta.",
  "Nothing to suggest — either everything on this playlist has been started, or RetroAchievements has no times for the ones that haven't.":
    "Nada a sugerir — ou já começaste tudo o que está nesta lista, ou o RetroAchievements não tem tempos para o que falta.",
  "Click one to play it.": "Clica num para jogar.",
  "Include games you have played": "Incluir jogos que já jogaste",
  "Every game here RetroAchievements has a time for, whether or not you have played it. Times are how long their players actually took, in hardcore.":
    "Todos os jogos aqui para os quais o RetroAchievements tem tempo, tenhas jogado ou não. Os tempos são o que os seus jogadores demoraram mesmo, em hardcore.",
  "Every game on “{name}” RetroAchievements has a time for, played or not, downloaded or not. Times are how long their players actually took, in hardcore.":
    "Todos os jogos em “{name}” para os quais o RetroAchievements tem tempo, jogados ou não, transferidos ou não. Os tempos são o que os seus jogadores demoraram mesmo, em hardcore.",
  "RetroAchievements has no times for anything on this shelf.":
    "O RetroAchievements não tem tempos para nada nesta prateleira.",
  "Click one to play it, or to fetch one you haven't got yet.":
    "Clica num para jogar, ou para transferir um que ainda não tens.",
  "Not downloaded — click to fetch": "Não transferido — clica para transferir",
  "{n} achievements": "{n} conquistas",
  "Storage": "Armazenamento",
  "By console": "Por consola",
  "Biggest games": "Jogos maiores",
  "in total": "no total",
  "never started": "nunca iniciados",
  "sitting unused": "por usar",
  "{n} games": "{n} jogos",
  "Sizes are what is on your disk. A game kept as a folder counts everything in it.":
    "Os tamanhos são o que está no teu disco. Um jogo guardado como pasta conta tudo o que tem lá dentro.",
  "Nothing on the shelf yet.": "Ainda não há nada na estante.",
  "none found": "nenhum encontrado",
  "{n} files, {size}": "{n} ficheiros, {size}",
  "Save files and save states from RetroArch, PCSX2 and DuckStation, wherever they are installed. Restoring puts them in a folder of their own rather than over whatever you have played since — nothing of yours is overwritten.":
    "Ficheiros de save e save states do RetroArch, PCSX2 e DuckStation, onde quer que estejam instalados. Ao restaurar são colocados numa pasta própria em vez de por cima do que jogaste entretanto — nada teu é substituído.",
  "Get cores": "Obter cores",
  "Getting {n} of {total}…": "A obter {n} de {total}…",
  "{got} downloaded, {already} already there, {skipped} skipped.":
    "{got} transferidos, {already} já existiam, {skipped} ignorados.",
  "These were left alone, because RomSrx has no core to recommend for them or RetroArch is not set as their emulator:\n\n{list}":
    "Estes ficaram por alterar, porque o RomSrx não tem core a recomendar para eles ou o RetroArch não está definido como o seu emulador:\n\n{list}",
  "Get": "Obter",
  "Getting…": "A obter…",
  "Download the best core for this console and use it":
    "Transferir o melhor core para esta consola e usá-lo",
  "Installed {core} and set it for {console}.":
    "{core} instalado e definido para {console}.",
  "{core} was already installed. Set it for {console}.":
    "O {core} já estava instalado. Definido para {console}.",
  "Set RetroArch as this console's emulator first - the core has to go in its cores folder.":
    "Define primeiro o RetroArch como emulador desta consola — o core tem de ficar na pasta cores dele.",
  "That download holds no core.": "Essa transferência não contém nenhum core.",
  "The downloaded core could not be opened.":
    "Não foi possível abrir o core transferido.",
  "That download is far larger than a core.":
    "Essa transferência é muito maior do que um core.",
  "Emulator for this game": "Emulador para este jogo",
  "Emulator for this game…": "Emulador para este jogo…",
  "Leave a box empty to use the console's own setting. Anything filled in here applies to this game only.":
    "Deixa uma caixa vazia para usar a definição da consola. O que preencheres aqui aplica-se apenas a este jogo.",
  "The console's emulator": "O emulador da consola",
  "The console's core": "O core da consola",
  "The console's arguments": "Os argumentos da consola",
  "Use the console's settings": "Usar as definições da consola",
  "Saved for this game only.": "Guardado apenas para este jogo.",
  "This game uses its console's settings again.":
    "Este jogo volta a usar as definições da consola.",
  "Patch a game": "Aplicar um patch a um jogo",
  "Patch with a file…": "Aplicar patch a partir de um ficheiro…",
  "Pick the game and the patch to put on it. A patched copy is written next to the game — your own file is not changed.":
    "Escolhe o jogo e o patch a aplicar. É criada uma cópia com o patch ao lado do jogo — o teu ficheiro não é alterado.",
  "Game": "Jogo",
  "Patch": "Patch",
  "No game chosen": "Nenhum jogo escolhido",
  "No patch chosen": "Nenhum patch escolhido",
  "Choose…": "Escolher…",
  "Patch online instead…": "Aplicar online em vez disso…",
  "Choose a game and a patch first.": "Escolhe primeiro um jogo e um patch.",
  "Working… large discs take a minute or so.":
    "A trabalhar… discos grandes demoram cerca de um minuto.",
  "Done — \"{name}\", with its own .cue beside it.":
    "Pronto — \"{name}\", com um .cue próprio ao lado.",
  "Done — \"{name}\", next to your original.":
    "Pronto — \"{name}\", ao lado do teu original.",
  "That patch file is no longer where it was.":
    "Esse ficheiro de patch já não está onde estava.",
  "There is no patch to apply.": "Não há nenhum patch para aplicar.",
  "That file is far larger than a patch.": "Esse ficheiro é muito maior do que um patch.",
  "Replace the game": "Substituir o jogo",
  "That setting could not be saved, so nothing was patched.":
    "Não foi possível guardar essa definição, por isso nada foi alterado.",

  "A patch is a list of changes to make to a game you already have — a translation, a fan hack, or a fix a set needs.\n\nYou have chosen to replace the game: the patched version will take its name and YOUR ORIGINAL FILE WILL BE DELETED. If you want to keep it, turn that off in Settings → Downloads first.\n\nLarge discs take a minute or so.":
    "Um patch é uma lista de alterações a fazer a um jogo que já tens — uma tradução, um hack ou uma correção necessária para um conjunto de troféus.\n\nEscolheste substituir o jogo: a versão com patch fica com o nome dele e O TEU FICHEIRO ORIGINAL SERÁ APAGADO. Se o quiseres manter, desliga essa opção em Definições → Transferências primeiro.\n\nDiscos grandes demoram cerca de um minuto.",
  "Done. \"{name}\" is now the patched version, and your original has been deleted, as that setting asks.":
    "Pronto. \"{name}\" é agora a versão com patch, e o teu original foi apagado, como essa opção pede.",
  "Patch it": "Aplicar",
  "A patch is a list of changes to make to a game you already have — a translation, a fan hack, or a fix a set needs.\n\nRomSrx will download it and write a patched copy next to your game. Your download is not changed, so you can delete the copy if you don't want it.\n\nLarge discs take a minute or so.":
    "Um patch é uma lista de alterações a fazer a um jogo que já tens — uma tradução, um hack ou uma correção necessária para um conjunto de troféus.\n\nO RomSrx transfere-o e cria uma cópia com o patch ao lado do teu jogo. A tua transferência não é alterada, por isso podes apagar a cópia se não a quiseres.\n\nDiscos grandes demoram cerca de um minuto.",
  "Done. Play \"{name}\" — its own .cue was made beside it.\n\nYour original is still there, unchanged.":
    "Pronto. Joga \"{name}\" — foi criado um .cue próprio ao lado.\n\nO teu original continua lá, inalterado.",
  "Done. Play \"{name}\".\n\nIt is next to your original, which is unchanged.":
    "Pronto. Joga \"{name}\".\n\nEstá ao lado do teu original, que não foi alterado.",
  "Restart now": "Reiniciar agora",
  "Close this window when it finishes": "Fechar esta janela quando terminar",
  "Use the full width of the window": "Usar toda a largura da janela",
  "Restarting…": "A reiniciar…",
  "Your games are never included. The search index is only there if you tick it — it is large, and it can always be rebuilt from archive.org instead.":
    "Os teus jogos nunca são incluídos. O índice de pesquisa só é guardado se o selecionares — é grande e pode sempre ser reconstruído a partir do archive.org.",
  "Beside the downloads, in Patches": "Junto às transferências, em Patches",
  "Downloading the patch…": "A transferir o patch…",
  "Patch saved to {path}": "Patch guardado em {path}",
  "There is no patch to download.": "Não há nenhum patch para transferir.",
  "Patch this game online…": "Aplicar patch a este jogo online…",
  "Applying the patch…": "A aplicar o patch…",
  "Which patch?": "Qual patch?",
  "Apply": "Aplicar",
  "Patched copy saved to {path}": "Cópia com patch guardada em {path}",
  /* The patcher's refusals, the ones a person actually runs into. Anything
     not here falls back to the English, which is better than nothing. */
  "This patch is for a different dump of the game. The file is the right size but not the one it expects.":
    "Este patch é para uma versão diferente do jogo. O ficheiro tem o tamanho certo mas não é o que o patch espera.",
  "This app can only patch cartridge ROMs, and that file is not one.":
    "Esta aplicação só aplica patches a ROMs de cartucho, e esse ficheiro não é uma.",
  "That folder holds several ROMs, so which to patch is not clear.":
    "Essa pasta tem várias ROMs, por isso não é claro qual delas deve levar o patch.",
  "That archive holds several ROMs, so which to patch is not clear.":
    "Esse ficheiro tem várias ROMs, por isso não é claro qual delas deve levar o patch.",
  "That download is not a patch or an archive of one.":
    "Essa transferência não é um patch nem um ficheiro que contenha um.",
  "This xdelta patch is compressed in a way this app cannot read. Use xdelta3 or a tool that supports it.":
    "Este patch xdelta está comprimido de uma forma que esta aplicação não consegue ler. Usa o xdelta3 ou uma ferramenta que o suporte.",
  "This xdelta patch carries its own instruction table, which this app cannot read.":
    "Este patch xdelta traz a sua própria tabela de instruções, que esta aplicação não consegue ler.",
  "This patch was written for a newer xdelta than this app knows.":
    "Este patch foi criado para uma versão do xdelta mais recente do que esta aplicação conhece.",
  "The patch claims an implausibly large result.":
    "O patch indica um resultado de tamanho implausível.",
  "That patch download is far larger than a patch.":
    "Essa transferência é muito maior do que um patch.",
  "This patch is a .7z and py7zr isn't available.":
    "Este patch é um .7z e o py7zr não está disponível.",
  "The patched file did not come out as the patch expects.":
    "O ficheiro final não ficou como o patch esperava.",
  "That game is no longer where the library says.":
    "Esse jogo já não está onde a biblioteca indica.",
  "That download holds no patch this app can read.":
    "Essa transferência não contém nenhum patch que esta aplicação consiga ler.",
  "This file is not a patch this app recognises.":
    "Este ficheiro não é um patch reconhecido por esta aplicação.",
  "There is no ROM inside that archive.": "Não existe nenhuma ROM dentro desse ficheiro.",
  "No ROM was found in that game's folder.":
    "Não foi encontrada nenhuma ROM na pasta desse jogo.",
  "The patch file is damaged.": "O ficheiro do patch está danificado.",
  "Web pages": "Páginas web",
  "Open game pages in": "Abrir páginas de jogos em",
  "A window of this app": "Uma janela desta aplicação",
  "My default browser": "O meu navegador predefinido",

  /* -- folded menu groups -- */
  "Patches": "Patches",
  "Cover image": "Imagem de capa",

  /* -- the preview panel -- */
  "Preview": "Pré-visualizar",
  "{done} of {total} achievements": "{done} de {total} conquistas",
  "You have earned": "Já conquistaste",
  "In hardcore, the total the site counts.": "Em hardcore, o total que o site conta.",
  "{n}% of the set": "{n}% do conjunto",
  "RetroAchievements username": "Nome de utilizador do RetroAchievements",
  "for your achievement progress": "para o teu progresso de conquistas",
  "Save image…": "Guardar imagem…",
  "more": "mais",
  "Previous": "Anterior",
  "Next": "Seguinte",
  "{n} of {total}": "{n} de {total}",
  "Play": "Jogar",
  "Looking this game up…": "A procurar este jogo…",
  "Times and points from RetroAchievements; medians of their players' own times rather than estimates.":
    "Tempos e pontos do RetroAchievements; medianas dos tempos reais dos seus jogadores, e não estimativas.",
  "RetroAchievements has no achievement set for this game, so there are no times or points to show.":
    "O RetroAchievements não tem conjunto de conquistas para este jogo, por isso não há tempos nem pontos a mostrar.",

  /* -- how long to beat -- */
  "How Long / Achievements": "Duração / Conquistas",
  "Achievements": "Conquistas",
  "Points": "Pontos",
  "RetroPoints": "RetroPoints",
  "RetroRatio": "RetroRatio",
  "Beat the game": "Terminar o jogo",
  "Reaching the ending, in hardcore — no save states, no rewind.":
    "Chegar ao fim, em hardcore — sem save states, sem rebobinar.",
  "Master it": "Dominar",
  "Every achievement, also in hardcore.":
    "Todas as conquistas, também em hardcore.",
  "Asking…": "A perguntar…",
  "{n} min": "{n} min",
  "{h} h": "{h} h",
  "{h} h {m} min": "{h} h {m} min",
  "from {n} players": "de {n} jogadores",
  "Medians of RetroAchievements players' own times, not estimates — so one person leaving the emulator running does not move them.":
    "Medianas dos tempos reais dos jogadores do RetroAchievements, e não estimativas — por isso alguém que deixe o emulador a correr não as altera.",
  "Add your RetroAchievements Web API key in Settings → Cover art, and this can ask them how long the game takes.":
    "Adicione a sua chave da Web API do RetroAchievements em Definições → Capas, e isto poderá perguntar-lhes quanto tempo demora o jogo.",
  "RetroAchievements has no achievement set for this game, so nobody has been timed playing it.":
    "O RetroAchievements não tem conjunto de conquistas para este jogo, por isso ninguém foi cronometrado a jogá-lo.",
  "This game has a set, but nobody has finished it in hardcore often enough for a median to mean anything yet.":
    "Este jogo tem conjunto, mas ainda ninguém o terminou em hardcore vezes suficientes para que uma mediana signifique alguma coisa.",
  "RetroAchievements would not accept your API key.":
    "O RetroAchievements não aceitou a sua chave de API.",
  "Could not reach RetroAchievements.":
    "Não foi possível contactar o RetroAchievements.",

  /* -- the achievements themselves, under the times -- */
  "Load achievements": "Carregar conquistas",
  "Loading…": "A carregar…",
  "Check for ones you have just earned": "Procurar as que acabou de ganhar",
  "Refresh achievements": "Atualizar conquistas",
  "Which achievements to show": "Que conquistas mostrar",
  "Order the achievements": "Ordenar as conquistas",
  "All achievements": "Todas as conquistas",
  "Still locked": "Ainda por desbloquear",
  "Unlocked": "Desbloqueadas",
  "Missable only": "Só as que se podem perder",
  "Progression only": "Só as de progressão",
  "Set order": "Ordem do conjunto",
  "Most points": "Mais pontos",
  "Rarest first": "Mais raras primeiro",
  "Missable": "Pode perder-se",
  "Progression": "Progressão",
  "Win condition": "Condição de vitória",
  "{done} of {total} earned": "{done} de {total} ganhas",
  "{n} pts": "{n} pts",
  "{n} RP": "{n} RP",
  "{n}% have this": "{n}% têm esta",
  "None of them match that.": "Nenhuma corresponde a isso.",
  "Open this achievement on RetroAchievements":
    "Abrir esta conquista no RetroAchievements",
  "Click one to open it on RetroAchievements. Unlocks are counted in hardcore, and can take a few minutes to appear.":
    "Clica numa para a abrir no RetroAchievements. Os desbloqueios são contados em hardcore e podem demorar alguns minutos a aparecer.",
  "Add your RetroAchievements username in Settings → Cover art to see which of these you have earned.":
    "Adicione o seu nome de utilizador do RetroAchievements em Definições → Capas para ver quais destas já ganhou.",
  "Add your RetroAchievements Web API key in Settings → Cover art, and this can list the set.":
    "Adicione a sua chave da Web API do RetroAchievements em Definições → Capas, e isto poderá listar o conjunto.",
  "RetroAchievements has no achievement set for this game.":
    "O RetroAchievements não tem conjunto de conquistas para este jogo.",
  "RetroAchievements has no achievements listed for this game.":
    "O RetroAchievements não tem conquistas listadas para este jogo.",

  /* -- which copies of a game the achievement set was built from -- */
  "RA": "RA",
  "patch": "patch",
  "Check which copies here work with RetroAchievements":
    "Ver que cópias aqui funcionam com o RetroAchievements",
  "Clear the RetroAchievements marks on this game":
    "Limpar as marcas do RetroAchievements neste jogo",
  "Hide this note": "Ocultar esta nota",
  "Asking RetroAchievements which copies its set accepts…":
    "A perguntar ao RetroAchievements que cópias o seu conjunto aceita…",
  "{n} of the copies here are what the set was built from":
    "{n} das cópias aqui são aquelas de que o conjunto foi feito",
  "RetroAchievements' set is built from this exact file.":
    "O conjunto do RetroAchievements foi feito exatamente a partir deste ficheiro.",
  "RetroAchievements' set is built from this file, with a patch applied.":
    "O conjunto do RetroAchievements foi feito a partir deste ficheiro, com um patch aplicado.",
  "{n} of these {total} copies are dumps the achievement set was built from, marked below. Checked by name against the {listed} files RetroAchievements lists for {where} — the certain answer is the file's own hash, which only the download itself can give.":
    "{n} destas {total} cópias são dumps de que o conjunto de conquistas foi feito, marcados abaixo. Verificado por nome com os {listed} ficheiros que o RetroAchievements lista para {where} — a resposta certa é o hash do próprio ficheiro, que só a transferência pode dar.",
  "None of these {total} copies is among the {listed} files RetroAchievements lists for {where}. Another source may still have one.":
    "Nenhuma destas {total} cópias está entre os {listed} ficheiros que o RetroAchievements lista para {where}. Outra fonte pode ainda ter uma.",
  "{n} other systems on this card have no set, so their copies were not checked.":
    "Outros {n} sistemas neste cartão não têm conjunto, por isso as suas cópias não foram verificadas.",
  "Add your RetroAchievements Web API key in Settings → Cover art, and this can check which copies their set accepts.":
    "Adicione a sua chave da Web API do RetroAchievements em Definições → Capas, e isto poderá ver que cópias o conjunto aceita.",
  "RetroAchievements lists no files for this game's set.":
    "O RetroAchievements não lista ficheiros para o conjunto deste jogo.",

  /* -- the achievements window, and the shelf's own controls -- */
  "Unlocks are counted in hardcore, and can take a few minutes to appear. Click one to open it on RetroAchievements.":
    "Os desbloqueios são contados em hardcore e podem demorar alguns minutos a aparecer. Clica numa para a abrir no RetroAchievements.",
  "No game was named.": "Nenhum jogo foi indicado.",
  "Achievements": "Conquistas",
  "Library": "Biblioteca",
  "Clicking a cover": "Clicar numa capa",
  "Plays the game": "Joga o jogo",
  "Opens the preview": "Abre a pré-visualização",
  "With the preview, a play button appears on every cover and in every list row, so starting a game is still one click - it is just a different one.":
    "Com a pré-visualização, aparece um botão de jogar em cada capa e em cada linha da lista, por isso começar um jogo continua a ser um clique — só que outro.",
  "Open the achievement list when a game starts":
    "Abrir a lista de conquistas quando um jogo começa",
  "A window of this app's own, beside the game, listing every achievement in the set and which of them you have. Only for games RetroAchievements has a set for; nothing opens for the rest.":
    "Uma janela da própria aplicação, ao lado do jogo, com todas as conquistas do conjunto e quais já tens. Só para jogos com conjunto no RetroAchievements; para os outros não abre nada.",
  "Show how long each game takes": "Mostrar quanto tempo demora cada jogo",
  "No times on covers": "Sem tempos nas capas",
  "Show time to beat": "Mostrar tempo para terminar",
  "Show time to master": "Mostrar tempo para dominar",
  "Show both times": "Mostrar ambos os tempos",
  "beat": "terminar",
  "master": "dominar",

  /* -- who is signed in to RetroAchievements -- */
  "Your RetroAchievements profile": "O teu perfil no RetroAchievements",
  "Open my profile on RetroAchievements":
    "Abrir o meu perfil no RetroAchievements",
  "RP": "RP",
  "{points} points · {retro} RetroPoints": "{points} pontos · {retro} RetroPoints",
  "Rank {n} of {total}": "Posição {n} de {total}",
  "Last played {game}": "Jogaste {game}",
  "Profile": "Perfil",
  "Points": "Pontos",
  "Rank": "Posição",
  "Mastered": "Dominados",
  "Beaten": "Terminados",
  "Event": "Evento",
  "Site award": "Prémio do site",
  "mastered": "dominado",
  "Last played": "Jogados recentemente",
  "Awards": "Prémios",
  "Show more awards": "Mostrar mais prémios",
  "People you follow": "Pessoas que segues",
  "follows you": "segue-te",
  "Nothing right now": "Nada de momento",
  "Nothing played yet.": "Ainda não jogaste nada.",
  "You do not follow anybody yet.": "Ainda não segues ninguém.",
  "{mastery} mastered · {beaten} beaten · {event} event · {site} site":
    "{mastery} dominados · {beaten} terminados · {event} de evento · {site} do site",
  "Everything here is a link to RetroAchievements. Click a game, an award or a person to open its page.":
    "Tudo aqui é uma ligação para o RetroAchievements. Clica num jogo, num prémio ou numa pessoa para abrir a sua página.",
  "Asking RetroAchievements…": "A perguntar ao RetroAchievements…",
  "Open your profile on RetroAchievements":
    "Abrir o teu perfil no RetroAchievements",
  "Open in its own window": "Abrir numa janela própria",
  "Open this in a window of its own, beside the app":
    "Abrir isto numa janela própria, ao lado da aplicação",
  "Icons only": "Só ícones",
  "Hide the ones I mastered": "Ocultar os que dominei",
  "Every game you have beaten you also mastered.":
    "Todos os jogos que terminaste também dominaste.",
  "Nothing here yet.": "Ainda nada aqui.",
  "Show the achievements": "Mostrar as conquistas",
  "Open the list": "Abrir a lista",
  "More about this player": "Mais sobre este jogador",
  "Show what they have unlocked": "Mostrar o que já desbloqueou",
  "Member since {when}": "Membro desde {when}",
  "Open the achievement list": "Abrir a lista de conquistas",
  "Open this list in a window of its own": "Abrir esta lista numa janela própria",
  "Drag to arrange": "Arrasta para organizar",
  "Reset order": "Repor a ordem",
  "Put this tab back in the order RetroAchievements sends":
    "Repor este separador na ordem que o RetroAchievements envia",
  "pts": "pts",
  "Events & site": "Eventos e site",
  "{total} awards in all": "{total} prémios no total",
  "Achievements unlocked": "Conquistas desbloqueadas",
  "Games beaten": "Jogos terminados",
  "Counted once each, however many awards a game earned":
    "Contados uma vez cada, independentemente de quantos prémios um jogo deu",
  "Of games started": "Dos jogos começados",
  "{beaten} beaten out of {started} started":
    "{beaten} terminados em {started} começados",
  "Average completion": "Conclusão média",
  "Across the {n} games you have started": "Nos {n} jogos que começaste",
  "RetroPoints divided by points - how hard your sets are":
    "RetroPoints a dividir pelos pontos — a dificuldade dos teus conjuntos",
  "Points, 7 days": "Pontos, 7 dias",
  "Points, 30 days": "Pontos, 30 dias",
  "Points a week": "Pontos por semana",
  "Since {when}": "Desde {when}",
  "Move up": "Mover para cima",
  "Move down": "Mover para baixo",
  "Ask RetroAchievements again": "Perguntar de novo ao RetroAchievements",
  "Add your RetroAchievements username in Settings → Cover art.":
    "Adiciona o teu nome de utilizador do RetroAchievements em Definições → Capas.",

  /* -- more suggestions, ten at a time -- */
  "Only games with achievements": "Só jogos com conquistas",
  "Find more": "Procurar mais",
  "Looking for more…": "À procura de mais…",
  "Look at this one": "Ver este",
  "Click one to search for it, or its cover to look at it first. Suggestions come from IGDB's own “similar games”, narrowed to what this app can download.":
    "Clica num para o procurar, ou na capa para o veres primeiro. As sugestões vêm dos “jogos semelhantes” do IGDB, limitadas ao que esta aplicação consegue transferir.",

  /* -- comments on one achievement -- */
  "What people said about this one": "O que as pessoas disseram sobre esta",
  "Nobody has commented on this one.": "Ninguém comentou esta.",

  /* -- what opens when a game starts -- */
  "When a game starts": "Quando um jogo começa",
  "Open nothing": "Não abrir nada",
  "Open the built-in achievement list": "Abrir a lista de conquistas integrada",
  "Open the game's RetroAchievements page":
    "Abrir a página do jogo no RetroAchievements",
  "Either opens beside the game in a window of this app's own. The built-in list is this app's: it loads in an instant, filters and sorts, and needs no sign-in. Their page is the real thing - leaderboards, comments, the tickets - and remembers your sign-in between sessions. Only for games RetroAchievements has a set for; nothing opens for the rest.":
    "Qualquer uma abre ao lado do jogo, numa janela da própria aplicação. A lista integrada é desta aplicação: abre num instante, filtra e ordena, e não precisa de sessão iniciada. A página deles é a verdadeira — tabelas, comentários, tickets — e guarda a tua sessão entre utilizações. Só para jogos com conjunto no RetroAchievements; para os outros não abre nada.",

  /* -- games like the ones you have -- */
  "ranking {n} of {total}": "a ordenar {n} de {total}",
  "Games like the ones you have": "Jogos parecidos com os que tens",
  "Recommended": "Recomendados",
  "Games you might like": "Jogos de que podes gostar",
  "Read from the games you have, and the ones you have played most. Games with an achievement set come first.":
    "Lido a partir dos jogos que tens, e dos que mais jogaste. Os jogos com conjunto de conquistas vêm primeiro.",
  "because you have {name}": "porque tens {name}",
  "achievement set": "com conquistas",
  "Find it": "Procurar",
  "Click one to search for it. Suggestions come from IGDB's own “similar games”, narrowed to what this app can download.":
    "Clica num para o procurar. As sugestões vêm dos “jogos semelhantes” do IGDB, limitadas ao que esta aplicação consegue transferir.",
  "More of the series you already own. Fill in IGDB in Settings → Cover art for suggestions that go beyond them.":
    "Mais jogos das séries que já tens. Preenche o IGDB em Definições → Capas para sugestões que vão além disso.",
  "There is nothing on the shelf to go on yet.":
    "Ainda não há nada na prateleira em que basear isto.",
  "Nothing to suggest yet. Fill in IGDB in Settings → Cover art and this can ask what your games are like; without it, it can only offer more of the series you already own.":
    "Ainda nada a sugerir. Preenche o IGDB em Definições → Capas e isto poderá perguntar com que se parecem os teus jogos; sem isso, só pode oferecer mais jogos das séries que já tens.",
  "Nothing to suggest from this shelf.": "Nada a sugerir a partir desta prateleira.",

  /* -- picking consoles in bulk -- */
  "Select RetroArch consoles": "Selecionar consolas do RetroArch",
  "Tick every console this app has a libretro core for, leaving out the ones with a better standalone emulator — Sony's machines, the GameCube and the Wii":
    "Marcar todas as consolas para as quais esta aplicação tem um core libretro, deixando de fora as que têm melhor emulador próprio — as máquinas da Sony, a GameCube e a Wii",
  "{n} ticked. Sony's machines, the GameCube and the Wii are left out — their own emulators are better. Tick those by hand if you want them.":
    "{n} marcadas. As máquinas da Sony, a GameCube e a Wii ficam de fora — os emuladores próprios são melhores. Marca essas à mão se as quiseres.",
  "No consoles here have a core to recommend.":
    "Nenhuma consola aqui tem um core a recomendar.",

  /* -- a shelf ordered by what you have earned -- */
  "Most achievements earned": "Mais conquistas ganhas",
  "Hide mastered": "Ocultar dominados",
  "Leave out the sets you have already mastered":
    "Deixar de fora os conjuntos que já dominou",
  "Every game here is one you have already mastered.":
    "Todos os jogos aqui são jogos que já dominou.",

  /* -- cover art services -- */
  "Cover art": "Capas",
  "Covers come from libretro's free thumbnail server, which has the games that came in a box, under the names the preservation sets give them. The services below are searched by title instead, so they fill in the ones it misses. All three are free; all three want you to make an account first.":
    "As capas vêm do servidor gratuito de miniaturas da libretro, que tem os jogos que saíram em caixa, com os nomes que os conjuntos de preservação lhes dão. Os serviços abaixo são pesquisados por título, por isso preenchem os que faltam. Todos os três são gratuitos; todos exigem que crie primeiro uma conta.",
  "Use RetroAchievements": "Usar o RetroAchievements",
  "The only one of these three that is about retro games, and the only one with covers for hacks, translations and homebrew. Your key is on your":
    "O único destes três dedicado a jogos retro, e o único com capas para hacks, traduções e homebrew. A sua chave está na sua",
  "RetroAchievements settings page": "página de definições do RetroAchievements",
  ", under Keys. Only games with an achievement set are covered.":
    ", em Keys. Só são abrangidos os jogos com um conjunto de conquistas.",
  "Web API key": "Chave da Web API",
  "Ask this one earlier": "Perguntar a este mais cedo",
  "Ask this one later": "Perguntar a este mais tarde",
  "Ask earlier": "Perguntar mais cedo",
  "Ask later": "Perguntar mais tarde",
  "They are asked in the order shown and the first one with an answer wins, so put the one you trust most at the top. The arrows move them.":
    "São consultados pela ordem apresentada e ganha o primeiro que tiver resposta, por isso ponha no topo aquele em que mais confia. As setas movem-nos.",
  "Use IGDB": "Usar o IGDB",
  "Twitch's games database, and the closest thing games have to a TMDB. Make an application at":
    "A base de dados de jogos da Twitch, e o mais parecido com um TMDB que os jogos têm. Crie uma aplicação em",
  ", then copy its Client ID and Client Secret here.":
    " e copie aqui o Client ID e o Client Secret.",
  "Client ID": "Client ID",
  "Client Secret": "Client Secret",
  "Test": "Testar",
  "Use SteamGridDB": "Usar o SteamGridDB",
  "Artwork uploaded by people rather than publishers, so it covers translations, hacks and homebrew that no commercial database will. Make an account at":
    "Imagens enviadas por pessoas e não por editoras, por isso cobre traduções, hacks e homebrew que nenhuma base de dados comercial cobre. Crie uma conta em",
  "and generate an API key.": "e gere uma chave de API.",
  "API key": "Chave de API",
  "Your keys stay on this computer, in plain text, and are left out of backups on purpose — a backup is a file people pass around.":
    "As suas chaves ficam neste computador, em texto simples, e são deixadas de fora das cópias de segurança de propósito — uma cópia de segurança é um ficheiro que se passa a outras pessoas.",
  "Use these": "Usar estes",
  "only for games libretro has no cover for":
    "só para jogos sem capa na libretro",
  "first, and fall back to libretro": "primeiro, recorrendo à libretro",
  "instead of libretro entirely": "em vez da libretro por completo",
  "Only real box art is affected. Title screens and in-game snaps are always the last thing tried, whichever you pick here, so a proper cover from either side beats them. libretro has the exact regional box for each release and costs nothing to ask; these services have one cover per game and a daily allowance. 'Instead of' means exactly that — a game they cannot match shows no cover at all.":
    "Só afeta capas a sério. Os ecrãs de título e as imagens do jogo a correr são sempre a última coisa a ser tentada, escolha o que escolher aqui, por isso uma capa verdadeira de qualquer um dos lados vence-as. A libretro tem a caixa regional exata de cada lançamento e não custa nada consultar; estes serviços têm uma capa por jogo e um limite diário. «Em vez da» quer dizer mesmo isso — um jogo que não consigam identificar fica sem capa nenhuma.",
  "Nothing is signed in yet, so covers still come from libretro. This takes effect once a service above is working.":
    "Ainda não há nenhuma sessão iniciada, por isso as capas continuam a vir da libretro. Isto entra em vigor assim que um serviço acima estiver a funcionar.",
  "Look everything up again": "Procurar tudo outra vez",
  "Answers are remembered so a redraw doesn't spend your daily allowance asking the same questions. Use this after adding a key, or when a cover it found is the wrong game.":
    "As respostas são guardadas para que um redesenho não gaste o seu limite diário a fazer as mesmas perguntas. Use isto depois de adicionar uma chave, ou quando uma capa encontrada for do jogo errado.",
  "not set up": "por configurar",
  "in use": "em uso",
  "switched off": "desligado",
  "{n} looked up so far": "{n} procurados até agora",
  "Checking…": "A verificar…",
  "That worked.": "Funcionou.",
  "That did not work.": "Não funcionou.",
  "Could not reach the app.": "Não foi possível contactar a aplicação.",

  /* -- first run -- */
  "Nothing indexed yet": "Ainda não há nada indexado",
  "Build the index": "Construir o índice",
  "RomSrx searches its own local copy of what archive.org holds. Building that copy takes a couple of minutes and only has to happen once — everything after it is offline and instant.":
    "O RomSrx procura na sua própria cópia local do que o archive.org tem. Construir essa cópia demora alguns minutos e só tem de acontecer uma vez — tudo depois disso é offline e instantâneo.",
  "You can rebuild it any time with the": "Pode reconstruí-la a qualquer momento com o botão",
  "button in the corner.": "no canto.",

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
  // The button in Paths carries an ellipsis, which makes it its own key.
  "All consoles…": "Todas as consolas…",
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
  "{shown} of {total} games": "{shown} de {total} jogos",
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
  /* Shared by the library toolbar and the download list, both of which pick
     out every item in one list. "todos" agrees with those items and with the
     "Desselecionar todos" this toggles to. The backup window's button says
     "Select everything" instead - see that entry. */
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
  /* Play time, read from the emulator that ran the game. */
  "{time} played": "{time} de jogo",
  "<1m": "<1m",
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
  "Counting only RetroAchievements sets. Pick a console, or search for a game.":
    "A contar apenas conjuntos RetroAchievements. Escolha uma consola ou procure um jogo.",
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
  /* -- archive.org account window -- */
  "Signing in unlocks the sources marked 🔒 login. Your password is sent once to archive.org and is never stored by this app — only the resulting session is kept, on this computer.":
    "Iniciar sessão desbloqueia as fontes marcadas com 🔒 início de sessão. A sua palavra-passe é enviada uma vez para o archive.org e nunca é guardada por esta aplicação — só a sessão resultante fica guardada, neste computador.",
  "Create a free account": "Criar uma conta gratuita",
  "if you don't have one.": "se ainda não tiver uma.",
  "Signed in as": "Sessão iniciada como",
  "Session stored at {path}": "Sessão guardada em {path}",

  "Backup": "Cópia de segurança",
  "Saves your settings, download list, playlists, recently played and hand-picked covers to a zip. Your games and the search index are not included — those rebuild themselves.":
    "Guarda as suas definições, lista de transferências, listas de reprodução, jogados recentemente e capas escolhidas à mão num zip. Os jogos e o índice de pesquisa não são incluídos — esses reconstroem-se sozinhos.",
  "Backup saved to {path}\n\n{n} items.":
    "Cópia guardada em {path}\n\n{n} itens.",
  "Restore from a backup?\n\nYour current settings, download list and playlists on this machine are replaced by the ones in the file.":
    "Restaurar a partir de uma cópia?\n\nAs definições, a lista de transferências e as listas de reprodução atuais desta máquina são substituídas pelas do ficheiro.",
  "Restored {n} items.\n\nRomSrx needs to be restarted for all of it to take effect.":
    "Restaurados {n} itens.\n\nÉ preciso reiniciar o RomSrx para que tudo tenha efeito.",

  /* -- library: ordering and folding -- */
  "Drag to reorder": "Arraste para reordenar",
  "Collapse all": "Recolher tudo",
  "Collapse every console": "Recolher todas as consolas",
  "Expand every console": "Expandir todas as consolas",
  "Scroll back": "Recuar",
  "Scroll on": "Avançar",
  "Playlists": "Listas de reprodução",

  /* -- paths panel -- */
  "One console": "Uma consola",
  "Select this console": "Selecionar esta consola",
  "Clear selection": "Limpar seleção",
  "{n} consoles selected": "{n} consolas selecionadas",
  "Set emulator for these…": "Definir emulador para estas…",
  "Set core…": "Definir core…",
  "Emulator set for {n} consoles.": "Emulador definido para {n} consolas.",
  "Core set for {n} consoles.": "Core definido para {n} consolas.",
  "Find a console": "Procurar uma consola",
  "Find a console…": "Procurar uma consola…",
  "Looks for a folder named after each console — in the main folder, and beside the ones you have already set. Links what it finds, re-points any that moved, and leaves working ones alone. Nothing on disk is touched.":
    "Procura uma pasta com o nome de cada consola — na pasta principal e junto às que já definiu. Associa o que encontrar, reaponta as que mudaram e deixa em paz as que funcionam. Nada no disco é alterado.",

  /* -- settings tooltips -- */
  "A note in the app, and a desktop notification when the window is not the one you are looking at.":
    "Um aviso na aplicação e uma notificação no ambiente de trabalho quando a janela não é a que está a ver.",
  "Deletes the .zip once it is safely unpacked, usually halving the space used.":
    "Elimina o .zip assim que estiver extraído em segurança, normalmente reduzindo o espaço usado para metade.",
  "Finished files leave the list, so it only ever shows what you still want. Happens even while the app is closed.":
    "Os ficheiros concluídos saem da lista, para que esta mostre apenas o que ainda quer. Acontece mesmo com a aplicação fechada.",
  "How many downloads run at the same time. The rest wait their turn and start automatically as each one finishes.":
    "Quantas transferências decorrem ao mesmo tempo. As restantes esperam a sua vez e começam automaticamente à medida que cada uma termina.",
  "On, each console gets its own subfolder. Off, every download lands in the one folder above.":
    "Ligado, cada consola tem a sua própria subpasta. Desligado, todas as transferências vão para a pasta acima.",
  "Only .zip and .7z are unpacked. Its own folder keeps multi-disc games together; straight in suits emulators that scan one flat folder.":
    "Só .zip e .7z são extraídos. Uma pasta própria mantém os jogos de vários discos juntos; diretamente na pasta serve emuladores que analisam uma única pasta.",
  "archive.org throttles heavy use. Past 3, the extra connections mostly retry rather than go faster.":
    "O archive.org limita o uso intensivo. Acima de 3, as ligações extra passam mais tempo a repetir do que a acelerar.",
  "Save a backup…": "Guardar uma cópia…",
  "Restore from a backup…": "Restaurar a partir de uma cópia…",
  "Restore": "Restaurar",
  "Get covers automatically": "Obter capas automaticamente",
  "Fetch the box art as each game for this console finishes downloading":
    "Obter a capa assim que cada jogo desta consola acabar de transferir",
  "Detect console folders": "Detetar pastas das consolas",
  "Find console folders": "Encontrar pastas das consolas",
  "Hide this": "Ocultar",
  "What to back up": "O que guardar na cópia",
  "Settings and appearance": "Definições e aspeto",
  "Folders and emulator paths": "Pastas e caminhos dos emuladores",
  "Where games are saved, and each console's folder, covers folder and emulator. Untick this when restoring onto a different computer — its own folders are then left alone.":
    "Onde os jogos são guardados, e a pasta, a pasta de capas e o emulador de cada consola. Desmarque isto ao restaurar noutro computador — as pastas dele ficam intactas.",
  "Downloads in progress": "Transferências em curso",
  "Recently played": "Jogados recentemente",
  "Hand-picked covers": "Capas escolhidas à mão",
  "Choose where to save…": "Escolher onde guardar…",
  /* "tudo" rather than the "todos" of the other two select-alls: this one
     ticks every part of a backup, which are different kinds of thing, where
     those pick out all of one list of games or files. */
  "Select everything": "Selecionar tudo",
  "Tick at least one thing to back up.": "Selecione pelo menos uma coisa para guardar.",
  "Your games and the search index are never included — both are large and both rebuild themselves.":
    "Os jogos e o índice de pesquisa nunca são incluídos — ambos são grandes e ambos se reconstroem sozinhos.",
  "{n} files aren't in any console's folder, so they aren't shown.":
    "{n} ficheiros não estão na pasta de nenhuma consola, por isso não são mostrados.",
  "Unknown": "Desconhecida",
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
  "Sign in to unlock login-only sources": "Inicie sessão para desbloquear as fontes que exigem conta",

  /* -- theme -- */
  "Language": "Idioma",
  "Tone": "Tom",
  "Colour": "Cor",
  "Default": "Predefinido",
  "Dark": "Escuro",
  "Light": "Claro",
  /* The accent swatches, seen as the tooltip on each colour. */
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
    /* The key is the words, not the way they were laid out in the file. A
       sentence long enough to need wrapping in the markup arrived here with
       its newlines and its indentation still in it, so the key was
       "Saves your settings,\n        recently played…" - which no entry in
       any table will ever match, and the string silently stayed English
       however carefully it had been translated. Single-line markup is
       unaffected: collapsing runs of whitespace leaves it exactly as it was. */
    if (el.dataset.i18nText === undefined) {
      el.dataset.i18nText = node.data.trim().replace(/\s+/g, " ");
    }
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
