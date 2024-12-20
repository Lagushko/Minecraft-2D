# import wave
# import os

# file_names = ["default"]
# desired_duration = 0.7
# directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), "walk")

# for file_name in file_names:
#     file_path = os.path.join(directory, f"{file_name}.wav")

#     if os.path.isfile(file_path):
#         with wave.open(file_path, 'rb') as audio:
#             params = audio.getparams()
#             total_frames = params[3]
#             frame_rate = params[2]
#             total_duration = total_frames / frame_rate

#             optimal_parts = round(total_duration / desired_duration)
#             part_duration = total_duration / optimal_parts
#             frames_per_part = int(part_duration * frame_rate)

#             print(f"Файл {file_name}.wav будет нарезан на {optimal_parts} частей (~{part_duration:.2f} секунд каждая)")

#             for i in range(optimal_parts):
#                 start_frame = i * frames_per_part
#                 end_frame = start_frame + frames_per_part

#                 audio.setpos(start_frame)
#                 frames = audio.readframes(frames_per_part)

#                 part_file_path = os.path.join(directory, f"{file_name}{i + 1}.wav")
#                 with wave.open(part_file_path, 'wb') as output:
#                     output.setparams(params)
#                     output.writeframes(frames)

#                 print(f"Часть {i + 1} сохранена как {file_name}_{i + 1}.wav")

#     else:
#         print(f"Файл {file_name}.wav не найден.")

import wave
import os

# Параметры
file_names = ["default1", "default2", "default3", "default4", "metal1", "metal2", "metal3", "metal4"]  # Имена файлов без расширения
volume = 4  # Коэффициент увеличения громкости
directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), "walk")

# Функция для изменения громкости
def increase_volume(input_path, output_path, volume):
    with wave.open(input_path, "rb") as wav_in:
        params = wav_in.getparams()  # Сохранение параметров аудио
        frames = wav_in.readframes(params.nframes)

        # Конвертация аудиофреймов в список чисел
        audio_data = bytearray(frames)
        
        # Увеличение громкости
        for i in range(0, len(audio_data), 2):
            sample = int.from_bytes(audio_data[i:i+2], byteorder="little", signed=True)
            sample = int(sample * volume)
            sample = max(-32768, min(32767, sample))  # Ограничение для 16-битного аудио
            audio_data[i:i+2] = sample.to_bytes(2, byteorder="little", signed=True)

        # Сохранение нового файла
        with wave.open(output_path, "wb") as wav_out:
            wav_out.setparams(params)
            wav_out.writeframes(audio_data)

# Обработка файлов
for file_name in file_names:
    input_file = os.path.join(directory, file_name + ".wav")
    output_file = os.path.join(directory, file_name + ".wav")

    if os.path.exists(input_file):
        print(f"Processing: {input_file}")
        increase_volume(input_file, output_file, volume)
        print(f"Saved: {output_file}")
    else:
        print(f"File not found: {input_file}")