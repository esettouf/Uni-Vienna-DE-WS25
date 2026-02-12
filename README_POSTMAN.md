# B2B Postman Collection – Use Case Ablaufbeschreibung

Die Postman Collection in digioek-gruppe4-ass3.postman_collection.json bildet die vollständigen **B2B-Schnittstellen** der Plattform ab und demonstriert die Umsetzung der definierten Use Cases für **Business-Onboarding**, **Zertifizierung** sowie **Handel von THG-Zertifikaten**.

**Wichtig:**
- Bitte den GraphQL Endpoint https://localhost:8080/graphql als Variable 'baseURL' zur Collection hinzufügen. Diese geht beim Exportieren leider verloren.
- Dann können Schritt für Schritt in der angegebenen Reihenfolge die Use Cases ausgeführt werden. Dies ist notwendig, da z.B. die User erst angelegt werden und die JWT-Authentication-Tokens abgespeichert werden. 
Alle Abläufe sind reproduzierbar und containerisiert.

---

## B2B – UC2: Register Business Seller

Dieser Abschnitt beschreibt das vollständige **Onboarding eines Business-Sellers**.

### Register Business Seller
Ein Business-Seller registriert sich auf der Plattform.

**Systemaktion**
- Anlage eines neuen Users mit Rolle `business`
- Verifizierungsstatus zunächst `EMAIL_PENDING` 

---

### Login & Get Seller Token
Der Seller meldet sich mit seinen Zugangsdaten an.

**Ergebnis**
- JWT Access Token wird ausgestellt
- Token wird für alle weiteren B2B-Requests verwendet

---

### Get Seller User Infos
Abruf der aktuellen Benutzerinformationen des Sellers.

**Zweck**
- Kontrolle von Rolle, Verifizierungsstatus und Wallet
- Verifikation des erfolgreichen Logins

---

### Admin Login & Get Token
Ein Administrator meldet sich an.

**Zweck**
- Vorbereitung für administrative Freigaben
- Admin erhält JWT mit Rolle `admin`

---

### Platform Verifies Seller Account
Der Administrator verifiziert den Seller.

**Ergebnis**
- Verifizierungsstatus → `VERIFIED`
- Seller ist berechtigt, Zertifikate einzureichen und zu handeln

---

### Confirm User Verification
Abschließende Bestätigung der Verifikation.

---

## B2B – UC3: Certification Decision Event

Dieser Abschnitt demonstriert den **asynchronen Zertifizierungsprozess** inklusive Event-Mechanismus.

### Create Batch Certificate Requests
Der Business-Seller reicht mehrere Zertifizierungsanträge (Batch) ein.

**Ergebnis**
- Mehrere Certification Requests mit Status `SUBMITTED`

---

### Admin Login & Get Token
Admin meldet sich an, um die Zertifizierungsanträge zu bearbeiten.

---

### Confirm Certificates
Der Administrator bestätigt die Zertifizierungsanträge.

**Systemaktion**
- Status der Requests → `CONFIRMED`
- Zertifikate werden erzeugt
- **B2B Decision Event** wird in der Outbox gespeichert

---

### Pending for Confirmation 1
Der Business-Partner ruft alle offenen Decision Events ab.

**Ergebnis**
- Liste aller Events mit Status `PENDING`
- Enthält Entscheidung und Certificate-ID

---

### ACK 1
Der Business-Partner bestätigt den Empfang der Events.

**Ergebnis**
- Event Status → `ACKED`
- Event gilt als verarbeitet

---

### Create Batch Certificate Requests 2
Ein zweiter Zertifizierungsbatch wird eingereicht.

---

### Confirm Certificates 2
Der Administrator bestätigt den zweiten Batch.

---

### Pending for Confirmation 2
Abruf der neuen offenen Decision Events.

---

### ACK 2
Bestätigung des Empfangs der zweiten Event-Serie.

**Zweck**
- Nachweis von Idempotenz und Stabilität des Event-Mechanismus

---

## B2B – UC4 & UC5: Sell and Buy Orders

Dieser Abschnitt beschreibt den **B2B-Handel** von THG-Zertifikaten.

---

### Create Sell Order 1
Der Business-Seller erstellt ein Verkaufsangebot für ein Zertifikat.

**Systemaktion**
- Sell Order mit Status `PLACED`
- Zertifikat wird reserviert

---

### Register Business Buyer
Ein Business-Buyer registriert sich auf der Plattform.

---

### Login Buyer
Der Buyer meldet sich an und erhält ein JWT.

---

### Platform Verifies Buyer Account
Der Administrator verifiziert den Buyer.

**Voraussetzung**
- Nur verifizierte Buyer dürfen Kaufaufträge erstellen

---

### Marktübersicht aufrufen (Buyer)
Der Buyer ruft die Marktübersicht ab.

**Inhalt**
- Alle offenen Sell Orders
- Alle offenen Buy Bids

---

### Kaufauftrag erstellen 1
Der Buyer erstellt ein Kaufgebot (Bid).

**Systemaktion**
- Automatisches Matching bei passendem Preis
- Trade wird erstellt

---

### Kaufauftrag erstellen 2
Ein weiterer Kaufauftrag wird erstellt.

**Zweck**
- Demonstration der Matching-Logik

---

### Marktübersicht aufrufen (Seller)
Der Seller ruft erneut die Marktübersicht ab.

**Ergebnis**
- Nur offene Orders sichtbar
- Gematchte Orders sind entfernt

---

### Kaufauftrag 2 stornieren
Ein offenes Kaufgebot wird storniert.

**Ergebnis**
- Bid Status → `CANCELLED`

---