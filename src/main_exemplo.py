import numpy as np

BASE_ADDRESS = 0x80000000  # Endereço base inicial no arquivo `.hex`
MEMORY_SIZE = 32 * 1024    # 32 KiB de memória

def load_hex_to_memory_from_file(filename, mem, base_address):
    with open(filename, "r") as file:
        lines = file.readlines()
        current_address = base_address

        for line in lines:
            line = line.strip()
            if line.startswith("@"):
                # Ignora linhas com "@"
                continue
            else:
                # Converte os bytes para inteiros e carrega na memória
                bytes_data = [int(byte, 16) for byte in line.split()]
                for byte in bytes_data:
                    relative_address = current_address - base_address
                    if 0 <= relative_address < len(mem):
                        mem[relative_address] = byte
                        current_address += 1
                    else:
                        raise IndexError(
                            f"Endereço {current_address:08X} fora dos limites."
                        )


def main():
    # Separator
    print("-" * 80)
    
    # Offset de memória
    offset = 0x80000000

    # Registradores e labels
    x = [0] * 32
    x_label = [
        "zero", "ra", "sp", "gp", "tp", "t0", "t1", "t2",
        "s0", "s1", "a0", "a1", "a2", "a3", "a4", "a5",
        "a6", "a7", "s2", "s3", "s4", "s5", "s6", "s7",
        "s8", "s9", "s10", "s11", "t3", "t4", "t5", "t6"
    ]

    # Registrador PC inicializado
    pc = offset

    # Criando memória de 32 KiB
    mem = np.zeros(MEMORY_SIZE, dtype=np.uint8)
    
    # Carregando dados de um arquivo hex para a memória
   # load_hex_to_memory_from_file("../info/1_empty.hex.txt", mem, MEMORY_SIZE)
    
    # Preenchendo memória com instruções de teste
    mem[0x80000000 - offset] = 0xef
    mem[0x80000001 - offset] = 0x00
    mem[0x80000002 - offset] = 0x00
    mem[0x80000003 - offset] = 0x10
    mem[0x80000100 - offset] = 0x13
    mem[0x80000101 - offset] = 0x10
    mem[0x80000102 - offset] = 0xf0
    mem[0x80000103 - offset] = 0x01
    mem[0x80000104 - offset] = 0x73
    mem[0x80000105 - offset] = 0x00
    mem[0x80000106 - offset] = 0x10
    mem[0x80000107 - offset] = 0x00
    mem[0x80000108 - offset] = 0x13
    mem[0x80000109 - offset] = 0x50
    mem[0x8000010a - offset] = 0x70
    mem[0x8000010b - offset] = 0x40

    # Separator
    print("-" * 80)
    
    run = True
    while run:
        # Lendo instrução
        instruction = int.from_bytes(
            mem[(pc - offset):(pc - offset) + 4], byteorder="little"
        )

        # Decodificando instrução
        opcode = instruction & 0b1111111
        funct7 = (instruction >> 25) & 0b1111111
        imm = (instruction >> 20) & 0xFFF
        uimm = (instruction >> 20) & 0b11111
        rs1 = (instruction >> 15) & 0b11111
        funct3 = (instruction >> 12) & 0b111
        rd = (instruction >> 7) & 0b11111
        imm20 = (
            ((instruction >> 31) << 19) |
            (((instruction >> 12) & 0xFF) << 11) |
            (((instruction >> 20) & 1) << 10) |
            ((instruction >> 21) & 0x3FF)
        )
        
        # Processando instruções
        if opcode == 0b0010011:  # Tipo I (ex: slli)
            if funct3 == 0b001 and funct7 == 0b0000000:  # slli
                data = x[rs1] << uimm
                print(f"0x{pc:08x}: slli   {x_label[rd]},{x_label[rs1]},{uimm}  "
                      f"{x_label[rd]}=0x{x[rs1]:08x}<<{uimm}=0x{data:08x}")
                if rd != 0:
                    x[rd] = data
        
        elif opcode == 0b1110011:  # Tipo I (ex: ebreak)
            if funct3 == 0b000 and imm == 1:  # ebreak
                print(f"0x{pc:08x}: ebreak")
                previous = int.from_bytes(
                    mem[(pc - 4 - offset):(pc - offset)], byteorder="little"
                )
                next_inst = int.from_bytes(
                    mem[(pc + 4 - offset):(pc + 8 - offset)], byteorder="little"
                )
                if previous == 0x01f01013 and next_inst == 0x40705013:
                    run = False
        
        elif opcode == 0b1101111:  # Tipo J (ex: jal)
            simm = imm20 if (imm20 >> 20) == 0 else (0xFFF00000 | imm20)
            address = pc + (simm << 1)
            print(f"0x{pc:08x}: jal    {x_label[rd]},0x{address:05x}  "
                  f"pc=0x{address:08x},{x_label[rd]}=0x{pc + 4:08x}")
            if rd != 0:
                x[rd] = pc + 4
            pc = address - 4
        
        else:
            print(f"error: unknown instruction opcode at pc = 0x{pc:08x}")
            run = False
        
        # Incrementando PC
        pc += 4
    
    # Separator
    print("-" * 80)


if __name__ == "__main__":
    main()
