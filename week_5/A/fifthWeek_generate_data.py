import sys, os
from faker import Faker
import random

def generatePerson():
    seed = random.random()
    gender  = '?'
    if seed < 0.5:
        nam = fak.name_female()
        if 0.002 < seed < 0.1:
            gender = 'female'
        if 0.1 < seed < 0.2:
            gender = 'Female'
        if 0.2 < seed < 0.3:
            gender = 'fem.'
        if 0.3 < seed < 0.4:
            gender = 'f'
        if 0.4 < seed < 0.5:
            gender = 'F'
    else:
        nam = fak.name_male()
        if 0.5 < seed < 0.6:
            gender = 'male'
        if 0.6 < seed < 0.7:
            gender = 'Male'
        if 0.7 < seed < 0.8:
            gender = 'man'
        if 0.8 < seed < 0.9:
            gender = 'm'
        if 0.9 < seed < 0.998:
            gender = 'M'
    return [nam, gender]


def generateTitleThesis():
    tit = fak.text()
    fsl = tit.split('.')
    ttitle = fsl[0].title()
    return ttitle


def generateBirthYear(year_defense):
    seed = random.random()
    nyear = year_defense - int(37 - random.random() * 9)
    if seed < 0.25:
        byear = '(' + str(nyear) + ')'
    if 0.25 < seed < 0.5:
        byear = 'c.' + str(nyear)
    if 0.5 < seed < 0.75:
        byear = 'C.'+ str(nyear)
    if seed > 0.75:
        byear = '(' + str(int(nyear - seed * 3)) + '-' + str(int(nyear + seed *2)) + ')'
    return byear


# main part of the program

output_file = "phdThesesFranceThirteesToNineties.csv"
fak = Faker('fr_FR')
entries = 2_000 # when fast testing only (comment the next line out)
# entries = 29_889 # number of theses


with open(os.path.join(sys.path[0], output_file), mode='w') as output:
    output.write("author_name,year_of_birth,gender,thesis_title,year_of_defense\n")
    for i in range(entries):
        person = generatePerson()
        thesis = generateTitleThesis()
        year_published = int(1963 + (random.random() - 0.5) * 55)
        birth_year_author = generateBirthYear(year_published)

        output.write("%s,%s,%s,%s,%d\n" % (
            person[0],
            birth_year_author,
            person[1],
            thesis,
            year_published))

        if i % 10_000 == 0:
            print('records created up to now:', i)
print(output_file, 'file created')

print("exit code 0")
