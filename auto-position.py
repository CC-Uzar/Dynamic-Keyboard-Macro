import asyncio
import websockets
import math
import win32gui
import win32con
import random
import mouse
from ctypes import wintypes
import ctypes


class Macro:
    def __init__(self):
        self.user32 = ctypes.windll.user32
        self.curr_coord = [0.0, 0.0, 0.0]
        # self.currCoord = [0,0]
        self.start = False
        self.track = False
        self.loop = None
        self.connection = None
        self.hwnd = None
        self.VK_CODES = {
            'f6': win32con.VK_F6,
            'esc': win32con.VK_ESCAPE
        }
        self.find_window_by_title("Minecraft* 1.8.9")

    def refocus_window(self):
        win32gui.ShowWindow(self.hwnd, win32con.SW_MINIMIZE)
        win32gui.ShowWindow(self.hwnd, win32con.SW_RESTORE)
        win32gui.SetForegroundWindow(self.hwnd)

        # Get the window rectangle (left, top, right, bottom)
        rect = win32gui.GetWindowRect(self.hwnd)
        left, top, right, bottom = rect

        # Calculate the center of the window
        center_x = (left + right) // 2
        center_y = ((top + bottom) // 2) + 12

        # Move the mouse to the center of the window
        mouse.move(center_x, center_y, absolute=True)
        mouse.click()

    def find_window_by_title(self, window_title):
        """
        Finds the window handle (HWND) by the window title.
        """
        if not win32gui.IsWindow(self.hwnd):
            hwnd = win32gui.FindWindow(None, window_title)
            if hwnd == 0:
                print(f"Window '{window_title}' not found.")
                print(f"Click the left arrow to find again.")
            else:
                print(f"Found window : {window_title} (HWND: {hwnd})")
                self.hwnd = hwnd
                if self.connection is None:
                    print("Type /cws in your Minecraft client to pair.")
                else:
                    print("Click the right arrow to toggle the macro")
        else:
            print(f"You've already connected to {window_title} (HWND: {self.hwnd})")
            if self.connection is None:
                print("Type /cws in your Minecraft client to pair.")
            else:
                print("Click the right arrow to toggle the macro")


    def send_key_to_window(self, key, action):
        """
        Sends a keypress to the specified window (HWND) using Windows messages.
        :param key: The key to send (e.g., 'a').
        :param action: Whether to 'press', 'hold', or 'release' the key.
        """
        if not win32gui.IsWindow(self.hwnd):
            raise ValueError(f"Specified window \"{win32gui.GetWindowText(self.hwnd)} (HWND: {self.hwnd})\" does not exist.")
        vk_code = ord(key.upper()) if self.VK_CODES.get(key, None) is None else self.VK_CODES[key]
        # Convert the key to a virtual key code

        if action:
            # Only send keydown to simulate holding the key
            win32gui.PostMessage(self.hwnd, win32con.WM_KEYDOWN, vk_code, 0)
            # print(f"Held key '{key}' on window (HWND: {self.hwnd})")

        elif not action:
            # Only send keyup to simulate releasing the key
            win32gui.PostMessage(self.hwnd, win32con.WM_KEYUP, vk_code, 0xC0000001)
            # print(f"Released key '{key}' on window (HWND: {self.hwnd})")

    def send_left_mouse_click(self, action):
        """
        Sends a left mouse click to the specified window (HWND).
        :param action: Whether to 'click', 'hold', or 'release' the left mouse button.
        """

        if action:
            # Simulate holding left mouse button
            win32gui.PostMessage(self.hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, 0)
            # print(f"Held left mouse button on window (HWND: {self.hwnd})")

        elif not action:
            # Simulate releasing left mouse button
            win32gui.PostMessage(self.hwnd, win32con.WM_LBUTTONUP, 0, 0)
            # print(f"Released left mouse button on window (HWND: {self.hwnd})")

    async def hold_to(self, key, coord, to_coord):
        coord_index = 0 if coord.lower() == 'x' else 2
        conditions = [lambda: self.curr_coord[coord_index] <= to_coord,
                      lambda: self.curr_coord[coord_index] >= to_coord]
        condition_index = 0 if to_coord > self.curr_coord[coord_index] else 1
        condition = conditions[condition_index]
        self.send_key_to_window(key, True)
        print(f"Target {coord}:{to_coord}")
        while condition():
            await asyncio.sleep(0.05)
        self.send_key_to_window(key, False)

    async def top_layer(self, row):
        for i in range(row, 19):
            print(f"\nTop Layer : Row {i + 1}")
            if i % 2 == 0:
                to_coord = random.uniform(142.1, 142.4)
                await self.hold_to('a', 'z', to_coord)
            else:
                to_coord = random.uniform(-142.4, -142.1)
                await self.hold_to('d', 'z', to_coord)
            if not i == 18:
                to_coord = float(math.floor(self.curr_coord[0])) + random.uniform(5.1, 5.5)
                await self.hold_to('s', 'x', to_coord)

    async def bottom_layer(self, row):
        for i in range(row, 19):
            print(f"\nBottom Layer : Row {i + 1}")
            if i % 2 == 0:
                to_coord = random.uniform(-142.5, -142.1)
                await self.hold_to('d', 'z', to_coord)
            else:
                to_coord = random.uniform(142.1, 142.5)
                await self.hold_to('a', 'z', to_coord)
            if not i == 18:
                to_coord = float(math.floor(self.curr_coord[0])) + random.uniform(-4.5, -4.1)
                await self.hold_to('w', 'x', to_coord)
            else:
                self.send_key_to_window('f6', True)
                await asyncio.sleep(0.1)
                self.send_key_to_window('f6', False)
                await asyncio.sleep(random.uniform(0.1, 0.3))

    async def macro_loop(self):
        try:
            self.send_key_to_window('5', True)
            await asyncio.sleep(0.1)
            self.send_key_to_window('5', False)
            await asyncio.sleep(random.uniform(0.1,0.3))

            self.send_left_mouse_click(True)
            await asyncio.sleep(0.1)
            self.send_left_mouse_click(False)
            await asyncio.sleep(random.uniform(0.1, 0.4))

            self.send_key_to_window('1', True)
            await asyncio.sleep(0.1)
            self.send_key_to_window('1', False)
            await asyncio.sleep(random.uniform(0.1, 0.3))

            await self.connection.send("(action)::start")
            self.send_left_mouse_click(True)

            if self.curr_coord[1] == 67:
                await self.bottom_layer(int((math.floor(self.curr_coord[0]) - 142) / -5))
                await self.top_layer(0)
            elif self.curr_coord[1] == 70:
                await self.top_layer(int((math.floor(self.curr_coord[0]) - 52) / 5))

            while True:
                await self.bottom_layer(0)
                await self.top_layer(0)
        except asyncio.CancelledError:
            self.send_left_mouse_click(False)
            self.send_key_to_window('w', False)
            self.send_key_to_window('a', False)
            self.send_key_to_window('s', False)
            self.send_key_to_window('d', False)
            self.send_key_to_window('t', True)
            await asyncio.sleep(0.1)
            self.send_key_to_window('t', False)
            self.refocus_window()
            self.send_key_to_window('esc', True)
            await asyncio.sleep(0.1)
            self.send_key_to_window('esc', False)
            raise
        except ValueError as e:
            print(e)

    async def handle_input(self, websocket):
        if self.connection is not None:
            await websocket.send("(log)::Connections full. Try again later.")
            await websocket.close()
            return

        print("Minecraft client connected.")
        if not win32gui.IsWindow(self.hwnd):
            print(f"Minecraft window not not paired, click the left arrow to pair.")
        else:
            print("Click the right arrow to toggle the macro")

        self.connection = websocket
        try:
            async for message in websocket:
                tag = message.split("::")[0]
                content = message.split("::")[1]
                if "(action)" in tag:
                    if content == "start" and not self.start:
                        self.start = True
                        self.loop = asyncio.create_task(self.macro_loop())

                    elif content == "stop" and self.start:
                        self.start = False
                        self.loop.cancel()
                        try:
                            await self.loop
                        except asyncio.CancelledError:
                            print("Killed macro loop.")
                        self.refocus_window()

                elif "(coord)" in tag:
                    self.curr_coord[0] = float(content.split(",")[0])
                    self.curr_coord[1] = math.floor(float(content.split(",")[1]))
                    self.curr_coord[2] = float(content.split(",")[2])

                elif "(log)" in tag:
                    print(content)

        except websockets.exceptions.ConnectionClosed as e:
            print(f"Connection closed unexpectedly: {e}")
        except asyncio.exceptions.IncompleteReadError as e:
            print(f"Incomplete read error: {e}")
        finally:
            self.connection = None
            print("Client disconnected.")

    async def key_input(self):
        while True:
            if self.user32.GetAsyncKeyState(win32con.VK_RIGHT) & 0x8000:  # Right Arrow key
                if not win32gui.IsWindow(self.hwnd):
                    print(f"Minecraft window not found, cancelling macro.")
                    print(f"Click the left arrow to pair with a window.")
                    await asyncio.sleep(1)
                    continue
                await self.toggle_macro()
                await asyncio.sleep(1)  # Prevent rapid toggling
            elif self.user32.GetAsyncKeyState(win32con.VK_LEFT) & 0x8000:  # Left Arrow key
                self.find_window_by_title("Minecraft 1.8.9")
                await asyncio.sleep(1)
            await asyncio.sleep(0.05)  # Polling interval

    async def toggle_macro(self):
        if self.connection is not None:
            if self.start:
                print("Killing macro...")
                await self.connection.send("(action)::stop")
            else:
                print("Starting macro...")
                await self.connection.send("(action)::setup")
        else:
            print("No connection established. Please connect a client.")

    async def main(self):
        async with websockets.serve(self.handle_input, "localhost", 6749) as server:
            await server.serve_forever()


async def main():
    macro = Macro()
    await asyncio.gather(macro.main(),macro.key_input())

if __name__ == "__main__":
    asyncio.run(main())
