car = {
    "brand": "Ford",
    "model": "Mustang",
    "year": 1964,
    "engine": {"cilinders": 8, "displacement": 7000}
}

def iterate_car(car):
    for key,value in car.items():
        if str(type(value))=="<class 'dict'>":
            iterate_car(value)
        else:
            print(key, "is", value)

iterate_car(car)
        

