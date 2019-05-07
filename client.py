from typing import List
from bs4 import BeautifulSoup
import requests
from collections import namedtuple


# documentation for beatifulsoup: https://www.crummy.com/software/BeautifulSoup/bs4/doc/

BASE_URL = "https://streeteasy.com"
BEAUTIFUL_SOUP_PARSER = "html.parser"

ApartmentFilter = namedtuple('ApartmentFiler', 
    ['neighborhood', 'min_bedrooms', 'min_bathrooms', 'max_price', 'amenities']
)

valid_neighborhoods = [
    'manhattan', 'brooklyn', 'queens'
]

class StreetEasyClient():
    def __init__(self, apartment_filter: ApartmentFilter) -> None:
        assert apartment_filter.neighborhood in valid_neighborhoods
        self.apartment_filter = apartment_filter
    
    # returns a list of urls that fit the criteria specified in the filter
    def get_apartments(self) -> List[str]:
        building_urls = self.get_all_buildings_urls()
        return building_urls

    def get_all_buildings_urls(self) -> List[str]:
        result = []
        soup = self.get_initial_buildings_soup()
        result.extend(self.get_building_urls_in_page(soup))

        # get how many pages that need to be processed
        pages = soup.find_all("span", {"class": "page"})

        if not pages:
            return result
        
        num_pages = int(pages[-1].get_text().strip())

        for i in range(2,num_pages+1):
            url = self.get_buildings_page_url(i)
            soup = self.get_soup(url)
            result.extend(self.get_building_urls_in_page(soup))
        
        return result
        
    def get_building_urls_in_page(self, soup: BeautifulSoup) -> List[str]:
        building_items = soup.find_all("li", {"class": "item building"})
        return [
            BASE_URL + f.find_all('h3', {'class': 'details-title'})[0].find_all('a')[0].get('href')
            for f in building_items
        ]

    def get_initial_buildings_soup(self) -> BeautifulSoup:
        url = self.get_first_buildings_page_url()

        # make two calls because initially the request is rejected becayse
        # street easy has robot detection
        r = requests.get(url)
        r = requests.get(url)
        r.raise_for_status()

        return BeautifulSoup(r.content, BEAUTIFUL_SOUP_PARSER)
    
    def get_soup(self, url: str) -> BeautifulSoup:
        r = requests.get(url)
        r.raise_for_status()
        return BeautifulSoup(r.content, BEAUTIFUL_SOUP_PARSER)


    def get_first_buildings_page_url(self) -> str:
        url = f"{BASE_URL}/rental-buildings/{self.apartment_filter.neighborhood}"
        if self.apartment_filter.amenities:
            url += f"/building_amenities:{','.join(self.apartment_filter.amenities)}"
        url += "?refined_search=true"
        return url
    
    def get_buildings_page_url(self, page_number: int) -> str:
        url = f"{BASE_URL}/rental-buildings/{self.apartment_filter.neighborhood}"
        if self.apartment_filter.amenities:
            url += f"/building_amenities:{','.join(self.apartment_filter.amenities)}"
        url += f"?page={page_number}&amp;refined_search=true"
        return url
