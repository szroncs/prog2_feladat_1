**Feladat: Okos Gyár – Szenzorhálózat Kezelő Rendszer**

**Cél:** Egy ipari szenzorhálózatot szimuláló Python alkalmazás fejlesztése, amely a beérkező adatokat feldolgozza, a hibákat kezeli, és eseményvezérelt módon riasztásokat küld.

### Specifikáció és Követelmények

1. **Interfészek és Absztrakt osztályok:**
   * Hozz létre egy `ISzenzor` nevű "interfészt" (tisztán absztrakt osztályt `abc.ABC` használatával), amely egy `meres()` absztrakt (virtuális) metódust definiál.
   * Készíts egy `AlapSzenzor` absztrakt osztályt, amely implementálja az `ISzenzor`-t. Tartalmazzon egy `szenzor_id` és egy `aktiv` (boolean) tulajdonságot. A `meres()` maradjon absztrakt.

2. **Származtatás és Virtuális metódusok:**
   * Származtass két osztályt az `AlapSzenzor`-ból: `HomersekletSzenzor` és `NyomasSzenzor`.
   * Mindkét osztály írja felül (override) a `meres()` metódust. A mérés generáljon véletlenszerű értékeket.

3. **Kivételkezelés:**
   * Hozz létre egy egyedi `KritikusErtekKivetel` nevű kivételosztályt.
   * Ha a `NyomasSzenzor` mérése során az érték meghalad egy kritikus határt, dobja el ezt a kivételt. Ezt a főprogramban megfelelő `try-except` blokkal kell lekezelni.

4. **Gyűjtemények és Generikus típusok:**
   * Hozz létre egy generikus osztályt `SzenzorKozpont[T]` néven, ahol a `T` típusparaméter csak `AlapSzenzor` leszármazott lehet (`TypeVar` használatával).
   * A központ egy belső szótárban (dictionary) tárolja a szenzorokat az azonosítójuk alapján.

5. **Indexelők (Indexer):**
   * A `SzenzorKozpont` osztályban valósítsd meg a `__getitem__` és `__setitem__` metódusokat (Python indexelők), hogy a központ példányaira tömbszerűen lehessen hivatkozni (pl. `kozpont["SZ-01"] = homerseklet_szenzor`).

6. **Események, Metódusreferenciák és Lambda kifejezések:**
   * A `SzenzorKozpont` tartalmazzon egy eseményt (feliratkozók listáját feladatokat/visszahívásokat tárolva): `riasztas_esemeny`.
   * A központ `osszes_meres()` metódusa fusson végig a szenzorokon. Ha egy mérés meghalad egy bizonyos átlagos értéket, hívja meg a feliratkozott függvényeket.
   * A főprogramban a feliratkozás történjen meg egyszer egy normál függvény metódusreferenciájaként átadva, egyszer pedig egy lambda kifejezéssel.

7. **Fájl- és Könyvtárkezelés:**
   * A program indulásakor ellenőrizze, hogy létezik-e egy `naplok` nevű könyvtár (ha nem, hozza létre).
   * Minden elkapott kivételt és riasztást írjon ki egy `naplok/hibalog.txt` nevű fájlba, hozzáfűzés (`append`) módban, időbélyeggel ellátva.

---

### Referenciamegoldás

```python
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
```
