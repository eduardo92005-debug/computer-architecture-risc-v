#
# Poxim-V factorial example
# 
# (C) Copyright 2024 Bruno Otavio Piedade Prado
#
# This file is part of Poxim-V.
#
# Poxim-V is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Poxim-V is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Poxim-V.  If not, see <https://www.gnu.org/licenses/>.
#

# Code section
.section .text
# Factorial recursive function
factorial:
    # begin
    begin:
        # Prologue
        addi sp, sp, -16
        sw ra, 0(sp)
    # Base case
    base:
        # Check if n != 0
        bnez a0, recursive
        # Returning 1
        li t0, 1
        j end
    # Recurrence
    recursive:
        # Saving n in stack
        sw a0, 4(sp)
        # factorial(n - 1)
        addi a0, a0, -1
        call factorial
        # Restoring n from stack
        lw a0, 4(sp)
        # Calculating n * fatorial(n - 1)
        mul t0, t0, a0
    # end
    end:
        # Epilogue
        lw ra, 0(sp)
        addi sp, sp, 16
        # Returning value
        mv a0, t0
        ret

# Main function
.global main
main:
    # Prologue
    addi sp, sp, -16
    sw ra, 0(sp)
    # factorial(5)
    li a0, 5
    call factorial
    # Epilogue
    lw ra, 0(sp)
    addi sp, sp, 16
    # Setting return value to zero (success)
    addi a0, zero, 0
    # Returning from call
    ret
