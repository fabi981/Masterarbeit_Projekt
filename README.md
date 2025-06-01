**Die Lernumgebung**

*Zielgruppe:* Schülerinnen und Schüler der zwölften Klasse eines Informatik-LKs

*Nötige Vorkenntnisse:* Vektorrechnung und Matrizenrechnung (oder wenigstens eines der beiden)

*Medien und Materialien:* Computer mit Internetanbindung

*Leitfrage:* 

Wie können die einzelnen Verarbeitungsschritte und -mechanismen des BERT-Transformer-Modells nachvollziehbar gemacht werden?

*Lernziele der Umgebung:* 




***Kapitel 1: Mathematische Grundlagen***

*Groblernziele und Kompetenzen:*

Die SuS...

... wiederholen grundlegende Operationen der Vektor- und Matrizenrechnung.

... lernen die Kosinusähnlichkeit als Maß zur Bestimmung semantischer
Nähe zwischen Einbettungsvektoren kennen. Sie können diese grafisch im
zweidimensionalen Raum anhand der Richtung einordnen. Sie können können
die Kosinusähnlichkeit zweidimensionaler Vektoren berechnen.

... verstehen das Prinzip der Projektion als Anschauungsmodell für
interne Berechnungen im BERT-Modell.

*Beschreibung:*

Vektoradditionen und -multiplikationen sind in mehreren Stellen des BERT-Modells relevant, so etwa in den sechs Rechenschritten der Self-Attention und bei der anschließenden linearen Transformationen in den Feedforward-Netzwerken. Ebenso ist der Betrag von Vektoren relevant, um die Kosinusähnlichkeit bilden zu können. Das Skalarprodukt ist ebenso ein Teil der linearen Transformationen.

Alle diese Rechenoperationen werden in Kürze (im Sinne der Wiederholung) definiert. SuS erhalten Rechenaufgaben im Lückenformat. Anschließend wird ihnen die richtige Lösung präsentiert.



Die Kosinusähnlichkeit cos(A, B) wird als neue Operation der Vektorrechnung eingeführt. Sie beschreibt die Ähnlichkeit zwischen zwei Vektoren (im Folgenden Worteinbettungen) A und B folgendermaßen: 

cos(A,B) = 1: Die beiden Vektoren sind sich maximal ähnlich. Im grafischen Vektorraum zeigen sie exakt in die gleiche Richtung.

cos(A,B) = 0: Die beiden Vektoren sind sich nicht ähnlich. Im grafischen Vektorraum stehen sie orthogonal zueinander.

cos(A,B) = -1: Auch hier sind sich die beiden Vektoren nicht ähnlich (ggf. sogar gegensätzlich ähnlich zueinander). Im grafischen Vektorraum zeigen sie in die entgegengesetzte Richtung.

Hierzu werden Rechenaufgaben bereitgestellt.



Die Projektion (eine leicht vereinfachte Form der fachmathematischen Projektion) als Anschauungsmodell für Multiplikationsvorgänge im Self-Attention-Mechanismus wird vorgestellt. Knapp zusammengefasst: Es sei eine Projektionsmatrix P gegeben, die in ihrer Diagonalen aus Nullen und Einsen besteht und der Rest mit Nullen aufgefüllt ist. 

#Hier Bild einer Projektionsmatrix einfügen.#

Multipliziert man einen Vektor A mit dieser Projektionsmatrix P, so erhält man einen Ergebnisvektor, der A entspricht, jedoch an den Stellen, an denen die Diagonale Null ist, ebenfalls Null ist.

#Hier Bild der Projektionsrechnung#

Erklärt wird die 'Projektion' anhand eines Regalbeispiels. Im Anschluss folgt eine enaktive Ausschneideaufgabe, die den Mechanismus verdeutlicht.

#Hier Grafiken des Regalbeispiels und der Ausschneideaufgabe einfügen#



***Kapitel 2: Analogie zum biologischen Neuron***

*Groblernziele und Kompetenzen:*

Die SuS

... kennen den Aufbau des biologischen Neurons und kennen die
elektrischen und chemischen Mechanismen der Informationsweitergabe im
menschlichen Körper.

... können das das Konzept der synaptischen Gewichtung im
biologischen Neuron auf künstliche Neuronen und das BERT-Modell
übertragen.

... können die Rolle von Aktivierungsfunktionen in neuronalen
Netzwerken und analog dazu das Membranpotential in biologischen Neuronen
einordnen.

*Beschreibung:*



***Kapitel 3: Anwendungsszenarien und Beispielmodelle zur Emotionserkennung***

*Groblernziele und Kompetenzen:*

Die SuS...

... analysieren Emotionen auf Fotos mithilfe eines
Klassifikationsmodells.

...  interpretieren Emotionen in eigenen Sprachmemos.

...  untersuchen Emotionen in Texten durch Einsatz eines TextEmotionserkennungsmodells.

*Beschreibung:*

***Kapitel 4: Tokenisierung und Encoding von Eingabedaten***

*Groblernziele und Kompetenzen:*

Die SuS...

... verstehen das Konzept des Tokens.

...  verstehen das WordPiece-Tokenisierungsmodell

... können erklären, wie IDs und Einbettungsmatrizen Vektorlisten erzeugen.

... können den Begriff der Einbettung definieren.

... beschreiben, wie durch Positional Encoding Positionsinformationen in die Einbettungen einfließen.

... berechnen und interpretieren semantische Ähnlichkeiten mithilfe der Kosinusähnlichkeit.

*Beschreibung:*



***Kapitel 5: Das Innenleben des BERT-Modells: Die Encoderschichten***

*Groblernziele und Kompetenzen:*

Die SuS...

... analysieren den Encoder als zentrale Verarbeitungsstruktur des BERTModells und erschließen dessen Aufbau aus mehreren Schichten.


*Beschreibung:*

***Kapitel 6: Das Vortraining des BERT-Modells***

*Groblernziele und Kompetenzen:*

Die SuS...

... können den Vortrainingsprozess von BERT in eigenen Worten beschreiben und erproben zentrale Mechanismen in Anwendungsaufgaben.

... verstehen das Prinzip des Masked Language Modeling.

...  verstehen die Vortrainingsaufgabe der Next Sentence Prediction.

*Beschreibung:*

***Kapitel 7: Der Self-Attention-Mechanismus***

*Groblernziele und Kompetenzen:*

Die SuS...

... verstehen den Self-Attention-Mechanismus und rekonstruieren dessen
Berechnungslogik.

... verstehen, wie Wörter anhand im Self-Attention-Mechanismus
gewichtet werden.

...  vollziehen die sechs Berechnungsschritte der Self-Attention nach.

*Beschreibung:*

***Kapitel 8: Der erweiterte Self-Attention-Mechanismus: Multi-Headed-Self-Attention***

*Groblernziele und Kompetenzen:*

Die SuS...

...  verstehen, dass die Self-Attention weiter optimiert werden kann, indem
Einbettungen auf mehrere Köpfe aufgeteilt und parallel zueinander werden.


*Beschreibung:*


**Musterkapitel 4: Lernziele - Unterrichtsverlaufsplan - Weiterführende Materialien**





Der Server ist leider gerade down.

**Anleitung zum Testen der Umgebung (ohne Speicherung von Nutzerdaten)**

1. Repository runterladen: git clone https://github.com/fabi981/Masterarbeit_Projekt.git (oder das Verzeichnis manuell herunterladen).
2. Die Pakete der requirements.txt müssen installiert werden: pip install -r requirements.txt
3. Die Apps sind auf den localhost '127.0.0.1' umgestellt. Falls es sich trotzdem nicht starten lässt: Die IP-Adresse in Zeile 99 des Dash-Module.py umstellen.
4. Die Dash-App über die Konsole starten: python3 Masterarbeit_Projekt.py


**Hinweise für Entwickler:**

*pages_10:* Enthält die Hintergrundbilder der Lernumgebung in ihrer aktuellsten Version. Diese wurden in GoodNotes erstellt und in PNG konvertiert.

--> wichtige Informationen: Will man die Hintergrundbilder erweitern oder austauschen, muss man Dateien des Formats 'Aufgabe3-xxx.png' im 
*pages_10*-Ordner einfügen oder ersetzen. Bei Erstellung eines neuen Ordners an Hintergrundbildern müssen folgende Variablen in der *Dash-Module.py* angepasst werden: 

ASSETS_DIR (Zeile 138): Ordnername 

files (Zeile 142): Hier können Dateinamen und das Bildformat festgelegt werden. Die Bilddateien müssen vollständig bis zu einer gewünschten Seite sein.


*Masterarbeit_Projekt.py:* Startet die Dash-Module.py und die Flask-Module.py in separaten Prozessen. Diese Datei muss per Konsole ausgeführt werden, um den Server zu starten.

*Dash-Module.py:* Enthält die Frontend-Steuerung mit Plotly-Dash.

--> wichtige Informationen: Die globalen Servervariablen befinden sich in Codezeile 84 bis 87. Hier werden die Host-IP und die gewünschten Ports festgelegt. Der *dash_port* der *Dash-Module.py* gibt nahezu alle Frontend-Funktionen aus. Aufgerufen werden kann der Server am Ende über beide Ports.

*Flask-Module.py:* Enthält die Backend-Steuerung mit Flask.

--> wichtige Informationen: Die globalen Servervariablen befinden sich in Codezeile 99 bis 102. Hier werden die Host-IP und die gewünschten Ports festgelegt. Der *flask_port* der *Flask-Module.py* steuert die Nutzerauthentifizierung und die ausgelagerte Funktion. 

**Navigations- und GUI-Elemente**: 

Die Kapitelnavigation wird über das Dictionary *CHARACTER_MAPPING (Zeile 149)* gesteuert. 

Positionierung und Format der Textfelder werden im Dictionary *TEXT_FIELDS (Zeile 177)* zentral festgelegt. 

Positionierung und Format der  Checkboxen werden im Dictionary CHECK_BOXES *(Codezeile 531)* zentral festgelegt. 

Alle weiteren Elemente wurden im *app.layout (Zeile 977)* definiert.



