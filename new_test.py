import re

def replace_newlines(text):
    return re.sub("\n{3,}", "\n\n", text)

text = "Hello world\n\n\nI'm a Python program\n\n\n\nNice to meet you"
new_text = replace_newlines(text)

print(new_text)
'''

k = 'infw'
k.replace('infw', 'inw')
print(k)

def find_matching_parentheses(md_content, i):
    opening_square_bracket_index = -1
    closing_parentheses_index = -1
    closing_square_bracket_count = 1
    opening_parentheses_count = 1
    for j in range(1, i+1):
        if md_content[i-j] == ']':
            closing_square_bracket_count += 1
        elif md_content[i-j] == '[':
            closing_square_bracket_count -= 1
            if closing_square_bracket_count == 0:
                opening_square_bracket_index = i-j
                break
    for k in range(i+2, len(md_content)):
        if md_content[k] == '(':
            opening_parentheses_count += 1
        elif md_content[k] == ')':
            opening_parentheses_count -= 1
            if opening_parentheses_count == 0:
                closing_parentheses_index = k
                break
    return opening_square_bracket_index, closing_parentheses_index

def remove_nested_newlines(md_content):
    i = 0
    while i < len(md_content) - 1:
        if md_content[i] == ']' and md_content[i+1] == '(':
            j, k = find_matching_parentheses(md_content, i)
            if j != -1 and k != -1:
                brackets_content = md_content[j+1:i]
                parentheses_content = md_content[i+2:k]
                brackets_content = brackets_content.replace('\n', ' ')
                parentheses_content = parentheses_content.replace('\n', ' ').replace(' ', '')
                print('brackets_content: ', brackets_content)
                print('parentheses_content: ', parentheses_content)
                md_content = md_content[:j+1] + brackets_content + md_content[i: i+2] + parentheses_content + md_content[k:]
                i = j + len(brackets_content) + 2 + len(parentheses_content) + 1
        i += 1
    return md_content

#print(remove_nested_newlines("Hello [World](link/to/the/world)\nGoodbye [World\n2](anoth  \n [jn\no](  )\n  er/link)\nAnd [another\none](yet/anot --her/link)"))
'''
text = '''
Hello [World](link/to/the/world)\nGoodbye [World\n2](anoth  \n [jn\no](  )\n  er/link)\nAnd [another\none](yet/anot --her/link)

[![With Tiny Chum](https://static.wikia.nocookie.net/hellokitty/images/b/be/Sanrio_Characters_Hello_Kitty --Tiny_Chum_Image006.png/revision/latest?cb=20170619001838)With Tiny Chum](https://hellokitty.fandom.com/wiki/Hello_Kitty/wiki/File:Sanrio_Characters_Hello_Kitty --Tiny_Chum_Image006.png "Sanrio Characters Hello Kitty--Tiny Chum Image006.png (27 KB)")
'''
#print(remove_nested_newlines(text))
# This example will output: "Hello [World](link/to/the/world)\nGoodbye [World 2](another/link)\nAnd [another one](yet/another/link)"
# The newlines within link titles and destinations are removed.

# without regex
def remove_lines_inbetween(md_content):
    result = ""
    is_inside = False
    runnung_string = ""
    for i in range(len(md_content)):
        if md_content[i] == "]":
            is_inside = True
            result += md_content[i]
        elif md_content[i] == "(":
            is_inside = False
            result += md_content[i]
            runnung_string = ""
        else:
            if md_content[i].strip() == "" and is_inside:
                runnung_string += md_content[i]
            else:
                if is_inside:
                    result += runnung_string + md_content[i]
                else:
                    result += md_content[i]
                is_inside = False
                runnung_string = ""
    return result
#print(remove_lines_inbetween("[link]   \n ("))

    # It will also work for multiple links
#print(remove_lines_inbetween("[link1] d  \n (https://example1.com)\n [link2]   \n (https://example2.com)"))