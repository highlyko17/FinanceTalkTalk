import matplotlib
matplotlib.use('Agg')

import requests
import openai
import zipfile
import io
import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
import pandas as pd
from flask import Flask, render_template, request
import base64
import numpy as np
from matplotlib import font_manager, rc

rc('font', family='AppleGothic')
plt.rcParams['axes.unicode_minus'] = False

# Flask 애플리케이션 생성
app = Flask(__name__)

# API 인증키 설정
dart_api_key = '0e5ab0c2d0153186cb4aa21520923ad730404cd8'
openai.api_key = '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'
NEWS_API_KEY = '1ccc7972e0d9465fa31a5eaf02ee236e'
NEWS_API_URL = 'https://newsapi.org/v2/everything'

# 사용자 맞춤형 키워드
categories = [
    'finance', 'stock', 'market', 'investment', 'economy',
    'crypto', 'bonds', 'commodities', 'real estate', 'personal finance'
]

def call_open_dart_api_json(corp_code=None, bgn_de=None, end_de=None, last_reprt_at=None, pblntf_ty=None,
                            pblntf_detail_ty=None, corp_cls=None, sort='date', sort_mth='desc',
                            page_no='1', page_count='10'):
    url = 'https://opendart.fss.or.kr/api/list.json'
    params = {
        'crtfc_key': dart_api_key,
        'corp_code': corp_code,
        'bgn_de': bgn_de,
        'end_de': end_de,
        'last_reprt_at': last_reprt_at,
        'pblntf_ty': pblntf_ty,
        'pblntf_detail_ty': pblntf_detail_ty,
        'corp_cls': corp_cls,
        'sort': sort,
        'sort_mth': sort_mth,
        'page_no': page_no,
        'page_count': page_count
    }
    params = {key: value for key, value in params.items() if value is not None}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None

def simplify_and_translate(text):
    def split_text(text, max_tokens=3000):
        # 대략적인 단어 수를 기반으로 텍스트를 나누는 간단한 방법
        words = text.split()
        chunks = [words[i:i + max_tokens] for i in range(0, len(words), max_tokens)]
        return [' '.join(chunk) for chunk in chunks]

    prompts = split_text(text)
    simplified_texts = []
    for prompt in prompts:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that simplifies complex financial contents."},
                {"role": "user", "content": f"다음 내용을 금융 지식이 적은 사람도 이해할 수 있게 간단하게 설명해주세요:\n\n{prompt}\n\n설명은 쉬운 용어를 사용하고, 전문 용어는 풀어서 설명해주세요."}
            ]
        )
        simplified_texts.append(response.choices[0].message['content'].strip())
    
    return ' '.join(simplified_texts)


@app.route('/')
def index():
    html_content = '''
    <h1>Welcome to the Financial Info App</h1>
    <ul>
        <li><a href="/search">Search for Public Filings</a></li>
        <li><a href="/stock">Stock Exchange Decisions</a></li>
        <li><a href="/preferences">Set Your Preferences</a></li>
        <li><a href="/financial-indicators">View Financial Indicators</a></li>
        <li><a href="/financial-statements">View Financial Statements</a></li>
    </ul>
    '''
    return html_content

@app.route('/search')
def search():
    result = call_open_dart_api_json(
        sort='date',
        sort_mth='desc',
        page_no='1',
        page_count='10'
    )
    simplified_items = []
    if result:
        items = result.get('list', [])
        for item in items:
            detailed_info = f"""
            공시 제목: {item.get('title')}
            공시 날짜: {item.get('rcept_dt')}
            공시 유형: {item.get('pblntf_ty')}
            공시 상세 유형: {item.get('pblntf_detail_ty')}
            회사명: {item.get('corp_name')}
            """
            simplified_text = simplify_and_translate(detailed_info)
            simplified_items.append(simplified_text)
    
    html_content = '<h1>Public Filings</h1>'
    if simplified_items:
        html_content += '<ul>'
        for item in simplified_items:
            html_content += f'<li>{item}</li>'
        html_content += '</ul>'
    else:
        html_content += '<p>No data found or error occurred.</p>'
    
    return html_content

@app.route('/stock', methods=['GET', 'POST'])
def stock():
    if request.method == 'POST':
        corp_name = request.form['corp_name']
        corp_code = get_corp_code(corp_name)
        if corp_code:
            bgn_de = request.form['bgn_de']
            end_de = request.form['end_de']
            result = call_open_dart_api_json(corp_code, bgn_de, end_de)
            simplified_items = []
            if result:
                list_items = result.get('list', [])
                for item in list_items:
                    detailed_info = f"""
                    회사명: {item.get('corp_name')}
                    결정일: {item.get('bddd')}
                    평가 기간: {item.get('exevl_pd')}
                    주식 교환 비율: {item.get('extr_rt')}
                    비율 기준: {item.get('extr_rt_bs')}
                    평가 의견: {item.get('exevl_op')}
                    주식 교환 이유: {item.get('extr_pp')}
                    """
                    simplified_text = simplify_and_translate(detailed_info)
                    simplified_items.append(simplified_text)
            
            html_content = f'<h1>Stock Exchange Decisions for {corp_name}</h1>'
            if simplified_items:
                html_content += '<ul>'
                for item in simplified_items:
                    html_content += f'<li>{item}</li>'
                html_content += '</ul>'
            else:
                html_content += '<p>No data found or error occurred.</p>'
            return html_content
        else:
            return f"<h1>Company name '{corp_name}' not found.</h1>", 404

    html_content = '''
    <h1>Stock Exchange Decisions</h1>
    <form method="post">
        <label for="corp_name">Company Name:</label>
        <input type="text" id="corp_name" name="corp_name" required>
        <br>
        <label for="bgn_de">Start Date (YYYYMMDD):</label>
        <input type="text" id="bgn_de" name="bgn_de" required>
        <br>
        <label for="end_de">End Date (YYYYMMDD):</label>
        <input type="text" id="end_de" name="end_de" required>
        <br>
        <input type="submit" value="Submit">
    </form>
    '''
    return html_content

@app.route('/preferences', methods=['GET', 'POST'])
def preferences():
    if request.method == 'POST':
        selected_categories = request.form.getlist('categories')
        query = ' OR '.join(selected_categories)
        news_data = fetch_financial_news(query, NEWS_API_KEY)
        articles = news_data.get('articles', [])
        
        html_content = '<h1>Selected News Articles</h1>'
        if articles:
            html_content += '<ul>'
            for article in articles[:10]:  # Limit to 10 articles
                html_content += f'<li><a href="{article["url"]}">{article["title"]}</a></li>'
            html_content += '</ul>'
        else:
            html_content += '<p>No news articles found.</p>'
        
        return html_content
    
    html_content = '<h1>Select Your Financial Interests</h1>'
    html_content += '<form method="post">'
    for category in categories:
        html_content += f'<input type="checkbox" name="categories" value="{category}">{category}<br>'
    html_content += '<input type="submit" value="Submit">'
    html_content += '</form>'
    return html_content

@app.route('/financial-indicators', methods=['GET', 'POST'])
def financial_indicators():
    if request.method == 'POST':
            corp_names = request.form.get('corp_names').split(', ')
            bsns_year = request.form.get('bsns_year')
            report_option = request.form.get('report_option')
            idx_option = request.form.get('idx_option')

            report_code = {
                '1': '11013',
                '2': '11012',
                '3': '11014',
                '4': '11011'
            }.get(report_option)

            idx_code = {
                '1': 'M210000',
                '2': 'M220000',
                '3': 'M230000',
                '4': 'M240000'
            }.get(idx_option)

            if not report_code or not idx_code:
                return "잘못된 입력입니다."

            financial_data = []
            for name in corp_names:
                corp_code = get_corp_code(name)
                if corp_code:
                    company_data = get_financial_data(corp_code, bsns_year, report_code, idx_code)
                    for item in company_data:
                        financial_data.append((item[0], item[1], name))
                else:
                    return f"{name}의 고유번호를 찾을 수 없습니다."

            img_base64 = plot_financial_data(financial_data)
            return render_template('index.html', img_base64=img_base64)
    return render_template('index.html')

    html_content = '''
    <h1>View Financial Indicators</h1>
    <form method="post">
        <label for="corp_name">Company Name:</label>
        <input type="text" id="corp_name" name="corp_name" required>
        <br>
        <label for="bsns_year">Business Year (YYYY):</label>
        <input type="text" id="bsns_year" name="bsns_year" required>
        <br>
        <label for="report_option">Report Type:</label>
        <select id="report_option" name="report_option" required>
            <option value="1">1분기보고서</option>
            <option value="2">반기보고서</option>
            <option value="3">3분기보고서</option>
            <option value="4">사업보고서</option>
        </select>
        <br>
        <label for="idx_option">Indicator Category:</label>
        <select id="idx_option" name="idx_option" required>
            <option value="1">수익성지표</option>
            <option value="2">안정성지표</option>
            <option value="3">성장성지표</option>
            <option value="4">활동성지표</option>
        </select>
        <br>
        <input type="submit" value="Submit">
    </form>
    '''
    return html_content

@app.route('/financial-statements', methods=['GET', 'POST'])
def financial_statements():
    if request.method == 'POST':
        corp_name = request.form['corp_name']
        bsns_year = request.form['bsns_year']
        reprt_choice = request.form['reprt_choice']
        fs_choice = request.form['fs_choice']

        reprt_codes = {
            '1': '11013',
            '2': '11012',
            '3': '11014',
            '4': '11011'
        }
        fs_divisions = {
            '1': 'OFS',
            '2': 'CFS'
        }
        reprt_code = reprt_codes.get(reprt_choice, '11011')
        fs_div = fs_divisions.get(fs_choice, 'OFS')

        corp_code = get_corp_code(corp_name)
        if not corp_code:
            return f"<h1>Company name '{corp_name}' not found.</h1>", 404

        financial_data = get_financial_statement(dart_api_key, corp_code, bsns_year, reprt_code, fs_div)
        if financial_data:
            simplified_data = simplify_and_translate(str(financial_data))
            html_content = f'<h1>Financial Statements for {corp_name} ({bsns_year})</h1>'
            html_content += '<pre>' + simplified_data + '</pre>'
            return html_content
        else:
            return '<h1>No financial data found or error occurred.</h1>', 404

    html_content = '''
    <h1>View Financial Statements</h1>
    <form method="post">
        <label for="corp_name">Company Name:</label>
        <input type="text" id="corp_name" name="corp_name" required>
        <br>
        <label for="bsns_year">Business Year (YYYY):</label>
        <input type="text" id="bsns_year" name="bsns_year" required>
        <br>
        <label for="reprt_choice">Report Type:</label>
        <select id="reprt_choice" name="reprt_choice" required>
            <option value="1">1분기보고서</option>
            <option value="2">반기보고서</option>
            <option value="3">3분기보고서</option>
            <option value="4">사업보고서</option>
        </select>
        <br>
        <label for="fs_choice">Financial Statement Type:</label>
        <select id="fs_choice" name="fs_choice" required>
            <option value="1">개별재무제표 (OFS)</option>
            <option value="2">연결재무제표 (CFS)</option>
        </select>
        <br>
        <input type="submit" value="Submit">
    </form>
    '''
    return html_content

def fetch_financial_news(query, api_key):
    params = {
        'q': query,
        'apiKey': api_key,
        'language': 'en',
        'sortBy': 'relevancy',
    }
    response = requests.get(NEWS_API_URL, params=params)
    return response.json()

def get_corp_code(corp_name):
    url = 'https://opendart.fss.or.kr/api/corpCode.xml'
    params = {'crtfc_key': dart_api_key}
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        with zipfile.ZipFile(io.BytesIO(response.content)) as zip_file:
            xml_filename = zip_file.namelist()[0]
            with zip_file.open(xml_filename) as xml_file:
                tree = ET.parse(xml_file)
                root = tree.getroot()
                for corp in root.findall('list'):
                    name = corp.find('corp_name').text
                    corp_code = corp.find('corp_code').text
                    if name == corp_name:
                        return corp_code
        return None
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None

def get_financial_statement(crtfc_key, corp_code, bsns_year, reprt_code, fs_div):
    url = 'https://opendart.fss.or.kr/api/fnlttSinglAcntAll.json'
    params = {
        'crtfc_key': crtfc_key,
        'corp_code': corp_code,
        'bsns_year': bsns_year,
        'reprt_code': reprt_code,
        'fs_div': fs_div
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        return None

def get_financial_data(corp_code, bsns_year, reprt_code, idx_cl_code):
    url = 'https://opendart.fss.or.kr/api/fnlttCmpnyIndx.json'
    params = {
        'crtfc_key': dart_api_key,
        'corp_code': corp_code,
        'bsns_year': bsns_year,
        'reprt_code': reprt_code,
        'idx_cl_code': idx_cl_code
    }

    response = requests.get(url, params=params)
    data = response.json()

    if data['status'] == '013':
        print(f"Error: {data['message']}")
        return []
    else:
        if 'list' in data:
            return [(item.get('idx_nm', '지표명 없음'), item.get('idx_val', '지표값 없음')) for item in data['list']]
        else:
            return []
        
def plot_financial_data(financial_data):
    df = pd.DataFrame(financial_data, columns=['지표명', '지표값', '회사'])
    df['지표값'] = pd.to_numeric(df['지표값'], errors='coerce')
    df = df.dropna()

    plt.figure(figsize=(14, 8))

    unique_metrics = df['지표명'].unique()
    bar_width = 0.2
    index = np.arange(len(unique_metrics))

    for i, company in enumerate(df['회사'].unique()):
        company_data = df[df['회사'] == company]

        # Ensure that the length of x and y values match
        x_values = index[:len(company_data)]  # Match the length of the company_data
        y_values = company_data['지표값'].values

        plt.bar(x_values + i * bar_width, y_values, bar_width, label=company)

    plt.ylabel('지표값')
    plt.xlabel('지표명')
    plt.title('다중 회사 재무 지표 시각화')
    plt.xticks(index + bar_width, unique_metrics)
    plt.legend()
    plt.grid(axis='y')

    # 이미지 저장
    img = io.BytesIO()
    plt.savefig(img, format='png')
    plt.close()
    img.seek(0)
    
    # Base64 인코딩
    img_base64 = base64.b64encode(img.getvalue()).decode('utf-8')
    
    return img_base64

if __name__ == '__main__':
    app.run(debug=True)
