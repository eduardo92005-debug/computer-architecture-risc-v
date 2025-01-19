#
# Poxim-V multiplication/division/remainder example
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
# Multiplication function
multiplication:
    # Multiplication operations
    mul t0, a0, a1
    mulh t1, t0, a2
    mulhsu t2, a1, t0
    mulhu t3, a1, a2
    # Returning from call
    ret

# Division function
division:
    # Division operations
    div t0, a1, a0
    div t1, a0, a0
    div t2, a1, zero
    divu t3, a1, a2
    divu t4, a2, a0
    divu t5, a0, zero
    # Returning from call
    ret

# Remainder function
remainder:
    # Remainder operations
    rem t0, a1, a0
    rem t1, a1, a2
    rem t2, a2, zero
    remu t3, a0, a1
    remu t4, a2, a1
    remu t5, a1, zero
    # Returning from call
    ret

# Main function
.global main
main:
    # Prologue
    addi sp, sp, -16
    sw ra, 0(sp)
    # Setting up arguments
    li a0, -1
    li a1, 1234567
    li a2, 9876543
    # Calling functions
    call multiplication
    call division
    call remainder
    # Epilogue
    lw ra, 0(sp)
    addi sp, sp, 16
    # Setting return value to zero (success)
    addi a0, zero, 0
    # Returning from call
    ret
