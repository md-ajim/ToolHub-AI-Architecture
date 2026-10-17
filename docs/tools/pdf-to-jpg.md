# PDF to JPG

**Tool ID:** `pdf_to_jpg`  
**Category:** PDF tools  
**Status:** active  
**Version:** 1.0

## Product contract

Convert every page of a PDF into a JPEG image. The tool is free, can be used
without an account, and returns a ZIP archive containing page-ordered JPEGs.

## Input and output

- Input: one valid, unencrypted PDF (maximum 25 MB and 50 pages).
- Output: a ZIP archive of JPEG files rendered at 150 DPI.
- Processing: synchronous server processing for the MVP.
- Storage: the result follows the existing temporary media-storage flow.

## API

`POST /api/v1/pdf/to-image/` with multipart field `file`.

The endpoint returns the standard success envelope with the result filename,
size, and download URL. Invalid, malformed, encrypted, or oversized PDFs
return a validation error without exposing internal processing details.

## UI and quality requirements

The public route is `/tools/pdf/to-jpg`. It uses the shared upload area and
tool layout, exposes idle, processing, success, and error states, and links to
related PDF tools. The page is responsive and uses semantic theme tokens.

