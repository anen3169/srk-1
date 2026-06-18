from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
import re

app = Flask(__name__)

def url_mi(sorgu):
    return re.match(r'^https?://', sorgu) is not None

def site_cek(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 YS-Browser/1.0'}
        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()
        r.encoding = r.apparent_encoding
        soup = BeautifulSoup(r.text, 'html.parser')
        
        title = soup.title.string.strip() if soup.title else url
        
        meta = soup.find('meta', attrs={'name': 'description'})
        desc = meta['content'].strip() if meta and meta.get('content') else 'Açıklama yok'
        
        results = []
        results.append({'url': url, 'title': title, 'desc': desc[:200]})
        
        for a in soup.find_all('a', href=True)[:10]:
            link = a['href']
            if link.startswith('http'):
                text = a.get_text(strip=True)
                if text and 10 < len(text) < 100:
                    results.append({
                        'url': link,
                        'title': text,
                        'desc': ''  # Kaynağı yazmıyorum artık
                    })
        return results, None
    except Exception as e:
        return None, f"Site çekilemedi: {str(e)}"

@app.route('/', methods=['GET'])
def index():
    query = request.args.get('q', '').strip()
    results = []
    error = None
    
    if query:
        if url_mi(query):
            results, error = site_cek(query)
        else:
            error = "Lütfen https:// ile başlayan tam URL gir"
    
    return render_template('index.html', query=query, results=results, error=error)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)