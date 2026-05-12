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

## Project Notes
- **Filenames**: Automatically generated if not provided in the request.
- **Security**: All API routes are protected by `ApiKeyMiddleware`.

## Pending Tasks
- Improve error handling for large file uploads.
- Add comprehensive unit tests.
