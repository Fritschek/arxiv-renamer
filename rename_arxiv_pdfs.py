import os
import re
import requests

MAX_FILENAME_LENGTH = 200

def extract_arxiv_number(filename):
    """
    Extract the arXiv number from the filename.
    """
    pattern = r'\d{4}\.\d{4,5}(v\d+)?'
    match = re.search(pattern, filename)
    if match:
        return match.group()
    return None

def clean_filename(filename):
    """
    Remove or replace characters that are not allowed in filenames on Windows.
    Also, limit the length of the filename.
    """
    invalid_chars = [":", "*", "?", "|", "<", ">", "\""]
    for char in invalid_chars:
        filename = filename.replace(char, "")
    return filename[:MAX_FILENAME_LENGTH]

def fetch_arxiv_metadata(arxiv_number):
    """
    Fetch the metadata (authors and title) for a given arXiv number.
    """
    url = f'http://export.arxiv.org/api/query?id_list={arxiv_number}'
    response = requests.get(url)
    if response.status_code == 200:
        author_match = re.findall(r'<name>([\s\S]*?)</name>', response.text)
        title_match = re.search(r'<title>([\s\S]*?)</title>', response.text)

        authors = [author.strip() for author in author_match] if author_match else []
        title = title_match.group(1).strip() if title_match else None

        return authors, title
    return [], None

def unique_filename(base_path, filename):
    """
    Generate a unique filename by appending a number if the file already exists.
    """
    counter = 1
    name, extension = os.path.splitext(filename)
    while os.path.exists(os.path.join(base_path, filename)):
        filename = f"{name} ({counter}){extension}"
        counter += 1
    return filename

def format_author_name(name):
    """
    Format the author's name to extract the last name.
    """
    names = name.split()
    last_name = names[-1]
    return last_name

def rename_arxiv_pdfs(folder_path):
    """
    Rename all arXiv PDFs in the specified folder.
    """
    pdf_files = [f for f in os.listdir(folder_path) if f.endswith('.pdf')]
    for pdf_file in pdf_files:
        arxiv_number = extract_arxiv_number(pdf_file)
        if not arxiv_number:
            continue

        authors, title = fetch_arxiv_metadata(arxiv_number)

        if authors and title:
            first_author = authors[0]
            formatted_author = format_author_name(first_author)
            new_name = f"{formatted_author}_{'_'.join(title.split())}.pdf"
            if len(authors) > 1:
                new_name = f"{formatted_author} et al._{'_'.join(title.split())}.pdf"
        
            new_name = clean_filename(new_name)
            new_name = unique_filename(folder_path, new_name)
            os.rename(os.path.join(folder_path, pdf_file), os.path.join(folder_path, new_name))
            print(f"Renamed '{pdf_file}' to '{new_name}'")

folder_path = "./"  # Point this to the directory with your PDFs
rename_arxiv_pdfs(folder_path)
