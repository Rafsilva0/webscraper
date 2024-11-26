import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

#Defining Variables
SCRAPING_URL= 'https://www.xcaret.com/es/preguntas-frecuentes/' #insert your URL to be scraped here
BOT_HANDLE= 'xcaretgenerative' #this is your bot handle
KNOWLEDGE_API_TOKEN= 'ae13cba4f874cc31e9f4af8ac74982cc' #this is the token from your bot
QUESTION_TYPE = 'h3'
QUESTION_CLASS= 'font-semibold text-base5' #this is the identifier for questions on the site
ANSWER_TYPE = 'div'
ANSWER_CLASS= 'font-thin text-grey text-base' #this is the identifier for answers on the site
KNOWLEDGE_SOURCE_NAME = 'Test1'

def get_existing_knowledge_source_id(api_url, headers, source_name):
    response = requests.get(api_url + '/sources', headers=headers)
    if response.status_code == 200:
        sources = response.json().get('data', [])
        for source in sources:
            if source.get('name') == source_name:
                return source.get('id')
    return None

# Function to extract FAQs from URL
def extract_faqs_from_url(url, knowledge_source_id):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Finding each FAQ item
    faq_questions = soup.find_all(QUESTION_TYPE, class_= QUESTION_CLASS) #you need to find the html format of the questions. if it's a div, change the first section to div for example and then include the class
    faq_answers = soup.find_all(ANSWER_TYPE, class_= ANSWER_CLASS) #same as above, but for the
    
    articles = []
    for i, (question, answer) in enumerate(zip(faq_questions, faq_answers)):
        question_text = question.get_text(strip=True)
        answer_text = answer.get_text(separator=' ', strip=True)

        article = {
            "id": f"faq_{i}",
            "name": question_text,
            "content": answer_text,
            "url": url,
            "knowledge_source_id": f"{knowledge_source_id}",
            "language": "en",
            "external_created": datetime.now().isoformat(),
            "external_updated": datetime.now().isoformat(),
            "enabled": True,
            "metadata": {}
        }
        articles.append(article)
    
    return articles

# Function to create a knowledge source
def create_knowledge_source(api_url, headers, name):
    data = {"name": name}
    response = requests.post(api_url + '/sources', headers=headers, json=data)
    if response.status_code == 201:
        return response.json()['data']['id']
    else:
        raise Exception(f"Failed to create knowledge source: {response.text}")

# Function to upload an article
def upload_articles(api_url, headers, articles):
    try:
        response = requests.post(api_url + '/articles', headers=headers, json={"articles": articles})
        if response.status_code != 200:
            raise Exception(f"Failed to upload articles: {response.text}")
        return response.json()  # Assuming the API returns a JSON response on successful upload
    except Exception as e:
        print(f"An error occurred while uploading articles: {e}")
        raise

# Main script
api_url = f'https://{BOT_HANDLE}.ada.support/api/knowledge/v1'
headers = {
    'Authorization': f'Bearer {KNOWLEDGE_API_TOKEN}',  # Replace with your actual access token
    # Add other necessary headers
}

# Get the Knowledge Source ID
knowledge_source_id = get_existing_knowledge_source_id(api_url, headers, KNOWLEDGE_SOURCE_NAME)

if not knowledge_source_id:
    knowledge_source_id = create_knowledge_source(api_url, headers, KNOWLEDGE_SOURCE_NAME)

# Scrape FAQs
url = SCRAPING_URL
faqs = extract_faqs_from_url(SCRAPING_URL, knowledge_source_id)

upload_response = upload_articles(api_url, headers, faqs)
print(upload_response)
