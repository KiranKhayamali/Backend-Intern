def get_fullname(firstname: str, lastname: str) -> str:
    return f"{firstname.title()} {lastname.title()}"

print(get_fullname("kiran", "khayamali"))