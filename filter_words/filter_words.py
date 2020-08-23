FILTER = {}
FILTER[0] = '茅厕东'
FILTER[1] = '习包子'
FILTER_MAX = 2


class GFW(object):
    def __init__(self):
        self.d = {}

    def set(self, keywords):
        """设置关键字到GFW类"""
        q = {}
        k = ''
        for word in keywords:
            word += chr(11)
            p = self.d
            print(f"keywords:{keywords}, word:{word}, self.d:{p}")
            for char in word:
                char = char.lower()
                if p == '':
                    q[k] = {}
                    p = q[k]
                if not (char in p):
                    p[char] = ''
                    q = p
                    k = char
                p = p[char]
                print(f"set char:{char}, k:{k} p:{p}")

    def replace(self, text, mask):
        p = self.d
        i = 0
        j = 0
        z = 0
        result = []
        ln = len(text)
        print(f"rsv_test:{text}, replace_ln:{ln}. mask:{mask}")
        while i + j < ln:
            t = text[i + j].lower()
            if not (t in p):
                j = 0
                i += 1
                p = self.d
                continue
            p = p[t]
            j += 1
            if chr(11) in p:
                p = self.d
                result.append(text[z:i])
                result.append(mask)
                i = i + j
                z = i
                j = 0
        result.append(text[z:i + j])
        print(f"result:{result}")
        return "".join(result)

    def check(self, text):
        p = self.d
        i = 0
        j = 0
        result = []
        ln = len(text)
        while i + j < ln:
            t = text[i + j].lower()
            print(f"rsv_test:{text}, t:{t}. self.d:{p}")
            if not (t in p):
                j = 0
                i += 1
                p = self.d
                continue
            p = p[t]
            j += 1
            if chr(11) in p:
                p = self.d
                result.append((i, j, text[i: i + j]))
                i = i + j
                j = 0
        print(f"check_result:{result}")
        return result


gw = GFW()
gw.set(FILTER.values())

ck = gw.check
replace = gw.replace

if __name__ == '__main__':
    text = "茅厕东， 习包子"
    cr = ck(text)
    print(f"cr:{cr}")
    rc = replace(text, '*')
    print(f"replace:{rc}")

    # =============================
    max = FILTER_MAX
    FILTER.update({max: "中国"})
    FILTER_MAX += 1

    gw.set(['中国'])
    text2 = "中国有最伟大的GWF"
    cc = ck(text2)
    rr2 = replace(text2, '我国')
    print(f"cc2:{cc}, rr2:{rr2}")

    gw.set(['美国', '分裂'])
    print(f"gw set:{gw.d}")
