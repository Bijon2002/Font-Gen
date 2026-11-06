# Font-Gen Implementation Plan

## Product modes

1. **Handwriting template**: download a printable template, fill it in, upload a photo, and receive a TTF.
2. **Style from image**: upload a title image, pick the face color, enter the text shown in the image, and receive a font with AI-completed letters.
3. **Transparent title cutout**: export the colored title artwork as a transparent PNG for CapCut.

## Implementation phases

- [x] Create the FastAPI backend and React frontend structure.
- [x] Add template generation and handwriting-cell extraction.
- [x] Add font construction with FontTools.
- [x] Add color-based style extraction and transparent PNG cutouts.
- [x] Add optional Gemini-powered missing-letter completion.
- [x] Add frontend controls for both modes and downloads.
- [ ] Add production API URL configuration and deploy backend/frontend.
- [ ] Add visual regression fixtures and expand multilingual support.

## Current limitations

- A TTF stores a single flat color; 3D layers remain available through the PNG cutout.
- AI completion requires `GEMINI_API_KEY`; without it, style mode uses detected letters only and reports missing glyphs.
- Punctuation, kerning, and connected-letter splitting are deferred.
