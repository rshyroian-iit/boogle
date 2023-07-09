import re

k = 'infw'
k.replace('infw', 'inw')
print(k)

def find_matching_parentheses(md_content, i):
    opening_square_bracket_index = -1
    closing_parentheses_index = -1
    closing_square_bracket_count = 1
    opening_parentheses_count = 1
    # find the matching opening square bracket
    for j in range(1, i+1):
        if md_content[i-j] == ']':
            closing_square_bracket_count += 1
        elif md_content[i-j] == '[':
            closing_square_bracket_count -= 1
            if closing_square_bracket_count == 0:
                opening_square_bracket_index = i-j
                break
    # find the matching closing parentheses
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
        print(i)
        if md_content[i] == ']' and md_content[i+1] == '(':
            j, k = find_matching_parentheses(md_content, i)
            #print(j, k)
            if j != -1 and k != -1:
                brackets_content = md_content[j+1:i]
                parentheses_content = md_content[i+2:k]
                if '\n' in brackets_content or '\n' in parentheses_content:
                    md_content = md_content[:j+1] + brackets_content.replace('\n', ' ') + md_content[i: i+2] + parentheses_content.replace('\n', ' ').replace(' ', '') + md_content[k:]
                    print(len(brackets_content), len(parentheses_content))
                    i = j + len(brackets_content.replace('\n', ' ')) + 2 + len(parentheses_content.replace('\n', ' ').replace(' ', '')) + 1
        i += 1
    return md_content

print(remove_nested_newlines("Hello [World](link/to/the/world)\nGoodbye [World\n2](anoth  \n [jn\no](  )\n  er/link)\nAnd [another\none](yet/another/link)"))
# This example will output: "Hello [World](link/to/the/world)\nGoodbye [World 2](another/link)\nAnd [another one](yet/another/link)"
# The newlines within link titles and destinations are removed.

