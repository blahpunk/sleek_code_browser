
# Sleek Code Browser

Sleek Code Browser is a modern, responsive tool designed to simplify the process of browsing, viewing, and copying code from your projects. With a sleek, dark-themed interface, this application makes it easy to navigate your project folders, view the content of code files, and quickly copy snippets or entire files to the clipboard.

## Features

- **Project Folder Navigation**: Quickly select your project folder and browse its contents with an intuitive tree view.
- **Automatic File Selection**: Common code files like `.py`, `.js`, `.html`, and more are automatically selected and ready for viewing, while other files remain unchecked for optional review.
- **Code Viewing**: Display the content of selected files directly within the application. Lines of code are color-coded, and visual indicators mark the start and end of files.
- **Easy Copying**: With a simple click, copy file contents or specific snippets to your clipboard for easy pasting into your editor.
- **Bookmark and Jump**: Use bookmark-style tabs to quickly jump to specific files within the project.

## Installation

### Prerequisites

- **Python 3.x**
- **PyQt5**: Install it using pip if it's not already installed.

```bash
pip install PyQt5
```

### Cloning the Repository

Clone the repository from GitHub:

```bash
git clone https://github.com/blahpunk/sleek_code_browser.git
cd sleek_code_browser
```

## Usage

1. **Launch the Application**: Run the `main.py` file to start the Sleek Code Browser:

   ```bash
   python main.py
   ```

2. **Select Your Project Folder**: Click the "Select Folder" button to browse and choose your project directory.

3. **View Code Files**: Automatically selected code files are displayed in the tree view. Click "Show" to view the content of these files in the main display area.

4. **Copy Code**: Use the "Copy All" button to copy all displayed content to your clipboard, or click the copy icon next to individual files to copy their contents.

## Contributing

We welcome contributions! If you have ideas for improvements or find any issues, feel free to submit a Pull Request or open an issue on GitHub.

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.
