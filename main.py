# HEALTHCARE INTELLIGENCE SYSTEM

print("================================")
print(" HEALTHCARE INTELLIGENCE SYSTEM")
print("================================")

print("welcome to our health care data project")

print("We are learning Python and Data Science.")

print("Our goal is to analyse healthcare information")


# PATIENT REGISTRATION

patient_names = []
patient_ages = []
patient_genders = []

number_to_register = 3

for patient_number in range(number_to_register):

    print("\n--- PATIENT REGISTRATION ---")

    patient_name = input("Enter patient name: ")

    patient_age = int(input("Enter patient age: "))

    patient_gender = input("Enter patient gender: ")

    patient_names.append(patient_name)
    patient_ages.append(patient_age)
    patient_genders.append(patient_gender)


# DISPLAY REGISTERED PATIENTS

print("\n--- REGISTERED PATIENTS ---")

for i in range(len(patient_names)):

    print("\nPatient number:", i + 1)
    print("Name:", patient_names[i])
    print("Age:", patient_ages[i])
    print("Gender:", patient_genders[i])


# PATIENT AGE ANALYSIS

total_age = sum(patient_ages)

number_of_patients = len(patient_ages)

average_age = total_age / number_of_patients

print("\n--- PATIENT AGE ANALYSIS ---")

print("Total age:", total_age)

print("Number of patients:", number_of_patients)

print("Average age:", round(average_age, 2))

# PATIENT AGE CLASSIFICATION

print("\n--- PATIENT AGE CLASSIFICATION ---")

for i in range(len(patient_names)):

    age = patient_ages[i]

    if age < 18:
        age_group = "Child/Adolescent"

    elif age < 65:
        age_group = "Adult"

    else:
        age_group = "Older Adult"

    print(patient_names[i], ":", age_group)

    # PATIENT POPULATION ANALYSIS

children = 0
adults = 0
older_adults = 0

for age in patient_ages:

    if age < 18:
        children += 1

    elif age < 65:
        adults += 1

    else:
        older_adults += 1

# FUNCTION TO CALCULATE PERCENTAGES

def calculate_percentage(category_count, total_patients):
    if total_patients == 0:
        return 0

    percentage = (category_count / total_patients) * 100
    return percentage
total_patients = len(patient_ages)

children_percentage = calculate_percentage(children, total_patients)

adults_percentage = calculate_percentage(adults, total_patients)

older_adults_percentage = calculate_percentage(older_adults, total_patients)

print("\n--- PATIENT POPULATION ANALYSIS ---")

print("Children/Adolescents:", children, round(children_percentage, 2), "%")

print("Adults:", adults, round(adults_percentage, 2), "%")

print("Older Adults:", older_adults, round(older_adults_percentage, 2), "%")
