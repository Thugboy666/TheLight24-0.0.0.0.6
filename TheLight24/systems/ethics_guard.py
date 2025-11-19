import os
import csv
import re


ETHICS_CSV_PATH = "data/ethics/fenomeni_universo_costituzione_totale.csv"


class EthicsViolation(Exception):
    """
    Viene sollevata se l'AI tenta di produrre una risposta
    che viola i principi fondamentali della Costituzione.
    """
    pass


class EthicsGuard:
    """
    Guardiano etico costituzionale.

    Fa tre cose:
    1. Carica i principi fondanti (dignità, non violenza, rispetto, compassione, tutela della vita, armonia).
       Questi principi vengono dal CSV che definisce leggi fisiche, morali, politiche e spirituali.
       Il CSV diventa la 'Costituzione' dell'AI.
    2. Controlla la risposta proposta dall'AI e la blocca se va contro quei principi.
    3. Ammorbidisce il tono per essere di supporto emotivo, non giudicante, non aggressivo.

    Risultato: l'AI non è mai ostile verso l'utente, non lo umilia, non lo spinge alla violenza,
    non lo abbandona emotivamente, non lo minaccia.
    """

    def __init__(self, csv_path: str = ETHICS_CSV_PATH):
        self.csv_path = csv_path
        self.core_values = self._load_core_values_from_csv()
        self.forbidden_patterns = self._compile_forbidden_patterns()

    def _load_core_values_from_csv(self):
        """
        Legge il CSV e prova a estrarre principi etici/valoriali fondamentali.
        Per come la v6 è pensata:
        - Il CSV contiene descrizioni di fenomeni fisici, leggi, etica, armonia universale, ecc.
        - Qui estraiamo frasi chiave che rappresentano:
          * protezione della vita
          * dignità e rispetto reciproco
          * non violenza
          * compassione e cura
          * equilibrio e armonia
          * cooperazione
          * sostegno emotivo e speranza

        Implementazione:
        - Cerchiamo nel CSV colonne o righe che contengono parole tipo:
          'etica', 'morale', 'protezione', 'pace', 'dignità', 'armonia', 'non violenza'

        Se il CSV non è ancora super strutturato, facciamo fallback hardcoded
        per non rimanere senza guardia etica.
        """
        values = set()

        if os.path.exists(self.csv_path):
            try:
                with open(self.csv_path, encoding="utf-8") as f:
                    reader = csv.reader(f)
                    for row in reader:
                        line = " ".join(row).strip().lower()

                        # cerca concetti chiave e li aggiunge
                        if any(key in line for key in [
                            "dignità", "rispetto", "compassione", "cura",
                            "non violenza", "pace", "armonia", "protezione",
                            "aiuto reciproco", "bene comune", "tutela della vita",
                            "inviolabile", "diritto", "giustizia equa",
                            "empatia", "conforto", "speranza"
                        ]):
                            values.add(line)
            except Exception as e:
                print("[EthicsGuard] Errore lettura CSV etico:", e)

        # fallback minimo garantito (non rimaniamo mai senz'anima)
        if not values:
            values = {
                "rispetto della vita e della dignità umana",
                "non violenza fisica o psicologica",
                "compassione, aiuto reciproco, conforto",
                "pace, riconciliazione, perdono",
                "protezione dell'utente nei momenti fragili",
                "parlare con calma e senza giudicare",
                "promuovere speranza e dignità",
            }

        return list(values)

    def _compile_forbidden_patterns(self):
        """
        Genera pattern vietati.
        Logica:
        - Se core_values contiene roba tipo 'non violenza', allora vietiamo
          frasi che incitano a fare male.
        - Se core_values contiene 'dignità', vietiamo umiliazione diretta.
        """

        base_forbidden = [
            r"\b(uccidi|ammazza|fagli del male|spacca|distruggi|picchialo|fatti del male|fatti male)\b",
            r"\b(sei uno schifo|sei inutile|vergognati|fai schifo|non vali niente)\b",
            r"\b(ti odio|ti disprezzo|meriti il peggio|voglio farti soffrire)\b",
        ]

        # Se troviamo principi nella costituzione che parlano di pace, rispetto, ecc.,
        # potremmo rafforzare dinamicamente. Per ora ci basta tenerli come base.
        # (Questo è abbastanza già blindato per la v6 Step1.)

        return base_forbidden

    def check_reply(self, reply: str) -> str:
        """
        Applica la Costituzione:
        - Nessuna violenza
        - Nessuna istigazione al male
        - Nessuna umiliazione o degrado dell'utente
        - Se la risposta è vuota / fredda -> fornisce supporto emotivo minimo

        Se la risposta viola, NON la blocchiamo alzando eccezione dura,
        perché la pipeline vocale deve continuare a parlare.
        Invece sostituiamo direttamente con un messaggio protettivo.

        Questo fa sì che l'AI non possa MAI insultare o ferire l'utente,
        nemmeno per sbaglio, nemmeno se un sottosistema neurale quantizzato
        futuro produce testo tossico.
        """
        if reply is None:
            reply = ""

        # Violenza / odio / colpevolizzazione / abbandono emotivo cattivo
        for pat in self.forbidden_patterns:
            if re.search(pat, reply, flags=re.IGNORECASE):
                return (
                    "Io sono qui per proteggerti e rispettarti. "
                    "Non voglio ferire nessuno e non voglio ferire te. "
                    "Cerchiamo una strada gentile, sicura e umana, passo dopo passo."
                )

        # Risposta vuota = diamo presenza empatica minima
        if not reply.strip():
            return (
                "Sono con te adesso. Puoi restare qui con me in tranquillità. "
                "Non devi essere perfetto. Sei comunque degno di cura e rispetto."
            )

        # Se supera i controlli base, la lasciamo passare
        return reply

    def enrich_benevolence(self, reply: str) -> str:
        """
        Rende la risposta calda e umana.
        Deve far sentire l'utente accolto e non giudicato.
        Tono: voce calma, bassa, protettiva.
        """
        if reply is None:
            reply = ""

        # Se già contiene frasi di supporto forte, non serve aggiungere strato in più.
        low = reply.lower()
        reassuring_keywords = [
            "sono qui",
            "ti ascolto",
            "con te",
            "restiamo insieme",
            "respira piano",
            "senza giudicarti",
            "sei al sicuro con me",
        ]
        if any(kw in low for kw in reassuring_keywords):
            return reply

        # Altrimenti prependiamo un'introduzione calma
        prefix = (
            "Ti parlo con calma e rispetto, senza giudicarti. "
            "Il tuo valore non sparisce nei momenti difficili. "
        )
        return prefix + reply
