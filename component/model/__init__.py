# if you only have few io a module is not necessary and you can simply use a scripts.py file
# in a big module with lot of model, it can make sense to split things in separate for the sake of maintenance

# if you use a module import all the functions here to only have 1 call to make
from .geo4lup_model import *
