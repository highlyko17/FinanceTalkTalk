from flask import Blueprint, render_template_string, request
from services.news_service import articles_data, start_news_update_thread
from utils.data_processing import simplify_and_translate

bp = Blueprint('news', __name__)

# 뉴스 업데이트 스레드 시작
start_news_update_thread()

@bp.route('/news')
def news():
    # articles_data에서 뉴스 기사 가져오기
    articles = articles_data[:5]  # 최대 5개의 기사만 가져오기
    
    html_content = '''
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
    '''
    
    if articles:
        for article in articles:
            simplified_content = simplify_and_translate(article['content'])

            html_content += f'''
            <article>
                <h2><a href="{article['url']}" target="_blank">{article['title']}</a></h2>
                <p>{simplified_content}</p>
            </article>
            '''
    else:
        html_content += '<p>현재 표시할 뉴스가 없습니다. 잠시 후 다시 시도해 주세요.</p>'
    
    html_content += '''
        </div>
        <footer>
            <p>&copy; 2024 Financial Info App. All Rights Reserved.</p>
        </footer>
    </body>
    </html>
    '''
    
    return html_content



@bp.route('/preferences', methods=['GET', 'POST'])
def preferences():
    if request.method == 'POST':
        selected_categories = request.form.getlist('categories')
        query = ' OR '.join(selected_categories)

        # articles_data에서 해당 카테고리의 뉴스 기사 필터링
        filtered_articles = [article for article in articles_data if any(category in query for category in selected_categories)]
        articles = filtered_articles[:5]  # 최대 5개의 기사만 가져오기
        
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
            for article in articles:
                simplified_content = simplify_and_translate(article['content'])
                html_content += f'<li><a href="{article["url"]}" target="_blank">{article["title"]}</a><p>{simplified_content}</p></li>'
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
            <h1>Financial News Categories</h1>
            <form action="/preferences" method="POST">
                <label><input type="checkbox" name="categories" value="economy"> Economy</label><br>
                <label><input type="checkbox" name="categories" value="business"> Business</label><br>
                <label><input type="checkbox" name="categories" value="markets"> Markets</label><br>
                <label><input type="checkbox" name="categories" value="technology"> Technology</label><br>
                <label><input type="checkbox" name="categories" value="investment"> Investment</label><br>
                <label><input type="checkbox" name="categories" value="personal-finance"> Personal Finance</label><br>
                <button type="submit">Submit</button>
            </form>
        </div>
        <footer>
            <p>&copy; 2024 Financial Info App. All Rights Reserved.</p>
        </footer>
    </body>
    </html>
    '''

    return html_content
