import re

thing = "duplicate column name"
if re.search("duplicate column name", thing):
    print("yes")
else:
    print("n")
