import asyncio
import os
import time
from winrt.windows.media.control import GlobalSystemMediaTransportControlsSessionManager as MediaManager
import subprocess
#імпорти бібліотек



async def get_media_info():
    #получю айди процеса спотифай і ставлю на нього трекер
    sessions = await MediaManager.request_async()
    current_session = sessions.get_current_session()
    TARGET_ID = current_session.source_app_user_model_id
    #print(f'Активный идентификатор: {current_session.source_app_user_model_id}')

    if current_session is None:
        raise Exception('Нет активной медиа-сессии')

    if current_session.source_app_user_model_id == TARGET_ID:
        info = await current_session.try_get_media_properties_async()
        info_dict = {song_attr: info.__getattribute__(song_attr) for song_attr in dir(info) if song_attr[0] != '_'}
        info_dict['genres'] = list(info_dict['genres'])
        return info_dict

    raise Exception(f'Программа {TARGET_ID} не является текущей медиа-сессией')


def restart_app():
    #тут презапуск спотифай
    os.system('TASKKILL /F /IM Spotify.exe')
    exe_path = 'spotify'
    si = subprocess.STARTUPINFO()
    si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    process = subprocess.Popen(
        exe_path,
        startupinfo=si,
        creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
    )
    print('ad')

async def play_media(album_title):
    sessions = await MediaManager.request_async()
    current_session = sessions.get_current_session()
    TARGET_ID = current_session.source_app_user_model_id

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
            print('Воспроизведение запущено!')
            break
        else:
            raise Exception(f'Программа {TARGET_ID} не является текущей медиа-сессией')


if __name__ == '__main__':
    while True:
        try:
            time.sleep(1)
            current_media_info = asyncio.run(get_media_info())
            print(current_media_info)
            if current_media_info['title'] == 'Advertisement':
                restart_app()
                time.sleep(2)
                asyncio.run(play_media(current_media_info['album_title']))

        except Exception as e:
            print(f'Ошибка: {e}')