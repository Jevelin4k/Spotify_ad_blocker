import asyncio
from winrt.windows.media.control import GlobalSystemMediaTransportControlsSessionManager as MediaManager
import subprocess
import time
import os
import pygetwindow as gw
import psutil
import ctypes
import sys
import win32gui
import win32con
import time


# імпорти бібліотек

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def run_as_admin():
    try:
        if is_admin():
            return  # Уже запущено с правами администратора

        # Запуск текущего скрипта с правами администратора
        try:
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, ' '.join(sys.argv), None, 0)
        except:
            print("Ошибка при попытке запустить с правами администратора")

    except Exception:
        pass


async def get_media_info():
    # получю айди процеса спотифай і ставлю на нього трекер
    try:
        sessions = await MediaManager.request_async()
        current_session = sessions.get_current_session()
        TARGET_ID = current_session.source_app_user_model_id
        # print(f'Активный идентификатор: {current_session.source_app_user_model_id}')
    except Exception:
        pass
        # print('Not ready')

    if current_session is None:
        pass
        # raise Exception('Нет активной медиа-сессии')

    if current_session.source_app_user_model_id == TARGET_ID:
        info = await current_session.try_get_media_properties_async()
        info_dict = {song_attr: info.__getattribute__(song_attr) for song_attr in dir(info) if song_attr[0] != '_'}
        info_dict['genres'] = list(info_dict['genres'])
        return info_dict

    pass
    # raise Exception(f'Программа {TARGET_ID} не является текущей медиа-сессией')


def get_active_window_title():
    active_window = gw.getActiveWindow()
    if active_window:
        return active_window.title
    return None


def kill():
    result = subprocess.Popen('TASKKILL /F /IM Spotify.exe', stdout=subprocess.PIPE,
                              creationflags=subprocess.CREATE_NO_WINDOW)
    print(result)


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
                        spotify_windows = None
                    #print("Spotify показан")
                    break
                else:
                    #print("Spotify не найден")
                    continue


def restart_app():
    try:
        kill()
    except Exception as e:
        print(e)
        pass

    spotify_path = os.path.expanduser("~") + "\\AppData\\Local\\Microsoft\\WindowsApps\\Spotify.exe"

    time.sleep(1)

    subprocess.Popen(
        [spotify_path, "--minimized", "--quiet"],
        creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NO_WINDOW | subprocess.CREATE_BREAKAWAY_FROM_JOB | subprocess.SW_HIDE
    )
    hide_spotify()
    return True

    '''spotify_windows = gw.getWindowsWithTitle("Spotify")
    if spotify_windows:
        spotify_windows[0].minimize()
        spotify_windows = None'''


async def play_media(album_title):
    while True:
        try:
            sessions = await MediaManager.request_async()
            current_session = sessions.get_current_session()
            TARGET_ID = current_session.source_app_user_model_id
            break
        except Exception:
            pass
            # print('wait')

    while True:
        if current_session is None:
            pass

        if current_session.source_app_user_model_id == TARGET_ID:
            info = await current_session.try_get_media_properties_async()
            info_dict = {song_attr: info.__getattribute__(song_attr) for song_attr in dir(info) if
                         song_attr[0] != '_'}
            info_dict['genres'] = list(info_dict['genres'])
            album_title = info_dict['title']

            if album_title == '':
                continue

            await current_session.try_play_async()
            await current_session.try_skip_next_async()
            # print('Воспроизведение запущено!')
            break
        else:
            # raise Exception(f'Программа {TARGET_ID} не является текущей медиа-сессией')
            pass


def main():
    while True:
        try:

            time.sleep(1)

            current_media_info = asyncio.run(get_media_info())
            #print(current_media_info)
            # print(current_media_info)

            '''if input('>>>') == 'y':
                time.sleep(10)
                while True:
                    try:
                        restart_app()
                        time.sleep(1)
                        asyncio.run(play_media(current_media_info['album_title']))
                        break
                    except Exception:
                        print(Exception)
                        continue
            else:
                exit()'''

            if current_media_info['title'] == "Advertisement":
                #print(current_media_info)
                while True:
                    try:
                        x = restart_app()
                        # print('add skiped')
                        if x:
                            asyncio.run(play_media(current_media_info['title']))
                        break
                    except Exception:
                        continue
                time.sleep(1)


            elif (current_media_info['artist'] == 'Spotify') and (current_media_info['album_title'] == '') or (current_media_info['album_title'] == '') and (current_media_info['track_number'] == 0):
                #print(current_media_info)
                while True:
                    try:
                        res = restart_app()
                        # print('add skiped')
                        if res is True:
                            while True:
                                try:
                                    asyncio.run(play_media(current_media_info['title']))
                                    break
                                except Exception:
                                    continue
                        break
                    except Exception:
                        continue
                time.sleep(1)

            current_media_info = None

        except Exception as e:
            break


if __name__ == '__main__':

    while True:
        time.sleep(1)

        try:
            for proc in psutil.process_iter():
                name = proc.name()
                if name == "Spotify.exe":
                    try:
                        main()
                        current_media_info = None
                        spotify_windows = None
                        name = None
                        proc = None

                    except Exception as e:
                        print(e)
                        current_media_info = None
                        spotify_windows = None
                    break

                else:
                    continue

            '''try:
                spotify_windows = gw.getWindowsWithTitle("Spotify")
                if spotify_windows:
                    print('1')
                    main()'''



        except Exception:
            pass
