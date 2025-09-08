#REIMAGE CONCEPT PRICING
import pytz
import datetime
import math


def choose_date():
    while True:
        print()
        print("Available days are Thursdays to Sundays.")
        date_str = input("Enter your preferred date (YYYY-MM-DD): ")
        try:
            date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d")
            # weekday(): Monday=0, ..., Sunday=6
            if date_obj.weekday() in [3, 4, 5, 6]:
                print(f"{date_obj.strftime('%A, %Y-%m-%d')} is Available.")
                return date_str
            else:
                print(f"{date_obj.strftime('%A, %Y-%m-%d')} is Not Available. Please choose a date from Thursday to Sunday.")
        except ValueError:
            print("Invalid date format. Please use YYYY-MM-DD.")

def choose_time():
    tz_types = [
        ("US/Pacific", "Pacific"),
        ("US/Mountain", "Mountain"),
        ("US/Central", "Central"),
        ("US/Eastern", "Eastern"),
        ("GMT", "GMT"),
        ("Europe/London", "BST"),
    ]
    print()
    print("Select your timezone type:")
    for i, (_, label) in enumerate(tz_types, 1):
        print(f"{i}. {label}")
    print()
    while True:
        tz_choice = input("Enter the number for your timezone: ")
        try:
            tz_index = int(tz_choice) - 1
            if 0 <= tz_index < len(tz_types):
                tz_str = tz_types[tz_index][0]
                tz_label = tz_types[tz_index][1]
                local_tz = pytz.timezone(tz_str)
                cst_tz = pytz.timezone("US/Central")
                # Calculate time difference
                now = datetime.datetime.now()
                local_now = local_tz.localize(now)
                cst_now = local_now.astimezone(cst_tz)
                diff_hours = (cst_now.hour - local_now.hour) % 24
                if diff_hours == 0:
                    diff_str = "(same as CST)"
                elif diff_hours > 0:
                    diff_str = f"(+{diff_hours} hours ahead of CST)"
                else:
                    diff_str = f"({abs(diff_hours)} hours behind CST)"
                print(f"Your selected timezone is {tz_label}. Time difference to CST: {diff_str}")
                break
            else:
                print("Invalid selection. Please choose a valid number.")
        except ValueError:
            print("Invalid input. Please enter a number.")
    while True:
        time_str = input("Enter your preferred start/arrival time (hh:mm am/pm (e.g., 02:30 pm)) in your local time: ")
        try:
            today = datetime.datetime.now()
            time_obj = datetime.datetime.strptime(time_str.strip().lower(), "%I:%M %p")
            local_dt = local_tz.localize(datetime.datetime(today.year, today.month, today.day, time_obj.hour, time_obj.minute))
            cst_dt = local_dt.astimezone(cst_tz)
            cst_hour = cst_dt.hour
            if 8 <= cst_hour <= 19:
                print(f"You selected {time_obj.strftime('%I:%M %p')} in {tz_label}. That is {cst_dt.strftime('%I:%M %p')} CST.")
                return cst_dt.strftime('%I:%M %p')
            else:
                print(f"The time you selected converts to {cst_dt.strftime('%I:%M %p')} CST, which is outside the available window (8am to 7pm CST). Please choose a time that falls within this range.")
        except ValueError:
            print("Invalid time format. Please use hh:mm am/pm (e.g., 02:30 pm).")

def offers_pkg():
    offers = ["Basic", "Standard", "Premium"]
    while True:
        print()
        print("Choose an offer for your package: ")
        for i, off in enumerate(offers, 1):
            print(f"{i}. {off}")
        print()
        try:
            choice = int(input("Choose an offer by the number: "))
            if 1 <= choice <= len(offers):
                return offers[choice - 1]
            else:
                print()
                print("Invalid choice. Please try again.")
        except ValueError:
            print()
            print("Invalid input. Please enter a number.")
    

def package_price(pkgs, num_images, num_hours, num_persons):
    base_price = 200  # Base price for the concept
    image_price = 10  # Price per additional image
    hourly_rate = 150  # Hourly rate for the session
    studio_fee = 200  # Studio fee for indoor sessions
    individual_fee = 70  # Individual fee for personal sessions

    if pkgs == "Wedding":
        return base_price + (hourly_rate * num_hours) + (image_price * num_images)
    elif pkgs == "Engagement":
        return base_price + (hourly_rate * num_hours) + (image_price * num_images)
    elif pkgs == "Outdoor Portrait":
        return base_price + (hourly_rate * num_hours) + (image_price * num_images) + (individual_fee * num_persons)
    elif pkgs == "Indoor Portrait":
        return base_price + (hourly_rate * num_hours) + (image_price * num_images) + (individual_fee * num_persons)
    elif pkgs == "Studio Session":
        return base_price + studio_fee + (hourly_rate * num_hours) + (image_price * num_images) + (individual_fee * num_persons)
    elif pkgs == "Family Session":
        return base_price + (hourly_rate * num_hours) + (image_price * num_images) + (individual_fee * num_persons)
    elif pkgs == "Event Coverage":
        return base_price + (hourly_rate * num_hours) + (image_price * num_images)
    else:
        return "Invalid concept"        
    
def choose_pkg():
    pkgs = ["Wedding", "Engagement", "Outdoor Portrait", "Indoor Portrait", "Studio Session", "Family Session", "Event Coverage"]
    while True:
        print()
        print("Choose a package to get started: ")
        print()
        for i, pkg in enumerate(pkgs, 1):
            print(f"{i}. {pkg}")
        print()
        try:
            choice = int(input("Choose a package by the number: "))
            if 1 <= choice <= len(pkgs):
                return pkgs[choice - 1]
            else:
                print()
                print("Invalid choice. Please try again.")
        except ValueError:
            print()
            print("Invalid input. Please enter a number.")

def main():
    print()
    print("Welcome to REIMAGE CONCEPT PRICING")
    pkgs = choose_pkg()
    if pkgs == "Invalid choice":
        print("You selected an invalid package. Please restart and choose a valid option.")
        return
    
    off = offers_pkg()
    date_str = choose_date()
    time_str = choose_time()


    def get_int_input(prompt):
        while True:
            val = input(prompt)
            try:
                num = float(val)
                rounded = int(math.ceil(num))
                if num != rounded:
                    confirm = input(f"You entered {num}. Should I round it up to {rounded}? (Y/N): ").strip().lower()
                    if confirm == 'y':
                        return rounded
                    elif confirm == 'n':
                        continue
                    else:
                        print("Invalid input. Please enter Y or N.")
                        continue
                return rounded
            except ValueError:
                print("Invalid input. Please enter a number.")
    
    print()
    num_images = get_int_input("Enter the number of additional images you want: ")
    print()
    num_hours = get_int_input("Enter the number of hours for the session: ")
    print()
    num_persons = get_int_input("Enter the number of persons involved: ")

    print()
    total_price = package_price(pkgs, num_images, num_hours, num_persons)
    if total_price == "Invalid concept":
        print("There was an error with the package selection. Please try again.")
    else:
        print(f"The total price for the {off} {pkgs} package on {date_str} at {time_str} CST is: ${total_price:,}")
if __name__ == "__main__":
    main()





