from database.db import get_all_rental_requests

if __name__ == "__main__":
    df = get_all_rental_requests()
    print(df.to_string(index=False))
