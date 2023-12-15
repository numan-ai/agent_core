def fex_Number_value_from_digits(entity):
    digits = []
    
    for digit in get_field(entity, 'digits'):
        digits.append(str(get_field(digit, 'value')))
    
    # print(digits)
    return int(''.join(digits))


def fex_String_value_from_characters(entity):
    chars = []
    for char in get_field(entity, 'characters'):
        chars.append(char)
    return ''.join(chars)
