from flask import Blueprint, render_template_string, request
from services.news_service import articles_data
from api.news_api import fetch_financial_news
from config import NEWS_API_KEY, CATEGORIES
from utils.data_processing import simplify_and_translate, explain_term, extract_terms, summarize_text

bp = Blueprint('news', __name__)

@bp.route('/news')
def news():
    # Fetching real-time financial news
    news_data = fetch_financial_news('financial')
    articles = news_data.get('articles', [])

    # Prepare articles with explanations and summaries
    processed_articles = []
    for article in articles:
        title = article.get('title', 'No Title')
        url = article.get('url', '#')
        content = article.get('content', '')

        # Extract and explain terms
        terms = extract_terms(content)
        term_explanations = {term: explain_term(term) for term in terms}
        
        # Simplify and translate content
        simplified_content = simplify_and_translate(content)
        
        # Summarize content
        summary = summarize_text(content)

        processed_articles.append({
            'title': title,
            'url': url,
            'summary': summary,
            'simplified_content': simplified_content,
            'term_explanations': term_explanations
        })

    template = '''
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>금융 뉴스</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background-color: #f4f4f4;
                margin: 0;
                padding: 0;
            }
            header {
                background-color: #333;
                color: white;
                padding: 10px 0;
                text-align: center;
            }
            nav {
                margin: 10px;
                text-align: center;
            }
            nav a {
                margin: 0 15px;
                text-decoration: none;
                color: #333;
                font-weight: bold;
            }
            nav a:hover {
                color: #0066cc;
            }
            footer {
                background-color: #333;
                color: white;
                text-align: center;
                padding: 10px 0;
                position: fixed;
                bottom: 0;
                width: 100%;
            }
            .container {
                max-width: 1200px;
                margin: 20px auto;
                padding: 20px;
                background-color: white;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            }
            h1 {
                color: #333;
                text-align: center;
                margin-bottom: 20px;
            }
            article {
                border-bottom: 1px solid #ddd;
                padding-bottom: 20px;
                margin-bottom: 20px;
            }
            h2 {
                color: #0066cc;
                margin: 0;
                font-size: 18px;
            }
            a {
                color: #0066cc;
                text-decoration: none;
            }
            a:hover {
                text-decoration: underline;
            }
            p {
                margin: 10px 0;
            }
            .summary {
                font-style: italic;
                color: #666;
            }
            .terms {
                margin-top: 10px;
                padding-top: 10px;
                border-top: 1px solid #ddd;
            }
            .term {
                margin-bottom: 10px;
            }
        </style>
        </head>
        <body>
            <header>
                <h2>FinanceTalkTalk</h2>
            </header>
            <nav>
                <a href="/">Home</a>
                <a href="/search">Public Filings</a>
                <a href="/stock">Stock Exchange Decisions</a>
                <a href="/preferences">Preferences</a>
                <a href="/financial-indicators">Financial Indicators</a>
                <a href="/financial-statements">Financial Statements</a>
                <a href="/news">News</a>
            </nav>
            <div class="container">
                <h1>Financial News</h1>
                {% for article in articles %}
                    <article>
                        <h2><a href="{{ article.url }}" target="_blank">{{ article.title }}</a></h2>
                        <p><strong>Summary:</strong> <span class="summary">{{ article.summary }}</span></p>
                        <p><strong>Simplified Content:</strong> {{ article.simplified_content }}</p>
                        <div class="terms">
                            <h3>Financial Terms Explained</h3>
                            {% for term, explanation in article.term_explanations.items() %}
                                <div class="term">
                                    <strong>{{ term }}:</strong> {{ explanation }}
                                </div>
                            {% endfor %}
                        </div>
                    </article>
                {% endfor %}
            </div>
            <footer>
                <p>&copy; 2024 Financial Info App. All Rights Reserved.</p>
            </footer>
        </body>
    </html>
    '''
    
    return render_template_string(template, articles=processed_articles)


@bp.route('/preferences', methods=['GET', 'POST'])
def preferences():
    if request.method == 'POST':
        selected_categories = request.form.getlist('categories')
        query = ' OR '.join(selected_categories)
        news_data = fetch_financial_news(query)
        articles = news_data.get('articles', [])
        
        html_content = '''
        <!DOCTYPE html>
        <html lang="ko">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Financial Preferences</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    background-color: #f4f4f4;
                    margin: 0;
                    padding: 0;
                }
                header {
                    background-color: #333;
                    color: white;
                    padding: 10px 0;
                    text-align: center;
                }
                nav {
                    margin: 10px;
                    text-align: center;
                }
                nav a {
                    margin: 0 15px;
                    text-decoration: none;
                    color: #333;
                    font-weight: bold;
                }
                footer {
                    background-color: #333;
                    color: white;
                    text-align: center;
                    padding: 10px 0;
                    position: fixed;
                    bottom: 0;
                    width: 100%;
                }
                .container {
                    max-width: 1200px;
                    margin: 20px auto;
                    padding: 20px;
                    background-color: white;
                    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                }
                h1 {
                    color: #333;
                    text-align: center;
                }
                ul {
                    list-style-type: none;
                    padding: 0;
                }
                li {
                    margin: 10px 0;
                }
                li a {
                    text-decoration: none;
                    color: #0066cc;
                }
                li a:hover {
                    text-decoration: underline;
                }
            </style>
        </head>
        <body>
            <header>
                <h2>FinanceTalkTalk</h2>
            </header>
            <nav>
                <a href="/">Home</a>
                <a href="/search">Public Filings</a>
                <a href="/stock">Stock Exchange Decisions</a>
                <a href="/preferences">Preferences</a>
                <a href="/financial-indicators">Financial Indicators</a>
                <a href="/financial-statements">Financial Statements</a>
                <a href="/news">News</a>
            </nav>
            <div class="container">
                <h1>Selected News Articles</h1>'''

        if articles:
            html_content += '<ul>'
            for article in articles[:10]:  # Limit to 10 articles
                html_content += f'<li><a href="{article["url"]}">{article["title"]}</a></li>'
            html_content += '</ul>'
        else:
            html_content += '<p>No news articles found.</p>'

        html_content += '''
            </div>
            <footer>
                <p>&copy; 2024 Financial Info App. All Rights Reserved.</p>
            </footer>
        </body>
        </html>
        '''
        return html_content

    html_content = '''
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Financial Preferences</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background-color: #f4f4f4;
                margin: 0;
                padding: 0;
            }
            header {
                background-color: #333;
                color: white;
                padding: 10px 0;
                text-align: center;
            }
            nav {
                margin: 10px;
                text-align: center;
            }
            nav a {
                margin: 0 15px;
                text-decoration: none;
                color: #333;
                font-weight: bold;
            }
            footer {
                background-color: #333;
                color: white;
                text-align: center;
                padding: 10px 0;
                position: fixed;
                bottom: 0;
                width: 100%;
            }
            .container {
                max-width: 1200px;
                margin: 20px auto;
                padding: 20px;
                background-color: white;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            }
            h1 {
                color: #333;
                text-align: center;
            }
        </style>
    </head>
    <body>
        <header>
            <h2>FinanceTalkTalk</h2>
        </header>
        <nav>
            <a href="/">Home</a>
            <a href="/search">Public Filings</a>
            <a href="/stock">Stock Exchange Decisions</a>
            <a href="/preferences">Preferences</a>
            <a href="/financial-indicators">Financial Indicators</a>
            <a href="/financial-statements">Financial Statements</a>
            <a href="/news">News</a>
        </nav>
        <div class="container">
            <h1>Select Your Financial Interests</h1>
            <form method="post">'''
    
    for category in CATEGORIES:
        html_content += f'<input type="checkbox" name="categories" value="{category}">{category}<br><br>'
    
    html_content += '''
            <input type="submit" value="Submit">
            </form>
        </div>
        <footer>
            <p>&copy; 2024 Financial Info App. All Rights Reserved.</p>
        </footer>
    </body>
    </html>
    '''
    
    return html_content