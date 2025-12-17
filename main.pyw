import asyncio
from winrt.windows.media.control import GlobalSystemMediaTransportControlsSessionManager as MediaManager
import subprocess
import time
import os
import pygetwindow as gw
import psutil
import ctypes
import sys




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
    result = subprocess.Popen('TASKKILL /F /IM Spotify.exe', stdout=subprocess.PIPE, creationflags=subprocess.CREATE_NO_WINDOW)
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


def restart_app():
    try:
        kill()
    except Exception:
        #print(e)
        pass


    spotify_path = os.path.expanduser("~") + "\\AppData\\Local\\Microsoft\\WindowsApps\\Spotify.exe"

    while True:
        if check_for_proc() is False:
            subprocess.Popen(
                [spotify_path, "--minimized"],
                creationflags=subprocess.CREATE_NO_WINDOW | subprocess.SW_HIDE
            )
        elif check_for_proc() is True:
            continue



    for _ in range(11):
        spotify_windows = gw.getWindowsWithTitle("Spotify")
        if spotify_windows:
            spotify_windows[0].minimize()
            spotify_windows = None
            break

        else:
            subprocess.Popen([spotify_path, "--minimized"], creationflags=subprocess.CREATE_NO_WINDOW)  # ////////////////////////////////////


            time.sleep(1)

            spotify_windows = gw.getWindowsWithTitle("Spotify")
            if spotify_windows:
                spotify_windows[0].minimize()
                spotify_windows = None
                break
            else:
                continue



# print('ad')

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

            if current_media_info['title'] == 'Advertisement':
                while True:
                    try:
                        restart_app()
                        # print('add skiped')
                        break
                    except Exception:
                        continue
                time.sleep(1)

                while True:
                    try:
                        asyncio.run(play_media(current_media_info['title']))
                        break
                    except Exception:
                        continue

            current_media_info = None



        except Exception as e:
            break


if __name__ == '__main__':

    while True:
        time.sleep(15)

        try:
            '''for proc in psutil.process_iter():
                name = proc.name()
                if name == "Spotify.exe":
                    main()
                    break
                else:
                    continue'''

            try:
                spotify_windows = gw.getWindowsWithTitle("Spotify")
                if spotify_windows:
                    main()

                current_media_info = None
                spotify_windows = None

            except Exception:
                spotify_windows = None
                continue


        except Exception:
            pass
