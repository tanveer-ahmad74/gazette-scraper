import csv
import requests
from bs4 import BeautifulSoup


def get_detail_data(link, headers):
    try:
        response_detail_page = requests.get(link, headers=headers)
        soup_detail_page = BeautifulSoup(response_detail_page.content, 'html.parser')
        category_types = soup_detail_page.find_all('dd')[1].text
        brief_description = soup_detail_page.find('div', class_='full-notice').get_text(strip=True)
        return category_types, brief_description
    except Exception as e:
        return '', ''


def scrape_gazette_data(url, headers, output_csv='assessment.csv', num_results=15):
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    all_divs = soup.find_all('div', class_='feed-item')[:num_results]

    column_names = ['notice_text', 'publish_date', 'address_of_deceased', 'claim_deadline_date', 'notice_types',
                    'brief_description', 'category_types']

    with open(output_csv, 'a', newline='', encoding='utf-8') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(column_names)

        for div in all_divs:
            publication_date = div.find('time').text
            notice_text = div.find('h3').text            # extract notice text
            deceased, claim_deadline_date, notice_type = '', '', ''

            notice_detail_col = div.find_all('dt')[1:]
            for detail in notice_detail_col:
                if detail.text == 'Address of Deceased':
                    deceased = detail.find_next('dd').text
                elif detail.text == 'Date of Claim Deadline':
                    claim_deadline_date = detail.find_next('dd').text
                elif detail.text == 'Notice Type':
                    notice_type = detail.find_next('dd').text

            href = div.find('a').get('href')
            link = f'https://www.thegazette.co.uk{href}'   # navigate to detail page for extract further relevant detail
            category_types, brief_description = get_detail_data(link, headers)

            csv_writer.writerow([notice_text, publication_date, deceased, claim_deadline_date, notice_type,
                                 brief_description, category_types])


if __name__ == "__main__":
    url = 'https://www.thegazette.co.uk/all-notices/notice?text=&categorycode-all=all&noticetypes=&location-postcode-1=&location-distance-1=1&location-local-authority-1=&numberOfLocationSearches=1&start-publish-date=&end-publish-date=&edition=&london-issue=&edinburgh-issue=&belfast-issue=&sort-by=&results-page-size=15'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    scrape_gazette_data(url, headers)
