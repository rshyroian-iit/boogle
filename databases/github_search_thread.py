import requests
import base64

def get_github_repositories(query, limit=5):
    url = 'https://api.github.com/search/repositories'
    headers = {
        'Accept': 'application/vnd.github.v3+json'
    }
    params = {
        'q': query,
        'sort': 'stars',
        'order': 'desc',
        'per_page': limit
    }

    response = requests.get(url, headers=headers, params=params)
    results = response.json()

    formatted_results = []
    for item in results['items']:
        readme = get_readme(item['full_name'])
        content = f"Name: {item['name']}\nDescription: {item['description']}\nReadme: {readme}"
        formatted_results.append({
            'content': content,
            'url': item['html_url'],
        })

    return formatted_results

def get_readme(repo):
    url = f'https://api.github.com/repos/{repo}/readme'
    headers = {
        'Accept': 'application/vnd.github.v3+json'
    }

    response = requests.get(url, headers=headers)
    result = response.json()

    if 'content' in result:
        # README content is base64-encoded
        return base64.b64decode(result['content']).decode()
    else:
        return 'No README found'

print(get_github_repositories('syllabus scraper', limit=2))
