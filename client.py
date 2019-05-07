from typing import List
import bs4
from bs4 import BeautifulSoup
import requests
from collections import namedtuple
import re


# documentation for beatifulsoup: https://www.crummy.com/software/BeautifulSoup/bs4/doc/

BASE_URL = "https://streeteasy.com"
BEAUTIFUL_SOUP_PARSER = "html.parser"

ApartmentFilter = namedtuple('ApartmentFiler', 
    ['neighborhood', 'min_bedrooms', 'min_bathrooms', 'max_price', 'amenities']
)

valid_amenities = [
    'doorman','elevator','gym','laundry','parking','pool'
]

class StreetEasyClient():
    def __init__(self, apartment_filter: ApartmentFilter) -> None:
        self.apartment_filter = apartment_filter
        for amenity in apartment_filter.amenities:
            assert amenity in valid_amenities, f"Invalid amentity provided, valid amenities are {valid_amenities}"
    
    # returns a list of urls that fit the criteria specified in the filter
    def get_apartments(self) -> List[str]:
        building_urls = self.get_all_buildings_urls()
        return [
            apt_url
            for building_url in building_urls
            for apt_url in self.get_matching_apartments(building_url)
        ]


    def get_matching_apartments(self, building_url: str) -> List[str]:
        soup = self.get_soup(building_url)
        result = []
        apartment_descs = soup.find_all("div", {"class":"ActiveListingsUnit-itemContent"})

        for desc in apartment_descs:
            price = self._parse_price_from_apt_desc(desc)
            
            num_beds, num_baths = 0, 0
            apt_properties =  desc.find_all('span', {'class': 'ActiveListingsUnit-itemProperty'})
            for prop in apt_properties:
                class_name = prop.span['class'][1]
                content = prop.text.strip().lower()
                if "bed" in class_name:
                    num_beds = 0 if content == "studio" else int(list(filter(str.isdigit, content))[0])
                elif "bath" in class_name:
                    num_baths = int(list(filter(str.isdigit, content))[0])
            
            if (price <= self.apartment_filter.max_price and num_beds >= self.apartment_filter.min_bedrooms 
                and num_baths >= self.apartment_filter.min_bathrooms):
                property_url = desc.find("a", {"class": "ActiveListingsUnit-address"})["href"].split('?')[0]
                result.append(property_url)

        return result



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

    
    @staticmethod
    def _parse_price_from_apt_desc(apt_desc: bs4.element.Tag) -> int:
        price = apt_desc.find("div", {"class": "ActiveListingsUnit-itemPrice"})
        price = price.text.strip()
        price = re.search(r'\$.+', price).group(0)
        price = price.strip('$').replace(',','')
        return int(price)

