# =====================================================================
#  config.py - IMPOSTAZIONI del progetto "Test Alexa con Voice Monkey"
# =====================================================================
#  Questo è l'UNICO file da modificare per passare da Wokwi alla
#  scheda vera. Il codice in main.py resta identico.
#
#  ATTENZIONE: qui dentro c'è il token di Voice Monkey, che è come una
#  password. Non pubblicare questo file e non condividere il progetto
#  Wokwi in pubblico con il token vero dentro.
# =====================================================================

# ---------------------------------------------------------------------
# 1) DOVE GIRA IL CODICE
# ---------------------------------------------------------------------
# True  = simulatore Wokwi (usa la rete "Wokwi-GUEST" e il pulsante su GPIO4)
# False = scheda ESP32 vera (usa SSID/password qui sotto e il tasto BOOT su GPIO0)
SIMULATORE = True

# ---------------------------------------------------------------------
# 2) WI-FI
# ---------------------------------------------------------------------
# Rete del simulatore Wokwi (non cambiarla)
WOKWI_SSID = "Wokwi-GUEST"
WOKWI_PASSWORD = ""
# Canale della rete Wokwi: solo come promemoria. In Arduino si può
# passare a WiFi.begin() per risparmiare qualche secondo, ma in
# MicroPython wlan.connect() non lo accetta: il canale viene trovato
# automaticamente con la scansione.
WOKWI_CANALE = 6

# Rete di casa (usata solo con SIMULATORE = False)
WIFI_SSID = "NomeDellaTuaRete"
WIFI_PASSWORD = "PasswordDellaTuaRete"

# Quanti secondi aspettare al massimo per il collegamento
WIFI_TIMEOUT_S = 20

# Ogni quanti secondi controllare che il Wi-Fi sia ancora collegato
WIFI_CONTROLLO_OGNI_S = 5

# ---------------------------------------------------------------------
# 3) VOICE MONKEY
# ---------------------------------------------------------------------
# Token API: lo trovi su voicemonkey.io -> Dashboard -> API Credentials
VM_TOKEN = "INCOLLA_QUI_IL_TUO_TOKEN"

# ID della "monkey" (dispositivo trigger) che fa partire la routine Alexa
VM_MONKEY = "test-allarme"

# ID dello speaker Echo che deve parlare (serve solo se ANNUNCIO = True)
VM_SPEAKER = "eco-soggiorno"

# False = fa partire solo la routine Alexa collegata alla monkey
# True  = fa pronunciare ad Alexa il testo qui sotto sullo speaker scelto
ANNUNCIO = False
TESTO_ANNUNCIO = "Prova del sistema di allarme riuscita"
LINGUA_ANNUNCIO = "it-IT"

# Modelli degli indirizzi delle API v3 di Voice Monkey.
# Le parole tra {graffe} vengono sostituite da main.py con i valori
# sopra, già codificati per l'URL (spazi, accenti, ecc.).
# Se un giorno Voice Monkey cambia gli indirizzi, basta modificare qui.
URL_ROUTINE = "https://api-v3.voicemonkey.io/trigger?token={token}&device={device}"
URL_ANNUNCIO = ("https://api-v3.voicemonkey.io/announce"
                "?token={token}&device={device}&speech={testo}&language={lingua}")

# Secondi massimi di attesa per la risposta di Voice Monkey
HTTP_TIMEOUT_S = 10

# ---------------------------------------------------------------------
# 4) LED E PULSANTE
# ---------------------------------------------------------------------
# LED: GPIO2 sia in Wokwi sia sulla scheda vera (LED blu della DevKit V1)
PIN_LED = 2

# Pulsante:
#  - scheda vera: GPIO0 = tasto BOOT già montato sulla scheda
#  - Wokwi: il modello DevKit V1 non ha il GPIO0 sui piedini, quindi
#    il pulsante del circuito è collegato a GPIO4 (piedino D4)
PIN_PULSANTE_WOKWI = 4
PIN_PULSANTE_SCHEDA = 0

# Tempo minimo tra due test, per evitare pressioni ripetute
PAUSA_TRA_TEST_S = 10
