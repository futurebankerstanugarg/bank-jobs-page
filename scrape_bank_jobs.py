import requests
from bs4 import BeautifulSoup
import re

def scrape_bank_jobs():
    url = "https://www.freejobalert.com/latest-notifications/"
    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        response.raise_for_status()
    except requests.RequestException as e:
        return [{"title": "Error", "link": "#", "date": "N/A", "error": f"Failed to fetch page: {e}"}]

    soup = BeautifulSoup(response.text, 'html.parser')
    notifications = []
    # Adjust selector based on page structure (inspect the page)
    job_listings = soup.find_all('div', class_='entry-content')  # Update if needed

    bank_keywords = [
        'bank', 'sbi', 'idbi', 'indian overseas', 'canara', 'punjab national',
        'bank of', 'ibps', 'rbi', 'nabard', 'clerk', 'po', 'probationary officer',
        'specialist officer', 'lbo', 'jam'
    ]

    for listing in job_listings:
        links = listing.find_all('a')
        for link in links:
            title = link.get_text(strip=True)
            href = link.get('href', '#')
            if title and any(keyword.lower() in title.lower() for keyword in bank_keywords):
                date_elem = link.find_parent().find_next_sibling()  # Adjust as needed
                date = date_elem.get_text(strip=True) if date_elem else "N/A"
                notifications.append({
                    "title": title,
                    "link": href if href.startswith('http') else f"https://www.freejobalert.com{href}",
                    "date": date
                })

    return notifications if notifications else [{"title": "No bank jobs found", "link": "#", "date": "N/A"}]

def generate_html(jobs):
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bank Jobs - FreeJobAlert</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f4f4f4; }
        h1 { text-align: center; color: #333; }
        .container { max-width: 800px; margin: 0 auto; background: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
        .job { margin-bottom: 15px; padding: 10px; border-bottom: 1px solid #ddd; }
        .job a { color: #007bff; text-decoration: none; font-weight: bold; }
        .job a:hover { text-decoration: underline; }
        .job p { margin: 5px 0; color: #555; }
        .error { color: red; font-style: italic; }
    </style>
</head>
<body>
    <h1>Latest Bank Job Notifications</h1>
    <div class="container">
"""
    for job in jobs:
        html_content += f"""
        <div class="job">
            <a href="{job['link']}" target="_blank">{job['title']}</a>
            <p>Date: {job['date']}</p>
"""
        if 'error' in job:
            html_content += f'<p class="error">{job["error"]}</p>'
        html_content += "</div>"

    html_content += """
    </div>
</body>
</html>
"""
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)

if __name__ == "__main__":
    jobs = scrape_bank_jobs()
    generate_html(jobs)
