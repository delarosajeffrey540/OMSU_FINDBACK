# Offline Login Images

Place these image files in this folder:

- `omsu-logo.png` - the official OMSU logo.
- `omsu-campus.jpg` - a campus building photo for the login background.

## Setup

1. Open the official university logo at <https://omsu.edu.ph/images/omsc.logo.png>. Right-click it, choose **Save image as**, and save it here as `omsu-logo.png`.
2. Open this campus-building image: <https://images.unsplash.com/photo-1562774053-701939374585?fit=crop&w=1600&q=85&fm=jpg>. Right-click, choose **Save image as**, and save it here as `omsu-campus.jpg`. You may instead use a campus photo you have permission to use.
3. Keep the two files in `static/images/branding/` beside this README.
4. Restart the Flask app and open `/login`. Local files are used first; online images are only fallbacks.

The login page remains functional without the image files, but the logo and campus photo require these local files for fully offline display.