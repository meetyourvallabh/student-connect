s = "3[abc]4[ab]c"


def get_str(n,s1):
    return n*str(s1)


final_res = ""
for i in range(len(s)):
    #print("occured : ",s[i])
    if s[i] == "[":
        n = int(s[i-1])
        st = ''
        for j in range(i+1,len(s)):
            if s[j]=="]":
                break
            else:
                st = st + s[j]
        #print(n*(st))
        final_res = final_res + get_str(n,st)

def parenthetic_contents(string):
    """Generate parenthesized contents in string as pairs (level, contents)."""
    stack = []
    for i, c in enumerate(string):
        if c == '[':
            stack.append(i)
        elif c == ']' and stack:
            start = stack.pop()
            yield(string[start-1], string[start + 1: i])
            #yield (len(stack), string[start + 1: i])

#print(list(parenthetic_contents('2[3[a]b]')))

#for comb in list(parenthetic_contents('2[3[a]b]')):
#    print(comb)


def get1(s):
    res = ""
    s = tuple(s)
    n = int(s[0])
    print(n,s[1])
    if "[" in str(s[1]):
        res = get1(list(parenthetic_contents(s[1]))[-1])
        print(res)
    res = n * res
    return res


print(get1(list(parenthetic_contents('2[3[a]b]'))[-1]))