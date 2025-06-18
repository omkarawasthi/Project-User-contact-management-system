from dotenv import load_dotenv
from datetime import date, timedelta


load_dotenv()

# function to calculate age
def calculate_age(born):
    today = date.today()
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))


# find birthday of users in next seven days.
def find_birthday_next_week(days):
    from user.models import Contact

    birthday_names = []
    for day in range(days):
        dateis = date.today() + timedelta(days=day)
        month = dateis.month
        day = dateis.day

        birthday_contacts = Contact.objects.filter(
            date_of_birth__month=month,
            date_of_birth__day=day,
        )
        count = birthday_contacts.count()

        if count == 0:
            return "No upcoming birthdays."
        
        for contact in birthday_contacts:
            birthday_names.append({
                "name": f"{contact.first_name} {contact.last_name}",
                "birthday": dateis.strftime("%Y-%m-%d"),
            })

    return {"Users Having Birthday next week :":birthday_names}
