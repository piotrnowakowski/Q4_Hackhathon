from markitdown import MarkItDown
import os

def convert_pdf_to_markdown(pdf_path, markdown_path):
    """
    Converts a PDF file to a Markdown format and saves it.

    Args:
        pdf_path (str): Path to the PDF file.
        markdown_path (str): Path to save the Markdown file.
    """
    md = MarkItDown()
    result = md.convert(pdf_path)
    text_content = result.text_content

    # Save text content to a Markdown file
    with open(markdown_path, 'w', encoding='utf-8') as markdown_file:
        markdown_file.write(text_content)
    
    print(f"Markdown file saved at: {markdown_path}")

# Example usage
if __name__ == "__main__":
    data_folder = "data"
    markdown_folder = "markdown"
    
    # Create markdown folder if it doesn't exist
    if not os.path.exists(markdown_folder):
        os.makedirs(markdown_folder)
    
    for filename in os.listdir(data_folder):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(data_folder, filename)
            markdown_file_path = os.path.join(markdown_folder, os.path.splitext(filename)[0] + ".md")
            convert_pdf_to_markdown(pdf_path, markdown_file_path)

