#PRICING CODE FOR PHOTOGRAPHY SERVICES
import pytz
import datetime
import math
import inspect

PACKAGE_NAMES = [
    "Wedding (free couple engagement session)",
    "Engagement (2 persons)",
    "Portrait (max 2 persons)",
    "Family Session (max 6 persons)",
    "Event Coverage"
]

def location_type():
    locations = ["Studio", "Outdoor Location"]
    studio_address = "YOUR STUDIO ADDRESS HERE"
    # Add or remove outdoor locations here
    outdoor_options = ["LOCATION 1", "LOCATION 2", "LOCATION 3"]  # Extend this list as needed
    outdoor_links = {
        "LOCATION 1": "https://maps.google.com/?q=ABC+Location+Address",
        "LOCATION 2": "https://maps.google.com/?q=XYZ+Location+Address",
        "LOCATION 3": "https://maps.google.com/?q=XYZ1+Location+Address"
    }
    while True:
        print("\nChoose a preferred location type:")
        for i, loc in enumerate(locations, 1):
            print(f"{i}. {loc}")
        try:
            choice = int(input("Choose a location type by the number: "))
            if choice == 1:
                return "Studio", studio_address, choice
            elif choice == 2:
                print("\nOutdoor location options:")
                for i, opt in enumerate(outdoor_options, 1):
                    print(f"{i}. {opt}")
                print(f"{len(outdoor_options)+1}. Choose later")
                try:
                    outdoor_choice = int(input("Select outdoor location by number (or choose later): "))
                    if 1 <= outdoor_choice <= len(outdoor_options):
                        loc_name = outdoor_options[outdoor_choice - 1]
                        link = outdoor_links.get(loc_name, "")
                        return "Outdoor Location", f"{loc_name} ({link})" if link else loc_name, choice
                    elif outdoor_choice == len(outdoor_options)+1:
                        return "Outdoor Location", "To be decided", choice
                except ValueError:
                    pass
                print("Invalid input. Defaulting to 'To be decided'.")
                return "Outdoor Location", "To be decided", choice
            else:
                print("Invalid choice. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def choose_date():
    while True:
        print()
        print("Available days are Thursdays to Sundays.")
        date_str = input("Enter your preferred date (YYYY-MM-DD): ")
        try:
            date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d")
            today = datetime.datetime.now().date()
            if date_obj.date() <= today:
                print("Preferred date must be from tomorrow onwards. Please choose a future date.")
                continue
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
                # Calculate UTC offsets
                local_offset = local_now.utcoffset().total_seconds() / 3600
                cst_offset = cst_now.utcoffset().total_seconds() / 3600
                diff_hours = local_offset - cst_offset
                if diff_hours == 0:
                    diff_str = "(same as CST)"
                elif diff_hours > 0:
                    diff_str = f"(+{diff_hours:.1f} hours ahead of CST)"
                else:
                    diff_str = f"({abs(diff_hours):.1f} hours behind CST)"
                print()
                print(f"Your selected timezone is {tz_label}. Time difference to CST: {diff_str}")
                break
            else:
                print("Invalid selection. Please choose a valid number.")
        except ValueError:
            print("Invalid input. Please enter a number.")
    while True:
        time_str = input("Enter your preferred start/arrival time (hh:mm am/pm (e.g., 02:30 pm)) in your local time: ")
        print()
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
                print()
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
    

def package_price(pkgs, num_images, num_hours, num_persons, offer=None):
    # Define rates for each package
    package_rates = {
        PACKAGE_NAMES[0]: {"base": 2599.99, "hourly": 299.99},  # Wedding
        PACKAGE_NAMES[1]: {"base": 249.99, "hourly": 149.99},   # Engagement
        PACKAGE_NAMES[2]: {"base": 249.99, "hourly": 149.99},   # Portrait
        PACKAGE_NAMES[3]: {"base": 349.99, "hourly": 149.99},   # Family Session
        PACKAGE_NAMES[4]: {"base": 499.99, "hourly": 299.99},   # Event Coverage
    }
    image_price = 14.99  # Price per additional image
    studio_fee = 200  # Studio fee for indoor sessions
    individual_fee = 99.99  # Individual fee for personal sessions

    # Set extra offer price based on package and offer
    extra_offer_price = 0
    if offer == "Standard":
        if pkgs == PACKAGE_NAMES[0]:
            extra_offer_price = 999.99
        elif pkgs in [PACKAGE_NAMES[1], PACKAGE_NAMES[2], PACKAGE_NAMES[3]]:
            extra_offer_price = 399.99
        elif pkgs == PACKAGE_NAMES[4]:
            extra_offer_price = 599.99
    elif offer == "Premium":
        if pkgs == PACKAGE_NAMES[0]:
            extra_offer_price = 1599.99
        elif pkgs in [PACKAGE_NAMES[1], PACKAGE_NAMES[2], PACKAGE_NAMES[3]]:
            extra_offer_price = 599.99
        elif pkgs == PACKAGE_NAMES[4]:
            extra_offer_price = 999.99

    if pkgs in package_rates:
        base_price = package_rates[pkgs]["base"]
        hourly_rate = package_rates[pkgs]["hourly"]
        # Wedding
        if pkgs == PACKAGE_NAMES[0]:
            return base_price + (hourly_rate * num_hours) + (image_price * num_images) + extra_offer_price
        # Engagement
        elif pkgs == PACKAGE_NAMES[1]:
            return base_price + (hourly_rate * num_hours) + (image_price * num_images) + extra_offer_price
        # Portrait
        elif pkgs == PACKAGE_NAMES[2]:
            return base_price + (hourly_rate * num_hours) + (image_price * num_images) + (individual_fee * num_persons) + extra_offer_price
        # Family Session
        elif pkgs == PACKAGE_NAMES[3]:
            return base_price + (hourly_rate * num_hours) + (image_price * num_images) + (individual_fee * num_persons) + extra_offer_price
        # Event Coverage
        elif pkgs == PACKAGE_NAMES[4]:
            return base_price + (hourly_rate * num_hours) + (image_price * num_images) + extra_offer_price
    else:
        return "Invalid concept"

def deliverables(pkg_index, offer, pkgs_name):
    # pkg_index: 1-based index of package chosen
    # offer: string, e.g., "Basic"
    print()
    # Only print the header if not in summary mode  
    frame = inspect.currentframe().f_back
    caller = frame.f_code.co_name
    if caller != "main":
        print(f"Deliverables included in the {offer} {pkgs_name} package:")
    shared_items = ["Online gallery for viewing and sharing", "Print release for personal use", "1 year online storage of images", "1 photographer"]
    offer_map = {
        "Basic": {
            (2,3,4,): ["5 high-resolution retouched images", "30 mins coverage"],
            (1,): ["1 hour studio engagement session", "6 hour wedding coverage", "11 by 14 inch leather cover photobook"],
            (5,): ["Basic edit and delivery of all images taken", "1 hour coverage"],
        },
        "Standard": {
            (2,3,4,): ["10 high-resolution retouched images", "1 hour coverage", "11 by 14 inch canvas print"],
            (1,): ["1 hour studio or location engagement session", "7 hour wedding coverage", "11 by 14 inch leather cover photobook", "11 by 14 inch canvas print for hanging"],
            (5,): ["Basic edit and delivery of all images taken", "2 hours coverage"],
        },
        "Premium": {
            (2,3,4,): ["20 high-resolution retouched images", "1 hour 30 mins coverage", "6 by 8 inch leather cover photobook", "11 by 14 inch canvas print", "20oz coffe mug"],
            (1,): ["2 hour engagement session (1hr/studio & 1hr/location)", "8 hour wedding coverage", "11 by 14 inch leather cover photobook", "11 by 14 inch canvas print", "20oz coffe mug"],
            (5,): ["Basic edit and delivery of all images taken", "4 hours coverage"],
        }
    }
    items = []
    if offer in offer_map:
        for keys, deliverable_list in offer_map[offer].items():
            if pkg_index in keys:
                items = deliverable_list
                break
    # Always include shared items for all packages
    for item in items + shared_items:
        print(f"- {item}")
    print()


def choose_pkg():
    pkgs = PACKAGE_NAMES
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
                # Return both the name and the index (1-based)
                return pkgs[choice - 1], choice
            else:
                print()
                print("Invalid choice. Please try again.")
        except ValueError:
            print()
            print("Invalid input. Please enter a number.")

def main():
    print()
    print("Welcome to YOUR BUSINESS NAME HERE!")
    pkgs, pkg_index = choose_pkg()
    if pkgs == "Invalid choice":
        print("You selected an invalid package. Please restart and choose a valid option.")
        return

    location = None
    location_address = None
    location_choice_index = None
    if pkg_index in [2, 3, 4]:
        location, location_address, location_choice_index = location_type()

    off = offers_pkg()
    # Display deliverables before date selection
    print("\nThese are the expected deliverables:")
    deliverables(pkg_index, off, pkgs)
    while True:
        cont = input("Do you want to continue with this offer? (Y/N): ").strip().lower()
        if cont == 'y':
            break
        elif cont == 'n':
            off = offers_pkg()
            deliverables(pkg_index, off, pkgs)
        else:
            print("Invalid input. Please enter Y or N.")
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
    # Only ask for num_images if Engagement, Portrait, or Family Session is chosen
    if pkgs in [PACKAGE_NAMES[1], PACKAGE_NAMES[2], PACKAGE_NAMES[3]]:
        num_images = get_int_input("Enter the number of additional retouched images you want: ")
    else:
        num_images = 0
    print()
    num_hours = get_int_input("Enter the number of additional hours you want for the package: ")
    print()
    # Only ask for num_persons if Portrait or Family Session is chosen
    if pkgs in [PACKAGE_NAMES[2], PACKAGE_NAMES[3]]:
        num_persons = get_int_input("Enter the number of additional persons involved: ")
    else:
        num_persons = 0

    print()
    total_price = package_price(pkgs, num_images, num_hours, num_persons, off)
    if total_price == "Invalid concept":
        print("There was an error with the package selection. Please try again.")
    else:
        print("ORDER SUMMARY")
        print()
        print(f"Total price: ${total_price:,.2f}")
        print(f"Offer selected: {off}")
        print(f"Package selected: {pkgs}")
        print(f"Date of event: {date_str}")
        print(f"Time of event: {time_str} CST")
        if num_hours > 0:
            print(f"Number of additional hours: {num_hours}")
        if num_persons > 0:
            print(f"Number of additional persons: {num_persons}")
        if num_images > 0:
            print(f"Number of additional retouched images: {num_images}")
        if location_choice_index == 1 and location_address:
            print("Location type: Studio")
            print(f"Studio address: {location_address}")
        elif location_choice_index == 2 and location_address:
            if location_address == "To be decided":
                print("Location type: Outdoor Location")
                print("Outdoor location: To be decided")
            else:
                outdoor_name, hyperlink = location_address.split('(')[0].strip(), location_address.split('(')[1].rstrip(')') if '(' in location_address and ')' in location_address else (location_address, "")
                print(f"Location type: {outdoor_name}")
                if hyperlink:
                    print(f"{outdoor_name} address: {hyperlink}")
                else:
                    print(f"{outdoor_name} address: {location_address}")
    # Display deliverables again at the end
    print("\nSummary of Base Deliverables:")
    deliverables(pkg_index, off, pkgs)
if __name__ == "__main__":
    main()





