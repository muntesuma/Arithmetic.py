from queue import PriorityQueue     
import pickle           
 
class Arifm:                        # создание класса
    def __init__(self):             # создание конструктора класса
        self.endcode_result = ""
        self.bits_to_follow = 0
 
    def generate_dictionary(self, file):                                   
        symbols = {} 
        for symbol in file :
            symbols[symbol] = symbols.get(symbol, 0) + 1
        symbols = sorted(symbols.items(), key = lambda x: x[1])
        symbols = symbols[::-1]
        symbols = {s[0]: s[1] for s in symbols}
        summ = 0
        self.symbols_index = {}
        self.symbols = []
        for i, symbol in enumerate(symbols):
            print(symbol)
            summ += symbols[symbol]
            self.symbols.append(summ)
            self.symbols_index[symbol] = i + 1
        self.symbols = [0] + self.symbols
 
    def save_dictionary(self):  # функция сохранения словаря в файл code_arifmeted.txt с помощью библеотеки pickle
        temp = {}
        for i in self.symbols_index:
            temp[i] = self.symbols[self.symbols_index[i]] 
        pickle.dump(temp, open("arifmetic_dictionary.txt", 'wb'))
 
    def load_dictionary(self):  
        loaded = pickle.load(open("arifmetic_dictionary.txt", 'rb'))
        loaded = sorted(loaded.items(), key = lambda x: x[1])
        #loaded = loaded[::-1]
        loaded = {s[0]: s[1] for s in loaded}
        self.symbol_by_index = {}
        self.symbols = []
        print(loaded)
        for i, temp in enumerate(loaded):  
            self.symbol_by_index[i + 1] = temp
            self.symbols.append(loaded[temp])
        self.symbols = [0] + self.symbols
        print(self.symbol_by_index)
        print(self.symbols)
 
    def encode(self, file):
        l0, h0 = 0, 65535
        l1, h1 = 0, 0    
        delitel = self.symbols[-1]
        first_qtr = (h0 + 1) // 4
        half = first_qtr * 2
        third_qtr = first_qtr * 3
        self.bits_to_follow = 0
        for symbol in file:
            j = self.symbols_index[symbol]
            l1 = l0 + self.symbols[j - 1] * (h0 - l0 + 1) // delitel
            h1 = l0 + self.symbols[j] * (h0 - l0 + 1) // delitel - 1
            while True: 
                if h1 < half:
                    self.bits_plus(0)
                elif l1 >= half:
                    self.bits_plus(1)
                    l1 -= half
                    h1 -= half
                elif l1 >= first_qtr and h1 < third_qtr:
                    self.bits_to_follow += 1
                    l1 -= first_qtr
                    h1 -= first_qtr
                else:
                    break
                l1 += l1
                h1 += h1 + 1
                l0, h0 = l1, h1
        self.bits_to_follow += 1
        if l1 < first_qtr:
            self.bits_plus(0)
        else:
            self.bits_plus(1)
        self.endcode_result += 16 * '0'
        self.endcode_result = '1' + self.endcode_result
        return self.bitstring_to_bytes(self.endcode_result)
 
    def decode(self, file):
        l0, h0 = 0, 65535
        l1, h1 = 0, 0 
        delitel = self.symbols[-1]
        first_qtr = (h0 + 1) // 4
        half = first_qtr * 2
        third_qtr = first_qtr * 3
        file = self.string_for_decode(file)[1:]
        value = int(file[:16], 2)
        print(file[:16], value)
        ans = ""
        counter = 16
        for i in range(16, len(file)):
            freq = ((value - l0 + 1) * delitel - 1) // (h0 - l0 + 1)
            j = 1
            while self.symbols[j] <= freq:
                j += 1
            l1 = l0 + self.symbols[j - 1] * (h0 - l0 + 1) // delitel
            h1 = l0 + self.symbols[j] * (h0 - l0 + 1) // delitel - 1
            while True:
                if h1 < half:
                    pass
                elif l1 >= half:    
                    l1 -= half
                    h1 -= half
                    value -= half
                elif l1 >= first_qtr and h1 < third_qtr:
                    l1 -= first_qtr
                    h1 -= first_qtr
                    value -= first_qtr
                else:
                    break
                l1 += l1
                h1 += h1 + 1
                if counter >= len(file):
                    break
                value += value + int(file[counter])
                counter += 1
            #print(j)
            if counter >= len(file):
                break
            ans += self.symbol_by_index[j]
            l0, h0 = l1, h1
 
            #print(ans)
        #print(ans)
        return ans
 
    def bits_plus(self, bit):
        self.endcode_result += str(bit)
        while self.bits_to_follow > 0:
            self.bits_to_follow -= 1
            self.endcode_result += str(int(not bit))
 
    def string_for_decode(self, file):
        temp = ""
        temp = bin(file[0])[2:]
        for i in range(1, len(file)):
            temp += bin(file[i])[2:].zfill(8)
            #print(bin(file[i])[2:])
        return temp
 
    def bitstring_to_bytes(self, s):
        v = int(s, 2)
        b = bytearray()
        while v:
            b.append(v & 0xff)
            v >>= 8
        return bytes(b[::-1])
 
def save_file(file, name, is_encoded):  # функция сохранения файла
    # f = open(name, "w")               # открытие файла на перезапись
    try:
        if is_encoded:              # если файл ЗАШИФРОВАН то все коды сохраняются через ","
            f = open(name, "wb")    # открытие файла на перезапись
            f.write(file)
        else:                       # если файл НЕ ЗАШИФРОВАН то расшифрованный текст сохраняется в файл
            f = open(name, "w")     # открытие файла на перезапись
            f.write(file)
    finally:
        f.close()   # закрытие файла
 
def read_file(name, is_encodeed):               # функция чтения файла
    # link_code_txt = open(name, "rt", encoding = "utf-8-sig")                                        # открытие файла на чтение в текстовом режиме с текстом на русском или английском языке
    if is_encodeed:  # если файл ЗАШИФРОВАН:
        link_code_txt = open(name, "rb")
        temp = link_code_txt.read()             # копирование содержимого файла link_code_txt в переменную temp для возможножности закрытия этого файла
        link_code_txt.close()                   # закрытие файла link_code_txt
        # return pickle.load(open(name, 'rb'))
        # return list(map(int, list(filter(lambda x: not(x is None or x == ''), temp.split(',')))))   # коды в файле разделяются "," и переводятся в числовой формат, добавляются в одну строку и эта строка - возвращаемое значение
        return temp
    else:                                                       # если файл НЕ ЗАШИФРОВАН:
        link_code_txt = open(name, "rt", encoding="utf-8-sig")
        file = ''                                               # все символы файла добавляются в одну строку и эта строка - возвращаемое значение
        for str_temp in link_code_txt:
            for char_temp in str_temp:
                file += char_temp
        link_code_txt.close()                                   # закрытие файла link_code_txt
        return file                                             # возвращаемое значение
 
 
def bitstring_to_bytes(s):
    v = int(s, 2)
    b = bytearray()
    while v:
        b.append(v & 0xff)
        v >>= 8
    return bytes(b[::-1])
 
 
def encode(file, dictionary):                   # функция шифрования или расшифрования
    decoded_file = ""                           # объявление массива decoded_file
    for temp in file:
        decoded_file += dictionary.get(temp)    # добавление новых значений в массив
    return bitstring_to_bytes(decoded_file)     # (за-)расшифрованный массив - возвращаемое значение
 
 
 
def reverse_dictionary(dictionary):                     # функция для переворачивания таблицы Хаффмана
    reverse_dictionary = {}                             # объявление словаря reverse_dictionary
    print(dictionary)
    for temp in dictionary:  # TODO
        reverse_dictionary[dictionary[temp]] = temp
    return reverse_dictionary                           # возвращение перевернтого словаря
 
 
def save_file(file, name, is_encoded):  # функция сохранения файла
    # f = open(name, "w")               # открытие файла на перезапись
    try:
        if is_encoded:                  # если файл ЗАШИФРОВАН то все коды сохраняются через ","
            # for temp in file:
            #     f.write((str)(temp))
            #     f.write(',')
            f = open(name, "wb")        # открытие файла на перезапись
            f.write(file)
        else:                           # если файл НЕ ЗАШИФРОВАН то расшифрованный текст сохраняется в файл
            f = open(name, "w")         # открытие файла на перезапись
            # for temp in file:
            #     f.write((str)(temp))
            f.write(file)
    finally:
        f.close()  # закрытие файла
 
def save_dictionary(dictionary):    # функция сохранения словаря в файл arifmetic_dictionary.txt с помощью библеотеки pickle
    pickle.dump(dictionary, open("arifmetic_dictionary.txt", 'wb'))
 
def load_dictionary():              # функция загрузки словаря из файла arifmetic_dictionary.txt с помощью библеотеки pickle
    return pickle.load(open("arifmetic_dictionary.txt", 'rb'))
 
def main():                                     # объявление основной функции
    mode = int(input("Для шифрования файла введите 0\nДля расшифрования файла введите 1\nВыбор режима: "))
    # 0 - зашифровать, 1 - расшифровать
    process = Arifm()
    if mode == 0:                               # режим ШИФРОВАНИЯ файла
        file = read_file("code.txt", False)     # загрузка не зашифрованного файла
        process.generate_dictionary(file)       # создание словаря
        print(process.symbols)
        print(process.symbols_index)
        #valid(dictionary)
        process.save_dictionary()
        save_file(process.encode(file), "encoded.bin", True)    # шифрование и сохранение зашифрованного файла
    elif mode == 1:                             # режим РАСШИФРОВАНИЯ файла
        file = read_file("encoded.bin", True)   # загрузка зашифрованного файла
        process.load_dictionary()
        save_file(process.decode(file), "decoded.txt", False)  
 
 
if __name__ == "__main__":
    main()  # запуск основной функции