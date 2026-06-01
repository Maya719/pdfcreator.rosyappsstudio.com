# PDF Creator Memories

## Project Structure
- The project follows a Laravel-inspired structure for Python using FastAPI.
- `app/http/controller`: Contains the controller classes.
- `routes`: Contains `api.py` and `web.py` for routing.
- `bootstrap`: Contains `autoload.py` for environment and path setup.
- `config`: Contains configuration files.
- `storage`: Contains `public` and `private` disks for file storage.
- `resources/views`: Contains Jinja2 templates.

## Implemented Features
- `bootstrap/autoload.py`: Handles environment loading, `sys.path` configuration, and ensures compulsory directories (`uploads`, `pdfs`) exist.
- `bootstrap/app.py`: Centralized application factory (`create_app`) for FastAPI, handling all middleware, routes, and mounting.
- `public/app.py`: Clean entry point using the application factory.
- `WordToPdfController`: Uses a pure-Python pipeline (**Mammoth** + **xhtml2pdf**) to convert `.docx` to PDF while preserving basic styling (bold, italics, tables) without any external server software or watermarks.
- **Modular Conversion Architecture**: The conversion logic is separated into specialized modules under `app/http/controller/converters/`. High-fidelity rendering logic and shared utilities are housed in `app/helpers/pdf_utils.py`.
- **Browser-Engine Conversion (Pin Point Exact)**: DOCX conversion now uses a **Headless Browser (Playwright/Chromium)** combined with the **`docx-preview.js`** engine. This provides the highest possible fidelity on Linux (no LibreOffice needed) by rendering the document in a virtual browser before capturing it as a PDF.
- **Pure-Python Pipeline**: The application remains standalone and pip-installable, using `playwright` for both HTML and DOCX rendering. LibreOffice remains removed.
- **Cross-Platform High Fidelity**: The browser-based approach ensures that images, fonts, and complex Word layouts are preserved identically across all environments.

## Project Notes
- **Filenames**: Automatically generated if not provided in the request.
- **Security**: All API routes are protected by `ApiKeyMiddleware`.

## Pending Tasks
- Improve error handling for large file uploads.
- Add comprehensive unit tests.
