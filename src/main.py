import numpy as np

BASE_ADDRESS = 0x80000000  # Endereço base inicial no arquivo `.hex`
MEMORY_SIZE = 1024 * 1024    # 32 KiB de memória
TEXT = '''
6F 00 00 0A 6F 00 40 08 6F 00 00 08 6F 00 C0 07
6F 00 80 07 6F 00 40 07 6F 00 00 07 6F 00 C0 06
6F 00 80 06 6F 00 40 06 6F 00 00 06 6F 00 C0 05
6F 00 80 05 00 00 00 00 00 00 00 00 00 00 00 00
17 05 00 00 13 05 05 08 97 05 00 00 93 85 85 07
23 20 05 00 13 05 45 00 E3 4C B5 FE 67 80 00 00
13 01 01 FF 23 22 A1 00 13 05 00 02 B7 05 02 00
93 85 65 02 23 20 B1 00 B3 05 20 00 EF 00 40 01
13 01 01 01 6F 00 00 00 13 05 10 00 6F F0 5F FD
13 10 F0 01 73 00 10 00 13 50 70 40 67 80 00 00
17 81 00 00 13 01 01 F6 EF F0 9F F9 EF 00 C0 00
6F F0 1F FB 00 00 00 00 13 05 00 00 67 80 00 00
'''

def load_hex_to_memory_from_text(TEXT, mem, base_address):
    lines = TEXT.strip().splitlines()
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
    load_hex_to_memory_from_text(TEXT, mem, MEMORY_SIZE)
    
    # Preenchendo memória com instruções de teste
    


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
        print(f"Processing instruction at 0x{pc:08x}: opcode={opcode:08b}, instruction=0x{instruction:08x}")
        # Processando instruções
        if opcode == 0b0010011 and (funct3 == 0b001 and funct7 == 0b0000000):  # Tipo I (ex: slli)  # slli
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
            #imm20 = (instruction >> 12) & 0xFFFFF
            simm = imm20 if (imm20 >> 20) == 0 else (0xFFF00000 | imm20)
            address = pc + (simm << 1)
            print(f"0x{pc:08x}: jal    {x_label[rd]},0x{address:08x}  "
                  f"pc=0x{address:08x},{x_label[rd]}=0x{pc + 4:08x}")
            if rd != 0:
                x[rd] = pc + 4
            pc = address - 4
        elif opcode == 0b0010111:  # Tipo U (auipc)
            # Imediato de 20 bits (bits 31:12 da instrução)
            imm20 = (instruction >> 12) & 0xFFFFF

            # Extensão de sinal e deslocamento de 12 bits
            sext_imm = imm20 << 12

            # Registrador destino (bits 11:7)
            rd = (instruction >> 7) & 0b11111

            # Calcula o valor do registrador destino
            result = pc + sext_imm

            # Atualiza o registrador destino com o valor calculado
            x[rd] = result & 0xFFFFFFFF  # Garante que o resultado seja tratado como 32 bits

            # Mostra a saída formatada com soma explícita
            print(f"0x{pc:08x}: auipc  {x_label[rd]},0x{imm20:08x}          "
                f"{x_label[rd]}=0x{pc:08x}+0x{sext_imm:08x}=0x{result:08x}")

            # Incrementa o PC para a próxima instrução
            #pc += 4
        elif opcode == 0b0010011:  # Tipo I (addi)
            # Funct3 define qual operação do tipo I está sendo executada
            funct3 = (instruction >> 12) & 0b111
            if funct3 == 0b000:  # ADDI
                imm12 = (instruction >> 20) & 0xFFF  # Imediato de 12 bits
                # Extensão de sinal para 32 bits
                imm12 = imm12 if (imm12 >> 11) == 0 else (0xFFFFF000 | imm12)
                
                rs1 = (instruction >> 15) & 0b11111  # Registrador fonte
                rd = (instruction >> 7) & 0b11111    # Registrador destino
                
                result = x[rs1] + imm12  # Soma o valor do registrador rs1 com o imediato
                x[rd] = result & 0xFFFFFFFF  # Armazena o resultado (ajustado para 32 bits)
                
                print(f"0x{pc:08x}: addi   {x_label[rd]},{x_label[rs1]},{imm12:08x}  "
                    f"{x_label[rd]}=0x{result:08x},{x_label[rs1]}=0x{x[rs1]:08x}")
                
                pc = pc + 4  # Incrementa o PC para a próxima instrução

        else:
            print(f"error: unknown instruction opcode at pc = 0x{pc:08x}, {opcode: 08x}")
            run = False
        
        # Incrementando PC
        pc += 4
    
    # Separator
    print("-" * 80)


if __name__ == "__main__":
    main()
