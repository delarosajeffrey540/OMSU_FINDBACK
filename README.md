# OMSU FindBack
Flask + MySQL starter implementation based on the uploaded 43-page OMSU FindBack prototype.

See `docs/INSTALLATION_TUTORIAL.md` for the complete Windows + XAMPP setup tutorial.

**Features:** local pretrained object detection suggestions for report photos, private Socket.IO messaging between claimants and report owners, editable campus categories/locations, AI and semester-period activity analytics, in-app/email notifications, and CSRF/session/upload hardening.

See `docs/FEATURES_AND_DEPLOYMENT.md` for model behavior, setup, privacy, configuration, migration, and deployment notes. The vision model is generic pretrained object detection; it is not trained on OMSU items and never verifies ownership or approves matches.
