from client import ApartmentFilter, StreetEasyClient
from argparse import ArgumentParser


def parse_arguments():
    parser = ArgumentParser()
    parser.add_argument("--neighborhood", required=True, help="Neighborhood to search in")
    parser.add_argument("--min-bedrooms", required=True, type=int, help="Minimum number of bedrooms")
    parser.add_argument("--min-bathrooms", required=True, type=int, help="Minimum number of bathrooms")
    parser.add_argument("--max-price", required=False, type=int, help="Max price of the apartment")
    parser.add_argument("--amenities", required=False, nargs='+', default=[], help=("Amenities that should be present "
                        "in the unit. Possible values include laundry,parking,pool,doorman,elevator,gym"))

    return parser.parse_args()


if __name__ == '__main__':
    args = parse_arguments()
    apartment_filter = ApartmentFilter(args.neighborhood, args.min_bedrooms, args.min_bathrooms, args.max_price, args.amenities)
    client = StreetEasyClient(apartment_filter)
    urls = client.get_apartments()
    
    for u in urls:
        print(u)