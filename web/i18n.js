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
  "session": "sessão", "sessions": "sessões",
  "Open this session's folder": "Abrir a pasta desta sessão",
  "Could not open that folder.": "Não foi possível abrir essa pasta.",
  "Delete this session": "Eliminar esta sessão",
  "Keep this session past the fifteen days":
    "Manter esta sessão para além dos quinze dias",
  "Kept past the fifteen days — click to unpin":
    "Mantida para além dos quinze dias — clique para deixar de fixar",
  "This session is pinned.": "Esta sessão está fixada.",
  "Could not change that.": "Não foi possível alterar isso.",
  "Delete the {when} session from {day}{what}? {n} file(s), {size}. This cannot be undone — these files are not backed up anywhere else.":
    "Eliminar a sessão das {when} de {day}{what}? {n} ficheiro(s), {size}. "
    + "Isto não pode ser desfeito — estes ficheiros não estão guardados "
    + "em mais lado nenhum.",
  "Session deleted.": "Sessão eliminada.",
  "Could not read that session.": "Não foi possível ler essa sessão.",
  "Could not delete that session.":
    "Não foi possível eliminar essa sessão.",
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
  "Fastest to master": "Mais rápidos de dominar",
  "Shortest sets on RetroAchievements": "Conjuntos mais curtos do RetroAchievements",
  "reading every set…": "a ler todos os conjuntos…",
  "reading the times…": "a ler os tempos…",
  "could not read the sets": "não foi possível ler os conjuntos",
  "no achievements": "sem proezas",
  "Achievements": "Proezas",
  "set": "conjunto",
  "sets": "conjuntos",
  "Only games that have achievements. One game can carry many sets — 299 of them are hacks of Super Mario World — so the count shows both.":
    "Apenas jogos que têm proezas. Um jogo pode ter vários conjuntos — 299 deles são hacks do Super Mario World — por isso a contagem mostra os dois.",
  "Only games that have achievements":
    "Apenas jogos que têm proezas",
  "Earlier saves":
    "Saves anteriores",
  "Browse sessions":
    "Ver sessões",
  "Go back to an earlier save":
    "Voltar a um save anterior",
  "Reading…":
    "A ler…",
  "Could not read the saved sessions.":
    "Não foi possível ler as sessões guardadas.",
  "Nothing kept yet — close a game and whatever it saved will appear here.":
    "Ainda não há nada — feche um jogo e o que ele gravar aparece aqui.",
  "{n} file(s) put back.":
    "{n} ficheiro(s) repostos.",
  "{n} of them will be written over.":
    "{n} deles serão substituídos.",
  "Put back {n} file(s) from {day} at {at}? {over} A copy of what is there now is kept first, so this can be undone.":
    "Repor {n} ficheiro(s) de {day} às {at}? {over} É guardada primeiro uma cópia do que lá está agora, por isso isto pode ser desfeito.",
  "Every session is kept for fifteen days. Restoring puts those files back where they came from — and copies what is there now first, so you can change your mind.":
    "Cada sessão é guardada durante quinze dias. Restaurar repõe esses ficheiros de onde vieram — e copia primeiro o que lá está agora, para poder mudar de ideias.",
  "Every time you close a game, whatever it saved is copied here and kept for fifteen days — filed under the emulator, then the day, then the time you stopped. Restoring one puts those files back where they came from, and takes a copy of what is there now first, so picking the wrong evening is not the end of it.":
    "Sempre que fecha um jogo, o que ele gravou é copiado para aqui e guardado durante quinze dias — arrumado por emulador, depois por dia e depois pela hora a que parou. Restaurar repõe esses ficheiros de onde vieram, e guarda primeiro uma cópia do que lá está agora, por isso escolher a noite errada não é o fim do mundo.",
  "Source": "Origem",
  "Where this came from": "De onde veio",
  "Test speeds": "Testar velocidades",
  "The same setup on another computer": "A mesma configuração noutro computador",
  "RomSrx has no account of its own. Point this at a folder your own cloud keeps in step — OneDrive, Google Drive, Dropbox — or at your own WebDAV server, and your settings, playlists and saves follow you between computers. Nothing is stored by anyone but you.":
    "O RomSrx não tem conta própria. Aponte isto para uma pasta que a sua "
    + "nuvem mantenha sincronizada — OneDrive, Google Drive, Dropbox — ou "
    + "para o seu próprio servidor WebDAV, e as suas definições, listas e "
    + "saves seguem-no entre computadores. Nada é guardado por mais ninguém.",
  "Keep in step using": "Manter sincronizado através de",
  "nothing — this computer only": "nada — apenas este computador",
  "a folder my cloud syncs": "uma pasta que a minha nuvem sincroniza",
  "my own WebDAV server": "o meu próprio servidor WebDAV",
  "A folder is the easy one: pick a directory inside OneDrive, Google Drive, Dropbox or iCloud and their own program does the carrying. WebDAV is for Nextcloud, a NAS, Koofr or Box — the big three do not speak it. Either way RomSrx stores nothing itself.":
    "A pasta é a opção simples: escolha uma pasta dentro do OneDrive, Google "
    + "Drive, Dropbox ou iCloud e o programa deles trata do transporte. O "
    + "WebDAV é para Nextcloud, um NAS, Koofr ou Box — os três grandes não o "
    + "falam. De qualquer forma o RomSrx não guarda nada.",
  "Folder": "Pasta",
  "C:\\Users\\you\\OneDrive\\RomSrx":
    "C:\\Users\\you\\OneDrive\\RomSrx",
  "https://cloud.example.com/remote.php/dav/files/you":
    "https://cloud.example.com/remote.php/dav/files/you",
  "Address": "Endereço",
  "Provider": "Fornecedor",
  "still loading…": "ainda a carregar…",
  "could not read the index — press to retry":
    "não foi possível ler o índice — clique para tentar de novo",
  "Fill in the address for a provider you use":
    "Preencher o endereço de um fornecedor que use",
  "choose one to fill in the address…":
    "escolha um para preencher o endereço…",
  "Nextcloud or ownCloud": "Nextcloud ou ownCloud",
  "Koofr": "Koofr",
  "pCloud": "pCloud",
  "Box": "Box",
  "Fastmail": "Fastmail",
  "Synology NAS": "NAS Synology",
  "Replace USERNAME with your own, and check the address against your provider’s own instructions — some accounts sit on a different server (pCloud has a separate European one, for instance). Most providers can give you an app password for this, which you can revoke on its own if you ever lose the computer.":
    "Substitua USERNAME pelo seu, e confirme o endereço nas instruções do "
    + "seu fornecedor — algumas contas estão num servidor diferente (o "
    + "pCloud tem um europeu à parte, por exemplo). A maioria dos "
    + "fornecedores dá-lhe uma palavra-passe de aplicação para isto, que "
    + "pode revogar sozinha se alguma vez perder o computador.",
  "Username": "Nome de utilizador",
  "Password": "Palavra-passe",
  "Most servers can give you an app password for this, so your real one never goes here. It is kept on this computer in plain text, like the archive.org sign-in and the artwork keys, and it is left out of backups.":
    "A maioria dos servidores dá-lhe uma palavra-passe de aplicação para isto, "
    + "por isso a verdadeira nunca vai aqui. Fica neste computador em texto "
    + "simples, como a sessão do archive.org e as chaves das capas, e fica "
    + "fora das cópias de segurança.",
  "What travels": "O que viaja",
  "Sync on its own": "Sincronizar sozinho",
  "Until the index is built, this is the only part of Settings that can do anything — and it is the part that lets you skip building one from scratch. Restore a backup, or point RomSrx at the computer you already use, and your settings, playlists and saves come with you.":
    "Até o índice estar criado, esta é a única parte das Definições que faz alguma coisa — e é a parte que lhe permite evitar criar um do zero. Restaure uma cópia de segurança, ou aponte o RomSrx para o computador que já usa, e as suas definições, listas e saves vêm consigo.",
  "Fetches when the app opens, and sends after you close a game — which is the moment a save is final. Never while you are playing, and never more than once a minute. Closing the app is deliberately not one of the moments: it would either hold the window open or be cut off half-done.":
    "Obtém quando a aplicação abre, e envia depois de fechar um jogo — que é o momento em que um save fica final. Nunca enquanto está a jogar, e nunca mais do que uma vez por minuto. Fechar a aplicação não é de propósito um desses momentos: ou segurava a janela aberta ou seria cortado a meio.",
  "from {who}": "de {who}",
  "Played on {who}, and carried here by a sync":
    "Jogado em {who}, e trazido para aqui por uma sincronização",
  "Choose…": "Escolher…",
  "Use the usual choice": "Usar a escolha habitual",
  "{n} of {all} · {size}": "{n} de {all} · {size}",
  "Carrying {files} files · {size}": "A levar {files} ficheiros · {size}",
  "Everything ticked here is carried to your other computers. Where this machine keeps its games and emulators is never carried — they live on different drives.":
    "Tudo o que estiver marcado aqui é levado para os seus outros computadores. O local onde esta máquina guarda os jogos e emuladores nunca é levado — estão em discos diferentes.",
  "How you like the app — not where this computer keeps its games":
    "Como gosta da aplicação — não onde este computador guarda os jogos",
  "Games waiting to be downloaded": "Jogos à espera de serem transferidos",
  "Downloads that were part way through":
    "Transferências que ficaram a meio",
  "Your shelves, and the games on them":
    "As suas prateleiras, e os jogos nelas",
  "What you played last, and when": "O que jogou por último, e quando",
  "The medians looked up from RetroAchievements":
    "As medianas obtidas do RetroAchievements",
  "Pictures found for games, so another computer need not look again":
    "Imagens encontradas para os jogos, para outro computador não ter de as procurar outra vez",
  "Memory cards — the one thing here you cannot download again":
    "Cartões de memória — a única coisa aqui que não pode transferir de novo",
  "Snapshots of a running game. By far the largest of these":
    "Instantâneos de um jogo a correr. De longe o maior destes",
  "The copy taken every time you close a game":
    "A cópia feita sempre que fecha um jogo",
  "Test the connection": "Testar a ligação",
  "Where this computer keeps its games and emulators never travels — two machines put them on different drives, and a synced folder path would point the other one at somewhere that does not exist. If the same file changed on both computers, the newer one wins and the older is kept beside it rather than thrown away.":
    "O local onde este computador guarda os jogos e emuladores nunca viaja — "
    + "duas máquinas põem-nos em discos diferentes, e um caminho "
    + "sincronizado apontaria a outra para um sítio que não existe. Se o "
    + "mesmo ficheiro mudou nos dois computadores, o mais recente ganha e o "
    + "mais antigo fica guardado ao lado em vez de ser deitado fora.",
  "Settings and preferences": "Definições e preferências",
  "Download list": "Lista de transferências",
  "Downloads in progress": "Transferências em curso",
  "Recently played": "Jogados recentemente",
  "How long games take": "Duração dos jogos",
  "Cover art": "Capas",
  "Memory cards and saves": "Cartões de memória e saves",
  "Save states": "Estados guardados",
  "Earlier saves": "Saves anteriores",
  "Sync now": "Sincronizar agora",
  "Syncing…": "A sincronizar…",
  "Sync finished.": "Sincronização concluída.",
  "Already in step.": "Já está sincronizado.",
  "Tick something to carry first.": "Escolha primeiro o que quer levar.",
  "Sync now? This would {what}.": "Sincronizar agora? Isto iria {what}.",
  "send {n} ({size})": "enviar {n} ({size})",
  "fetch {n}": "obter {n}",
  "{n} changed in both places": "{n} mudaram nos dois sítios",
  "Where both changed, the newer one wins and the older is kept beside it.":
    "Onde ambos mudaram, o mais recente ganha e o mais antigo fica ao lado.",
  "Sent {sent}, fetched {got}{kept}.": "Enviados {sent}, obtidos {got}{kept}.",
  ", kept {n} older copies": ", guardadas {n} cópias mais antigas",
  "Working. Using {where}": "A funcionar. A usar {where}",
  "Could not reach it.": "Não foi possível contactá-lo.",
  "Could not save that.": "Não foi possível guardar isso.",
  "kept — leave blank to keep it": "guardada — deixe em branco para a manter",
  "Choosing…": "A escolher…",
  "Browse…": "Procurar…",
  "Testing…": "A testar…",
  "Try each source for a few seconds and say how fast it is right now":
    "Experimenta cada fonte durante alguns segundos e diz a que velocidade está agora",
  "{rate} and climbing · {n} seeding":
    "{rate} e a subir · {n} a semear",
  "Could not test those sources.":
    "Não foi possível testar essas fontes.",
  "needs an account": "precisa de uma conta",
  "no one seeding": "ninguém a semear",
  "sent nothing": "não enviou nada",
  "nothing to try": "nada para experimentar",
  "not a direct link": "não é uma ligação direta",
  "torrents unavailable in this build":
    "torrents indisponíveis nesta versão",
  "not in that torrent any more": "já não está nesse torrent",
  "no answer": "sem resposta",
  "romset {name}": "romset {name}",
  "An arcade board rather than a cartridge. RetroAchievements knows this set by the romset's name, so this file and no other will work with it.":
    "Uma placa de arcade e não um cartucho. O RetroAchievements identifica este conjunto pelo nome do romset, por isso só este ficheiro funciona com ele.",
  "patch failed": "patch falhou",
  "The patch could not be applied, so this is still the plain game rather than the hack: ":
    "Não foi possível aplicar o patch, por isso isto continua a ser o jogo original e não o hack: ",
  "patch on {base}": "patch sobre {base}",
  "This set is a fan hack. The download fetches {base}, then RetroAchievements' own patch is applied to it to produce the hack.":
    "Este conjunto é um hack de fãs. A transferência traz {base} e depois é aplicado o patch do próprio RetroAchievements para criar o hack.",
  "Keep sharing finished files for":
    "Continuar a partilhar os ficheiros terminados durante",
  "minutes, 0 to stop at once": "minutos, 0 para parar de imediato",
  "MiNERVA is run by volunteers and every file here comes off somebody else's connection. Left at 0 this app takes and gives nothing back, which works only as long as most people do not do it. Any number here keeps the finished file shared for that long — and means uploading, so it tells the swarm your address for that much longer too. The adapter and proxy settings above still apply.":
    "A MiNERVA é mantida por voluntários e cada ficheiro daqui sai da ligação de outra pessoa. Deixado a 0, esta aplicação recebe e não devolve nada, o que só funciona enquanto a maioria não fizer o mesmo. Qualquer número aqui mantém o ficheiro terminado partilhado durante esse tempo — e isso é enviar, por isso revela o seu endereço ao enxame durante mais tempo. As definições de adaptador e proxy acima continuam a aplicar-se.",
  "achievements ✓": "proezas ✓",
  "not checked": "não verificado",
  "Hashed and confirmed: this is one of the copies the RetroAchievements set was built from.":
    "Verificado: esta é uma das cópias a partir das quais o conjunto do RetroAchievements foi criado.",
  "This format is a compressed disc image the app cannot open, so the hash could not be worked out. It may well be the right copy — there is simply no way to say so from here.":
    "Este formato é uma imagem de disco comprimida que a aplicação não consegue abrir, por isso não foi possível calcular a soma. Pode muito bem ser a cópia certa — simplesmente não há como o confirmar daqui.",
  "{file} will not earn achievements — see the download list.":
    "{file} não vai dar proezas — veja a lista de transferências.",
  "This copy was hashed and is not one the RetroAchievements set was built from, so it will not earn achievements. It is still a real dump — most likely a different revision. Another copy may work.":
    "Esta cópia foi verificada e não é uma daquelas a partir das quais o conjunto do RetroAchievements foi criado, por isso não vai dar proezas. Continua a ser uma cópia real — muito provavelmente outra revisão. Outra cópia pode funcionar.",
  "could not run that search — try again":
    "não foi possível fazer essa pesquisa — tente novamente",
  "Add all to a playlist": "Adicionar todos a uma lista",
  "Add every suggestion to a playlist": "Adicionar todas as sugestões a uma lista",
  "Add every suggestion to the download list":
    "Adicionar todas as sugestões à lista de transferências",
  "Add everything this app can fetch to a playlist":
    "Adicionar tudo o que esta app consegue obter a uma lista",
  "Add everything this app can fetch to the download list":
    "Adicionar tudo o que esta app consegue obter à lista de transferências",
  "Fetch everything this app can": "Obter tudo o que esta app conseguir",
  "Find more": "Procurar mais", "Show different ones": "Mostrar outros",
  "Refresh list": "Atualizar lista", "Select": "Selecionar", "Done": "Concluído",
  "Show all three": "Mostrar os três",
  "Mastered": "Dominados", "Beaten": "Terminados",
  "Events & site": "Eventos e site",
  "No awards yet.": "Ainda sem prémios.",
  "Columns": "Colunas",
  "Hue": "Matiz", "Strength": "Intensidade", "Lightness": "Luminosidade",
  "Test": "Testar", "Sent": "Enviada", "Not available": "Indisponível",
  "Notifications are working.": "As notificações estão a funcionar.",
  "Move left": "Mover para a esquerda", "Move right": "Mover para a direita",
  "Achievement checks": "Verificação de proezas",
  "Check every result automatically": "Verificar automaticamente todos os resultados",
  "Only when I press the RA button": "Só quando eu carregar no botão RA",
  "Choose any colour": "Escolher qualquer cor",
  "Custom colour": "Cor personalizada",
  "Sound": "Som", "Download sound": "Som das transferências",
  "Download sound is off": "O som das transferências está desligado",
  "Off": "Desligado", "Volume": "Volume", "Columns": "Colunas",
  "Show every game": "Mostrar todos os jogos",
  "From my library": "Da minha biblioteca",
  "Only the ones something on your shelf suggested":
    "Apenas os sugeridos por algo na tua estante",
  "Add to download list": "Adicionar à lista de transferências",
  "Deselect all": "Desmarcar tudo",
  "Pick games by clicking them": "Escolhe jogos clicando neles",
  "Finding copies… {done}/{total}": "A procurar cópias… {done}/{total}",
  "No copies of those in your index.": "Não há cópias desses no teu índice.",
  "Tell me when a game is installed": "Avisar quando um jogo for instalado",
  "Ready to play": "Pronto a jogar",
  "{name} is installed": "{name} está instalado",
  "Click one to look at it. The button on the right starts it.":
    "Clica num para o ver. O botão à direita inicia-o.",
  "Click one to look at it, or to fetch one you haven't got yet. The button on the right starts it.":
    "Clica num para o ver, ou para obter um que ainda não tens. O botão à direita inicia-o.",
  "Played": "Jogados",
  "Hide beaten": "Ocultar terminados",
  "Hide mastered": "Ocultar dominados",
  "Beaten": "Terminado",
  "Mastered": "Dominado",
  "Leave out games you have already finished":
    "Deixar de fora os jogos que já acabaste",
  "Show them as a carousel": "Mostrar em carrossel",
  "Show them in a row": "Mostrar em fila",
  "Copies in your index": "Cópias no teu índice",
  "Looking for copies…": "À procura de cópias…",
  "No copies of this in your index.": "Não há cópias disto no teu índice.",
  "Download this game…": "Transferir este jogo…",
  "{n} games with an achievement set": "{n} jogos com um conjunto de proezas",
  "smallest sets first, across {n} consoles":
    "conjuntos mais pequenos primeiro, em {n} consolas",
  "smallest sets first, out of the {n} matching games with a set":
    "conjuntos mais pequenos primeiro, dos {n} jogos correspondentes com conjunto",
  "quickest first, out of the {n} games timed so far":
    "mais rápidos primeiro, dos {n} jogos cronometrados até agora",
  "quickest first, out of the {n} matching games that have a time":
    "mais rápidos primeiro, dos {n} jogos correspondentes que têm tempo",
  "no times yet — run Time every set in Settings → Library, once":
    "ainda sem tempos — execute Cronometrar todos os conjuntos em Definições → Biblioteca, uma vez",
  "none of these have a time yet — only games Time every set reached can be ordered by one":
    "nenhum destes tem tempo ainda — só os jogos que Cronometrar todos os conjuntos alcançou podem ser ordenados por tempo",
  "{n} more still being timed — pick this sort again in a moment.":
    "Faltam {n} por cronometrar — escolhe esta ordem outra vez daqui a pouco.",
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

  "Sign the emulators in to RetroAchievements":
    "Iniciar sessão nos emuladores no RetroAchievements",
  "Check": "Verificar",
  "Sign in to any one of your emulators and this copies that login into the others, so you only do it once. It reads the token out of the emulator that has it — you are never asked for your RetroAchievements password, and none is stored here. Emulators that keep their login in Windows Credential Manager rather than a settings file cannot be filled in this way, and are listed as such.":
    "Inicie sessão em qualquer um dos seus emuladores e isto copia essa sessão "
    + "para os outros, para só o fazer uma vez. Lê o token do emulador que o "
    + "tem — nunca lhe é pedida a palavra-passe do RetroAchievements, e "
    + "nenhuma é guardada aqui. Os emuladores que guardam a sessão no Gestor "
    + "de Credenciais do Windows em vez de um ficheiro de definições não "
    + "podem ser preenchidos assim, e são indicados como tal.",
  "Looking…": "A verificar…",
  "Signing in…": "A iniciar sessão…",
  "Signed in as {who}, read from {which}.":
    "Sessão iniciada como {who}, lida do {which}.",
  "Already signed in: {list}.": "Já com sessão iniciada: {list}.",
  "{which}: run it once and come back.":
    "{which}: abra-o uma vez e volte aqui.",
  "{which}: keeps its login in Windows rather than a settings file, so it has to be signed in there.":
    "{which}: guarda a sessão no Windows e não num ficheiro de definições, "
    + "por isso a sessão tem de ser iniciada lá.",
  "Nothing left to do.": "Não há mais nada a fazer.",
  "None of your emulators is signed in to RetroAchievements yet. Sign in to one of them and this can copy it to the rest.":
    "Nenhum dos seus emuladores tem sessão iniciada no RetroAchievements. "
    + "Inicie sessão num deles e isto copia-a para os restantes.",
  "Sign {list} in as {who}? Their settings files will be changed.":
    "Iniciar sessão em {list} como {who}? Os ficheiros de definições "
    + "deles vão ser alterados.",
  "{n} signed in.": "{n} com sessão iniciada.",
  "Could not read the emulators' settings.":
    "Não foi possível ler as definições dos emuladores.",
  "Which set of achievements for this game":
    "Que conjunto de conquistas deste jogo",
  "Base Set": "Conjunto base",
  "{n} consoles": "{n} consolas",
  "Show": "Mostrar",
  "Which emulator or console to show":
    "Que emulador ou consola mostrar",
  "Everything": "Tudo",
  "Search by game or note": "Procurar por jogo ou nota",
  "Add a note…": "Adicionar uma nota…",
  "A note about this session": "Uma nota sobre esta sessão",
  "Could not write that down.": "Não foi possível guardar a nota.",
  "Nothing matches that.": "Nada corresponde a isso.",
  "{n} achievements": "{n} conquistas",
  "worth {n} points": "que valem {n} pontos",
  "achievement": "conquista",
  "achievements": "conquistas",
  "How big the rows are": "Tamanho das linhas",
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
  "Open my list": "Abrir a minha lista",
  "Open your own list for this game": "Abrir a tua própria lista deste jogo",
  "More about this player": "Mais sobre este jogador",
  "Mastered in {time}": "Dominado em {time}",
  "Beaten in {time}": "Terminado em {time}",
  "on {when}": "em {when}",
  "Unlocked {when}": "Desbloqueada em {when}",
  "Still locked": "Ainda bloqueada",
  "{done} of {total} · {share}%": "{done} de {total} · {share}%",
  "Unlocked": "Desbloqueada",
  "Top {n}%": "Top {n}%",
  "Site Rank": "Posição no site",
  "Last Activity": "Última atividade",
  "Member Since": "Membro desde",
  "Show what people said about this one": "Ver o que disseram sobre esta",
  "Last seen": "Visto pela última vez",
  "Open this game on RetroAchievements": "Abrir este jogo no RetroAchievements",
  "Open their profile on RetroAchievements":
    "Abrir o perfil dele no RetroAchievements",
  "Followed users ranking": "Classificação de quem segues",
  "All time": "Desde sempre",
  "This week": "Esta semana",
  "Today": "Hoje",
  "points won": "pontos ganhos",
  "points": "pontos",
  "you": "tu",
  "Nobody has won anything yet.": "Ainda ninguém ganhou nada.",
  "now": "agora",
  "{n} min ago": "há {n} min",
  "{n} h ago": "há {n} h",
  "{n} d ago": "há {n} d",
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
  "Rebuilding the index": "A reconstruir o índice",
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

  /* -- achievement compatibility, the Want to Play list and hardcore -- */
  "Will this copy earn achievements?": "Esta cópia vai dar conquistas?",
  "Working out this file's hash…": "A calcular o hash deste ficheiro…",
  "It is {name}.": "É {name}.",
  "Checked {n} days ago.": "Verificado há {n} dias.",
  "Checked over a month ago — worth checking again.":
    "Verificado há mais de um mês — vale a pena verificar de novo.",
  "This copy is one the achievement set is built from.":
    "Esta cópia é uma daquelas a partir das quais o conjunto de conquistas foi criado.",
  "This copy is not one of the dumps the achievement set accepts, so it will not earn achievements.":
    "Esta cópia não é um dos ficheiros que o conjunto de conquistas aceita, por isso não vai dar conquistas.",
  "This app cannot check disc games: their hash is taken from inside the image. Cartridge consoles only.":
    "Esta aplicação não consegue verificar jogos em disco: o hash é retirado de dentro da imagem. Apenas consolas de cartucho.",
  "There is more than one ROM here, so which to check is not clear.":
    "Há aqui mais do que uma ROM, por isso não é claro qual verificar.",
  "This game is in an archive this app cannot open, so the ROM inside it could not be checked.":
    "Este jogo está num arquivo que esta aplicação não consegue abrir, por isso a ROM lá dentro não pôde ser verificada.",
  "This file is not the kind of ROM its console expects.":
    "Este ficheiro não é o tipo de ROM que a sua consola espera.",
  "That file could not be read.": "Não foi possível ler esse ficheiro.",
  "Add your RetroAchievements Web API key in Settings → Cover art, and this can check the copy on this machine against their set.":
    "Preencha a chave da API Web do RetroAchievements em Definições → Capas, e isto pode comparar a cópia nesta máquina com o conjunto deles.",
  "There is nothing here to check.": "Não há nada aqui para verificar.",
  "Already checking.": "Já a verificar.",
  "See which copies work": "Ver que cópias funcionam",
  "Download that copy": "Transferir essa cópia",
  "Their set is built from {name}, and your index has it.":
    "O conjunto deles foi criado a partir de {name}, e o seu índice tem esse ficheiro.",
  "Achievement compatibility": "Compatibilidade com conquistas",
  "Check every copy": "Verificar todas as cópias",
  "Checking {done} of {total}…": "A verificar {done} de {total}…",
  "Checked {n} games.": "{n} jogos verificados.",
  "Stopped.": "Parado.",
  "{n} earn achievements": "{n} dão conquistas",
  "{n} will not": "{n} não dão",
  "{n} not checked": "{n} não verificados",
  "Won't earn achievements": "Não dão conquistas",
  "Only the copies whose hash is not in their set":
    "Apenas as cópias cujo hash não está no conjunto",
  "Closest to mastering": "Mais perto da mestria",
  "{time} played, as counted by RetroAchievements":
    "{time} jogados, segundo o RetroAchievements",
  "RetroArch achievements": "Conquistas do RetroArch",
  "Signed in as {user}, with hardcore on. Your play will count.":
    "Com sessão iniciada como {user}, em hardcore. O seu tempo de jogo vai contar.",
  "RetroArch is not signed in to RetroAchievements, so nothing you play there will be recorded.":
    "O RetroArch não tem sessão iniciada no RetroAchievements, por isso nada do que jogar lá será registado.",
  "Achievements are switched off in RetroArch.":
    "As conquistas estão desligadas no RetroArch.",
  "Hardcore is off in RetroArch, so unlocks will be softcore — no points, and no mastery.":
    "O hardcore está desligado no RetroArch, por isso os desbloqueios serão softcore — sem pontos e sem mestria.",
  "RetroArch is signed in as {them}, not {you}.":
    "O RetroArch tem sessão iniciada como {them}, não como {you}.",
  "Want to play": "Quero jogar",
  "Your Want to Play list": "A sua lista Quero Jogar",
  "Games you want to play": "Jogos que quer jogar",
  "The list you keep on retroachievements.org. Each one is matched against your index, so the games this app can fetch say so.":
    "A lista que mantém em retroachievements.org. Cada jogo é comparado com o seu índice, por isso os que esta aplicação consegue obter dizem-no.",
  "Reading your list…": "A ler a sua lista…",
  "Asking RetroAchievements again…":
    "A perguntar de novo ao RetroAchievements…",
  "Add your RetroAchievements username and Web API key in Settings → Cover art, and your list will appear here.":
    "Preencha o seu nome de utilizador e a chave da API Web do RetroAchievements em Definições → Capas, e a sua lista aparecerá aqui.",
  "Your Want to Play list is empty. Add games to it on retroachievements.org and they will show up here.":
    "A sua lista Quero Jogar está vazia. Adicione jogos em retroachievements.org e aparecerão aqui.",
  "{total} on your list · {get} this app can fetch · {none} not in your index":
    "{total} na sua lista · {get} que esta aplicação consegue obter · {none} fora do seu índice",
  "Only the ones this app can fetch":
    "Apenas os que esta aplicação consegue obter",
  "Already in your library": "Já na sua biblioteca",
  "Ready to download": "Pronto a transferir",
  "A hack or translation — needs the patcher, not a download":
    "Um hack ou tradução — precisa do patcher, não de uma transferência",
  "No copy in your index": "Sem cópia no seu índice",
  "Nothing here matches those filters.":
    "Nada aqui corresponde a esses filtros.",
  "Add all to download list": "Adicionar todos à lista de transferências",
  "Refresh list": "Atualizar lista",
  "{n} added to your download list":
    "{n} adicionados à lista de transferências",
  "They are all on the list already.": "Já estão todos na lista.",
  "Every one of those is already in your library.":
    "Todos esses já estão na sua biblioteca.",


  /* -- the rest of the interface: the toolbars, the tooltips, the
        progress lines and the windows that report what was found -- */
  "A note in the app. Run this in a browser rather than the desktop window and the browser's own notification comes with it.":
    "Um aviso dentro da aplicação. Se a executar num browser em vez da janela de ambiente de trabalho, vem também a notificação do próprio browser.",
  "A window of this app keeps the page beside your library, and signing in there is remembered between sessions. Your own browser is the other option, and keeps you signed in wherever you already are.":
    "Uma janela desta aplicação mantém a página ao lado da sua biblioteca, e a sessão iniciada aí fica guardada entre utilizações. A outra opção é o seu próprio browser, que o mantém com sessão iniciada onde já está.",
  "Asking RetroAchievements… {done} of {total}":
    "A perguntar ao RetroAchievements… {done} de {total}",
  "Badges only, without their names": "Só os emblemas, sem os nomes",
  "Below: other games with achievement sets on this console. Nothing on your shelf suggested these.":
    "Abaixo: outros jogos com conjuntos de conquistas nesta consola. Não houve nada na sua estante que os sugerisse.",
  "Compatibility marks": "Marcas de compatibilidade",
  "Disc {n}": "Disco {n}",
  "Could not read the library.": "Não foi possível ler a biblioteca.",
  "Done — {total} sources": "Concluído — {total} fontes",
  "Every console": "Todas as consolas",
  "Every game on the shelf, played or not. Times are how long RetroAchievements' players actually took, in hardcore; a dash means they have no time for it.":
    "Todos os jogos da estante, jogados ou não. Os tempos são quanto os jogadores do RetroAchievements demoraram realmente, em hardcore; um travessão significa que não têm tempo para esse jogo.",
  "Every game on “{name}”, played or not, downloaded or not. Times are how long RetroAchievements' players actually took, in hardcore; a dash means they have no time for it.":
    "Todos os jogos de “{name}”, jogados ou não, transferidos ou não. Os tempos são quanto os jogadores do RetroAchievements demoraram realmente, em hardcore; um travessão significa que não têm tempo para esse jogo.",
  "Everything is already timed — nothing has changed since the last run.":
    "Está tudo cronometrado — nada mudou desde a última vez.",
  "Find my emulators": "Encontrar os meus emuladores",
  "Found no emulators this app knows. Pointing one console at its program by hand is enough - the rest are found next time, since it looks beside the ones already set.":
    "Não foi encontrado nenhum emulador que esta aplicação conheça. Basta apontar uma consola ao seu programa à mão — os restantes são encontrados da próxima vez, porque a procura passa a olhar ao lado dos que já estão definidos.",
  "Found {names} — every console is already set to them.":
    "Encontrado: {names} — todas as consolas já estão apontadas para eles.",
  "Found {names} — the consoles already set were left alone.":
    "Encontrado: {names} — as consolas já definidas ficaram como estavam.",
  "Found {names}.": "Encontrado: {names}.",
  "Hardcore is the mode RetroAchievements ranks people on - no save states, no rewind, no cheats - and it is a switch inside RetroArch, not here. This reads its configuration and says what it found, so an evening's play does not quietly land as softcore. Nothing is changed, and your login token is never read.":
    "O hardcore é o modo pelo qual o RetroAchievements classifica as pessoas — sem save states, sem rebobinar, sem cheats — e é uma opção dentro do RetroArch, não aqui. Isto lê a configuração dele e diz o que encontrou, para que uma noite de jogo não acabe em softcore sem ninguém dar por isso. Nada é alterado, e o seu token de sessão nunca é lido.",
  "Hide them": "Escondê-las",
  "Hide these games": "Esconder estes jogos",
  "Leave out the ones I went on to master":
    "Deixar de fora os que acabei por dominar",
  "Leave them alone": "Deixar como estão",
  "More": "Mais",
  "Mute": "Silenciar",
  "No games here yet. Anything you download lands in this folder and will show up on Refresh.":
    "Ainda não há jogos aqui. Tudo o que transferir vai parar a esta pasta e aparece ao Atualizar.",
  "Nothing timed yet. This asks about every game with a set your index can fetch — thousands of requests, about half an hour, once.":
    "Ainda não há nada cronometrado. Isto pergunta por todos os jogos com conjunto que o seu índice consiga obter — milhares de pedidos, cerca de meia hora, uma só vez.",
  "Patching…": "A aplicar o patch…",
  "Put the awards back in the order they came in":
    "Repor os prémios pela ordem em que chegaram",
  "RA set": "Conjunto RA",
  "RomSrx — {n} downloading, {pct}%":
    "RomSrx — {n} a transferir, {pct}%",
  "RomSrx — {name} {pct}%": "RomSrx — {name} {pct}%",
  "Reading your folders…": "A ler as suas pastas…",
  "Replace them": "Substituí-los",
  "RetroAchievements could not be reached — this is the list as it stood on {date}.":
    "Não foi possível contactar o RetroAchievements — esta é a lista tal como estava a {date}.",
  "RetroAchievements could not be reached — this is the list from your last visit.":
    "Não foi possível contactar o RetroAchievements — esta é a lista da sua última visita.",
  "RetroAchievements gives a median time one game at a time, so this asks about every game with a set that your index can fetch — thousands of requests, half an hour or so, once. It is saved permanently; running it again only asks about sets that are new or have changed. Until then, 'fastest to beat' can only order the results on screen.":
    "O RetroAchievements dá um tempo mediano um jogo de cada vez, por isso isto pergunta por todos os jogos com conjunto que o seu índice consiga obter — milhares de pedidos, cerca de meia hora, uma só vez. Fica guardado permanentemente; correr outra vez só pergunta pelos conjuntos novos ou que mudaram. Até lá, «mais rápido de terminar» só consegue ordenar os resultados que estão no ecrã.",
  "RetroAchievements profile": "Perfil RetroAchievements",
  "Save": "Guardar",
  "Scan": "Analisar",
  "Search/Library": "Pesquisa/Biblioteca",
  "Select every {console} game": "Selecionar todos os jogos de {console}",
  "Show a tick or a cross on each game":
    "Mostrar um visto ou uma cruz em cada jogo",
  "Show mastered, beaten and events together":
    "Mostrar dominados, terminados e eventos em conjunto",
  "Show my library": "Mostrar a minha biblioteca",
  "Show the search": "Mostrar a pesquisa",
  "Show these games": "Mostrar estes jogos",
  "Showing all {total}": "A mostrar todos os {total}",
  "Showing {shown} of {total}": "A mostrar {shown} de {total}",
  "Sort": "Ordenar",
  "Stop": "Parar",
  "The marks say whether the copy you have is one its achievement set was built from. Hiding them leaves the shelf as it was; nothing is forgotten, and the answer is still in each game's preview and right-click menu.":
    "As marcas dizem se a cópia que tem é uma daquelas a partir das quais o conjunto de conquistas foi feito. Escondê-las deixa a estante como estava; nada é esquecido, e a resposta continua na pré-visualização de cada jogo e no menu do botão direito.",
  "This copy comes from one of RetroAchievements' own collections, so it almost certainly works — though its name is not one the set lists.":
    "Esta cópia vem de uma das coleções do próprio RetroAchievements, por isso é quase certo que funciona — ainda que o nome não seja um dos que o conjunto lista.",
  "This set has been reworked since you last looked: {before} points became {after}.":
    "Este conjunto foi reformulado desde a última vez que o viu: {before} pontos passaram a {after}.",
  "This set has changed since you last looked: {before} achievements became {after}.":
    "Este conjunto mudou desde a última vez que o viu: {before} conquistas passaram a {after}.",
  "Time every set": "Cronometrar todos os conjuntos",
  "Times": "Tempos",
  "Times to beat and master": "Tempos para terminar e dominar",
  "Total time played, all sessions": "Tempo total de jogo, todas as sessões",
  "View": "Vista",
  "What Time every set found, in Settings → Library. Restoring this means the two whole-site time orders work right away, without asking RetroAchievements about thousands of games again.":
    "O que o Cronometrar todos os conjuntos encontrou, em Definições → Biblioteca. Restaurar isto faz com que as duas ordenações por tempo em todo o site funcionem de imediato, sem voltar a perguntar ao RetroAchievements por milhares de jogos.",
  "When the app opens": "Quando a aplicação abre",
  "Where Save cover image puts box art. Blank asks each time. Your emulator's thumbnails folder works here.":
    "Onde o Guardar imagem de capa coloca as capas. Em branco, pergunta de cada vez. A pasta de miniaturas do seu emulador serve.",
  "Where this console's games are saved. Blank uses the main folder.":
    "Onde ficam guardados os jogos desta consola. Em branco, usa a pasta principal.",
  "Which copies on a card the achievement set was built from. Checking every result costs a request per console behind every card; left to the button, it is asked one game at a time.":
    "Quais das cópias de um cartão deram origem ao conjunto de conquistas. Verificar todos os resultados custa um pedido por cada consola atrás de cada cartão; deixado ao botão, é perguntado um jogo de cada vez.",
  "Whichever you pick, the other is one click away in the header. Opening on the library reads your folders straight away, which is a moment's work on a large shelf.":
    "Escolha o que escolher, o outro fica a um clique no cabeçalho. Abrir na biblioteca lê as suas pastas logo de início, o que demora um momento numa estante grande.",
  "Working out what still needs asking…": "A apurar o que falta perguntar…",
  "Works out the hash RetroAchievements knows each dump by and checks it against the set, which is the certain version of the name match shown on search results. Cartridge consoles only - a disc's hash is taken from inside the image, which this app does not open. Each file is only ever read once; the answers are kept.":
    "Calcula o hash pelo qual o RetroAchievements conhece cada dump e compara-o com o conjunto, que é a versão certa da correspondência por nome mostrada nos resultados da pesquisa. Só consolas de cartucho — o hash de um disco é tirado de dentro da imagem, que esta aplicação não abre. Cada ficheiro só é lido uma vez; as respostas ficam guardadas.",
  "{done} of {total} sources": "{done} de {total} fontes",
  "{done} of {total} sources · about {eta}":
    "{done} de {total} fontes · cerca de {eta}",
  "{done} of {total} sources — finishing up":
    "{done} de {total} fontes — a terminar",
  "{empty} consoles have no program set and will be filled in. {taken} are already pointed at something else - replace those too?":
    "{empty} consolas não têm programa definido e vão ser preenchidas. {taken} já apontam para outra coisa — substituir também essas?",
  "{n} consoles pointed at {names}.": "{n} consolas apontadas para {names}.",
  "{n} games timed. Run it again whenever you like — it only asks about sets that are new or have changed.":
    "{n} jogos cronometrados. Volte a correr quando quiser — só pergunta pelos conjuntos novos ou que mudaram.",
  "{n} left": "faltam {n}",
  "{n} left · about {eta}": "faltam {n} · cerca de {eta}",
  "{n} more come from RetroAchievements' own collections and almost certainly work, though their names are not ones the set lists.":
    "Mais {n} vêm das coleções do próprio RetroAchievements e é quase certo que funcionam, ainda que os nomes não sejam dos que o conjunto lista.",
  "{n} selected": "{n} selecionados",
  "{time} played in total": "{time} jogados no total",

  /* -- regions --

     Shown on file rows, on game cards and in the preferred-region
     list, all from the same table, so the name you pick in Settings
     is the name you then read on the cards. -- */
  "USA": "EUA",
  "Europe": "Europa",
  "Japan": "Japão",
  "World": "Mundo",
  "Australia": "Austrália",
  "Korea": "Coreia",
  "Asia": "Ásia",
  "Austria": "Áustria",
  "Belgium": "Bélgica",
  "Brazil": "Brasil",
  "Canada": "Canadá",
  "China": "China",
  "Croatia": "Croácia",
  "Denmark": "Dinamarca",
  "Finland": "Finlândia",
  "France": "França",
  "Germany": "Alemanha",
  "Greece": "Grécia",
  "Hong Kong": "Hong Kong",
  "India": "Índia",
  "Ireland": "Irlanda",
  "Israel": "Israel",
  "Italy": "Itália",
  "Latin America": "América Latina",
  "Mexico": "México",
  "Netherlands": "Países Baixos",
  "New Zealand": "Nova Zelândia",
  "Norway": "Noruega",
  "Poland": "Polónia",
  "Portugal": "Portugal",
  "Russia": "Rússia",
  "Scandinavia": "Escandinávia",
  "South Africa": "África do Sul",
  "Spain": "Espanha",
  "Sweden": "Suécia",
  "Switzerland": "Suíça",
  "Taiwan": "Taiwan",
  "UK": "Reino Unido",
  "Unknown": "Desconhecida",

  /* -- the keyboard, and the sheet that lists it -- */
  "A key pressed while you are typing is just typing — these only work outside a text box.":
    "Uma tecla premida enquanto escreve é apenas escrita — estes atalhos só funcionam fora de uma caixa de texto.",
  "Add it to the download list": "Adicioná-lo à lista de transferências",
  "Clear the search, or close what is open":
    "Limpar a pesquisa, ou fechar o que está aberto",
  "Jump to the search box": "Ir para a caixa de pesquisa",
  "Keyboard shortcuts": "Atalhos de teclado",
  "Did you mean {title}?": "Queria dizer {title}?",
  "Move through the results": "Percorrer os resultados",
  "Open the one you are on": "Abrir aquele em que está",
  "This list": "Esta lista",

  /* -- swapping a copy that does not work for one that does -- */
  "Delete the old copy": "Apagar a cópia antiga",
  "Delete the old copy that would not have earned achievements?":
    "Apagar a cópia antiga que não daria conquistas?",
  "Keep both": "Manter as duas",
  "Replaced. The old copy is gone.":
    "Substituída. A cópia antiga desapareceu.",
  "{name} is installed, and its copy is one the achievement set was built from.":
    "{name} está instalado, e esta cópia é uma daquelas a partir das quais o conjunto de conquistas foi feito.",

  /* -- taking less of the machine while things arrive -- */
  "A ceiling on the whole app rather than on each download, so three at once share it rather than taking three times as much. Anything under 32 KB/s is treated as no limit — at that rate a disc image takes a fortnight, and nobody meant to type it.":
    "Um limite para toda a aplicação e não para cada transferência, por isso três ao mesmo tempo partilham-no em vez de levarem o triplo. Abaixo de 32 KB/s conta como sem limite — a essa velocidade uma imagem de disco demora duas semanas, e ninguém quis escrever isso.",
  "Downloads stop pulling while a game this app launched is open, and carry on the moment it closes. Nothing is cancelled and nothing restarts — the transfer waits where it is. Only games started from here: one opened in the emulator itself is invisible to this app.":
    "As transferências param enquanto um jogo iniciado por esta aplicação estiver aberto, e continuam assim que ele fechar. Nada é cancelado e nada recomeça — a transferência espera onde está. Só jogos iniciados aqui: um aberto no próprio emulador é invisível para esta aplicação.",
  "KB/s, 0 for no limit": "KB/s, 0 para sem limite",
  "Limit speed to": "Limitar a velocidade a",
  "Pause while a game is running": "Pausar enquanto um jogo está a correr",

  /* -- room on the disk -- */
  "Download anyway": "Transferir mesmo assim",
  "There may not be room for this.": "Pode não haver espaço para isto.",
  "{folder} needs {need} and has {free} free":
    "{folder} precisa de {need} e tem {free} livres",
  "{size} free": "{size} livres",

  /* -- the saves, backed up on their own -- */
  "Back the saves up": "Fazer cópia dos saves",
  "Back up now": "Fazer cópia agora",
  "Backing up…": "A fazer a cópia…",
  "No emulator saves found.": "Não foram encontrados saves de emuladores.",
  "None yet. They will go in {folder}.":
    "Ainda nenhuma. Vão ficar em {folder}.",
  "Taken when the app opens, if one is due — there is no scheduler, because a backup of a machine nobody is using is a backup of nothing new. Saves only, never the index, and the app only ever reads an emulator's folder. Off by default: these run to hundreds of megabytes each.":
    "Feita quando a aplicação abre, se estiver na altura — não há agendador, porque a cópia de uma máquina que ninguém está a usar não traz nada de novo. Só os saves, nunca o índice, e a aplicação apenas lê a pasta do emulador. Desligado por omissão: cada uma ocupa centenas de megabytes.",
  "The one thing here that cannot be downloaded again. Kept separately from the backup above, and the last three are kept.":
    "A única coisa aqui que não se pode voltar a transferir. Guardada à parte da cópia acima, e ficam as três últimas.",
  "every day": "todos os dias",
  "every month": "todos os meses",
  "every week": "todas as semanas",
  "never": "nunca",
  "{n} kept, {size} in {folder}": "{n} guardadas, {size} em {folder}",
  "{n} save files backed up.": "{n} ficheiros de save copiados.",

  /* -- the ones archive.org will only serve to an account -- */
  "Download the other {n} now?": "Transferir os outros {n} agora?",
  "Download {n}": "Transferir {n}",
  "Sign in here and they will download straight away.":
    "Inicie sessão aqui e serão transferidos de imediato.",
  "Sign in to get all {total}, or close this to download just the other {rest}.":
    "Inicie sessão para obter os {total}, ou feche isto para transferir apenas os outros {rest}.",
  "{n} of these need an archive.org account — you'll be asked to sign in.":
    "{n} destes precisam de uma conta archive.org — ser-lhe-á pedido para iniciar sessão.",
  "{n} of these need an archive.org account:":
    "{n} destes precisam de uma conta archive.org:",
  "{n} of these still need an account and would fail.":
    "{n} destes continuam a precisar de uma conta e falhariam.",
  "…and {n} more": "…e mais {n}",

  /* -- MiNERVA, which shares a console at a time -- */
  "Nothing on this PC is set up to open a magnet link.":
    "Não há nada neste PC configurado para abrir uma ligação magnet.",
  "Open it in your torrent client and choose file number {n} — that is this game and nothing else.":
    "Abra-o no seu cliente de torrents e escolha o ficheiro número {n} — é este jogo e mais nada.",
  "Open it in your torrent client to choose what to fetch.":
    "Abra-o no seu cliente de torrents para escolher o que obter.",
  "Open the magnet": "Abrir o magnet",
  "{name} comes from MiNERVA, which shares a whole console as one torrent.":
    "{name} vem do MiNERVA, que partilha uma consola inteira como um só torrent.",
  "{n} others were left alone.": "Os outros {n} ficaram como estavam.",

  "Shared as part of a whole-console torrent — opens in your torrent client":
    "Partilhado como parte de um torrent de uma consola inteira — abre no seu cliente de torrents",
  "torrent": "torrent",

  /* -- torrents, and what they cost -- */
  "Games from MiNERVA come as one torrent per console; this app takes only the file you asked for. Unlike a download, a torrent also uploads — everyone in the swarm sees your address, not just one server.":
    "Os jogos do MiNERVA vêm como um torrent por consola; esta aplicação leva apenas o ficheiro que pediu. Ao contrário de uma transferência, um torrent também envia — toda a gente no enxame vê o seu endereço, não apenas um servidor.",
  "I understand, download it": "Compreendo, transferir",
  "Left blank the proxy is used without one. Kept with the app's other settings on this PC, in plain text, the same as the archive.org details — so a shared machine is a reason not to put one here.":
    "Em branco, o proxy é usado sem um. Fica guardado com as outras definições da aplicação neste PC, em texto simples, tal como os dados do archive.org — por isso um computador partilhado é uma razão para não pôr aqui nada.",
  "Limit upload to": "Limitar o envio a",
  "Only use this network adapter": "Usar apenas este adaptador de rede",
  "Open it in your torrent client and pick {name} — that one file and nothing else.":
    "Abra-o no seu cliente de torrents e escolha {name} — esse ficheiro e mais nenhum.",
  "Proxy sign-in": "Início de sessão do proxy",
  "SOCKS5 proxy": "Proxy SOCKS5",
  "Say as little as possible about this client":
    "Dizer o mínimo possível sobre este cliente",
  "Settings → Downloads → Torrents can bind this to a VPN adapter, which stops that.":
    "Em Definições → Transferências → Torrents pode ligar isto a um adaptador de VPN, o que impede isso.",
  "The kill switch, and the setting that matters most. Name your VPN's adapter and nothing leaves by any other route — if the VPN drops, the transfers stop instead of quietly carrying on over your ordinary connection. Left blank, torrents use whatever route the machine would.":
    "O interruptor de emergência, e a definição que mais importa. Indique o adaptador da sua VPN e nada sai por outro caminho — se a VPN cair, as transferências param em vez de continuarem discretamente pela sua ligação normal. Em branco, os torrents usam o caminho que a máquina usaria.",
  "The kind of endpoint a VPN provider sells for torrenting. Peers and trackers both go through it and names are resolved at the far end, so your DNS server is not told what you are fetching. One warning: these magnets have no trackers, so peers are found over DHT, which is UDP — and most SOCKS5 proxies will not carry UDP. If nothing is ever found, this is why, and binding to the adapter above is the better answer.":
    "O tipo de ponto de acesso que um fornecedor de VPN vende para torrents. Tanto os pares como os trackers passam por ele e os nomes são resolvidos do outro lado, por isso o seu servidor de DNS não fica a saber o que está a obter. Um aviso: estes magnets não têm trackers, por isso os pares são encontrados por DHT, que é UDP — e a maioria dos proxies SOCKS5 não transporta UDP. Se nunca encontrar nada, é por isto, e ligar ao adaptador acima é a melhor resposta.",
  "This one comes by BitTorrent, which works differently from the rest of the app.":
    "Este vem por BitTorrent, que funciona de forma diferente do resto da aplicação.",
  "Those are already on the list.": "Esses já estão na lista.",
  "Torrents": "Torrents",
  "Torrents upload while they download and there is no way to have one without the other. Capping it keeps the rest of your connection usable; setting it to nothing at all makes you a peer nobody wants to talk to, which makes your own downloads slower.":
    "Os torrents enviam enquanto transferem e não há forma de ter um sem o outro. Limitar mantém o resto da ligação utilizável; pôr a zero torna-o um par com quem ninguém quer falar, o que torna as suas próprias transferências mais lentas.",
  "While it downloads it also uploads, so everyone else fetching that collection can see your address — not just one server.":
    "Enquanto transfere também envia, por isso toda a gente que estiver a obter essa coleção vê o seu endereço — e não apenas um servidor.",
  "e.g. 10.2.0.2, or a VPN adapter's name":
    "por exemplo 10.2.0.2, ou o nome de um adaptador de VPN",
  "host": "servidor",
  "libtorrent's anonymous mode: no client name and no version on the wire, and nothing that would identify this app to a peer. It does not hide your address — only the adapter or the proxy above can do that.":
    "O modo anónimo do libtorrent: sem nome nem versão do cliente na ligação, e nada que identifique esta aplicação a um par. Não esconde o seu endereço — só o adaptador ou o proxy acima o fazem.",
  "not available in this build": "não disponível nesta versão",
  "password": "palavra-passe",
  "port": "porta",
  "username": "utilizador",
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

/** A region, or a list of them, in the reader's language.
 *
 *  Regions arrive from the index as English names and are shown in three
 *  places - the badge on a file row, the chips on a game card, the line in a
 *  preview. Translating them at the point of display rather than in the data
 *  keeps the value the filters match on exactly as the index wrote it.
 *
 *  A name with no entry comes back unchanged, which is right: the index
 *  carries a long tail of them and an untranslated "Liechtenstein" is a
 *  better answer than a blank. */
function tRegion(text) {
  return String(text ?? "")
    .split(",")
    .map((one) => t(one.trim()))
    .filter(Boolean)
    .join(", ");
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
