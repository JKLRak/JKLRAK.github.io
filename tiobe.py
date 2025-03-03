import requests
import wikipedia
from bs4 import BeautifulSoup
import os
from googlesearch import search

# Definiujemy 2 alternatywne metody znalezienia wikipedi
# Wydaje się lepsza pierwsza
def get_wikipedia_summary(language):
    query = f"{language} (programming language) wikipedia.com"
    summary = f"Could not retrieve information for {language}."

    try:
        # Search Google for the query and get the first result
        search_results = search(query, num=1, stop=1, pause=2)
        wikipedia_url = next(search_results)
        summary = wikipedia.summary(search_results)
    except Exception as e:
        print(f"Error retrieving information for {language}: {e}")

    return summary
def get_wikipedia_summary_2(language):
    try:
        result = wikipedia.search(language + "(programming language)")[0]
        print(language + " (programming language)")
        summary = wikipedia.summary(result)
    except Exception as e:
        summary = f"Could not retrieve information for {language}."
    return summary

# Pobieramy stronę tiobe
url = "https://www.tiobe.com/tiobe-index/"
response = requests.get(url)
soup = BeautifulSoup(response.content, "html.parser")

# Folder docs i pod folder images
output_dir = "docs"
os.makedirs(output_dir, exist_ok=True)
images_dir = os.path.join(output_dir, "images")
os.makedirs(images_dir, exist_ok=True)

# Prepare a list for languages and additional information
languages_data = []

# Znajdujemy td-top20
top20_cells = soup.find_all("td", class_="td-top20")

for cell in top20_cells:
    image = cell.find("img")
    
    if image and "src" in image.attrs:
        img_url = image["src"]
        language = image["alt"].replace(" page", "")
        img_name = language.replace("/", "_").replace(" ","_") + ".png"

        # Ewentualnie dodajemy www.tiobe.com
        if img_url.startswith("/"):
            img_url = "https://www.tiobe.com" + img_url

        # Pobieramy
        img_response = requests.get(img_url)
        if img_response.status_code == 200:
            img_path = os.path.join(images_dir, img_name)
            with open(img_path, "wb") as f:
                f.write(img_response.content)
            print(f"Downloaded: {img_name}")
        else:
            print(f"Failed to download {img_url}")

        # Tutaj actually dostajemy summary
        summary = get_wikipedia_summary(language)

        # Dodajemy
        languages_data.append({
            'name': language,
            'image': img_path,
            'summary': summary,
        })

        # Dodajemy do docs .md
        language_md_content = f"# {language}\n\n"
        language_md_content += f"![{language}](images/{img_name})\n\n"
        language_md_content += f"## Description:\n{summary}\n\n"

        language_md_filename = language.replace("/", "_").replace(" ", "_").lower() + ".md"
        language_md_path = os.path.join(output_dir, language_md_filename)

        with open(language_md_path, "w") as file:
            file.write(language_md_content)

        print(f"Generated Markdown file: {language_md_filename}")

# Generate main index.md file with links to individual language pages
markdown_content = "# Top 20 Programming Languages according to Tiobe\n\n"
markdown_content += "## List of Languages\n\n"

position = 1
for data in languages_data:
    language_md_filename = data['name'].replace("/", "_").replace(" ", "_").lower() + ".md"
    markdown_content += f"- {position}: [{data['name']}]({language_md_filename})\n"
    position += 1

# Save the main index.md file
index_md_path = os.path.join(output_dir, "index.md")
with open(index_md_path, "w") as file:
    file.write(markdown_content)

print("Main Markdown file 'index.md' generated successfully!")
