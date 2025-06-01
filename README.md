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

Der Aufbau des biologischen Neurons (inklusive Zellkörper, Dendriten, Axon, synaptischem Spalt und Myelinhülle) wird erklärt und das Verständnis mit einer Lückentext-Aufgabe überprüft. 

##Hier Abbildung##

Der elektrische Übertragungsweg zwischen Nervenzellen (inklusive Ruhepotential, Reizsschwellen, Depolarisation, Repolarisation, Hyperporatisation und Signalstärke) wird erläutert. Das Verständnis wird anhand einer Beschreibungsaufgabe überprüft.

#Hier Abbildungen#

Hieraus wird das technische Korrelat der Aktivierungsfunktionen und der Gewichte (inklusive Schwellenwert) hergeleitet.

Der chemische Übertragungsweg zwischen Nervenzellen (inklusive der Beschreibung einzelner Neurotransmitter und ihrer Funktionen) wird erläutert, um das Verständnis des biologischen Neurons abzurunden.

#Abbildung einfügen#

***Kapitel 3: Anwendungsszenarien und Beispielmodelle zur Emotionserkennung***

*Groblernziele und Kompetenzen:*

Die SuS...

... analysieren Emotionen auf Fotos mithilfe von Klassifikationsmodellen der Sprach-, Text- und Bilderkennung.

...  interpretieren Emotionen der Mitschüler und vergleichen ihre Klassifikationsleistung mit dem Modell.

...  untersuchen Emotionen in YouTube-Kommentartexten.

... werden dazu motiviert, eigene Modelle der HuggingFace-Bibliothek auszutesten.

*Beschreibung:*

Im ersten Schritt testen SuS die Modelle: Sie schießen gegenseitig bilder und nehmen Sprachnachrichten auf, in denen sie sich fragen stellen. Dies geschieht direkt in der Lernumgebung. Zwei Funktionen stehen zur Verfügung (die jedoch noch ein wenig Debugging erfordern). Sie können ihre Aufzeichnungen per Button-Klick direkt hochladen, sodass die Modelle ihre Emotionen auswerten. Im Anschluss folgen weitere Aufgaben, in denen sie diskutieren, wer die Emotionen besser interpretiert: Mensch oder Maschine. Es folgt eine Transferaufgabe (KI-Perspektive), in denen diskutiert wird, wo solche Technologien eingesetzt werden (könnten). 

#Bilder einfügen#

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

Die SuS durchlaufen den gesamten Prozess der Eingabe eines Satzes in ein BERT-Modell bis hin zum Entstehen der Vektor-Eingaben, die vom BERT-Encoder verarbeitet werden. Die Verarbeitungsschritte umfassen die Tokenisierung (d. h. das Zerlegen der Wörter des Satzes in Tokens bzw. Fragmente), das Auslesen der IDs der Tokens, das Ablesen der Einbettungen aus einer Embedding-Tabelle und das Positional Encoding (um die Bedeutung der Position der Tokens im Satz einfließen zu lassen). Dieses Kapitel wird weiter unten näher erläutert und mit einer Unterrichtsstruktur für eine Doppelstunde umrahmt.

#Abbildung einfügen#

***Kapitel 5: Das Innenleben des BERT-Modells: Die Encoderschichten***

*Groblernziele und Kompetenzen:*

Die SuS...

... analysieren den Encoder als zentrale Verarbeitungsstruktur des BERTModells und erschließen dessen Aufbau aus mehreren Schichten.


*Beschreibung:*

Was genau mit den Worteinbettungen des Satzes im Modell geschieht, wird in diesem Kapitel erläutert: Ein Transformer besteht aus z.B. L=12 Schichten. Von Schicht zu Schicht werden die Einbettungsvektoren mit Gewichten im Rahmen von linearen Transformationen (durch ein Feedforward-Netzwerk) verarbeitet. Dabei greift eine nicht-lineare GELU-Aktivierungsfunktion, die eine gute Menge der Signale am Übertragen verhindert (analog zum menschlichen Körper, wie in Kapitel 2 beschrieben). 

#Hier Bild einfügen#

Dieses Kapitel muss um einen Explorationsblock angereichert werden. D.h. hier fehlen Aufgaben und Veranschaulichungen für das vertiefte Verständnis.

Die Besonderheit bzw. Innovation von Transformatoren ist es, dass vor der linearen Transformation ein Self-Attention-Mechanismus greift. Dies ist Thema von Kapitel 7.

***Kapitel 6: Das Vortraining des BERT-Modells***

*Groblernziele und Kompetenzen:*

Die SuS...

... können den Vortrainingsprozess von BERT in eigenen Worten beschreiben und erproben zentrale Mechanismen in Anwendungsaufgaben.

... verstehen das Prinzip des Masked Language Modeling.

...  verstehen die Vortrainingsaufgabe der Next Sentence Prediction.

*Beschreibung:*

Vortraining in BERT umfasst die beiden Aufgaben 'Masked Language Modeling' und 'Next Sentence Prediction'. Sie erzeugen im Bert-Modell ein allgemeines, rudimentäres Sprachverständnis und sind inspiriert durch das Lesenlernen von Kindern: 'Masked Language Modeling' sind einfach formuliert Lückentext-Aufgaben, in denen das Modell teilen des Trainingstextes [MASK]-Tokens zuweist und versucht, diese richtig zu erraten. Bei der 'Next Sentence Prediction' versucht das Modell bei zwei Sätzen A und B zu erraten, ob B semantisch auf Satz A folgen könnte.

Bisher existieren zu diesem Kapitel ein einleitender Text und eine Beschreibung der Trainingsprozesse.

#Abbildung#

Außerdem wurden verständisprüfende Multiple-Choice-Aufgaben und Aufgaben zum Durchführen der beiden Vorgänge eingebaut. Im Sinne der Exploration könnte dies durch weitere, umfangreichere Aufgaben ergänzt werden.

#Abbildung#

***Kapitel 7: Der Self-Attention-Mechanismus***

*Groblernziele und Kompetenzen:*

Die SuS...

... verstehen den Self-Attention-Mechanismus und rekonstruieren dessen
Berechnungslogik.

... verstehen, wie Wörter anhand im Self-Attention-Mechanismus
gewichtet werden.

...  vollziehen die sechs Berechnungsschritte der Self-Attention nach.

*Beschreibung:*

Hierzu liegt lediglich eine grobe Ideenskizze vor: Die sechs Schritte der Berechnung der Self-Attention werden Schritt für Schritt durchlaufen. Dies muss explorative geschehen. D.h. die SuS sehen in jedem Schritt genau, was gerade mit dem Embedding-Vektor passiert. BertVIZ (https://github.com/jessevig/bertviz) ist hierfür eine gute Grundlage. Es visualisiert die Aufmerksamkeits-Scores: Es können zwei Sätze A und B in dieses Tool eingegeben werden. Für jede einzelne Transformerschicht kann BERTViz eingesehen, wie relevant ein Wort des Satzes A für für die umliegenden Wörter des Satzes B ist (und umgekehrt). Ein Thema einer anderen Abschlussarbeit könnte sein, dieses BERTViz Tool weiterzuentwickeln, sodass sämtliche Schritte der Self-Attention auf visueller Ebene offengelegt werden.  

***Kapitel 8: Der erweiterte Self-Attention-Mechanismus: Multi-Headed-Self-Attention***

*Groblernziele und Kompetenzen:*

Die SuS...

...  verstehen, dass die Self-Attention weiter optimiert werden kann, indem
Einbettungen auf mehrere Köpfe aufgeteilt und parallel zueinander werden.


*Beschreibung:*

Multi-Headed-Self-Attention verfeinert den Mechanismus aus Kapitel 7, indem ein Einbettungsvektor in z.B. zwölf Teilvektoren aufgeteilt wird und diese separat eine Self-Attention durchlaufen und schließlich wieder zusammengesetzt werden. Auch hierzu existieren noch keine explorativen Blöcke.

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



