package main

import (
	"bufio"
	"encoding/hex"
	"fmt"
	"os"
	"strings"
)

func main() {
	// Abrindo o arquivo .hex
	file, err := os.Open("../info/1_empty.hex.txt")
	if err != nil {
		fmt.Println("Erro ao abrir o arquivo:", err)
		return
	}
	defer file.Close()

	// Outputting separator
	fmt.Println("--------------------------------------------------------------------------------")

	// Setting memory offset to 0x80000000
	const offset = 0x80000000

	// Creating 32 registers initialized with zero and labels
	var x [32]uint32
	xLabels := [32]string{
		"zero", "ra", "sp", "gp", "tp", "t0", "t1", "t2", "s0", "s1", "a0", "a1", "a2", "a3", "a4", "a5", "a6", "a7",
		"s2", "s3", "s4", "s5", "s6", "s7", "s8", "s9", "s10", "s11", "t3", "t4", "t5", "t6",
	}

	// Creating pc register initialized with memory offset
	var pc uint32 = offset

	// Creating 32 KiB memory for both data and instructions
	mem := make([]byte, 32*1024)

	// Reading and processing each line in the hex file
	scanner := bufio.NewScanner(file)
	for scanner.Scan() {
		line := strings.TrimSpace(scanner.Text())
		if len(line) > 0 && line[0] == '@' {
			// Process address
			address := uint32(0)
			_, err := fmt.Sscanf(line, "@%x", &address)
			if err != nil {
				fmt.Println("Erro ao ler o endereço:", err)
				continue
			}
			pc = address
			fmt.Printf("Endereço carregado: 0x%08X\n", pc)
		} else {
			// Process data (hex bytes)
			hexData := strings.ReplaceAll(line, " ", "")
			data, err := hex.DecodeString(hexData)
			if err != nil {
				fmt.Println("Erro ao decodificar os dados hexadecimais:", err)
				continue
			}

			// Log the data being processed
			fmt.Printf("Processando dados hexadecimais para o endereço 0x%08X: %s\n", pc, hexData)

			// Storing the data in memory
			for i, byteValue := range data {
				mem[pc-offset+uint32(i)] = byteValue
				// Log each byte written to memory
				fmt.Printf("Escrevendo byte 0x%02X no endereço 0x%08X\n", byteValue, pc-offset+uint32(i))
			}
			fmt.Printf("Dados carregados no endereço 0x%08X: ", pc)
			for _, b := range data {
				fmt.Printf("0x%02X ", b)
			}
			fmt.Println() // Separating the line
			pc += uint32(len(data))
		}
	}

	if err := scanner.Err(); err != nil {
		fmt.Println("Erro ao ler o arquivo:", err)
		return
	}

	// Outputting separator
	fmt.Println("--------------------------------------------------------------------------------")

	// Setting run condition
	run := true

	// Loop while condition is true
	for run {
		// Reading instruction from memory (4 byte alignment)
		instruction := uint32(mem[(pc-offset)]<<24) | uint32(mem[(pc-offset)+1])<<16 | uint32(mem[(pc-offset)+2])<<8 | uint32(mem[(pc-offset)+3])

		// Log the instruction being processed
		fmt.Printf("Instrução lida da memória em pc = 0x%08X: 0x%08X\n", pc, instruction)

		// Retrieving instruction opcode (6:0)
		opcode := instruction & 0b1111111

		// Retrieving instruction fields
		funct7 := instruction >> 25
		imm := instruction >> 20
		uimm := (instruction & (0b11111 << 20)) >> 20
		rs1 := (instruction & (0b11111 << 15)) >> 15
		funct3 := (instruction & (0b111 << 12)) >> 12
		rd := (instruction & (0b11111 << 7)) >> 7
		imm20 := ((instruction >> 31) << 19) | (((instruction & (0b11111111 << 12)) >> 12) << 11) | (((instruction & (0b1 << 20)) >> 20) << 10) | ((instruction & (0b1111111111 << 21)) >> 21)

		// Outputting instruction being executed
		fmt.Printf("Executando instrução em pc = 0x%08X: opcode = 0x%02X\n", pc, opcode)

		// Checking instruction opcode
		switch opcode {
		case 0b0010011:
			// I type (0010011) - slli (funct3 == 001 and funct7 == 0000000)
			if funct3 == 0b001 && funct7 == 0b0000000 {
				// Calculating operation data
				data := x[rs1] << uimm
				// Outputting instruction to console
				fmt.Printf("0x%08X: slli   %s,%s,%u  %s=0x%08X<<%u=0x%08X\n", pc, xLabels[rd], xLabels[rs1], imm, xLabels[rd], x[rs1], imm, data)
				// Updating register if not x[0] (zero)
				if rd != 0 {
					x[rd] = data
				}
			}
		case 0b1110011:
			// I type (1110011) - ebreak (funct3 == 000 and imm == 1)
			if funct3 == 0b000 && imm == 1 {
				// Outputting instruction to console
				fmt.Printf("0x%08X: ebreak\n", pc)
				// Retrieving previous and next instructions
				previous := uint32(mem[(pc-4-offset)]<<24) | uint32(mem[(pc-4-offset)+1])<<16 | uint32(mem[(pc-4-offset)+2])<<8 | uint32(mem[(pc-4-offset)+3])
				next := uint32(mem[(pc+4-offset)]<<24) | uint32(mem[(pc+4-offset)+1])<<16 | uint32(mem[(pc+4-offset)+2])<<8 | uint32(mem[(pc+4-offset)+3])
				// Halting condition
				if previous == 0x01f01013 && next == 0x40705013 {
					run = false
				}
			}
		case 0b1101111:
			// J type (1101111)
			simm := imm20
			if imm20>>20 != 0 {
				simm = 0xFFF00000
			}
			// Calculating operation address
			address := pc + (simm << 1)
			// Outputting instruction to console
			fmt.Printf("0x%08X: jal    %s,0x%05X    pc=0x%08X,%s=0x%08X\n", pc, xLabels[rd], imm, address, xLabels[rd], pc+4)
			// Updating register if not x[0] (zero)
			if rd != 0 {
				x[rd] = pc + 4
			}
			// Setting next pc minus 4
			pc = address - 4
		default:
			// Outputting error message
			fmt.Printf("erro: opcode de instrução desconhecida em pc = 0x%08X\n", pc)
			// Halting simulation
			run = false
		}

		// Output the state of registers
		fmt.Println("Estado dos registros:")
		for i := 0; i < 32; i++ {
			fmt.Printf("%s = 0x%08X\n", xLabels[i], x[i])
		}

		// Incrementing pc by 4
		pc += 4
	}

	// Outputting separator
	fmt.Println("--------------------------------------------------------------------------------")
}
