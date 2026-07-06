# PDF Note System

A personal PDF reading and note-taking system based on Streamlit, featuring a dual-page reader layout, rich text notes (Markdown + images), bookmark navigation, and automatic data management.

## Features

### Bookshelf Management
- Display all imported PDF books in a list
- Upload new PDF files
- Each book has independent storage with metadata, last page, and bookmarks
- Delete books (removes all associated notes and images)
- Rename books

### Dual-Page Reader
- **Layout**: Left page + Right page + Right-side note panel (ratio 2:2:1.5)
- **Single Page Mode**: Switch to single page layout with 1:1 book/note ratio
- **Page Navigation**: Previous/Next buttons, page slider, numeric input jump
- **Shortcuts**: Left/Right arrow keys for page turning
- **Note Badges**: Display note count per page

### Note System
- Markdown formatting (headings, lists, bold, italic, tables, code blocks)
- Image insertion (drag & drop or click to upload)
- Auto-record page number and creation/update timestamps
- Note panel shows notes for current page
- Hover to auto-expand note entries
- Edit and delete notes

### Bookmark System
- Add/delete bookmarks
- Bookmark list in sidebar (collapsed by default)
- Click bookmark to jump to page
- Bookmark notes/annotations

### Statistics
- Book count, note count, bookmark count
- Notes file size, images file size

## Quick Start

### Prerequisites
- Python 3.9+
- Streamlit 1.28+
- PyMuPDF (fitz) 1.23+
- Pillow 10.0+
- uv (Python package manager)

### Installation & Run

**Method 1: Using startup scripts (recommended)**
```bash
# Install uv (first time only)
pip install uv

# Start the application
Double-click start.bat

# Stop the application
Double-click stop.bat
```

**Method 2: Command line**
```bash
# Install dependencies
uv sync

# Start the application
uv run streamlit run app.py --server.port 8103 --server.address 0.0.0.0
```

### Access
- Local: http://localhost:8103
- Network: http://your-ip:8103

## Project Structure

```
pdf-note-system/
├── app.py                    # Main application entry
├── pages/
│   ├── 1_bookshelf.py        # Bookshelf management page
│   └── 2_bookmarks.py        # Bookmark management page
├── components/
│   ├── reader.py             # Reader core component
│   ├── note_panel.py         # Note panel component
│   ├── bookmark_manager.py   # Bookmark management component
│   └── image_uploader.py     # Image upload component
├── utils/
│   ├── pdf_handler.py        # PDF processing utility
│   ├── note_storage.py       # Note storage utility
│   ├── image_handler.py      # Image processing utility
│   └── logger.py             # Logging utility
├── data/                     # Data directory (auto-created)
│   ├── shelf.json
│   └── books/
│       └── {book_id}/
│           ├── book.pdf
│           ├── notes.json
│           └── images/
├── logs/                     # Log directory
├── requirements.txt          # Dependencies
├── pyproject.toml            # Project configuration
├── start.bat                 # Windows startup script
└── stop.bat                  # Windows stop script
```

## Usage Guide

### Upload a Book
1. Click "Bookshelf" in the left sidebar
2. Click "Browse files" to select a PDF
3. Optionally customize the book title
4. Click upload

### Start Reading
1. Find the book on the bookshelf
2. Click the eye icon to start reading

### Add a Note
1. Click the note panel on the right side
2. Enter selected text
3. Write note content (Markdown supported)
4. Optionally upload images
5. Click save

### Add a Bookmark
1. Click the bookmark button in the reader
2. Optionally add a note
3. Confirm

### Page Navigation
- **Button**: Previous / Next
- **Arrow Keys**: Left / Right
- **Slider**: Drag to jump
- **Input**: Type page number directly

## Shortcuts

| Key | Action |
|-----|--------|
| Left Arrow | Previous page |
| Right Arrow | Next page |

## Data Storage

- **Shelf config**: `data/shelf.json`
- **Notes**: `data/books/{book_id}/notes.json`
- **Images**: `data/books/{book_id}/images/`
- **Logs**: `logs/app_YYYYMMDD.log`

## Tech Stack

- **Framework**: Streamlit 1.28+
- **PDF Processing**: PyMuPDF (fitz) 1.23+
- **Image Processing**: Pillow 10.0+
- **Package Manager**: uv
- **Logging**: Python logging module

## Development

### Code Style
- Python 3.9+
- Streamlit native components
- Logging for all core modules
- JSON file storage

### Extending
- Add components in `components/`
- Add utilities in `utils/`
- Add pages in `pages/`

## License

MIT License

## Contributing

Issues and Pull Requests are welcome!
