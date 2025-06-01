**Die Lernumgebung**


**Musterkapitel 4: Lernziele - Unterrichtsverlaufsplan - Weiterführende Materialien**



**Anleitung zum Aufsetzen des Servers**



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



