import sys

dict_type: dict[int, str] = {
    0: "NOTYPE",
    1: "OBJECT",
    2: "FUNC",
    3: "SECTION",
    4: "FILE",
    5: "COMMON",
    6: "TLS",
    10: "LOOS",
    12: "HIOS",
    13: "LOPROC",
    15: "HIPROC"
}
dict_vis: dict[int, str] = {
    0: "DEFAULT",
    1: "INTERNAL",
    2: "HIDDEN",
    3: "PROTECTED"}

dict_bind: dict[int, str] = {
    0: "LOCAL",
    1: "GLOBAL",
    2: "WEAK",
    10: "LOOS",
    12: "HIOS",
    13: "LOPROC",
    15: "HIPROC"}

dict_index: dict[int, str] = {
    0: "UNDEF",
    65280: "LOPROC",
    65311: "HIPROC",
    65312: "LOOS",
    65343: "HIOS",
    65521: "ABS",
    65522: "COMMON",
    65535: "HIRESERVE"
}

names_func = {"0": 0}
count_reg = 0
reg = {
    0: "zero",
    1: "ra",
    2: "sp",
    3: "gp",
    4: "tp",
    5: "t0",
    6: "t1",
    7: "t2",
    8: "s0",
    9: "s1",
    10: "a0",
    11: "a1",
    12: "a2",
    13: "a3",
    14: "a4",
    15: "a5",
    16: "a6",
    17: "a7",
    18: "s2",
    19: "s3",
    20: "s4",
    21: "s5",
    22: "s6",
    23: "s7",
    24: "s8",
    25: "s9",
    26: "s10",
    27: "s11",
    28: "t3",
    29: "t4",
    30: "t5",
    31: "t6"}


def conv_10to16(number):
    if number >= 0:
        return hex(number)
    return hex(number + 2 ** 32)


def command_parce(bit_str, address):
    opcode = bit_str[25:32]
    reg_rd = bit_str[20:25]
    if opcode == "0110111":
        return '%7s\t%s, %s\n' % ("lui", reg[int(reg_rd, 2)], str(conv_10to16(int((bit_str[0:20]), 2) - 2 ** 20 * int(bit_str[0]))))
    elif opcode == "0010111":
        return '%7s\t%s, %s\n' % ("auipc", reg[int(reg_rd, 2)],
                                  str(hex(int((bit_str[0:20]), 2) - 2 ** 20 * int(bit_str[0]))))
    elif opcode == "1101111":
        jump = int(bit_str[0] + bit_str[12:20] + bit_str[11] + bit_str[1:11] + "0", 2) - (2 ** 21) * int(
            bit_str[0])  # это прыжок
        address += jump
        if hex(address) not in names_func:
            name = "L" + str(names_func["0"])
            names_func[hex(address)] = name
            names_func["0"] += 1
        return '%7s\t%s, %s <%s>\n' % ("jal", reg[int(bit_str[20:25], 2)], hex(address), names_func[hex(address)])
    elif opcode == "1100111":
        return '%7s\t%s, %d(%s)\n' % ("jalr", reg[int(bit_str[20:25], 2)], int(bit_str[:12], 2) - 2 ** 12 * int(bit_str[0]),
                                      reg[int(bit_str[12:17], 2)])
    elif opcode == "1100011":
        im = int(bit_str[0] + bit_str[24] + bit_str[1:7] + bit_str[20:24], 2) * 2 - 2 ** 13 * int(bit_str[0])
        im += address
        if hex(im) in names_func:
            name = names_func[hex(im)]
        else:
            name = "L" + str(names_func["0"])
            names_func[hex(im)] = name
            names_func["0"] += 1

        r = reg[int(bit_str[7:12], 2)]
        comm = ""
        if bit_str[17:20] == "000":
            comm = "beq"
        elif bit_str[17:20] == "001":
            comm = "bne"
        elif bit_str[17:20] == "100":
            comm = "blt"
        elif bit_str[17:20] == "101":
            comm = "bge"
        elif bit_str[17:20] == "110":
            comm = "bltu"
        elif bit_str[17:20] == "111":
            comm = "bgeu"
        return '%7s\t%s, %s, %s, <%s>\n' % (comm, reg[int(bit_str[12:17], 2)], r, hex(im), name)
    elif opcode == "0110011":
        r = reg[int(bit_str[7:12], 2)]
        command = ""
        if bit_str[:7] == "0000001":
            if bit_str[17:20] == "000":
                command = "mul"
            elif bit_str[17:20] == "001":
                command = "mulh"
            elif bit_str[17:20] == "010":
                command = "mulhsu"
            elif bit_str[17:20] == "011":
                command = "mulhu"
            elif bit_str[17:20] == "100":
                command = "div"
            elif bit_str[17:20] == "101":
                command = "divu"
            elif bit_str[17:20] == "110":
                command = "rem"
            elif bit_str[17:20] == "111":
                command = "remu"
        else:
            if bit_str[17:20] == "000":
                if bit_str[1] == "0":
                    command = "add"
                else:
                    command = "sub"
            elif bit_str[17:20] == "001":
                command = "sll"
            elif bit_str[17:20] == "010":
                command = "slt"
            elif bit_str[17:20] == "011":
                command = "sltu"
            elif bit_str[17:20] == "100":
                command = "xor"
            elif bit_str[17:20] == "101":
                if bit_str[1] == "0":
                    command = "srl"
                else:
                    command = "sra"
            elif bit_str[17:20] == "110":
                command = "or"
            elif bit_str[17:20] == "111":
                command = "and"
        return '%7s\t%s, %s, %s\n' % (command, reg[int(bit_str[20:25], 2)], reg[int(bit_str[12:17], 2)], r)
    elif opcode == "0010011":
        im = int(bit_str[:12], 2) - int(bit_str[0]) * 2 ** 12
        command = ""
        if bit_str[17:20] == "000":
            command = "addi"
        elif bit_str[17:20] == "001":
            im = int(bit_str[7:12], 2)
            command = "slli"
        elif bit_str[17:20] == "010":
            command = "slti"
        elif bit_str[17:20] == "011":
            command = "sltiu"
        elif bit_str[17:20] == "100":
            command = "xori"
        elif bit_str[17:20] == "101":
            im = int(bit_str[7:12], 2)
            if bit_str[1] == "0":
                command = "srli"
            else:
                command = "srai"
        elif bit_str[17:20] == "110":
            command = "ori"
        elif bit_str[17:20] == "111":
            command = "andi"
        return '%7s\t%s, %s, %s\n' % (command, reg[int(bit_str[20:25], 2)], reg[int(bit_str[12:17], 2)], im)
    elif opcode == "0000011":
        command = ""
        if bit_str[17:20] == "000":
            command = "lb"
        elif bit_str[17:20] == "001":
            command = "lh"
        elif bit_str[17:20] == "010":
            command = "lw"
        elif bit_str[17:20] == "100":
            command = "lbu"
        elif bit_str[17:20] == "101":
            command = "lhu"
        return '%7s\t%s, %d(%s)\n' % (command, reg[int(bit_str[20:25], 2)], int(bit_str[:12], 2) - 2 ** 12 * int(bit_str[0]),
                                      reg[int(bit_str[12:17], 2)])
    elif opcode == "0100011":
        command = ""
        im = int(bit_str[:7] + bit_str[20:25], 2) - 2 ** 12 * int(bit_str[0])
        if bit_str[17:20] == "000":
            command = "sb"
        elif bit_str[17:20] == "001":
            command = "sh"
        elif bit_str[17:20] == "010":
            command = "sw"
        return '%7s\t%s, %d(%s)\n' % (command, reg[int(bit_str[7:12], 2)], im, reg[int(bit_str[12:17], 2)])
    elif opcode == "1110011":
        if bit_str[11] == "0":
            return '%7s\n' % "ecall"
        else:
            return '%7s\n' % "ebreak"
    elif bit_str == "00000001000000000000000000001111":
        return '%7s\n' % "pause"
    elif bit_str == "10000011001100000000000000001111":
        return '%7s\n' % "fence.tso"
    elif opcode == "0001111":
        p_fence = ("i" if bit_str[4] == "1" else "") + ("o" if bit_str[5] == "1" else "") + (
            "r" if bit_str[6] == "1" else "") + ("w" if bit_str[7] == "1" else "")
        s_fence = ("i" if bit_str[8] == "1" else "") + ("o" if bit_str[9] == "1" else "") + (
            "r" if bit_str[10] == "1" else "") + ("w" if bit_str[11] == "1" else "")
        return '%7s\t%s, %s\n' % ("fence", p_fence, s_fence)
    return "invalid_instruction"


def transfer_hex(our_byts):
    s = str(hex(int.from_bytes(our_byts, 'little')))[2:]
    while len(s) < 8:
        s = '0' + s
    return s


class title:
    def __init__(self, our_bytes, index):
        self.p_type = our_bytes[index:index + 4]
        index += 4
        self.p_offset = our_bytes[index:index + 4]
        index += 4
        self.p_vaddr = our_bytes[index:index + 4]
        index += 4
        self.p_paddr = our_bytes[index:index + 4]
        index += 4
        self.p_filesz = our_bytes[index:index + 4]
        index += 4
        self.memsz = our_bytes[index:index + 4]
        index += 4
        self.p_flags = our_bytes[index:index + 4]
        index += 4
        self.p_align = our_bytes[index:index + 4]


class section:
    def __init__(self, our_bytes):
        self.sh_name = our_bytes[0:4]
        self.sh_type = our_bytes[4:8]
        self.sg_flags = our_bytes[8:12]
        self.sh_addr = our_bytes[12:16]
        self.sh_offset = our_bytes[16:20]
        self.sh_size = our_bytes[20:24]
        self.sh_link = our_bytes[24:28]
        self.sh_info = our_bytes[28:32]
        self.sh_addralign = our_bytes[32:36]
        self.sh_entsize = our_bytes[36:40]


class elf_file:
    def __init__(self, our_bytes):
        self.our_bytes = our_bytes
        # Заголовок elf-file
        self.e_ident = our_bytes[:16]
        self.e_type = our_bytes[16:18]
        self.e_machine = our_bytes[18:20]
        self.e_version = our_bytes[20:24]
        self.e_entry = our_bytes[24:28]
        self.e_phoff = our_bytes[28:32]
        self.e_shoff = our_bytes[32:36]
        self.flags = our_bytes[36:40]
        self.e_ehsize = our_bytes[40:42]
        self.e_phentsize = our_bytes[42:44]
        self.e_phnum = our_bytes[44:46]
        self.e_shentsize = our_bytes[46:48]
        self.e_shnum = our_bytes[48:50]
        self.e_shstrndx = our_bytes[50:52]

        # Поля заголовка программы
        self.titeles = list()
        index = int.from_bytes(self.e_phoff, 'little')
        for i in range(int.from_bytes(self.e_phnum, 'little')):
            value = title(our_bytes, index)
            index += int.from_bytes(self.e_phentsize, 'little')
            self.titeles.append(value)

        # Поля заголовка секции
        self.page_title = list()
        index = int.from_bytes(self.e_shoff, 'little')
        len_title = int.from_bytes(self.e_shentsize, 'little')
        for i in range(int.from_bytes(self.e_shnum, 'little')):
            value = section(our_bytes[index: index + len_title])
            index += len_title
            self.page_title.append(value)

        # Специальный адрес
        self.min_address = 0

    def symtab(self):
        answer_ = "\n.symtab\n"
        symtb = section("")
        address = 0
        is_found = False
        for sh in self.page_title:
            if int.from_bytes(sh.sh_type, 'little') == 2:
                symtb = sh
            if (int.from_bytes(sh.sh_type, 'little') == 3) and (not is_found):
                address = int.from_bytes(sh.sh_offset, 'little')
                is_found = True

        if int.from_bytes(symtb.sh_offset, 'little') + int.from_bytes(symtb.sh_size, 'little') > len(self.our_bytes):
            raise Exception
        information = self.our_bytes[int.from_bytes(symtb.sh_offset, 'little'): int.from_bytes(symtb.sh_offset,
                                                                                               'little') + int.from_bytes(
            symtb.sh_size, 'little')]
        size_str = int.from_bytes(symtb.sh_entsize, 'little')

        answer_ += (('\n%6s %-17s %5s %-8s %-8s %-8s %6s %s\n' % (
            "Symbol", "Value", "Size", "Type", "Bind", "Vis", "Index", "Name")))

        for i in range(len(information) // size_str):
            value = hex(int.from_bytes(information[4 + i * size_str:8 + size_str * i], 'little'))
            size = int.from_bytes(information[8 + i * size_str:12 + size_str * i], 'little')
            bind = dict_bind[information[12 + i * size_str] // 16]
            type_ = dict_type[information[12 + i * size_str] % 16]
            vis = dict_vis[information[13 + i * size_str]]
            index = int.from_bytes(information[14 + i * size_str:16 + i * size_str], 'little')
            if index in dict_index.keys():
                index = dict_index[index]
            name = ""
            ind = address + int.from_bytes(information[i * size_str: 4 + i * size_str], 'little')
            while self.our_bytes[ind] != 0:
                name += chr(self.our_bytes[ind])
                ind += 1
            answer_ += ('[%4i] 0x%-15s %5i %-8s %-8s %-8s %6s %s\n' % (i, value[2:].upper(), size, type_, bind, vis, index, name))
            if type_ == "FUNC":
                names_func[value] = name
                if int(value, 16) < self.min_address or self.min_address == 0:
                    self.min_address = int(value, 16)
        return answer_

    def text(self):
        answer = []
        index_in_list = int.from_bytes(self.e_shstrndx, 'little')
        our_title = self.page_title[index_in_list]
        address = int.from_bytes(our_title.sh_offset, 'little')
        text_section = title("", 0)

        for sh in self.page_title:
            name = ""
            ind = int.from_bytes(sh.sh_name, 'little')
            while self.our_bytes[ind + address] != 0:
                name += chr(self.our_bytes[ind + address])
                ind += 1
            if name == ".text":
                text_section = sh
                break

        offset = int.from_bytes(text_section.sh_offset, 'little')
        size = int.from_bytes(text_section.sh_size, 'little')
        link = int.from_bytes(text_section.sh_link, 'little')

        for i in range(size // 4):
            tb2 = transfer_hex(self.our_bytes[offset + i * 4:offset + 4 * (i + 1)])
            s = str(bin(int.from_bytes(self.our_bytes[offset + i * 4:offset + 4 * (i + 1)], 'little')))[2:]
            while len(s) < 32:
                s = "0" + s
            address = self.min_address + 4 * i
            answer.append(
                ['   %05s:\t%08s\t%s' % (str(hex(address))[2:], str(tb2), command_parce(s, address)), address])
        answer_str = ".text\n"
        for i in range(len(answer)):
            if hex(answer[i][1]) in names_func:
                adr = hex(answer[i][1])[2:]
                while (len(adr)) < 8:
                    adr = "0" + adr
                answer_str += ('\n%08s \t<%s>:\n' % (adr, names_func[hex(answer[i][1])]))
            answer_str += answer[i][0]
        return answer_str


if __name__ == '__main__':
    sys.argv[1:]

with open(sys.argv[1], 'rb') as our_elf_file:
    bits = our_elf_file.read()

elf = elf_file(bits)
st_sym = elf.symtab()
st_text = elf.text()
answer = st_text + '\n' + st_sym

if len(sys.argv) == 3:
    with open(sys.argv[2], 'w') as outfile:
        outfile.write(answer)
else:
    print(answer)
