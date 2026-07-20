from sheets import load_birthdays

people = load_birthdays()

print(f"Loaded {len(people)} birthdays\n")

for person in people[:10]:
    print(person)