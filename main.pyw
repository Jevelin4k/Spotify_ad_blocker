import asyncio
from winrt.windows.media.control import GlobalSystemMediaTransportControlsSessionManager as MediaManager
import subprocess
import os
import pygetwindow as gw
import psutil
import win32gui
import win32con
import time
import threading
import re

import pystray
from PIL import Image
import sys

# імпорти бібліотек

#///// AD SKIP and RESTART /////

async def get_media_info(target_app: str = None):
    sessions = await MediaManager.request_async()

    # выбираем нужную сессию или берём текущую
    if target_app:
        session = next(
            (s for s in sessions.get_sessions()
             if s.source_app_user_model_id == target_app),
            None
        )
        if session is None:
            pass
            #raise RuntimeError(f"Сессия '{target_app}' не найдена")
    else:
        session = sessions.get_current_session()
        if session is None:
            #raise RuntimeError("Нет активной медиа-сессии")
            pass

    info = await session.try_get_media_properties_async()
    timeline = session.get_timeline_properties()

    info_dict = {
        attr: info.__getattribute__(attr)
        for attr in dir(info)
        if not attr.startswith('_')
    }
    info_dict['genres'] = list(info_dict['genres'])
    info_dict['position_sec'] = timeline.position.total_seconds()
    info_dict['duration_sec'] = timeline.end_time.total_seconds()
    info_dict['source_app'] = session.source_app_user_model_id

    return info_dict


def get_active_window_title():
    active_window = gw.getActiveWindow()
    if active_window:
        return active_window.title
    return None


def kill():
    result = subprocess.Popen('TASKKILL /F /IM Spotify.exe', stdout=subprocess.PIPE,
                              creationflags=subprocess.CREATE_NO_WINDOW)
    #print(result)


def check_for_proc():
    ls = []
    name_ = None
    for proc in psutil.process_iter():
        name = proc.name()
        if name == "Spotify.exe":
            name_ = name
            return True
        else:
            ls.append(name)
            continue

    if name_ not in ls:
        return False

def find_spotify_window():

    def enum_windows_callback(hwnd, windows):
        if win32gui.IsWindowVisible(hwnd):
            window_text = win32gui.GetWindowText(hwnd)
            if "Spotify" in window_text:
                windows.append(hwnd)
        return True

    windows = []
    win32gui.EnumWindows(enum_windows_callback, windows)
    return windows[0] if windows else None

def hide_spotify():
    hwnd = find_spotify_window()
    if hwnd:
        # Скрываем окно (SW_HIDE = 0) [citation:5]
        win32gui.ShowWindow(hwnd, win32con.SW_HIDE)
        #print("Spotify скрыт")
    else:
        #print("Spotify не найден")
        for _ in range(10):
            time.sleep(0.1)
            hwnd = find_spotify_window()
            if hwnd:
                # Скрываем окно (SW_HIDE = 0) [citation:5]
                win32gui.ShowWindow(hwnd, win32con.SW_HIDE)
                #print("Spotify скрыт")

                if hwnd:
                    # Показываем окно (SW_SHOW = 5)
                    win32gui.ShowWindow(hwnd, win32con.SW_SHOW)

                    spotify_windows = gw.getWindowsWithTitle("Spotify")
                    if spotify_windows:
                        spotify_windows[0].minimize()
                    #print("Spotify показан")
                    break
                else:
                    #print("Spotify не найден")
                    continue


def restart_app():
    try:
        kill()
        spotify_path = os.path.expanduser("~") + "\\AppData\\Local\\Microsoft\\WindowsApps\\Spotify.exe"

        time.sleep(1)

        subprocess.Popen(
            [spotify_path, "--minimized", "--quiet"],
            creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NO_WINDOW | subprocess.CREATE_BREAKAWAY_FROM_JOB | subprocess.SW_HIDE
        )
        hide_spotify()
        return True

    except Exception as e:
        #print(e)
        return False


async def play_media():
    while True:
        try:
            sessions = await MediaManager.request_async()
            current_session = sessions.get_current_session()
            TARGET_ID = current_session.source_app_user_model_id
            break
        except Exception:
            await asyncio.sleep(0.5)

    while True:
        await asyncio.sleep(1)

        if 'Spotify' not in current_session.source_app_user_model_id:
            await asyncio.sleep(0.5)
            continue

        if current_session.source_app_user_model_id == TARGET_ID:
            info = await current_session.try_get_media_properties_async()
            info_dict = {song_attr: info.__getattribute__(song_attr) for song_attr in dir(info) if
                         song_attr[0] != '_'}
            info_dict['genres'] = list(info_dict['genres'])

            if info_dict['title'] == '':
                continue

            await current_session.try_skip_next_async()
            await current_session.try_play_async()
            break


async def check_for_ad(current_media_info):
    if current_media_info['title'] == "Advertisement":
        await ad_spot(current_media_info)
        await asyncio.sleep(1)
        return True

    elif current_media_info['title'] in config_mangement().read_config():
        await ad_spot(current_media_info)
        await asyncio.sleep(1)
        return True

async def ad_spot(current_media_info):
    try:
        x = restart_app()
        if x:
            while True:
                spotify_windows = gw.getWindowsWithTitle("Spotify")
                if spotify_windows:
                    await play_media()
                    break
                else:
                    await asyncio.sleep(0.1)
        else:
            check_for_ad(current_media_info)
    except Exception as e:
        print(e)

    await asyncio.sleep(1)


#/////CONFIG//////

class config_mangement:
    def __init__(self):
        with open('config.txt', 'r', encoding='utf-8') as cfg:
            read_s = False
            self.ad_list = []
            for line in cfg.readlines():
                line = line.strip()

                if line == '//START//':
                    read_s = True
                    continue
                elif line == '//END//':
                    break
                if read_s:
                    self.ad_list.append(line)

    def read_config(self):
        return self.ad_list

    def write_config(self, text):
        with open('config.txt', 'r+', encoding='utf-8') as cfg:
            lines = cfg.readlines()

            if '//END//\n' in lines:
                idx = lines.index('//END//\n')
                lines.insert(idx, text + '\n')  # вставляємо перед //END//
            else:
                lines.append(text + '\n')
                lines.append('//END//\n')

            cfg.seek(0)
            cfg.writelines(lines)
            cfg.truncate()

    def delete_config(self):
        with open('config.txt', 'r', encoding='utf-8') as cfg:
            content = cfg.read()
        content = re.sub(r'(//START//\n).*?(//END//)', r'\1\2', content, flags=re.DOTALL)
        with open('config.txt', 'w', encoding='utf-8') as cfg:
            cfg.write(content)


#/////MAIN/////

async def main():
    while True:
        try:
            loop = asyncio.get_event_loop()
            sessions = await MediaManager.request_async()
            current = sessions.get_current_session()
            track_changed_event = asyncio.Event()

            def on_track_changed(session, args):
                loop.call_soon_threadsafe(track_changed_event.set)

            current.add_media_properties_changed(on_track_changed)

            try:
                info = await get_media_info()
                # print(info)

                if 'Spotify' not in info['source_app']:
                    continue

                if await check_for_ad(info) is True:
                    continue

                print(info)
                await asyncio.sleep(0.5)

                time_left = int(info['duration_sec']) - int(info['position_sec'])
                track_changed_event.clear()

                try:
                    await asyncio.wait_for(track_changed_event.wait(), timeout=time_left)
                except asyncio.TimeoutError:
                    pass

            except Exception as e:
                # print(e)
                await asyncio.sleep(1)
                continue

        except Exception:
            continue

#///// Menu /////


def on_exit(icon, item):
    icon.stop()
    sys.exit()


def manual_add_sync(icon, item):
    asyncio.run(manual_add())

async def manual_add():
    info = await get_media_info()
    config_mangement().write_config(info['title'])


def delete_config_sync(icon, item):
    asyncio.run(delete_config())

async def delete_config():
    config_mangement().delete_config()


def load_icon():
    img = Image.open('logo.png')

    menu = pystray.Menu(
        pystray.MenuItem('Manual add ad to list', manual_add_sync),
        pystray.MenuItem('Clear config', delete_config_sync),
        pystray.MenuItem('Exit', on_exit)
    )

    icon = pystray.Icon('SAB', img, 'Spotify Ad Blocker 4.0', menu)
    icon.run()


if __name__ == '__main__':
    while True:
        time.sleep(1)
        tray_thread = threading.Thread(target=load_icon, daemon=True)
        tray_thread.start()

        try:
            for proc in psutil.process_iter():
                name = proc.name()
                if name == "Spotify.exe":
                    try:
                        asyncio.run(main())

                        current_media_info = None
                        spotify_windows = None
                        name = None
                        proc = None
                        #main_proc = None
                    except Exception as e:
                        #print(e)
                        current_media_info = None
                        spotify_windows = None
                    break

                else:
                    continue
        except Exception:
            pass