import random
import time
import pickle
import os
import json
from colorama import Fore, Back, Style
from tabulate import tabulate

# ================================
# Helper Funktionen
# ================================

def drucke_bunt(text, color=Fore.WHITE):
    print(color + text + Style.RESET_ALL)

def pause():
    time.sleep(1)

def lade_spielstand(dateipfad):
    if os.path.exists(dateipfad):
        with open(dateipfad, "rb") as f:
            return pickle.load(f)
    return None

def speichere_spielstand(dateipfad, spielstand):
    with open(dateipfad, "wb") as f:
        pickle.dump(spielstand, f)

def quest_to_dict(quest):
    return {
        'titel': quest.titel,
        'beschreibung': quest.beschreibung,
        'belohnung': quest.belohnung,
        'abgeschlossen': quest.abgeschlossen,
        'quest_typ': quest.quest_typ
    }

# ================================
# Charakterklassen und Kampfmechanik
# ================================

class Charakter:
    def __init__(self, name, gesundheit, angriff, verteidigung, magie):
        self.name = name
        self.gesundheit = gesundheit
        self.angriff = angriff
        self.verteidigung = verteidigung
        self.magie = magie
        self.level = 1
        self.experience = 0
        self.inventar = []
        self.quest_log = []

    def status(self):
        return f"{Fore.GREEN}{self.name}{Style.RESET_ALL} - Level: {self.level}, HP: {self.gesundheit}, Angriff: {self.angriff}, Verteidigung: {self.verteidigung}, Magie: {self.magie}"

    def kampf(self, gegner):
        schaden = max(0, self.angriff - gegner.verteidigung)
        gegner.gesundheit -= schaden
        drucke_bunt(f"{self.name} trifft {gegner.name} für {schaden} Schaden!", Fore.RED)
        if gegner.gesundheit <= 0:
            drucke_bunt(f"{gegner.name} wurde besiegt!", Fore.YELLOW)
            self.experience += 10
            self.level_up()
        return gegner.gesundheit <= 0

    def level_up(self):
        if self.experience >= 100:
            self.level += 1
            self.experience = 0
            self.gesundheit += 10
            self.angriff += 2
            self.verteidigung += 2
            self.magie += 1
            drucke_bunt(f"{self.name} ist auf Level {self.level} gestiegen!", Fore.CYAN)

    def heilung(self):
        heilung = random.randint(10, 20)
        self.gesundheit += heilung
        drucke_bunt(f"{self.name} heilt sich um {heilung} HP!", Fore.GREEN)

    def inventar_zeigen(self):
        if self.inventar:
            headers = ["Name", "Beschreibung"]
            items = [[item['name'], item['beschreibung']] for item in self.inventar]
            print(tabulate(items, headers=headers, tablefmt="fancy_grid"))
        else:
            drucke_bunt("Du hast keine Items im Inventar.", Fore.RED)

    def item_nehmen(self, item):
        self.inventar.append(item)
        drucke_bunt(f"{self.name} hat das Item {item['name']} erhalten!", Fore.MAGENTA)

    def quest_log_zeigen(self):
        if self.quest_log:
            print(f"\n{Fore.YELLOW}Dein Quest-Log:{Style.RESET_ALL}")
            for quest in self.quest_log:
                drucke_bunt(f"Quest: {quest['titel']} - Status: {'Abgeschlossen' if quest['abgeschlossen'] else 'Nicht abgeschlossen'}", Fore.CYAN)
        else:
            drucke_bunt("Dein Quest-Log ist leer.", Fore.RED)

class Gegner:
    def __init__(self, name, gesundheit, angriff, verteidigung, magie):
        self.name = name
        self.gesundheit = gesundheit
        self.angriff = angriff
        self.verteidigung = verteidigung
        self.magie = magie

    def kampf(self, charakter):
        schaden = max(0, self.angriff - charakter.verteidigung)
        charakter.gesundheit -= schaden
        drucke_bunt(f"{self.name} trifft {charakter.name} für {schaden} Schaden!", Fore.RED)
        return charakter.gesundheit <= 0

# ================================
# Quest- und Weltenmanagement
# ================================

class Quest:
    def __init__(self, titel, beschreibung, belohnung, quest_typ="Hauptquest"):
        self.titel = titel
        self.beschreibung = beschreibung
        self.belohnung = belohnung
        self.abgeschlossen = False
        self.quest_typ = quest_typ

    def quest_info(self):
        return f"Quest: {self.titel}\nBeschreibung: {self.beschreibung}\nBelohnung: {self.belohnung}"

    def abschluss(self, charakter):
        if not self.abgeschlossen:
            drucke_bunt(f"{charakter.name} hat die Quest '{self.titel}' abgeschlossen!", Fore.GREEN)
            charakter.experience += self.belohnung
            self.abgeschlossen = True
            charakter.level_up()

class Welt:
    def __init__(self):
        self.quests = [
            Quest("Die Rache des Drachen", "Besiege den Drachen im Wald und rette das Dorf.", 50),
            Quest("Das verschwundene Artefakt", "Finde das Artefakt im alten Tempel.", 30),
            Quest("Die Geheimnisse des Tempels", "Entdecke die alten Geheimnisse des verlassenen Tempels.", 100)
        ]
        self.charakter = None

    def zeige_quests(self):
        print("\nVerfügbare Quests:")
        for index, quest in enumerate(self.quests):
            if not quest.abgeschlossen:
                print(f"{index + 1}. {quest.quest_info()}")

    def starte_quest(self, index):
        if self.charakter:
            quest = self.quests[index]
            quest.abschluss(self.charakter)
            self.charakter.quest_log.append(quest_to_dict(quest))
        else:
            print("Du musst einen Charakter erstellen, um eine Quest zu starten.")

    def interaktion_mit_npc(self):
        npc_antworten = [
            "Ich habe viel von dir gehört. Pass auf dich auf!",
            "Die Welt ist gefährlich, aber du wirst es schaffen!",
            "Hast du die Monster im Wald besiegt? Das wäre ein großes Abenteuer."
        ]
        drucke_bunt(random.choice(npc_antworten), Fore.BLUE)

# ================================
# Spielstart und Interaktionen
# ================================

def kampf_szenario(charakter, gegner):
    print(f"{charakter.name} tritt gegen {gegner.name} an!")
    while charakter.gesundheit > 0 and gegner.gesundheit > 0:
        aktion = input("\nWas möchtest du tun? (Angreifen / Zauber / Heilen): ").lower()
        if aktion == "angreifen":
            if charakter.kampf(gegner):
                break
        elif aktion == "zauber":
            zauber = Zauber("Feuerball", 20, 5)
            zauber.anwenden(charakter, gegner)
            if gegner.gesundheit <= 0:
                break
        elif aktion == "heilen":
            charakter.heilung()
        else:
            print("Ungültige Auswahl!")

def gegner_erstellen(level):
    name = f"Gegner-Level-{level}"
    gesundheit = random.randint(20, 40) + level * 5
    angriff = random.randint(5, 10) + level * 2
    verteidigung = random.randint(3, 6) + level
    magie = random.randint(2, 5) + level // 2
    return Gegner(name, gesundheit, angriff, verteidigung, magie)

def spiel_starten():
    drucke_bunt("Willkommen im Anime RPG!", Fore.CYAN)
    name = input("Wie heißt dein Charakter? ")
    charakter = Charakter(name, 100, 15, 5, 10)

    welt = Welt()
    welt.charakter = charakter

    print(f"\n{charakter.status()}")
    welt.zeige_quests()

    while True:
        auswahl = input("\nWähle eine Quest (1, 2) oder 'q' zum Beenden: ")
        if auswahl == '1' or auswahl == '2':
            quest_index = int(auswahl) - 1
            welt.starte_quest(quest_index)
        elif auswahl == 'q':
            print("Danke fürs Spielen!")
            break
        else:
            print("Ungültige Auswahl!")

        # Interaktion mit NPCs
        welt.interaktion_mit_npc()

        # Optionale Gegnerkämpfe
        if random.random() < 0.5:
            gegner = gegner_erstellen(charakter.level)
            kampf_szenario(charakter, gegner)
            print(f"{charakter.status()}")

        # Speicherfunktion
        if input("Möchtest du deinen Fortschritt speichern? (y/n): ").lower() == 'y':
            speichere_spielstand("spielstand.pkl", charakter)

# Spiel starten
if __name__ == "__main__":
    spiel_starten()
