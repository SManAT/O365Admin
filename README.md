Mit diesem Tool werden die Office365 Benutzer der Schule abgeglichen

1. Alle User werden via Powershell aus Azure geladen.  
   Dazu auf einer PS Admin CLI installieren:  
   ```ps
   Install-Module -Name AzureAD
   ```
   
2. Die Zugangsdaten werden in *config/config.yaml* abgelegt.  
   Das Passwort muss verschlüsselt abgelegt werden. Verwende dazu
   O365Admin.py um einen Passwort-Hash zu erstellen.
   
3. Lehrer Accounts werden anhand der A3 Lizenz 

4. Für Spezialkonten gibt es im Ordner *config/* die Datei *vip.yaml*
   Spezialkonten sind z.B. für Sekretariat, Testkonten, etc.
  
-- Lehrer und Spezialkonten werden niemals gelöscht --  
-- Alle Daten werden verschlüsselt in der SQLite DB abgelegt (vergl. *config/key.key*) --  
  
3. Die Schüler Accounts werden aus Sokrates via CSV Datei importiert.
   Auswertungen > Dynamische Suche > 100 Aktive Schüler > Exportieren als CSV
   Die Datei in das root Verzeichnis des Tools legen
   
5. Starte das Tool
   ```ps
   python O365Admin.py
   ```