import pygame
import time

# Pygame Initialization
pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("8080 CPU Simulator")
font = pygame.font.Font(None, 30)

# CPU State
cpu_state = {
    "A": 0x00,  # Accumulator
    "B": 0x00, "C": 0x00,
    "D": 0x00, "E": 0x00,
    "H": 0x00, "L": 0x00,
    "PC": 0x0000,  # Program Counter
    "SP": 0xFFFF,  # Stack Pointer
    "IR": 0x00,    # Instruction Register
    "Flags": {"Z": 0, "S": 0, "P": 0, "CY": 0},  # Zero, Sign, Parity, Carry
}

memory = [0x00] * 0x10000  # 64KB Memory
input_text = "06 01 04 FE 64 C2 02 00 76"  # Input for machine code
program_loaded = False  # Flag to indicate program is loaded
register_timers = {}  # Track timers for register color changes

# Helper Functions
def reset_system():
    """Reset all registers, flags, and memory."""
    global cpu_state, memory
    cpu_state.update({
        "A": 0x00,
        "B": 0x00, "C": 0x00,
        "D": 0x00, "E": 0x00,
        "H": 0x00, "L": 0x00,
        "PC": 0x0000,
        "SP": 0xFFFF,
        "IR": 0x00,
        "Flags": {"Z": 0, "S": 0, "P": 0, "CY": 0},
    })
    memory = [0x00] * 0x10000  # Reset memory to zeros

def highlight_register(reg):
    """Highlight a register to show it was recently accessed."""
    global register_timers
    register_timers[reg] = time.time()

def manage_register_timers():
    """Manage the highlight timers for registers."""
    global register_timers
    current_time = time.time()
    for reg in list(register_timers.keys()):
        if current_time - register_timers[reg] >= 1.0:  # 1 second duration
            del register_timers[reg]

def update_flags(value):
    """Update the CPU flags based on the result."""
    global cpu_state
    value = value & 0xFF  # Ensure 8-bit result
    cpu_state["Flags"]["Z"] = int(value == 0)  # Zero flag
    cpu_state["Flags"]["S"] = int(value & 0x80 != 0)  # Sign flag
    cpu_state["Flags"]["P"] = int(bin(value).count('1') % 2 == 0)  # Parity flag
    cpu_state["Flags"]["CY"] = int(value > 0xFF)  # Carry flag

def get_address():
    """Fetch a 16-bit address from the current program counter."""
    global cpu_state, memory
    low_byte = memory[cpu_state["PC"]]
    high_byte = memory[cpu_state["PC"] + 1]
    return (high_byte << 8) | low_byte

def draw_memory_map(screen):
    """Draw a memory map matrix of the first 64 bytes."""
    x, y = 300, 50  # Starting position of the matrix
    cell_size = 40  # Size of each square
    rows, cols = 8, 8  # 8x8 matrix

    for i in range(rows):
        for j in range(cols):
            addr = i * cols + j
            value = memory[addr]
            color = (255, 255, 255) #if value == 0x00 else (0, 255, 0)  # Highlight non-zero values
            pygame.draw.rect(screen, color, (x + j * cell_size, y + i * cell_size, cell_size, cell_size))
            text = font.render(f"{value:02X}", True, (0, 0, 0))
            screen.blit(text, (x + j * cell_size + 10, y + i * cell_size + 10))

# Fetch-Decode-Execute Cycle
def fetch_decode_execute():
    global cpu_state, memory
    pc = cpu_state["PC"]
    ir = memory[pc]  # Fetch instruction
    cpu_state["IR"] = ir  # Store the current instruction
    highlight_register("PC")  # Highlight PC
    cpu_state["PC"] += 1  # Increment PC to point to the next byte

    # Decode and execute instructions
    if ir == 0x3E:  # MVI A, data
        cpu_state["A"] = memory[cpu_state["PC"]]
        highlight_register("A")
        cpu_state["PC"] += 1

    elif ir == 0x06:  # MVI B, data
        cpu_state["B"] = memory[cpu_state["PC"]]
        highlight_register("B")
        cpu_state["PC"] += 1

    elif ir == 0x0E:  # MVI C, data
        cpu_state["C"] = memory[cpu_state["PC"]]
        highlight_register("C")
        cpu_state["PC"] += 1

    elif ir == 0x16:  # MVI D, data
        cpu_state["D"] = memory[cpu_state["PC"]]
        highlight_register("D")
        cpu_state["PC"] += 1

    elif ir == 0x1E:  # MVI E, data
        cpu_state["E"] = memory[cpu_state["PC"]]
        highlight_register("E")
        cpu_state["PC"] += 1

    elif ir == 0x26:  # MVI H, data
        cpu_state["H"] = memory[cpu_state["PC"]]
        highlight_register("H")
        cpu_state["PC"] += 1

    elif ir == 0x2E:  # MVI L, data
        cpu_state["L"] = memory[cpu_state["PC"]]
        highlight_register("L")
        cpu_state["PC"] += 1

    elif ir == 0x04:  # INR B
        cpu_state["B"] = (cpu_state["B"] + 1) & 0xFF
        highlight_register("B")
        update_flags(cpu_state["B"])

    elif ir == 0x0C:  # INR C
        cpu_state["C"] = (cpu_state["C"] + 1) & 0xFF
        highlight_register("C")
        update_flags(cpu_state["C"])

    elif ir == 0x14:  # INR D
        cpu_state["D"] = (cpu_state["D"] + 1) & 0xFF
        highlight_register("D")
        update_flags(cpu_state["D"])

    elif ir == 0x1C:  # INR E
        cpu_state["E"] = (cpu_state["E"] + 1) & 0xFF
        highlight_register("E")
        update_flags(cpu_state["E"])

    elif ir == 0x24:  # INR H
        cpu_state["H"] = (cpu_state["H"] + 1) & 0xFF
        highlight_register("H")
        update_flags(cpu_state["H"])

    elif ir == 0x2C:  # INR L
        cpu_state["L"] = (cpu_state["L"] + 1) & 0xFF
        highlight_register("L")
        update_flags(cpu_state["L"])

    elif ir == 0x3C:  # INR A
        cpu_state["A"] = (cpu_state["A"] + 1) & 0xFF
        highlight_register("A")
        update_flags(cpu_state["A"])

    elif ir == 0x76:  # HLT (Halt)
        return False

    elif ir == 0xFE:  # CPI data (compare A with immediate data)
        compare_value = memory[cpu_state["PC"]]
        highlight_register("A")
        update_flags(cpu_state["A"] - compare_value)  # Update flags based on subtraction
        cpu_state["PC"] += 1

    elif ir == 0xCA:  # JZ addr (Jump if zero)
        addr = get_address()
        if cpu_state["Flags"]["Z"]:  # Check zero flag
            cpu_state["PC"] = addr
        else:
            cpu_state["PC"] += 2

    elif ir == 0xC3:  # JMP addr (Unconditional jump)
        cpu_state["PC"] = get_address()

    elif ir == 0xC2:  # JNZ addr (Jump if not zero)
        addr = get_address()
        if not cpu_state["Flags"]["Z"]:  # Check zero flag
            cpu_state["PC"] = addr
        else:
            cpu_state["PC"] += 2

    elif ir == 0xD2:  # JNC addr (Jump if no carry)
        addr = get_address()
        if not cpu_state["Flags"]["CY"]:  # Check carry flag
            cpu_state["PC"] = addr
        else:
            cpu_state["PC"] += 2

    elif ir == 0xDA:  # JC addr (Jump if carry)
        addr = get_address()
        if cpu_state["Flags"]["CY"]:  # Check carry flag
            cpu_state["PC"] = addr
        else:
            cpu_state["PC"] += 2

    elif ir == 0xCD:  # CALL addr (Call subroutine)
        addr = get_address()
        # Push current PC onto stack
        cpu_state["SP"] -= 2
        memory[cpu_state["SP"]] = (cpu_state["PC"] & 0xFF)  # Low byte
        memory[cpu_state["SP"] + 1] = (cpu_state["PC"] >> 8) & 0xFF  # High byte
        highlight_register("SP")
        # Jump to the subroutine
        cpu_state["PC"] = addr

    elif ir == 0xC9:  # RET (Return from subroutine)
        # Pop return address from stack
        low_byte = memory[cpu_state["SP"]]
        high_byte = memory[cpu_state["SP"] + 1]
        cpu_state["PC"] = (high_byte << 8) | low_byte
        cpu_state["SP"] += 2
        highlight_register("SP")

    time.sleep(0.5)  # Simulate clock cycle
    return True

# Draw CPU
def draw_cpu(screen, state):
    screen.fill((0, 0, 0))  # Clear screen

    # Draw Registers
    x, y = 50, 50
    for reg, value in state.items():
        if isinstance(value, int):
            # Highlight recently accessed registers
            color = (0, 255, 0) if reg in register_timers else (0, 128, 255)
            pygame.draw.rect(screen, color, (x, y, 100, 40))
            text = font.render(f"{reg}: {value:02X}", True, (255, 255, 255))
            screen.blit(text, (x + 10, y + 10))
            y += 50

    # Draw Memory Map
    draw_memory_map(screen)

    # Draw Buttons
    pygame.draw.rect(screen, (0, 255, 0), (630, 50, 150, 40))  # Run Button
    text = font.render("Run Program", True, (0, 0, 0))
    screen.blit(text, (640, 60))

    pygame.draw.rect(screen, (255, 0, 0), (630, 100, 150, 40))  # Reset Button
    text = font.render("Reset", True, (255, 255, 255))
    screen.blit(text, (640, 110))

    pygame.draw.rect(screen, (0, 0, 255), (630, 150, 150, 40))  # Halt Button
    text = font.render("Halt", True, (255, 255, 255))
    screen.blit(text, (640, 160))

    # Draw Input Box
    pygame.draw.rect(screen, (255, 255, 255), (50, 500, 700, 40))
    text = font.render(input_text, True, (0, 0, 0))
    screen.blit(text, (60, 510))

    pygame.display.flip()


# Load Program into Memory
def load_program(program):
    global memory, cpu_state
    program = program.split()
    for i, byte in enumerate(program):
        memory[cpu_state["PC"] + i] = int(byte, 16)

# Main Loop
def main():
    global input_text, program_loaded, cpu_state, executing

    clock = pygame.time.Clock()
    running = True
    executing = False  # Execution flag

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                # Capture text input
                if event.key == pygame.K_RETURN:
                    program_loaded = True
                elif event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]
                else:
                    input_text += event.unicode

            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Check if "Run Program" button is clicked
                if 630 <= event.pos[0] <= 780 and 50 <= event.pos[1] <= 90 and program_loaded:
                    load_program(input_text)
                    executing = True

                # Check if "Reset" button is clicked
                if 630 <= event.pos[0] <= 780 and 100 <= event.pos[1] <= 140:
                    reset_system()
                    executing = False  # Stop execution after reset

                # Check if "Halt" button is clicked
                if 630 <= event.pos[0] <= 780 and 150 <= event.pos[1] <= 190:
                    executing = False

        # Manage Register Highlight Timers
        manage_register_timers()

        # Execute Program if running
        if executing:
            executing = fetch_decode_execute()

        draw_cpu(screen, cpu_state)
        clock.tick(30)  # Limit to 30 FPS

    pygame.quit()

if __name__ == "__main__":
    main()
