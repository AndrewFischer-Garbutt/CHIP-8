import numpy as np
import sys 

from window import window 

import time

from random import randint
import pygame

class chip8:
    def __init__(self):
        self.keyboard = np.zeros((16,), dtype=np.uint8)
        self.reg = np.zeros((16,), dtype=np.uint8)

        self.mem = np.zeros((4096,), dtype=np.uint8)

        self.stack = np.zeros((16,), dtype=np.uint16)
        self.stack_pointer = 0

        self.gfx = np.zeros((64 * 32,), dtype=np.uint8)

        self.pc = 0x200
        self.I = 0

        self.sound_timer = 0
        self.delay_timer = 0

        self.inst = -1

        self.print_memory = True

        self.WINDOW_HIGHT = 32
        self.WINDOW_WIDTH = 64
        self.PIXEL_SIZE = 10
        self.DRAW_COLOR = (0,0,0)

        self.wind = window(self.PIXEL_SIZE * self.WINDOW_WIDTH,
                self.PIXEL_SIZE * self.WINDOW_HIGHT,
                self.DRAW_COLOR)

        self.wind.draw_window()


        self.lookup_special_ops = {
                0x00E0 : self.clear_screen,
                0x00EE : self.return_from_subroutine
                }

        self.lookup_vx_vy = {
                0x5000 : self.skip_vx_vy_equal,
                0x8000 : self.store_vy_in_vx,
                0x8001 : self.set_vx_to_vx_or_vy,
                0x8002 : self.set_vx_to_vx_and_vy,
                0x8003 : self.set_vx_to_vx_xor_vy,
                0x8004 : self.add_vy_to_vx,
                0x8005 : self.subtract_vy_from_vx,
                0x8006 : self.shift_vx_left_1,
                0x8007 : self.subtract_vy_from_vx,
                0x800e : self.shift_vx_left_1,
                0x9000 : self.skip_vx_vy_not_equal
                }

        self.lookup_nnn = {
                0x0000 : self.jump_machine_language_subrutine_at_nnn,
                0x1000 : self.jump_to_address_nnn,
                0x2000 : self.execute_subroutine_at_nnn,
                0xA000 : self.store_nnn_in_i_register,
                }

        self.lookup_vx_byte = {
                0x3000 : self.skip_vx_nn_equal,
                0x4000 : self.skip_vx_nn_not_equal,
                0x6000 : self.store_nn_in_vx,
                0x7000 : self.add_nn_to_vx,
                0xc000 : self.set_vx_to_random_number_with_mask_nn,
                0xd000 : self.draw_sprite_at_position_vx_vy
                }

        self.lookup_vx = {
                0xE09E : self.skip_on_key_pressed,
                0xE0A1 : self.skip_on_key_not_press,
                0xF007 : self.store_delay_in_vx,
                0xF00A : self.wait_for_keypress_store_result_in_vx,
                0xF015 : self.set_delay_timer_to_vx,
                0xF018 : self.set_sound_timer_to_vx,
                0xF01E : self.add_vx_to_register_i,
                0xF029 : self.set_i_to_sprite_address,
                0xF033 : self.store_bcd_of_vx,
                0xF055 : self.store_v0_to_vx_in_memory,
                0xF065 : self.fill_registers_with_memory_starting_at_i
                }

        self.debug = True

    def init_memory(self):
        fonts = [
                0xF0, 0x90, 0x90, 0x90, 0xF0,
                0x20, 0x60, 0x20, 0x20, 0x70,
                0xF0, 0x10, 0xF0, 0x80, 0xF0,
                0xF0, 0x10, 0xF0, 0x10, 0xF0,
                0x90, 0x90, 0xF0, 0x10, 0x10,
                0xF0, 0x80, 0xF0, 0x10, 0xF0,
                0xF0, 0x80, 0xF0, 0x90, 0xF0,
                0xF0, 0x10, 0x20, 0x40, 0x40,
                0xF0, 0x90, 0xF0, 0x90, 0xF0,
                0xF0, 0x90, 0xF0, 0x10, 0xF0,
                0xF0, 0x90, 0xF0, 0x90, 0x90,
                0xE0, 0x90, 0xE0, 0x90, 0xE0,
                0xF0, 0x80, 0x80, 0x80, 0xF0,
                0xE0, 0x90, 0x90, 0x90, 0xE0,
                0xF0, 0x80, 0xF0, 0x80, 0xF0,
                0xF0, 0x80, 0xF0, 0x80, 0x80
                ]

        self.mem[0:len(fonts)] = fonts

        if len(sys.argv) > 1:
            with open(sys.argv[1], "rb") as f:
                byte = f.read(1)
                count = 0
                while byte != b"":
                    # Do stuff with byte.
                    if self.debug:
                        print("Reading byte {:02X}".format(int.from_bytes(byte, byteorder='big')))
                    self.mem[count + 0x200] = int.from_bytes(byte, byteorder='big')
                    byte = f.read(1)
                    count += 1
        else:
            print("Please specify a .ch8 file.")

        if self.print_memory:
            print("Wrote:")
            self.dump_hex(self.mem)

    def dump_hex(self, data):
        col_length = 32
        for pos in range(0, len(data), col_length):
            print("".join(["{:02X} ".format(d) for d in data[pos:pos+col_length]]))


    def jump_machine_language_subrutine_at_nnn(self):
        pass

    def clear_screen(self):
        self.wind.clear_screen()

    def return_from_subroutine(self):
        pass

    def jump_to_address_nnn(self):
        self.pc = (self.instr & 0x0fff) - 2

    def execute_subroutine_at_nnn(self):
        # I have questions about how this should
        # by implemented
        self.stack[self.stack_pointer] = self.pc
        self.stack_pointer += 1
        self.pc = (self.instr & 0x0fff) - 2

    def skip_vx_nn_equal(self):
        if self.reg[(self.instr & 0x0f00) >> 8] == self.instr & 0x00ff:
            self.pc += 2

    def skip_vx_nn_not_equal(self):
        if self.reg[(self.instr & 0x0f00) >> 8] != self.instr & 0x00ff:
            self.pc += 2

    def skip_vx_vy_equal(self):
        vx = self.reg[(self.instr & 0x0f00) >> 8]
        vy = self.reg[(self.instr & 0x00f0) >> 4]

        if vx == vy:
            self.pc += 2

    def store_nn_in_vx(self):
        self.reg[(self.instr & 0x0f00) >> 8] = 0x00ff & self.instr

    def add_nn_to_vx(self):
        self.reg[(self.instr & 0x0f00) >> 8] += 0x00ff & self.instr

    def store_vy_in_vx(self):
        vy = self.reg[(self.instr & 0x00f0) >> 4]
        self.reg[(self.instr & 0x0f00) >> 8] = vy

    def set_vx_to_vx_or_vy(self):
        vx = self.reg[(self.instr & 0x0f00) >> 8]
        vy = self.reg[(self.instr & 0x00f0) >> 4]

        self.reg[(self.instr & 0x0f00) >> 8] = vx | vy

    def set_vx_to_vx_and_vy(self):
        vx = self.reg[(self.instr & 0x0f00) >> 8]
        vy = self.reg[(self.instr & 0x00f0) >> 4]

        self.reg[(self.instr & 0x0f00) >> 8] = vx & vy

    def set_vx_to_vx_xor_vy(self):
        vx = self.reg[(self.instr & 0x0f00) >> 8]
        vy = self.reg[(self.instr & 0x00f0) >> 4]

        self.reg[(self.instr & 0x0f00) >> 8] = vx ^ vy

    def add_vy_to_vx(self):
        vx = self.reg[(self.instr & 0x0f00) >> 8]
        vy = self.reg[(self.instr & 0x00f0) >> 4]

        if vx + vy > 0xff:
            self.reg[15] = 1
        else:
            self.reg[15] = 0

        self.reg[(self.instr & 0x0f00) >> 8] = (vx + vy) & 0xffff

    def subtract_vy_from_vx(self):
        vx = self.reg[(self.instr & 0x0f00) >> 8]
        vy = self.reg[(self.instr & 0x00f0) >> 4]

        if vx > vy:
            self.reg[15] = 1
        else:
            self.reg[15] = 0

        self.reg[(self.instr & 0x0f00) >> 8] = vx - vy

    def shift_vx_right_1(self):
        vx = self.reg[(self.instr & 0x0f00) >> 8]
        self.reg[15] = vx % 2
        self.reg[(self.instr & 0x0f00) >> 8] = vx // 2


    def store_vy_minus_vx_in_vx(self):
        vx = self.reg[(self.instr & 0x0f00) >> 8]
        vy = self.reg[(self.instr & 0x00f0) >> 4]

        if vy > vx:
            self.reg[15] = 1
        else:
            self.reg[15] = 0

        self.reg[(self.instr & 0x0f00) >> 8] = vy - vx

    def shift_vx_left_1(self):
        vx = self.reg[(self.instr & 0x0f00) >> 8]

        self.reg[15] = (vx >> 15)
        self.reg[(self.instr & 0x0f00) >> 8] = (2 * vx) & 0xffff

    def skip_vx_vy_not_equal(self):
        vx = self.reg[(self.instr & 0x0f00) >> 8]
        vy = self.reg[(self.instr & 0x00f0) >> 4]

        if vx != vy:
            self.pc += 2

    def store_nnn_in_i_register(self):
        self.I = self.instr & 0x0fff

    def jump_to_nnn_plus_v0(self):
        self.pc = ((self.instr & 0x0fff) + self.reg[0]) - 2

    def set_vx_to_random_number_with_mask_nn(self):
        mask = self.instr & 0x00ff

        self.reg[(self.instr & 0x0f00) >> 8] = mask & randint(0,0xff)


    def draw_sprite_at_position_vx_vy(self):
        vx = self.reg[(self.instr & 0x0f00) >> 8]
        vy = self.reg[(self.instr & 0x00f0) >> 4]
        nbytes = self.instr & 0x000f
        self.wind.draw_sprite(vx, vy, self.mem[self.I:self.I + nbytes * 8])

    def skip_on_key_pressed(self):
        pass

    def skip_on_key_not_press(self):
        pass

    def store_delay_in_vx(self):
        pass

    def wait_for_keypress_store_result_in_vx(self):
        pass

    def wait_for_keypress_store_result_in_vx(self):
        vx = self.reg[(self.instr & 0x0f00) >> 8]

    def set_delay_timer_to_vx(self):
        vx = self.reg[(self.instr & 0x0f00) >> 8]
        self.delay_timer = vx

    def set_sound_timer_to_vx(self):
        pass

    def add_vx_to_register_i(self):
        vx = self.reg[(self.instr & 0x0f00) >> 8]
        self.I += vx

    def set_i_to_sprite_address(self):
        vx = self.reg[(self.instr & 0x0f00) >> 8]
        self.I = 5 * vx

    def store_bcd_of_vx(self):
        vx = self.reg[(self.instr & 0x0f00) >> 8]
        self.mem[self.I] = vx // 100
        self.mem[self.I + 1] = (vx // 10) % 10
        self.mem[self.I + 2] = vx % 10

    def store_v0_to_vx_in_memory(self):
        pass

    def fill_registers_with_memory_starting_at_i(self):
        pass

    def run_instruction(self):
        print(self.lookup_vx_vy.keys())
        print("Excuting {0}".format(hex(self.instr)))

        if self.instr in self.lookup_special_ops.keys():
            func = self.lookup_special_ops[self.instr]
        elif self.instr & 0xf000 in self.lookup_nnn.keys():
            func = self.lookup_nnn[self.instr & 0xf000]
        elif self.instr & 0xf00f in self.lookup_vx_vy.keys():
            func = self.lookup_vx_vy[self.instr & 0xf00f]
        elif self.instr & 0xf000 in self.lookup_vx_byte.keys():
            func = self.lookup_vx_byte[self.instr & 0xf000]
        else:
            func = self.lookup_vx[self.instr & 0xf0ff]

        if self.debug:
            print("Running {0}".format(func))
        func()

    def emulationCycles(self):
        running = True
        while running:
            # Fetch
            self.instr = (self.mem[self.pc] << 8) | self.mem[self.pc+1]
            if self.debug:
                print("pc = {0}".format(self.pc))
                print("Combining {0} and {1} into {2}.".format(hex(self.mem[self.pc]), hex(self.mem[self.pc+1]), hex(self.instr)))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            time.sleep(0.4)

            # Decode
            self.run_instruction()

            self.pc += 2


if __name__ == '__main__':
    ch = chip8()
    ch.init_memory()
    ch.emulationCycles()


