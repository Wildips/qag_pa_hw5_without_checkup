def pages_count(users_count, page_size):
    if int(users_count // page_size) == 0:
        return 1
    else:
        return int(users_count // page_size)
