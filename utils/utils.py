from faker import Faker


def get_random_user():
    fake = Faker()

    user = {
        "name": fake.name(),
        "phone": fake.phone_number(),
        "adress": fake.address(),
        "company": fake.company(),
    }

    return user
