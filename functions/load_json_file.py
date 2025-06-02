import json


# def load_file(json_file, buttons=False):
#     with open(f'{json_file}.json', 'r', encoding='utf-8') as json_file:
#         if buttons:
#             return json.load(json_file)
#         else:
#             result = ""
#             list_objects = json.load(json_file)["text"]
#             for item in list_objects:
#                 if len(list_objects) > 1:
#                     result += f"{item}\n"
#                 elif len(list_objects) == 1:
#                     result += f"{item}"
#             return result

def load_file(json_file, buttons=False):
    with open(f'{json_file}.json', 'r', encoding='utf-8') as json_file:
        if buttons:
            return json.load(json_file)
        else:
            result = ""
            list_objects = json.load(json_file)["text"]
            for item in list_objects:
                if len(list_objects) > 1:
                    result += f"{item}\n"
                elif len(list_objects) == 1:
                    result += f"{item}"
            return result