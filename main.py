import asyncio
from winrt.windows.media.control import GlobalSystemMediaTransportControlsSessionManager as MediaManager
import subprocess
import time
import os
import pygetwindow as gw
#імпорти бібліотек



async def get_media_info():
    #получю айди процеса спотифай і ставлю на нього трекер
    try:
        sessions = await MediaManager.request_async()
        current_session = sessions.get_current_session()
        TARGET_ID = current_session.source_app_user_model_id
        #print(f'Активный идентификатор: {current_session.source_app_user_model_id}')
    except Exception:
        pass
        #print('Not ready')

    if current_session is None:
        raise Exception('Нет активной медиа-сессии')

    if current_session.source_app_user_model_id == TARGET_ID:
        info = await current_session.try_get_media_properties_async()
        info_dict = {song_attr: info.__getattribute__(song_attr) for song_attr in dir(info) if song_attr[0] != '_'}
        info_dict['genres'] = list(info_dict['genres'])
        return info_dict

    raise Exception(f'Программа {TARGET_ID} не является текущей медиа-сессией')

def get_active_window_title():
    active_window = gw.getActiveWindow()
    if active_window:
        return active_window.title
    return None

def restart_app():
    #тут презапуск спотифай
    os.system('TASKKILL /F /IM Spotify.exe')
    spotify_path = os.path.expanduser("~") + "\\AppData\\Local\\Microsoft\\WindowsApps\\Spotify.exe"

    subprocess.Popen([spotify_path, "--minimized"], shell=True)
    #print("Spotify запущено у фоновому режимі!")

    time.sleep(3)

    import pygetwindow as gw
    spotify_windows = gw.getWindowsWithTitle("Spotify")
    if spotify_windows:
        spotify_windows[0].minimize()
        #print("Spotify згорнуто")
    else:
        pass
        #print("Spotify не знайдено у вікнах")


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
            #print('wait')


    while True:
        if current_session is None:
            raise Exception('Нет активной медиа-сессии')

        if current_session.source_app_user_model_id == TARGET_ID:
            info = await current_session.try_get_media_properties_async()
            info_dict = {song_attr: info.__getattribute__(song_attr) for song_attr in dir(info) if
                         song_attr[0] != '_'}
            info_dict['genres'] = list(info_dict['genres'])
            album_title = info_dict['album_title']

            if album_title == '':
                continue

            await current_session.try_play_async()
            await current_session.try_skip_next_async()
            #print('Воспроизведение запущено!')
            break
        else:
            raise Exception(f'Программа {TARGET_ID} не является текущей медиа-сессией')


if __name__ == '__main__':
    while True:
        try:
            time.sleep(1)
            current_media_info = asyncio.run(get_media_info())
            #print(current_media_info)

            '''if input('>>>') == 'y':
                time.sleep(10)
                while True:
                    try:
                        restart_app()
                        time.sleep(1)
                        asyncio.run(play_media(current_media_info['album_title']))
                        break
                    except Exception:
                        continue
            else:
                exit()'''

            if current_media_info['title'] == 'Advertisement':
                while True:
                    try:
                        restart_app()
                        break
                    except Exception:
                        continue
                time.sleep(1)

                while True:
                    try:
                        asyncio.run(play_media(current_media_info['album_title']))
                        break
                    except Exception:
                        continue


        except Exception as e:
            print(f'Ошибка: {e}')
