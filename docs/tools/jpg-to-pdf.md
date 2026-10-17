# JPG to PDF

**Tool ID:** `jpg_to_pdf`  
**Category:** PDF tools  
**Status:** active  
**Version:** 1.0

## Product contract

Combine one or more JPEG images into a single PDF, preserving their upload
order. The tool is free and can be used without an account.

## Input and output

- Input: 1–20 valid JPEG images, up to 25 MB per image.
- Output: one PDF with one image per page.
- Processing: synchronous server processing for the MVP.
- Storage: the result follows the existing temporary media-storage flow.

## API

`POST /api/v1/pdf/from-image/` with repeated multipart field `images`.

The endpoint returns the standard success envelope with the result filename,
size, and download URL. Invalid images and upload-limit violations return a
validation error without exposing internal processing details.

## UI and quality requirements

The public route is `/tools/pdf/from-jpg`. It reuses the shared upload area and
tool layout, provides idle, processing, success, and error states, and links to
related PDF tools. The page is responsive and uses semantic theme tokens.

