from client import ApartmentFilter, StreetEasyClient

if __name__ == '__main__':
    apartment_filter = ApartmentFilter('brooklyn', 2, 1, 3000, ['laundry'])
    client = StreetEasyClient(apartment_filter)
    urls = client.get_apartments()
    
    for u in urls:
        print(u)