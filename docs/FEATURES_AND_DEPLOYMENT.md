# OMSU FindBack: AI, messaging, analytics, and deployment

## Install and start locally

From the project root, activate the virtual environment and install the new dependencies:

```powershell
python -m pip install -r requirements.txt
Copy-Item .env.example .env
python app.py
```

Set the MySQL values and a long random `SECRET_KEY` in `.env`. If your existing `.env` sets `UPLOAD_FOLDER=static/uploads`, change it to `UPLOAD_FOLDER=instance/uploads`; startup now refuses to place uploaded files in the public static folder. On first startup, SQLAlchemy creates the new additive feature tables and inserts starter category/location lists when those lists are empty. Back up the database before upgrading an existing installation.

## Photo recognition

The report form runs Ultralytics YOLOv8 Nano with the standard pretrained COCO object-detection weights when a photo is selected; the button can also be used to retry. The bundled `yolov8n.pt` is resolved relative to this project, or `AI_MODEL_PATH` can point to another local weights file. The model runs on the application server CPU; uploaded photos are not sent to an AI vendor. It returns detected object labels and confidence values, maps common objects into active campus categories, and estimates a dominant color within a detected object's crop. Suggestions below 45% confidence do not autofill the name, item type, or category; users should verify the approximate color and manually identify unsupported items.

The matching page combines report details with cosine similarity between local YOLO image embeddings when both reports have photos. Embeddings are kept in a bounded in-process cache and refreshed when a photo file changes. The matcher considers up to the 100 most recent verified found reports per request. Image similarity is a ranking signal only; it is not proof that two photos show the same physical item or establish ownership.

This is genuine pretrained object detection, but it is not a custom OMSU model. COCO covers common object classes, not every personal item, brand, serial number, or campus object. The confidence is not a probability of ownership. Users must correct suggestions; moderators still verify claims. AI activity records contain the detected class, category, confidence, user, and timestamp—not a second copy of the image.

## Private messages and notifications

Submitting an eligible claim creates one conversation for that claim. The claimant and report owner can exchange private messages over Socket.IO. Admins and moderators can access conversations for safety review; the chat page discloses this. Messages are stored in the database, limited to 2,000 characters, and use authenticated, authorized conversation rooms.

In-app notifications are stored for new reports, claims, status updates, and messages. Email is optional: configure `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, and `SMTP_SENDER` in the private `.env`; keep the account credentials out of source control. Without SMTP configuration, in-app notifications continue to work.

## Claim handover history

Submitting a claim notifies the item owner and claimant to coordinate at the SSG Office and alerts active moderators and administrators. A moderator or administrator approves the claim only after the handover is verified. Approval marks the report `Recovered`, removes it from the student campus board and future matching, and notifies both parties. The new admin-only **Claim handover history** stores a transaction snapshot of the item, report, owner and claimant contact details, private claim evidence, handover location, reviewer, and completion time. This snapshot remains available if account details later change. Handle this personal information according to OMSU privacy and retention policy.

## Campus lists and reporting

Administrators can add, rename, deactivate, and reactivate categories and campus locations. Deactivation preserves the existing report text. The starter values are generic; replace them with OMSU's official campus/building names in **Categories & locations**.

The analytics page aggregates reports by category, location, and month, plus recorded AI analysis counts, average confidence, and frequent detected classes. Select the official semester's start/end dates in the date filters; the application does not assume OMSU's academic calendar. Analytics are descriptive and do not expose claim evidence.

## Security and production notes

- All browser POST forms use CSRF protection. Login, registration, and AI analysis are rate limited. Production requires a strong secret key and a shared Redis URL in `RATELIMIT_STORAGE_URI`; in-memory rate limiting is only suitable for a single local development process.
- Session cookies are HTTP-only and same-site; production marks them secure and redirects HTTP to HTTPS. Production startup requires `ALLOWED_HOSTS`, a strong secret key, and shared Redis rate-limit storage. The app adds a content security policy and anti-sniffing, frame, referrer, and permissions headers. Set `TRUST_PROXY=true` only when there is exactly one trusted reverse proxy in front of the app; otherwise leave it false.
- New uploads are stored under `instance/uploads` (outside Flask's public static directory) and are only served to signed-in users through a report-aware route. If an older installation has files under `static/uploads`, back them up, move them into the configured private upload directory, and remove public copies before exposing the site.
- Set a unique production `SECRET_KEY`, strong database credentials, private upload storage, SMTP settings, and a shared Redis service. Never commit `.env`, passwords, database dumps, uploaded images, or model weights.
- `db.create_all()` adds tables but is not a general schema-migration system. Back up MySQL before deployment and use a migration tool for future changes to existing table structures.
- The Socket.IO development runner is used by `python app.py`. For a public deployment, select a production WSGI/Socket.IO server configuration that supports WebSocket connections and set its trusted proxy/HTTPS settings. This project has not been deployed to hosting because this workspace is configured for local development.
