# =====================================================================
#  main.py - Test Alexa con Voice Monkey (MicroPython su ESP32)
# =====================================================================
#  Cosa fa:
#   1. all'avvio si collega al Wi-Fi e stampa l'indirizzo IP
#   2. premendo il pulsante (o scrivendo "test" nella console seriale)
#      chiama Voice Monkey, che fa partire la routine Alexa di test
#      oppure, con ANNUNCIO = True, fa parlare Alexa
#   3. stampa l'esito (codice HTTP e risposta, mai il token)
#
#  Significato del LED:
#   - acceso fisso ............ Wi-Fi collegato
#   - spento .................. Wi-Fi non collegato
#   - 3 lampeggi lenti ........ test inviato con successo
#   - lampeggio veloce 3 s .... errore (Wi-Fi assente o chiamata fallita)
#
#  Le impostazioni sono in config.py: è l'unico file da cambiare per
#  passare dal simulatore Wokwi alla scheda vera.
# =====================================================================

import gc
import sys
import time
import json
import select
import network
from machine import Pin

# La libreria HTTP si chiama "urequests" nelle versioni vecchie di
# MicroPython e "requests" in quelle nuove: proviamo entrambe.
try:
    import urequests as requests
except ImportError:
    import requests


# ---------------------------------------------------------------------
# IMPOSTAZIONI
# ---------------------------------------------------------------------
# Di norma le impostazioni arrivano da config.py. Se config.py manca
# (per esempio perché non l'hai ancora caricato), usiamo questi valori
# di riserva, pensati per il simulatore Wokwi.
try:
    import config as cfg
except ImportError:
    print("ATTENZIONE: config.py non trovato, uso le impostazioni di riserva per Wokwi")

    class cfg:
        SIMULATORE = True
        WOKWI_SSID = "Wokwi-GUEST"
        WOKWI_PASSWORD = ""
        WOKWI_CANALE = 6
        WIFI_SSID = "NomeDellaTuaRete"
        WIFI_PASSWORD = "PasswordDellaTuaRete"
        WIFI_TIMEOUT_S = 20
        WIFI_CONTROLLO_OGNI_S = 5
        VM_TOKEN = "INCOLLA_QUI_IL_TUO_TOKEN"
        VM_MONKEY = "test-allarme"
        VM_SPEAKER = "eco-soggiorno"
        ANNUNCIO = False
        TESTO_ANNUNCIO = "Prova del sistema di allarme riuscita"
        LINGUA_ANNUNCIO = "it-IT"
        URL_ROUTINE = "https://api-v3.voicemonkey.io/trigger?token={token}&device={device}"
        URL_ANNUNCIO = ("https://api-v3.voicemonkey.io/announce"
                        "?token={token}&device={device}&speech={testo}&language={lingua}")
        HTTP_TIMEOUT_S = 10
        PIN_LED = 2
        PIN_PULSANTE_WOKWI = 4
        PIN_PULSANTE_SCHEDA = 0
        PAUSA_TRA_TEST_S = 10


# Scegliamo rete e pulsante in base a dove gira il codice
if cfg.SIMULATORE:
    SSID = cfg.WOKWI_SSID
    PASSWORD = cfg.WOKWI_PASSWORD
    PIN_PULSANTE = cfg.PIN_PULSANTE_WOKWI
else:
    SSID = cfg.WIFI_SSID
    PASSWORD = cfg.WIFI_PASSWORD
    PIN_PULSANTE = cfg.PIN_PULSANTE_SCHEDA


# ---------------------------------------------------------------------
# HARDWARE: LED, pulsante e Wi-Fi
# ---------------------------------------------------------------------
led = Pin(cfg.PIN_LED, Pin.OUT)
led.value(0)

# Pulsante verso GND con resistenza di pull-up interna:
# valore 1 = rilasciato, valore 0 = premuto
pulsante = Pin(PIN_PULSANTE, Pin.IN, Pin.PULL_UP)

wlan = network.WLAN(network.STA_IF)
wlan.active(True)

# Traduzione in italiano dei codici di stato del Wi-Fi più comuni
# (usiamo getattr perché non tutte le versioni li hanno tutti)
SPIEGAZIONI_WIFI = {}
for _nome, _testo in (
    ("STAT_NO_AP_FOUND", "rete non trovata (SSID sbagliato, rete a 5 GHz o troppo lontana)"),
    ("STAT_WRONG_PASSWORD", "password sbagliata"),
    ("STAT_HANDSHAKE_TIMEOUT", "handshake scaduto (spesso: password sbagliata)"),
    ("STAT_ASSOC_FAIL", "il router ha rifiutato il collegamento"),
    ("STAT_BEACON_TIMEOUT", "segnale perso"),
):
    _codice = getattr(network, _nome, None)
    if _codice is not None:
        SPIEGAZIONI_WIFI[_codice] = _testo


# ---------------------------------------------------------------------
# FUNZIONI PER IL LED
# ---------------------------------------------------------------------
def led_mostra_wifi():
    """LED acceso se il Wi-Fi è collegato, spento se non lo è."""
    led.value(1 if wlan.isconnected() else 0)


def lampeggia(volte, acceso_ms, spento_ms):
    """Fa lampeggiare il LED, poi lo rimette nello stato del Wi-Fi."""
    led.value(0)
    time.sleep_ms(spento_ms)
    for _ in range(volte):
        led.value(1)
        time.sleep_ms(acceso_ms)
        led.value(0)
        time.sleep_ms(spento_ms)
    led_mostra_wifi()


def segnala_successo():
    # 3 lampeggi lenti
    lampeggia(3, 500, 500)


def segnala_errore():
    # lampeggio veloce per circa 3 secondi (15 x 200 ms)
    lampeggia(15, 100, 100)


# ---------------------------------------------------------------------
# WI-FI
# ---------------------------------------------------------------------
def collega_wifi():
    """Prova a collegarsi al Wi-Fi. Restituisce True se ci riesce."""
    if wlan.isconnected():
        return True

    led.value(0)
    print("Wi-Fi: collegamento a '{}' in corso...".format(SSID))

    # Chiudiamo un eventuale tentativo precedente rimasto a metà
    try:
        wlan.disconnect()
    except OSError:
        pass

    try:
        wlan.connect(SSID, PASSWORD)
    except OSError as errore:
        print("Wi-Fi: ERRORE nell'avvio del collegamento:", errore)
        return False

    inizio = time.ticks_ms()
    while not wlan.isconnected():
        if time.ticks_diff(time.ticks_ms(), inizio) > cfg.WIFI_TIMEOUT_S * 1000:
            stato = wlan.status()
            motivo = SPIEGAZIONI_WIFI.get(stato, "tempo scaduto")
            print("Wi-Fi: NON collegato - {} (stato {})".format(motivo, stato))
            return False
        time.sleep_ms(200)

    secondi = time.ticks_diff(time.ticks_ms(), inizio) / 1000
    print("Wi-Fi: COLLEGATO in {:.1f} s - indirizzo IP: {}".format(secondi, wlan.ifconfig()[0]))
    return True


# ---------------------------------------------------------------------
# VOICE MONKEY
# ---------------------------------------------------------------------
def codifica_url(testo):
    """Codifica un testo per metterlo dentro un URL.

    Lettere, numeri e - _ . ~ restano uguali; tutto il resto (spazi,
    lettere accentate, apostrofi, &, ?...) diventa %XX.
    Esempio: "è ok" -> "%C3%A8%20ok"
    """
    risultato = ""
    for byte in str(testo).encode("utf-8"):
        carattere = chr(byte)
        if ("A" <= carattere <= "Z" or "a" <= carattere <= "z"
                or "0" <= carattere <= "9" or carattere in "-_.~"):
            risultato += carattere
        else:
            risultato += "%{:02X}".format(byte)
    return risultato


def nascondi_token(testo):
    """Sostituisce il token con *** per poterlo stampare senza rischi."""
    testo = str(testo)
    if cfg.VM_TOKEN:
        testo = testo.replace(cfg.VM_TOKEN, "***")
        testo = testo.replace(codifica_url(cfg.VM_TOKEN), "***")
    return testo


def prepara_url():
    """Costruisce l'URL da chiamare partendo dai modelli in config.py."""
    if cfg.ANNUNCIO:
        modello = cfg.URL_ANNUNCIO
        dispositivo = cfg.VM_SPEAKER
    else:
        modello = cfg.URL_ROUTINE
        dispositivo = cfg.VM_MONKEY

    return modello.format(
        token=codifica_url(cfg.VM_TOKEN),
        device=codifica_url(dispositivo),
        testo=codifica_url(cfg.TESTO_ANNUNCIO),
        lingua=codifica_url(cfg.LINGUA_ANNUNCIO),
    )


def spiega_errore_rete(errore):
    """Prova a dare un suggerimento in italiano per gli errori più comuni."""
    testo = str(errore)
    codice = errore.args[0] if errore.args else None
    if codice == -202 or "getaddrinfo" in testo:
        return "nome del server non trovato (DNS): controlla Internet e l'URL"
    if codice in (110, 116) or "TIMEDOUT" in testo.upper():
        return "il server non ha risposto entro {} s".format(cfg.HTTP_TIMEOUT_S)
    if codice in (12,) or "ENOMEM" in testo:
        return "memoria insufficiente per la connessione HTTPS: riavvia la scheda"
    if codice in (103, 104, 113):
        return "connessione interrotta: riprova tra poco"
    if isinstance(codice, int) and codice < -1000:
        return "errore nella connessione sicura HTTPS"
    return "errore di rete"


def chiama_voice_monkey():
    """Chiama Voice Monkey. Restituisce True se la chiamata è riuscita."""
    if not cfg.VM_TOKEN or cfg.VM_TOKEN.startswith("INCOLLA"):
        print("ATTENZIONE: token di esempio in config.py, Voice Monkey risponderà con un errore")

    url = prepara_url()
    if cfg.ANNUNCIO:
        print("Voice Monkey: annuncio sullo speaker '{}': \"{}\"".format(
            cfg.VM_SPEAKER, cfg.TESTO_ANNUNCIO))
    else:
        print("Voice Monkey: attivo la monkey '{}'".format(cfg.VM_MONKEY))
    print("Voice Monkey: URL", nascondi_token(url))

    gc.collect()  # liberiamo memoria: HTTPS ne usa parecchia
    risposta = None
    try:
        try:
            risposta = requests.get(url, timeout=cfg.HTTP_TIMEOUT_S)
        except TypeError:
            # versioni molto vecchie di urequests non conoscono "timeout"
            risposta = requests.get(url)

        codice = risposta.status_code
        corpo = risposta.text
    except OSError as errore:
        print("Voice Monkey: ERRORE di rete - {} ({})".format(
            spiega_errore_rete(errore), nascondi_token(errore)))
        return False
    except Exception as errore:
        print("Voice Monkey: ERRORE imprevisto -", nascondi_token(errore))
        return False
    finally:
        if risposta is not None:
            risposta.close()
        gc.collect()

    print("Voice Monkey: codice HTTP", codice)
    print("Voice Monkey: risposta  ", nascondi_token(corpo)[:300])

    # Successo = codice 2xx e, se la risposta è JSON, "success" non falso
    riuscito = 200 <= codice < 300
    try:
        dati = json.loads(corpo)
        if isinstance(dati, dict) and dati.get("success") is False:
            riuscito = False
    except ValueError:
        pass  # la risposta non è JSON: ci basta il codice HTTP

    if riuscito:
        print("Voice Monkey: OK, richiesta accettata")
    elif codice in (401, 403):
        print("Voice Monkey: token non valido o non autorizzato - controlla VM_TOKEN")
    elif codice == 404:
        print("Voice Monkey: dispositivo o indirizzo non trovato - controlla ID e URL")
    elif codice == 429:
        print("Voice Monkey: troppe richieste - aspetta un po' e riprova")
    else:
        print("Voice Monkey: richiesta NON riuscita")
    return riuscito


# ---------------------------------------------------------------------
# TEST (pulsante o comando "test")
# ---------------------------------------------------------------------
ultimo_test = None  # momento dell'ultimo test, in millisecondi


def esegui_test(origine):
    global ultimo_test

    # Protezione: al massimo un test ogni PAUSA_TRA_TEST_S secondi
    adesso = time.ticks_ms()
    if ultimo_test is not None:
        trascorsi = time.ticks_diff(adesso, ultimo_test)
        attesa = cfg.PAUSA_TRA_TEST_S * 1000 - trascorsi
        if attesa > 0:
            print("Test ignorato: aspetta ancora {} s".format((attesa + 999) // 1000))
            return
    ultimo_test = adesso

    print()
    print("===== TEST avviato da: {} =====".format(origine))

    if not wlan.isconnected():
        print("Wi-Fi non collegato, provo a ricollegarmi...")
        if not collega_wifi():
            print("===== TEST FALLITO: Wi-Fi assente =====")
            segnala_errore()
            return
        led_mostra_wifi()

    if chiama_voice_monkey():
        print("===== TEST RIUSCITO =====")
        segnala_successo()
    else:
        print("===== TEST FALLITO =====")
        segnala_errore()
    print()


# ---------------------------------------------------------------------
# CONSOLE SERIALE: lettura dei comandi senza bloccare il programma
# ---------------------------------------------------------------------
console = select.poll()
console.register(sys.stdin, select.POLLIN)
riga_console = ""


def leggi_comando():
    """Restituisce una riga scritta nella console, oppure None."""
    global riga_console
    while console.poll(0):  # c'è almeno un carattere da leggere?
        carattere = sys.stdin.read(1)
        if carattere in ("\r", "\n"):
            comando = riga_console.strip().lower()
            riga_console = ""
            if comando:
                return comando
        else:
            riga_console += carattere
    return None


# ---------------------------------------------------------------------
# PROGRAMMA PRINCIPALE
# ---------------------------------------------------------------------
def main():
    print()
    print("=========================================")
    print(" Test Alexa con Voice Monkey - ESP32")
    print("=========================================")
    print("Modalità :", "SIMULATORE Wokwi" if cfg.SIMULATORE else "SCHEDA VERA")
    print("Azione   :", "ANNUNCIO vocale" if cfg.ANNUNCIO else "ROUTINE Alexa")
    print("LED su GPIO{}, pulsante su GPIO{}".format(cfg.PIN_LED, PIN_PULSANTE))

    if not collega_wifi():
        segnala_errore()
    led_mostra_wifi()

    print()
    print("Pronto! Premi il pulsante oppure scrivi 'test' e premi Invio.")

    stato_pulsante = pulsante.value()   # 1 = rilasciato
    ultimo_controllo_wifi = time.ticks_ms()
    wifi_era_collegato = wlan.isconnected()

    while True:
        # --- 1) Pulsante, con antirimbalzo ---
        valore = pulsante.value()
        if valore != stato_pulsante:
            time.sleep_ms(30)              # aspettiamo che il contatto si stabilizzi
            valore = pulsante.value()
            if valore != stato_pulsante:   # il cambiamento è reale
                stato_pulsante = valore
                if valore == 0:            # appena premuto
                    esegui_test("pulsante")

        # --- 2) Comandi dalla console seriale ---
        comando = leggi_comando()
        if comando == "test":
            esegui_test("console")
        elif comando is not None:
            print("Comando sconosciuto: '{}'. Scrivi 'test'.".format(comando))

        # --- 3) Controllo periodico del Wi-Fi e riconnessione ---
        if time.ticks_diff(time.ticks_ms(), ultimo_controllo_wifi) > cfg.WIFI_CONTROLLO_OGNI_S * 1000:
            ultimo_controllo_wifi = time.ticks_ms()
            if wlan.isconnected():
                if not wifi_era_collegato:
                    print("Wi-Fi: di nuovo collegato")
                wifi_era_collegato = True
            else:
                if wifi_era_collegato:
                    print("Wi-Fi: collegamento PERSO")
                wifi_era_collegato = False
                if collega_wifi():
                    wifi_era_collegato = True
                else:
                    segnala_errore()
                ultimo_controllo_wifi = time.ticks_ms()
            led_mostra_wifi()

        time.sleep_ms(10)


main()
