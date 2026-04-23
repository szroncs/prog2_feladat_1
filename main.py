import os
import random
from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Callable, Dict, List
from datetime import datetime
from pathlib import Path

# 1. Interfész (tisztán absztrakt osztály)
class ISzenzor(ABC):
    @abstractmethod
    def meres(self) -> float:
        pass

# 1. Absztrakt osztály
class AlapSzenzor(ISzenzor):
    def __init__(self, szenzor_id: str):
        self.szenzor_id = szenzor_id
        self.aktiv = True
        
    def __str__(self) -> str:
        return f"Szenzor({self.szenzor_id})"

# 3. Kivételkezelés (Egyedi kivétel)
class KritikusErtekKivetel(Exception):
    def __init__(self, szenzor_id: str, ertek: float):
        super().__init__(f"Kritikus hiba a(z) {szenzor_id} szenzornál! Érték: {ertek}")
        self.szenzor_id = szenzor_id
        self.ertek = ertek

# 2. Származtatás és Virtuális metódusok felülírása
class HomersekletSzenzor(AlapSzenzor):
    def meres(self) -> float:
        if not self.aktiv:
            return 0.0
        return random.uniform(-10.0, 50.0)

class NyomasSzenzor(AlapSzenzor):
    def meres(self) -> float:
        if not self.aktiv:
            return 0.0
        ertek = random.uniform(0.5, 3.5)
        if ertek > 3.0:
            raise KritikusErtekKivetel(self.szenzor_id, ertek)
        return ertek

# 4. Generikus típusok
T = TypeVar('T', bound=AlapSzenzor)

class SzenzorKozpont(Generic[T]):
    def __init__(self):
        self._szenzorok: Dict[str, T] = {}
        # 6. Események (Feliratkozók listája metódusreferenciáknak/lambdáknak)
        self.riasztas_esemeny: List[Callable[[str, float], None]] = []
        self._naplozo_konyvtar_beallitasa()

    # 7. Fájl- és könyvtárkezelés
    def _naplozo_konyvtar_beallitasa(self):
        self.log_dir = Path("naplok")
        self.log_dir.mkdir(exist_ok=True)
        self.log_file = self.log_dir / "hibalog.txt"

    def naplo_iras(self, uzenet: str):
        with open(self.log_file, "a", encoding="utf-8") as f:
            idobelyeg = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"[{idobelyeg}] {uzenet}\n")

    # 5. Indexelők (__getitem__, __setitem__)
    def __setitem__(self, kulcs: str, ertek: T):
        self._szenzorok[kulcs] = ertek

    def __getitem__(self, kulcs: str) -> T:
        return self._szenzorok[kulcs]

    def feliratkozas_riasztasra(self, callback: Callable[[str, float], None]):
        self.riasztas_esemeny.append(callback)

    def esemeny_kivaltasa(self, szenzor_id: str, ertek: float):
        for callback in self.riasztas_esemeny:
            callback(szenzor_id, ertek)

    def osszes_meres(self):
        for szenzor_id, szenzor in self._szenzorok.items():
            try:
                ertek = szenzor.meres()
                print(f"{szenzor_id} aktuális értéke: {ertek:.2f}")
                
                # Esemény kiváltása feltétel alapján
                if ertek > 40.0:
                    self.esemeny_kivaltasa(szenzor_id, ertek)
                    
            except KritikusErtekKivetel as e:
                # 3. Kivétel lekezelése
                print(f"KIVÉTEL ELKAPVA: {e}")
                self.naplo_iras(str(e))

# Tesztelés és Futtatás
def main():
    # Metódusreferenciaként átadandó függvény
    def konzolos_riasztas(szenzor_id: str, ertek: float):
        print(f"--> [METÓDUSREFERENCIA RIASZTÁS] Figyelem! {szenzor_id} kiugró értéket mért: {ertek:.2f}")

    # Generikus központ példányosítása
    kozpont = SzenzorKozpont[AlapSzenzor]()

    # 6. Feliratkozás metódusreferenciával és lambdával
    kozpont.feliratkozas_riasztasra(konzolos_riasztas)
    kozpont.feliratkozas_riasztasra(lambda s_id, val: kozpont.naplo_iras(f"[LAMBDA RIASZTÁS LOG] {s_id} - érték: {val:.2f}"))

    # 5. Elemek hozzáadása indexelővel
    kozpont["HOM-01"] = HomersekletSzenzor("HOM-01")
    kozpont["NYOM-01"] = NyomasSzenzor("NYOM-01")
    kozpont["HOM-02"] = HomersekletSzenzor("HOM-02")

    print("Mérések indítása...\n")
    # Többszöri futtatás, hogy nagyobb eséllyel generáljunk hibát vagy riasztást
    for i in range(3):
        print(f"--- {i+1}. Mérési Ciklus ---")
        kozpont.osszes_meres()
        print("-" * 25)

if __name__ == "__main__":
    main()
