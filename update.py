import os
import re
from bs4 import BeautifulSoup
from datetime import datetime
import time

def read_template():
    """
    Read template markdown file and extract metadata and content.
    Returns a dictionary with title, date, tag, and content if all values exist.
    Returns None if any values are missing.
    """
    template_path = os.path.join(os.path.dirname(__file__), 'template.md')
    
    if not os.path.exists(template_path):
        print("Template file not found")
        return None
    
    with open(template_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Extract metadata
    title_match = re.search(r'Title:\s*(.*?)(?:\n|$)', content)
    date_match = re.search(r'Date:\s*(.*?)(?:\n|$)', content)
    tag_match = re.search(r'Tag:\s*(.*?)(?:\n|$)', content)
    
    # Check if all metadata exists and has values
    if not (title_match and date_match and tag_match):
        print("Missing metadata in template file")
        return None
    
    title = title_match.group(1).strip()
    date = date_match.group(1).strip()
    tag = tag_match.group(1).strip()
    
    # Check if any values are empty
    if not (title and date and tag):
        print("Empty values in template file")
        return None
    
    # Extract content (everything after the metadata)
    pattern = r'Tag:\s*.*?\n\n(.*)'
    content_match = re.search(pattern, content, re.DOTALL)
    
    if not content_match:
        print("No content found in template file")
        return None
    
    article_content = content_match.group(1).strip()
    
    # Format date to YYYY-MM-DD for consistency
    try:
        date_obj = datetime.strptime(date, "%Y/%m/%d")
        formatted_date = date_obj.strftime("%Y-%m-%d")
    except ValueError:
        print(f"Invalid date format: {date}. Expected YYYY/MM/DD")
        return None
    
    return {
        'title': title,
        'date': formatted_date,
        'tag': tag,
        'content': article_content
    }

def clear_template():
    """
    Clear the values in the template file but keep the structure.
    """
    template_path = os.path.join(os.path.dirname(__file__), 'template.md')
    
    if not os.path.exists(template_path):
        return
    
    with open(template_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Clear values but keep the structure
    content = re.sub(r'(Title:)\s*.*?(?=\n|$)', r'\1', content)
    content = re.sub(r'(Date:)\s*.*?(?=\n|$)', r'\1', content)
    content = re.sub(r'(Tag:)\s*.*?(?=\n|$)', r'\1', content)
    
    # Clear content after metadata
    content = re.sub(r'(Tag:.*?\n\n).*', r'\1', content, flags=re.DOTALL)
    
    with open(template_path, 'w', encoding='utf-8') as file:
        file.write(content)
    
    print("Template file cleared")

def generate_html(post_data):
    """
    Generate HTML file from post data.
    """
    # Create Post directory if it doesn't exist
    post_dir = os.path.join(os.path.dirname(__file__), 'Post')
    os.makedirs(post_dir, exist_ok=True)
    
    # Create a filename from the title (simplified)
    filename = re.sub(r'[^\w\s]', '', post_data['title'])  # Remove special characters
    filename = re.sub(r'\s+', '_', filename)  # Replace spaces with underscores
    filename = filename.lower()  # Convert to lowercase
    filename = f"{filename}.html"
    
    # Path to new HTML file
    file_path = os.path.join(post_dir, filename)
    
    # HTML template
    html_template = f"""<!DOCTYPE html>
<html lang="zh">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Writing</title>
    <link rel="icon" href="../resources/icon.jpg" type="/image/jpeg">
    <link href="https://fonts.googleapis.com/css2?family=Lato:wght@100;300;400;700;900&family=Alegreya+Sans+SC:wght@400;700&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <link rel="stylesheet" href="../style.css">
</head>
<body>
    <header class="header">
        <h1 class="site-title">{post_data['title']}</h1>
        <p class="date">{post_data['date']}</p>
        <p class="tag">{post_data['tag']}</p>
    </header>

    <main id="content">
        <!-- Markdown rendered content will display here -->
    </main>

    <script>
        const markdownContent = 
`
{post_data['content']}
`;

        document.getElementById('content').innerHTML = marked.parse(markdownContent);
    </script>
</body>
</html>"""
    
    # Write HTML file
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(html_template)
    
    print(f"Generated HTML file: {filename}")
    return filename

def extract_post_info(html_content):
    """
    Extract title, date, and tag from a post HTML file.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Extract title
    title_element = soup.select_one('.site-title')
    title = title_element.text.strip() if title_element else "Unknown Title"
    
    # Extract date
    date_element = soup.select_one('.date')
    date = date_element.text.strip() if date_element else "No Date"
    
    # Extract tag
    tag_element = soup.select_one('.tag')
    tag = tag_element.text.strip() if tag_element else ""
    
    return {
        'title': title,
        'date': date,
        'tag': tag
    }

def update_index(new_tag=None):
    """
    Update the index.html file with posts from the Post directory.
    If new_tag is provided, update the topics section with the new tag.
    Now uses the JavaScript array format from the new index.html.
    """
    # Get all HTML files from Post directory
    post_files = []
    post_dir = os.path.join(os.path.dirname(__file__), 'Post')
    
    if not os.path.exists(post_dir):
        print(f"Post directory not found at {post_dir}")
        return
    
    for filename in os.listdir(post_dir):
        if filename.endswith('.html'):
            file_path = os.path.join(post_dir, filename)
            
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                
                post_info = extract_post_info(content)
                post_info['filename'] = filename
                
                try:
                    # Parse date to enable sorting
                    post_date = datetime.strptime(post_info['date'], '%Y-%m-%d')
                    post_info['datetime'] = post_date
                except ValueError:
                    # If date parsing fails, use a default old date
                    post_info['datetime'] = datetime(1900, 1, 1)
                
                post_files.append(post_info)
    
    # Sort posts by date (newest first)
    post_files.sort(key=lambda x: x['datetime'], reverse=True)
    
    # Read the current index.html file
    index_path = os.path.join(os.path.dirname(__file__), 'index.html')
    with open(index_path, 'r', encoding='utf-8') as file:
        index_content = file.read()
    
    # Instead of using BeautifulSoup which might modify the HTML structure,
    # use regex to find and replace the postData array
    
    # Convert posts to the required format
    post_data_entries = []
    for post in post_files:
        # Escape quotes in title and tags for JavaScript
        title = post['title'].replace('"', '\\"')
        
        post_entry = f'{{date: "{post["date"]}", url: "Post/{post["filename"]}", title: "{title}", tags: "{post["tag"]}"}}'
        post_data_entries.append(post_entry)
    
    # Join all entries with comma and newline
    post_data_array = ',\n            '.join(post_data_entries)
    
    # Create the complete array string
    post_data_js = f"""    document.addEventListener('DOMContentLoaded', () => {{
        // 文章数据
        const postData = [
            {post_data_array}
        ];
        
        // 获取容器元素"""
    
    # Find and replace the postData array in the file
    pattern = r'document\.addEventListener\(\'DOMContentLoaded\', \(\) => \{[^{]*const postData = \[[^\]]*\];[^{]*// 获取容器元素'
    new_content = re.sub(pattern, post_data_js, index_content, flags=re.DOTALL)
    
    # Handle adding new tags if needed
    if new_tag:
        # Use BeautifulSoup for the tag part only
        soup = BeautifulSoup(new_content, 'html.parser')
        topics_section = soup.select_one('.topic-links')
        
        if topics_section:
            # Get existing tags
            existing_tags = []
            for link in topics_section.select('.topic-link'):
                tag = link.get('data-tag')
                if tag != 'all':  # Skip the "All" tag
                    existing_tags.append(tag)
            
            # If the new tag doesn't exist, add it
            if new_tag not in existing_tags:
                # Create a new tag element
                new_tag_link = soup.new_tag('a')
                new_tag_link['class'] = 'topic-link'
                new_tag_link['data-tag'] = new_tag
                new_tag_link.string = new_tag
                
                # Add the new tag
                topics_section.append(new_tag_link)
                print(f"Added new tag: {new_tag}")
                
                # Update the content with the new tag
                new_content = str(soup)
    
    # Write the updated content back to index.html
    with open(index_path, 'w', encoding='utf-8') as file:
        file.write(new_content)
    
    print(f"Successfully updated index.html with {len(post_files)} posts.")

def main():
    # Step 1: Read template and extract data
    post_data = read_template()
    
    if not post_data:
        print("Skipping HTML generation due to missing or empty values")
        # Still update the index in case there are other changes
        update_index()
        return
    
    # Step 2: Generate HTML file
    filename = generate_html(post_data)
    
    # Step 3: Clear template
    clear_template()
    
    # Step 4: Update index.html, potentially with a new tag
    update_index(new_tag=post_data['tag'])
    
    print("Process completed successfully")

if __name__ == "__main__":
    main()