from django.test import TestCase

# Create your tests here.

import string
import random
char_str = string.digits+string.ascii_letters
char = random.sample(char_str,5)
char = ''.join(char)
print(char)