# Cow follower

Segédprogram állatok megfigyelésére szolgáló kamerarendszer videóanyagából a viselkedéselemző szoftver számára átadható videófájl(ok) készítése automata, vagy félautomata módon.

## Általános leírás

A szarvasmarha bolus projekt során a kísérletbve bevont telepeken kamerarendszer kerül kialakítására, az állatok megfigyelése céljából. Az állatok a terület bizonyos részein szabadon vándorolhatnak, így egy-egy kamera képéből időnként eltűnhetnek, takarásba kerülhetnek, vagy úgy fordulhatnak, hogy a viselkedésük nem lesz azonosítható. Analizálható videófelvétel tehát csak úgy nyerhető, ha valamilyen módon az egyes kamerák képei között váltogatunk. 

A szoftver feladata tehát az, hogy a kameraképek közötti váltogatást segítse, tartsa számon azokat a kamerákat, amik kapcsolódó területeket figyelnek meg, és az aktuálisan használt kamera képéről történő váltáshoz automatikusan azokat a kamerákat kínálja fel, ahova az állat átsétálhatott.

Az állatok követését nagyban megkönnyíti magának a követésnek a minél nagyobb fokú automatizációja. További hasznos fejlesztés lehet még az annotációk kézi bevitelének lehetősége is.

## Követelmények

A szoftverrel fejlesztése során a következő követelmények, illetve megvalósítandó részfeladatok merülnek fel:

 * A kamerák által rögzített videóanyaghoz történő (távoli, vagy helyi) hozzáférés megoldása
 * Az egyes felvételek időbeli szinkronizációja
 * A kamerák fizikai elhelyezésének, kapcsolatuknak logikai leírása
 * Kameraképek szimultán megjelenítése (aktuális kamera plusz szomszédos kamerák)
 * Kameraképek közötti váltás megoldása
 * Időbeli mozgás megoldása (előre-hátra, lassan-gyorsan, időhöz ugrás, markerek, markerhez ugrás stb.)
 * Metaadatok tárolása (ami leírja, hogy mikor melyik kamerát használjuk stb.)
 * Metaadatok kimentése, betöltése, szerkesztése
 * Kimeneti videófájl elkészítése a metaadatok alapján


Opcionális követelmények:
  
 * Az állatok kiválasztásának, majd (egy kameraálláson belül történő) követésének lehetősége. Követés megszakadásának jelzése.
 * Követése kiterjesztése több kamerára. Automatikus váltás a kameraállások között.
 * Annotációk felvitelének lehetősége.

## Technológiai megjegyzések

Számos ingyenes és fizetős videovágó szoftver lézetik. Többségük pluginekkel, scriptekkel bővíthető. 
