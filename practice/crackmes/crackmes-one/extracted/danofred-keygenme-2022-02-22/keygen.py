import sys

# here do that thing 

def main(args):
    # generate the key?
    print(args)
    len_args = len(args)
    key_len = len('tryHarderToMakeAGoodKeyGen')
    res = []
    for i in range (0, len_args):
        #print(ord(args[i]) ^ key_len)
        d=(ord(args[i])^key_len) % len_args
        res.append(args[d])

    return res

if __name__ == '__main__':
    arg1 = sys.argv[1]
    res=main(arg1)
    print('the result is, ',str(res))
