# ai-bar-fm

File manager **TUI a una sola lista**, ispirato ai tasti funzione di Midnight Commander e pensato per una piccola finestra terminale in **ai-bar**.

Il programma è scritto in **Bash 4+**, usa **mouse xterm/SGR**, la **palette classica a 16 colori di Midnight Commander** e cornici Unicode box-drawing (`┌─┐`, `│ │`, `└─┘`), con fallback ASCII. **Niente ncurses, dialog, fzf o dipendenze TUI**: su Linux servono soltanto Bash, `stty` e i comandi GNU di base (`cp`, `mv`, `mkdir`, `rm`).

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

## Aspetto classico Midnight Commander

L'interfaccia a **pannello singolo** segue le convenzioni dei colori classici di MC, senza dipendere dalla sua installazione:

| Elemento | Aspetto |
| --- | --- |
| Pannello e file ordinari | Grigio chiaro su blu |
| Directory | Bianco brillante su blu |
| File eseguibili | Verde brillante su blu |
| Collegamenti simbolici | Ciano su blu (rosso se interrotti) |
| Riga corrente | Nero su ciano |
| File marcati | Giallo su blu, oppure giallo su ciano se correnti |
| Barra comandi F3-F8 | Sfondo nero e tasti evidenziati in ciano |

La barra mantiene **F3 seleziona, F4 copia, F5 taglia, F6 incolla, F7 crea directory, F8 elimina**, cioe' le scorciatoie proprie di questo progetto; non altera i tasti per imitare MC. Le aree cliccabili restano disponibili anche in una finestra stretta di ai-bar.

L'uso di **colori ANSI standard**, anziche' di sequenze 256-color, consente il funzionamento con i terminali tradizionali. Si possono disattivare i colori con `ABFM_NO_COLOR=1` (oppure `NO_COLOR=1`) e forzare i bordi ASCII con `ABFM_ASCII=1`.

## Tasti

| Tasto | Azione |
| --- | --- |
| **F3** / Spazio | Seleziona o deseleziona il file corrente (`*`) |
| **F4** | Copia i file marcati, oppure la riga corrente, negli appunti interni |
| **F5** | Taglia i file marcati, oppure la riga corrente, negli appunti interni |
| **F6** | Incolla nella directory visualizzata |
| **F7** | Crea directory (digitare il nome e premere Invio) |
| **F8** | Elimina file e directory selezionati, dopo conferma (`s`) |
| ↑ / ↓, `j` / `k` | Muovi il cursore |
| PagSu / PagGiù, Home / End | Scorrimento veloce |
| Invio | Apri directory corrente |
| Backspace | Vai alla directory padre |
| Mouse sinistro | Seleziona la riga; un doppio click entra nella directory |
| Click sull'indicatore di selezione | Seleziona o deseleziona l'elemento |
| Rotella mouse | Scorre l'elenco |
| Click sulla barra F3–F8 | Attiva la relativa funzione, anche nella barra compatta |
| `r` | Aggiorna |
| `q` | Esci |

Le directory appaiono prima dei file, inclusi gli elementi nascosti. Il simbolo `@` indica un collegamento simbolico. La riga `../` permette di tornare al livello precedente. I segni di selezione vengono azzerati quando si cambia directory, ma gli appunti restano disponibili finché l'applicazione è aperta.

## Sicurezza e limiti della versione iniziale

- **Non sovrascrive**: quando il nome di destinazione esiste già, F6 lascia invariato l'elemento e lo segnala come non riuscito.
- F8 esegue una **cancellazione ricorsiva permanente** (`rm -rf`) dopo una conferma esplicita: **non** usa il cestino.
- La copia mantiene i metadati e i link simbolici usando `cp -a` (GNU coreutils). Taglia usa `mv`.
- Non si possono copiare directory dentro sé stesse.
- Gli appunti sono interni al programma, **non** agli appunti di sistema/desktop.
- Le directory sono ordinate secondo la locale della shell; il testo è troncato se troppo lungo. Il calcolo della larghezza usa il numero di caratteri Bash, e per caratteri Unicode a doppia larghezza l'allineamento del bordo può risultare imperfetto.
- Non esegue/apre file normali: per ora Invio serve solo a entrare nelle directory.
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
