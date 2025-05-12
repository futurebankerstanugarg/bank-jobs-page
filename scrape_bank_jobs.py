import requests
from bs4 import BeautifulSoup

def scrape_bank_jobs():
    url = "https://www.freejobalert.com/latest-notifications/"
    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        response.raise_for_status()
    except requests.RequestException as e:
        return [{"title": "Error fetching page", "link": "#", "date": "N/A", "error": str(e)}]

    soup = BeautifulSoup(response.text, 'html.parser')
    notifications = []

    # Try multiple possible containers (adjust based on inspection)
    job_container = (
        soup.find('div', class_='latest-notifications') or
        soup.find('div', class_='entry-content') or
        soup.find('div', class_='job-list') or
        soup.find('ul', class_='notifications')
    )
    if not job_container:
        return [{"title": "No job container found", "link": "#", "date": "N/A"}]

    # Find job items (try <li>, <div>, or <tr>)
    job_items = (
        job_container.find_all('li') or
        job_container.find_all('div', class_='job-item') or
        job_container.find_all('tr')
    )
    if not job_items:
        return [{"title": "No job items found", "link": "#", "date": "N/A"}]

    bank_keywords = [
        'sbi', 'idbi', 'indian overseas', 'canara', 'punjab national',
        'bank of', 'ibps', 'rbi', 'nabard', 'clerk', 'po', 'probationary officer',
        'specialist officer', 'lbo', 'jam', 'hdfc', 'icici', 'bank'
    ]

    for item in job_items:
        # Find the link
        link = item.find('a')
        if not link:
            continue
        title = link.get_text(strip=True)
        href = link.get('href', '#')

        # Filter for bank jobs
        if title and any(keyword.lower() in title.lower() for keyword in bank_keywords):
            # Exclude navigation or irrelevant links
            if any(x in title.lower() for x in ['banks', 'jammu and kashmir', 'all india', 'other']) or '#' in href:
                continue
            # Extract date (try multiple possibilities)
            date_elem = (
                item.find('span', class_='date') or
                item.find('td', class_='date') or
                item.find('div', class_='post-date') or
                item.find_next_sibling('span', class_='date')
            )
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
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
        .job a { color: #007bff; text-decoration: none; font-weight: bold; }
        .job a:hover { text-decoration: underline; }
        .error { color: red; font-style: italic; }
    </style>
</head>
<body>
    <h1>Latest Bank Job Notifications</h1>
    <div class="container">
        <table>
            <tr><th>Job Title</th><th>Date</th></tr>
"""
    for job in jobs:
        html_content += f"""
            <tr class="job">
                <td><a href="{job['link']}" target="_blank">{job['title']}</a></td>
                <td>{job['date']}</td>
            </tr>
"""
        if 'error' in job:
            html_content += f'<tr><td colspan="2" class="error">{job["error"]}</td></tr>'

    html_content += """
        </table>
    </div>
</body>
</html>
"""
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)

if __name__ == "__main__":
    jobs = scrape_bank_jobs()
    generate_html(jobs)
