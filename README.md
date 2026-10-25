# ai-bar-fm

File manager **TUI a una sola lista**, ispirato ai tasti funzione di Midnight Commander e pensato per una piccola finestra terminale in **ai-bar**.

Il programma è scritto in **Bash 4+**, usa bordi ASCII (`+`, `-`, `|`) e sequenze ANSI per evidenziare la riga corrente. **Niente ncurses, dialog, fzf o dipendenze TUI**: su Linux servono soltanto Bash, `stty` e i comandi GNU di base (`cp`, `mv`, `mkdir`, `rm`).

## Avvio

```bash
git clone https://github.com/vroby65/ai-bar-fm.git
cd ai-bar-fm
./ai-bar-fm
./ai-bar-fm "$HOME/Documenti"
```

> Finché la PR non è stata unita in `main`, si può provare il branch proposto con `git clone -b feat/bash-single-pane-file-manager https://github.com/vroby65/ai-bar-fm.git`.

Per un'installazione personale, dopo aver ottenuto il sorgente:

```bash
install -Dm755 ai-bar-fm "$HOME/.local/bin/ai-bar-fm"
```

L'interfaccia richiede un terminale interattivo di almeno **35 colonne × 12 righe**; la larghezza consigliata è **70+ colonne**. Per un terminale integrato che gestisce già la propria schermata:

```bash
ABFM_NO_ALT_SCREEN=1 ai-bar-fm
```

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

Avviare `ai-bar-fm` all'interno di **un PTY** integrato o di un emulatore terminale. Il programma usa `/dev/tty`, la modalità non canonica della tastiera, sequenze ANSI standard e (salvo l'opzione sopra) lo schermo alternativo. Non usa GUI e non necessita dell'ambiente desktop. Per la futura integrazione, si potrà aggiungere una modalità selezione che stampa il percorso scelto su stdout.

## Test

Il funzionamento è verificabile con Python 3 (usato **solo per i test**, non per eseguire il file manager):

```bash
bash -n ai-bar-fm
python3 tests/smoke.py
```

I test usano uno pseudo-terminale e directory temporanee per controllare selezione multipla/copia, taglia, creazione, cancellazione e mancata sovrascrittura.

## Licenza

MIT, vedere [LICENSE](LICENSE).
