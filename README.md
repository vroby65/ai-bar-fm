# ai-bar-fm

File manager **TUI a una sola lista**, ispirato ai tasti funzione di Midnight Commander e pensato per una piccola finestra terminale in **ai-bar**.

Il programma è scritto in **Bash 4+**, usa **mouse xterm/SGR**, il **tema grigio grafite** con convenzioni di navigazione simili a Lynx e cornici Unicode box-drawing (`┌─┐`, `│ │`, `└─┘`), con fallback ASCII. **Niente ncurses, dialog, fzf o dipendenze TUI**: su Linux servono soltanto Bash, `stty` e i comandi GNU di base (`cp`, `mv`, `mkdir`, `rm`).

## Installazione rapida (un solo comando)

Per scaricare e installare `ai-bar-fm` nella directory utente `~/.local/bin`, senza `sudo`, senza compilare e senza clonare il repository, esegui:

```bash
mkdir -p "$HOME/.local/bin" && curl -fsSL "https://raw.githubusercontent.com/vroby65/ai-bar-fm/main/ai-bar-fm" -o "$HOME/.local/bin/ai-bar-fm" && chmod +x "$HOME/.local/bin/ai-bar-fm"
```

Esegui subito il programma con:

```bash
"$HOME/.local/bin/ai-bar-fm"
```

Ripetere il comando di installazione scarica la versione aggiornata da `main`. Per il download e' necessario `curl`; il file manager in esecuzione non richiede `curl` ne' librerie TUI. Se `~/.local/bin` e' gia' nel `PATH`, basta digitare `ai-bar-fm` (anche da Fish).

## Avvio

```bash
git clone https://github.com/vroby65/ai-bar-fm.git
cd ai-bar-fm
./ai-bar-fm
./ai-bar-fm "$HOME/Documenti"
```

Per un'installazione personale, dopo aver ottenuto il sorgente:

```bash
install -Dm755 ai-bar-fm "$HOME/.local/bin/ai-bar-fm"
```

L'interfaccia richiede un terminale interattivo di almeno **35 colonne × 12 righe**; la larghezza consigliata è **70+ colonne**. Per un terminale integrato che gestisce già la propria schermata:

```bash
ABFM_NO_ALT_SCREEN=1 ai-bar-fm
```

Per utilizzare l’interfaccia senza colori o con cornici ASCII:

```bash
ABFM_NO_COLOR=1 ai-bar-fm
ABFM_ASCII=1 ai-bar-fm
```

## Tema grigio e navigazione stile Lynx

Il pannello usa uno **sfondo grigio grafite** (ANSI 256 colori), evitando l'azzurro intenso del tema precedente. La riga attiva e' in grigio chiaro con testo scuro. Restano i colori distintivi per directory, eseguibili, collegamenti simbolici, elementi marcati e la barra F3–F8.

La navigazione prende ispirazione da Lynx:

- **Su / Giu** (o `j` / `k`): sposta la riga evidenziata
- **Destra / Invio** (o `l`): entra nella directory evidenziata
- **Sinistra / Backspace** (o `h`): torna alla directory superiore

Mouse, doppio clic, rotella e funzioni F3–F8 rimangono attivi. Le directory continuano a mostrare il prefisso `/` e i file nascosti sono visibili per impostazione predefinita. Le opzioni `ABFM_NO_COLOR=1` (o `NO_COLOR`) e `ABFM_ASCII=1` permettono di disabilitare i colori e le cornici Unicode.

### Correzione clic ripetuti e locale italiana

Il calcolo dei millisecondi per riconoscere il doppio clic normalizza `EPOCHREALTIME`: accetta **sia la virgola sia il punto decimale**. Questo evita l'errore aritmetico che poteva comparire alla riga 194 con una locale italiana.

## Tasti

| Tasto | Azione |
| --- | --- |
| **F3** / Spazio | Seleziona o deseleziona il file corrente (`*`) |
| **F4** | Copia i file marcati, oppure la riga corrente, negli appunti interni |
| **F5** | Taglia i file marcati, oppure la riga corrente, negli appunti interni |
| **F6** | Incolla nella directory visualizzata |
| **F7** | Crea directory (digitare il nome e premere Invio) |
| **F8** | Elimina file e directory selezionati, dopo conferma (`s`) |
| **Ctrl+X**, poi **C** | `chmod`: cambia i permessi ottali di file o directory marcati, oppure correnti |
| **Ctrl+X**, poi **O** | `chown`: cambia utente o utente:gruppo dei file marcati, oppure correnti |
| **Ctrl+X**, poi **S** | `ln -s`: crea nella directory corrente un link simbolico al file/directory evidenziato |
| ↑ / ↓, `j` / `k` | Muovi il cursore |
| PagSu / PagGiù, Home / End | Scorrimento veloce |
| **Freccia destra** / Invio / `l` | Entra nella directory, oppure avvia un file eseguibile |
| **Freccia sinistra** / Backspace / `h` | Torna alla directory superiore (Lynx) |
| Mouse sinistro | Seleziona la riga; un doppio click apre una directory oppure esegue il file avviabile |
| Click sull'indicatore di selezione (colonna 3) | Seleziona o deseleziona l'elemento; il bordo esterno non è cliccabile |
| Rotella mouse | Scorre l'elenco |
| Click sulla barra F3–F8 | Attiva la relativa funzione, anche nella barra compatta |
| `r` | Aggiorna |
| `q` | Esci |

Le directory appaiono prima dei file e hanno **`/` davanti al nome** (per esempio `/Documenti`), secondo la convenzione visiva di MC. I file e le directory **nascosti (`.nome`) sono visibili per impostazione predefinita**. Il simbolo `@` indica un collegamento simbolico. La riga `/..` permette di tornare al livello precedente. I segni di selezione vengono azzerati quando si cambia directory, ma gli appunti restano disponibili finché l'applicazione è aperta.

## Esecuzione e gestione degli attributi

Premendo **Invio** oppure **freccia destra** su un file regolare con permesso di esecuzione, `ai-bar-fm` lo avvia direttamente, senza usare `eval`. Il programma figlio riceve il terminale normale con **stdin, stdout e stderr**; alla sua uscita il file manager attende Invio prima di ripristinare la TUI. Non apre automaticamente file privi del bit eseguibile.

Le scorciatoie **Ctrl+X, C/O/S** sono *sequenze*, non tre tasti tenuti contemporaneamente: premere `Ctrl+X`, rilasciare, quindi `c`, `o` oppure `s`.

- **chmod** accetta soltanto valori ottali di tre o quattro cifre (per esempio `755` o `0644`), senza ricorsione. Non modifica le destinazioni dei link simbolici: tali link vengono saltati.
- **chown** accetta `utente` o `utente:gruppo` (anche identificatori numerici), senza ricorsione e **senza usare sudo**. Se non hai i privilegi necessari, l'operazione viene segnalata come non riuscita.
- **Link simbolico** richiede il nome del nuovo link, creato nella **stessa cartella** del file selezionato con destinazione relativa. Il programma non sovrascrive link o file preesistenti.

Le operazioni `chmod` e `chown` si applicano ai file marcati con F3, oppure alla riga corrente se non ci sono marcature. La creazione del link utilizza sempre e soltanto la riga corrente.

## Ridisegno senza sfarfallio

I movimenti del cursore aggiornano soltanto la riga precedente e quella corrente; il terminale non viene cancellato a ogni pressione di tasto. Il ridisegno completo è riservato a cambio di directory, scorrimento, aggiornamento o ridimensionamento. Il bordo in fondo non invia più un ritorno a capo che faceva scorrere lo schermo e poteva sfalsare le coordinate mouse.

## Sicurezza e limiti della versione iniziale

- **Non sovrascrive**: quando il nome di destinazione esiste già, F6 lascia invariato l'elemento e lo segnala come non riuscito.
- F8 esegue una **cancellazione ricorsiva permanente** (`rm -rf`) dopo una conferma esplicita: **non** usa il cestino.
- La copia mantiene i metadati e i link simbolici usando `cp -a` (GNU coreutils). Taglia usa `mv`.
- Non si possono copiare directory dentro sé stesse.
- Gli appunti sono interni al programma, **non** agli appunti di sistema/desktop.
- Le directory sono ordinate secondo la locale della shell; il testo è troncato se troppo lungo. Il calcolo della larghezza usa il numero di caratteri Bash, e per caratteri Unicode a doppia larghezza l'allineamento del bordo può risultare imperfetto.
- Invio esegue direttamente i file con permesso di esecuzione; gli altri file normali non vengono aperti.
- Le sequenze dei tasti funzione sono quelle comuni dei terminali xterm e Linux; alcuni terminali grafici possono intercettare F3–F8 e richiedere la riconfigurazione delle scorciatoie.

## Integrazione con ai-bar

Avviare `ai-bar-fm` all'interno di **un PTY** integrato o di un emulatore terminale che supporti le sequenze mouse **xterm SGR (1000/1006)**. Il programma usa `/dev/tty`, la modalità non canonica della tastiera, sequenze ANSI standard e (salvo l'opzione sopra) lo schermo alternativo. Non usa GUI e non necessita dell'ambiente desktop. Per la futura integrazione, si potrà aggiungere una modalità selezione che stampa il percorso scelto su stdout.

## Test

Il funzionamento è verificabile con Python 3 (usato **solo per i test**, non per eseguire il file manager):

```bash
bash -n ai-bar-fm
python3 tests/smoke.py
```

I test usano uno pseudo-terminale e directory temporanee per controllare selezione multipla/copia, taglia, creazione, cancellazione, mancata sovrascrittura, eventi mouse, doppio click, rotella, pulsanti F3–F8 e interazione durante i prompt.

## Licenza

MIT, vedere [LICENSE](LICENSE).
