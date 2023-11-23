def create_file(object):
    filename = resolve("file name")
    filename_value = get_field(filename, 'value')
    
    print(">>> touch " + filename_value)


def create_folder(object):
    filename = resolve("name")
    filename_value = get_field(filename, 'value')
    
    print(">>> mkdir " + filename_value)


def delete_file(object):
    file = resolve("the file")
    print(file.fields)
    filename = resolve("file name")
    filename_value = get_field(filename, 'value')
    
    print(">>> rm " + filename_value)


def delete_folder(object):
    name = run("return the folder name")
    # name_value = run("add 'rdmir' to name")
    name_value = get_field(name, 'value')

    print(">>> rmdir " + name_value)


def run_shell_command(command):
    print('~~~', command, '~~~')


# def fex_FileName_value_from_name_and_extension(object):
#     name = get_field(object, 'name')
#     extension = get_field(object, 'extension')
#     return name + '.' + extension


def fex_FileName_value_from_name_and_extension(object):
    name_letters = []
    for letter in get_field(object, 'name'):
        name_letters.append(str(get_field(letter, 'value')))

    extension_letters = []
    for letter in get_field(object, 'extension'):
        extension_letters.append(str(get_field(letter, 'value')))

    name = "".join(name_letters)
    extension = "".join(extension_letters)

    return name + '.' + extension


def open_folder(object):
    name = get_field(object, 'name')
    run_query("execute", {
        "command": "cd " + name,
    })


def read_file(object):
    file_name_entiy = get_field(object, 'name')
    name = get_field(file_name_entiy, 'value')
    f = open(name)
    data = f.read()
    f.close()
    return Instance("String", {"value": data})


def parse_python_code(object):
    print('parse', object)
    return object


def parse_python_file(object):
    code = run_query("read", {
        "object": object,
    })
    code_value = get_field(code, 'value')

    ast = run_query("parse", {
        "object": Instance("PythonCode", {
            "value": code_value
        }),
    })


def evaluate_file_exists(expr):
    file = get_field(expr, 'object')
    file_name_entiy = get_field(file, 'name')
    name = get_field(file_name_entiy, 'value')
    result = os.path.exists(name)
    return Instance("Boolean", {"value": result})