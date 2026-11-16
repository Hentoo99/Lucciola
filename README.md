# Lucciola – Test Alexa con Voice Monkey (ESP32 + MicroPython)

Piccolo progetto di prova: l'ESP32 si collega al Wi‑Fi e, quando premi un
pulsante (o scrivi `test` nella console seriale), chiama **Voice Monkey**, che fa
partire una **routine Alexa**. In alternativa può far pronunciare ad Alexa una frase.

Funziona nel simulatore **Wokwi** e, senza toccare `main.py`, sulla scheda vera:
basta cambiare le impostazioni in `config.py`.

| File           | A cosa serve                                                      |
|----------------|-------------------------------------------------------------------|
| `main.py`      | Il programma (commentato in italiano)                             |
| `config.py`    | Tutte le impostazioni: Wi‑Fi, token, monkey, speaker, URL, pin    |
| `diagram.json` | Il circuito per Wokwi                                             |

### Cosa vedrai

**Sul seriale** (esempio)
```
Wi-Fi: COLLEGATO in 2.3 s - indirizzo IP: 10.10.0.2
Pronto! Premi il pulsante oppure scrivi 'test' e premi Invio.

===== TEST avviato da: pulsante =====
Voice Monkey: attivo la monkey 'test-allarme'
Voice Monkey: URL https://api-v3.voicemonkey.io/trigger?token=***&device=test-allarme
Voice Monkey: codice HTTP 200
Voice Monkey: risposta   {"success":true,"data":"OK"}
===== TEST RIUSCITO =====
```
Il token non viene mai stampato: al suo posto compare `***`.

**Sul LED**

| LED                          | Significato                                        |
|------------------------------|----------------------------------------------------|
| acceso fisso                 | Wi‑Fi collegato                                    |
| spento                       | Wi‑Fi non collegato (o collegamento in corso)      |
| 3 lampeggi lenti             | test inviato con successo                          |
| lampeggio veloce per 3 s     | errore: Wi‑Fi assente o chiamata fallita           |

Il pulsante ha l'antirimbalzo e accetta **al massimo un test ogni 10 secondi**
(se premi prima, sul seriale compare `Test ignorato: aspetta ancora N s`).

---

## 1. Creare il progetto in Wokwi

1. Vai su [wokwi.com](https://wokwi.com), accedi e clicca **New Project**.
2. Scegli **ESP32**, poi il modello **MicroPython** (MicroPython on ESP32).
3. Si apre un progetto con due schede: `main.py` e `diagram.json`.
   - **`main.py`**: cancella tutto e incolla il contenuto del nostro `main.py`.
   - **`diagram.json`**: cancella tutto e incolla il contenuto del nostro `diagram.json`.
     Comparirà l'ESP32 DevKit V1 con il LED blu (GPIO2, con resistenza da 220 Ω)
     e il pulsante verde.
4. Aggiungi `config.py`: clicca la freccetta accanto alle schede dei file
   (menu dei file) → **New file…** → scrivi `config.py` → incolla il contenuto
   del nostro `config.py`.
5. In `config.py` lascia `SIMULATORE = True`. Puoi già incollare il tuo token
   Voice Monkey (vedi punto 2), oppure lasciare quello di esempio per una prima prova.
6. Clicca il pulsante verde ▶ **Start**. Nel riquadro in basso (Serial Monitor)
   vedrai il collegamento a `Wokwi-GUEST` e l'indirizzo IP.
7. Clicca il **pulsante verde** nel circuito, oppure clicca nel Serial Monitor,
   scrivi `test` e premi Invio.

> **Perché in Wokwi il pulsante è su GPIO4 e non su GPIO0?**
> Il modello Wokwi della DevKit V1 non porta il GPIO0 sui piedini (il tasto BOOT è
> solo disegnato, non si può premere). Per questo nel simulatore il pulsante è su
> **GPIO4 (D4)**, mentre sulla scheda vera si usa il tasto **BOOT (GPIO0)**.
> La scelta è automatica in base a `SIMULATORE`.

> **Prima prova senza token vero.** Con il token di esempio Voice Monkey risponde
> `401` e il LED lampeggia veloce. Sembra un errore, ma ti conferma che Wi‑Fi,
> Internet e HTTPS funzionano: manca solo il token giusto.

> **Privacy.** Un progetto Wokwi salvato può essere aperto da chiunque abbia il
> link. Se dentro c'è il token vero, non condividere il link.

**Se Wokwi non accetta `config.py`:** `main.py` funziona lo stesso. Se non trova
`config.py`, usa le impostazioni di riserva scritte in cima a `main.py`
(sezione `IMPOSTAZIONI`, dentro `class cfg:`). In quel caso modifica lì il token.

**Se il progetto non parte in MicroPython:** apri il `diagram.json` del modello
creato da Wokwi, copia il valore di `"env"` (per esempio
`"micropython-20231005-v1.21.0"`) e mettilo al posto di quello nel nostro
`diagram.json`.

---

## 2. Configurare Voice Monkey

Voice Monkey è un servizio (con skill Alexa) che crea dei finti dispositivi
"smart home": quando l'ESP32 chiama le sue API, il dispositivo si "attiva" e
Alexa può far partire una routine.

1. **Account.** Vai su [voicemonkey.io](https://voicemonkey.io) e registrati
   (puoi accedere con lo stesso account Amazon usato con Alexa).
2. **Skill nell'app Alexa.** App Alexa → **Altro** → **Skill e giochi** →
   cerca **Voice Monkey** → **Abilita per l'uso** → collega l'account
   (stesso account del punto 1).
3. **Crea la monkey `test-allarme`.** Nella dashboard di Voice Monkey vai su
   **Devices** → aggiungi un nuovo dispositivo di tipo **routine trigger**
   e chiamalo `test-allarme`. Controlla l'**ID** del dispositivo (Device ID)
   mostrato nella dashboard: è quello da scrivere in `config.py` alla voce
   `VM_MONKEY`. Se l'ID è diverso dal nome (per esempio `test_allarme`), usa l'ID.
4. **Fai trovare il dispositivo ad Alexa.** App Alexa → **Dispositivi** → **+** →
   **Aggiungi dispositivo** → **Altro** → **Rileva dispositivi**
   (oppure di' "Alexa, trova dispositivi"). Deve comparire `test-allarme`.
5. **Token API.** Nella dashboard Voice Monkey apri la sezione **API**
   (credenziali / token) e copia il token in `config.py` → `VM_TOKEN`.
   Trattalo come una password.
6. **Speaker per l'annuncio (facoltativo, solo se `ANNUNCIO = True`).**
   Nella dashboard aggiungi un dispositivo di tipo **Speaker** e scegli il tuo Echo,
   poi segui la procedura guidata di Voice Monkey (di solito chiede di creare una
   routine Alexa dedicata allo speaker). Copia il suo **ID** in `config.py` →
   `VM_SPEAKER`.

> La dashboard di Voice Monkey cambia ogni tanto: se i nomi dei menu non
> coincidono, cerca le voci "Devices", "Speakers" e "API" nella documentazione:
> [voicemonkey.io/docs](https://voicemonkey.io/docs).

### Endpoint usati (API v3)

Sono in `config.py` come modelli: le parti tra `{}` vengono riempite da `main.py`
e codificate per l'URL (spazi → `%20`, `è` → `%C3%A8`, ecc.).

| Azione                    | URL                                                                                                    |
|---------------------------|--------------------------------------------------------------------------------------------------------|
| Routine (`ANNUNCIO=False`) | `https://api-v3.voicemonkey.io/trigger?token={token}&device={device}`                                 |
| Annuncio (`ANNUNCIO=True`) | `https://api-v3.voicemonkey.io/announce?token={token}&device={device}&speech={testo}&language={lingua}` |

Note:
- l'endpoint dell'annuncio nella v3 è **`/announce`** e il testo va nel
  parametro **`speech`** (nella vecchia v2 si chiamava `text`);
- `language` è un codice tipo `it-IT`; se Voice Monkey lo rifiutasse, toglilo
  dal modello `URL_ANNUNCIO`;
- con la v3 il parametro `device` vuole l'**ID** del dispositivo, non il vecchio
  nome della v2 (altrimenti la risposta è "Device not found").

Documentazione: [Routine Trigger API](https://voicemonkey.io/docs/api/trigger),
[Announcement API](https://voicemonkey.io/docs/api/announcement),
[Migrazione dalla v2](https://voicemonkey.io/docs/migrating-from-v2).

---

## 3. Creare la routine nell'app Alexa

1. App Alexa → **Altro** → **Routine** → **+** (crea routine).
2. **Nome**: per esempio `Test allarme ESP32`.
3. **Quando succede questo** → **Casa intelligente** → scegli **test-allarme** →
   seleziona l'evento di attivazione (di solito **"Premuto"** o
   **"Viene attivato"**) → **Avanti/Salva**.
4. **Aggiungi azione** → **Messaggi** → **Annuncia** (oppure **Alexa dice** →
   **Personalizzato**) → scrivi `Test riuscito` → scegli l'Echo.
5. **Aggiungi azione** → **Casa intelligente** → scegli una luce → **Accendi**.
6. **Aggiungi azione** → **Attendi** → **5 secondi**.
7. **Aggiungi azione** → **Casa intelligente** → la stessa luce → **Spegni**.
8. In **Da** (Alexa risponderà da) scegli il tuo Echo, poi **Salva**.
9. Controlla che la routine sia **attiva** (interruttore acceso).

Ora premi il pulsante: Alexa dice "Test riuscito" e la luce si accende per 5 secondi.
La prima volta possono servire alcuni secondi.

---

## 4. Caricare tutto sulla scheda vera con Thonny

1. **Installa [Thonny](https://thonny.org)** e collega l'ESP32 al PC con un cavo
   USB **dati** (non solo ricarica). Se la porta non compare, installa il driver
   **CP210x** o **CH340** (dipende dal chip USB della scheda).
2. **Installa MicroPython sulla scheda** (solo la prima volta):
   **Strumenti → Opzioni → Interprete** → scegli **MicroPython (ESP32)** e la porta →
   **Installa o aggiorna MicroPython (esptool)** → famiglia **ESP32**, variante
   **Espressif • ESP32 / WROOM** → **Installa**.
   Se si blocca su "Connecting…", tieni premuto **BOOT** finché parte la scrittura.
3. **Modifica `config.py`** sul PC:
   ```python
   SIMULATORE = False
   WIFI_SSID = "NomeDellaTuaRete"
   WIFI_PASSWORD = "PasswordDellaTuaRete"
   VM_TOKEN = "il-tuo-token"
   VM_MONKEY = "test-allarme"
   ```
4. **Copia i file sulla scheda**: apri `config.py` in Thonny →
   **File → Salva con nome… → Dispositivo MicroPython** → nome `config.py`.
   Fai lo stesso con `main.py` (nome esatto `main.py`).
   In alternativa: **Visualizza → File**, clic destro sui file → **Carica su /**.
5. **Avvia**: premi **EN/RST** sulla scheda (oppure clicca nello Shell di Thonny e
   premi **Ctrl+D**). `main.py` parte da solo a ogni accensione.
6. **Prova**: premi il tasto **BOOT** (GPIO0), oppure scrivi `test` nello Shell
   di Thonny e premi Invio. Il LED blu della scheda (GPIO2) fa da indicatore.
7. Per fermare il programma e modificare i file: pulsante **Stop** di Thonny
   (o **Ctrl+C** nello Shell).

> Non tenere premuto **BOOT** mentre premi **EN/RST** o mentre colleghi la scheda:
> l'ESP32 entrerebbe in modalità programmazione invece di avviare `main.py`.

---

## 5. Se non funziona

### Wi‑Fi

| Messaggio sul seriale | Causa probabile | Cosa fare |
|---|---|---|
| `NON collegato - rete non trovata` | SSID sbagliato, rete a 5 GHz, scheda troppo lontana | L'ESP32 vede solo il **2,4 GHz**. Controlla maiuscole/minuscole dell'SSID. Avvicinati al router. |
| `NON collegato - password sbagliata` / `handshake scaduto` | Password errata | Ricontrolla `WIFI_PASSWORD` (spazi, maiuscole). |
| `NON collegato - tempo scaduto` | Router lento o segnale debole | Aumenta `WIFI_TIMEOUT_S` in `config.py`. In Wokwi riprova: a volte il collegamento è lento. |
| `collegamento PERSO` | Router riavviato, segnale debole | Nessuna azione: il programma riprova da solo ogni 5 secondi. |
| In Wokwi si collega a `NomeDellaTuaRete` | `SIMULATORE = False` | In Wokwi metti `SIMULATORE = True`. |

### Chiamata a Voice Monkey

| Messaggio | Causa probabile | Cosa fare |
|---|---|---|
| `codice HTTP 401` / `403`, `INVALID_TOKEN` | Token errato o di esempio | Ricopia `VM_TOKEN` dalla dashboard, senza spazi. |
| `codice HTTP 400` / `404`, `Device not found` | ID della monkey/speaker sbagliato | Usa l'**ID** mostrato nella dashboard v3 (non il vecchio nome v2). |
| `codice HTTP 429` | Troppe richieste | Aspetta qualche minuto. Il limite di 10 s tra un test e l'altro aiuta. |
| `codice HTTP 5xx` | Problema temporaneo di Voice Monkey | Riprova più tardi. |
| `ERRORE di rete - nome del server non trovato (DNS)` (`-202`) | Niente Internet, oppure URL scritto male | Controlla che il router abbia Internet e l'URL in `config.py`. |
| `ERRORE di rete - il server non ha risposto entro 10 s` | Connessione lenta | Riprova, oppure aumenta `HTTP_TIMEOUT_S`. |
| `memoria insufficiente` / `errore nella connessione sicura HTTPS` | HTTPS usa molta RAM, o connessione interrotta | Riavvia la scheda (EN/RST) e riprova. |
| `ImportError: no module named 'urequests'` | Firmware MicroPython senza moduli di rete | Reinstalla un MicroPython recente per ESP32 (punto 4.2). |

### Tutto "OK" ma Alexa non fa niente

Se vedi `codice HTTP 200` e `TEST RIUSCITO`, la parte ESP32 funziona: il problema
è lato Alexa.
- La routine esiste ed è **attiva**? Il trigger è proprio **test-allarme**?
- Alexa vede il dispositivo `test-allarme`? Altrimenti rifai **Rileva dispositivi**.
- La skill Voice Monkey è abilitata e collegata allo **stesso account**?
- L'Echo è in modalità **Non disturbare** o ha il volume a zero?
- Con `ANNUNCIO = True`: lo speaker è configurato in Voice Monkey (punto 2.6) e
  `VM_SPEAKER` contiene il suo ID?

### Pulsante e LED

| Problema | Cosa fare |
|---|---|
| In Wokwi il pulsante non fa niente | Deve essere collegato a **D4** (GPIO4) e a GND, come nel nostro `diagram.json`. Puoi sempre scrivere `test` nel Serial Monitor. |
| `Test ignorato: aspetta ancora N s` | È voluto: massimo un test ogni 10 secondi (`PAUSA_TRA_TEST_S`). |
| Sulla scheda vera il LED non si accende | Alcune schede hanno il LED su un altro pin o non lo hanno: cambia `PIN_LED`. |
| Scrivo `test` ma non succede nulla | Assicurati di premere **Invio**. In Thonny scrivi nello **Shell** mentre il programma è in esecuzione. |
| Thonny dice "Device is busy" o non si collega | Premi **Stop**, chiudi altri programmi che usano la porta seriale (es. Arduino IDE). |
| `ATTENZIONE: config.py non trovato` | `config.py` non è sulla scheda (o ha un altro nome): ricaricalo come al punto 4.4. |
