from collections import defaultdict
import argparse
import logging
import glob
import math
import sys
import os
import mido

NOTE_NAMES = [
    'c', 'c#', 'd', 'd#', 'e', 'f', 'f#', 'g', 'g#', 'a', 'a#', 'b']

STRUDEL_SOUNDS = [
    "agogo","balafon","balafon_hard","balafon_soft","ballwhistle","belltree",
    "bongo","bytebeat","cabasa","cajon","casio","clash","clash2","clave",
    "clavisynth","conga","cowbell","dantranh","dantranh_tremolo",
    "dantranh_vibrato","darbuka","didgeridoo","fingercymbal","flexatone",
    "fmpiano","folkharp","framedrum","glockenspiel","gm_accordion",
    "gm_acoustic_bass","gm_acoustic_guitar_nylon","gm_acoustic_guitar_steel",
    "gm_agogo","gm_alto_sax","gm_applause","gm_bagpipe","gm_bandoneon",
    "gm_banjo","gm_baritone_sax","gm_bassoon","gm_bird_tweet",
    "gm_blown_bottle","gm_brass_section","gm_breath_noise","gm_celesta",
    "gm_cello","gm_choir_aahs","gm_church_organ","gm_clarinet","gm_clavinet",
    "gm_contrabass","gm_distortion_guitar","gm_drawbar_organ","gm_dulcimer",
    "gm_electric_bass_finger","gm_electric_bass_pick","gm_electric_guitar_clean",
    "gm_electric_guitar_jazz","gm_electric_guitar_muted","gm_english_horn",
    "gm_epiano1","gm_epiano2","gm_fiddle","gm_flute","gm_french_horn",
    "gm_fretless_bass","gm_fx_atmosphere","gm_fx_brightness","gm_fx_crystal",
    "gm_fx_echoes","gm_fx_goblins","gm_fx_rain","gm_fx_sci_fi",
    "gm_fx_soundtrack","gm_glockenspiel","gm_guitar_fret_noise",
    "gm_guitar_harmonics","gm_gunshot","gm_harmonica","gm_harpsichord",
    "gm_helicopter","gm_kalimba","gm_koto","gm_lead_1_square",
    "gm_lead_2_sawtooth","gm_lead_3_calliope","gm_lead_4_chiff",
    "gm_lead_5_charang","gm_lead_6_voice","gm_lead_7_fifths",
    "gm_lead_8_bass_lead","gm_marimba","gm_melodic_tom","gm_music_box",
    "gm_muted_trumpet","gm_oboe","gm_ocarina","gm_orchestra_hit",
    "gm_orchestral_harp","gm_overdriven_guitar","gm_pad_bowed",
    "gm_pad_choir","gm_pad_halo","gm_pad_metallic","gm_pad_new_age",
    "gm_pad_poly","gm_pad_sweep","gm_pad_warm","gm_pan_flute",
    "gm_percussive_organ","gm_piano","gm_piccolo","gm_pizzicato_strings",
    "gm_recorder","gm_reed_organ","gm_reverse_cymbal","gm_rock_organ",
    "gm_seashore","gm_shakuhachi","gm_shamisen","gm_shanai","gm_sitar",
    "gm_slap_bass_1","gm_slap_bass_2","gm_soprano_sax","gm_steel_drums",
    "gm_string_ensemble_1","gm_string_ensemble_2","gm_synth_bass_1",
    "gm_synth_bass_2","gm_synth_brass_1","gm_synth_brass_2","gm_synth_choir",
    "gm_synth_drum","gm_synth_strings_1","gm_synth_strings_2",
    "gm_taiko_drum","gm_telephone","gm_tenor_sax","gm_timpani",
    "gm_tinkle_bell","gm_tremolo_strings","gm_trombone","gm_trumpet",
    "gm_tuba","gm_tubular_bells","gm_vibraphone","gm_viola","gm_violin",
    "gm_voice_oohs","gm_whistle","gm_woodblock","gm_xylophone",
    "gong","gong2","guiro","handbells","handchimes","harmonica",
    "harmonica_soft","harmonica_vib","harp","kalimba","kalimba2","kalimba3",
    "kalimba4","kalimba5","kawai","korgkrz_fx","krz_fx","marimba",
    "marktrees","mc303_fx","mridangam_ardha","mridangam_chaapu",
    "mridangam_dhi","mridangam_dhin","mridangam_dhum","mridangam_gumki",
    "mridangam_ka","mridangam_ki","mridangam_na","mridangam_nam",
    "mridangam_ta","mridangam_tha","mridangam_thom","ocarina",
    "ocarina_small","ocarina_small_stacc","ocarina_vib","oceandrum",
    "organ_4inch","organ_8inch","organ_full","piano","piano1",
    "pipeorgan_loud","pipeorgan_loud_pedal","pipeorgan_quiet",
    "pipeorgan_quiet_pedal","psaltery_bow","psaltery_pluck",
    "psaltery_spiccato","pulse","recorder_alto_stacc","recorder_alto_sus",
    "recorder_alto_vib","recorder_bass_stacc","recorder_bass_sus",
    "recorder_bass_vib","recorder_soprano_stacc","recorder_soprano_sus",
    "recorder_tenor_stacc","recorder_tenor_sus","recorder_tenor_vib",
    "rolandmc303_fx","rx5_fx","saw","sawtooth","sax","sax_stacc","sax_vib",
    "saxello","saxello_stacc","saxello_vib","shaker_large","shaker_small",
    "sin","sine","sleighbells","slitdrum","sqr","square","steinway",
    "strumstick","super64","super64_acc","super64_vib","supersaw",
    "tambourine","tambourine2","tg33_fx","timpani","timpani_roll","timpani2",
    "tri","triangle","triangles","tubularbells","tubularbells2",
    "vibraphone","vibraphone_bowed","vibraphone_soft","vibraslap",
    "woodblock","wt_digital","wt_digital_bad_day","wt_digital_basique",
    "wt_digital_crickets","wt_digital_curses","wt_digital_echoes",
    "wt_vgame","xylophone_hard_ff","xylophone_hard_pp",
    "xylophone_medium_ff","xylophone_medium_pp","xylophone_soft_ff",
    "xylophone_soft_pp","yamaharx5_fx","yamahatg33_fx","z_sawtooth",
    "z_sine","z_square","z_tan","z_triangle","zzfx"
]

MIDI_SOUNDS = [
    "gm_piano","gm_piano","gm_epiano1","gm_piano","gm_epiano1","gm_epiano2","gm_harpsichord","gm_clavinet",
    "gm_celesta","gm_glockenspiel","gm_music_box","gm_vibraphone","gm_marimba","gm_xylophone","gm_tubular_bells","gm_dulcimer",
    "gm_drawbar_organ","gm_percussive_organ","gm_rock_organ","gm_church_organ","gm_reed_organ","gm_accordion","gm_harmonica","gm_bandoneon",
    "gm_acoustic_guitar_nylon","gm_acoustic_guitar_steel","gm_electric_guitar_jazz","gm_electric_guitar_clean",
    "gm_electric_guitar_muted","gm_overdriven_guitar","gm_distortion_guitar","gm_guitar_harmonics",
    "gm_acoustic_bass","gm_electric_bass_finger","gm_electric_bass_pick","gm_fretless_bass",
    "gm_slap_bass_1","gm_slap_bass_2","gm_synth_bass_1","gm_synth_bass_2",
    "gm_violin","gm_viola","gm_cello","gm_contrabass",
    "gm_tremolo_strings","gm_pizzicato_strings","gm_orchestral_harp","gm_timpani",
    "gm_string_ensemble_1","gm_string_ensemble_2","gm_synth_strings_1","gm_synth_strings_2",
    "gm_choir_aahs","gm_voice_oohs","gm_synth_choir","gm_orchestra_hit",
    "gm_trumpet","gm_trombone","gm_tuba","gm_muted_trumpet",
    "gm_french_horn","gm_brass_section","gm_synth_brass_1","gm_synth_brass_2",
    "gm_soprano_sax","gm_alto_sax","gm_tenor_sax","gm_baritone_sax",
    "gm_oboe","gm_english_horn","gm_bassoon","gm_clarinet",
    "gm_piccolo","gm_flute","gm_recorder","gm_pan_flute",
    "gm_blown_bottle","gm_shakuhachi","gm_whistle","gm_ocarina",
    "gm_lead_1_square","gm_lead_2_sawtooth","gm_lead_3_calliope","gm_lead_4_chiff",
    "gm_lead_5_charang","gm_lead_6_voice","gm_lead_7_fifths","gm_lead_8_bass_lead",
    "gm_pad_new_age","gm_pad_warm","gm_pad_poly","gm_pad_choir",
    "gm_pad_bowed","gm_pad_metallic","gm_pad_halo","gm_pad_sweep",
    "gm_fx_rain","gm_fx_soundtrack","gm_fx_crystal","gm_fx_atmosphere",
    "gm_fx_brightness","gm_fx_goblins","gm_fx_echoes","gm_fx_sci_fi",
    "gm_sitar","gm_banjo","gm_shamisen","gm_koto",
    "gm_kalimba","gm_shanai","gm_fiddle","gm_shanai",
    "gm_tinkle_bell","gm_agogo","gm_steel_drums","gm_woodblock",
    "gm_taiko_drum","gm_melodic_tom","gm_synth_drum","gm_reverse_cymbal",
    "gm_guitar_fret_noise","gm_breath_noise","gm_fx_rain","gm_fx_brightness",
    "gm_fx_echoes","gm_fx_echoes","gm_fx_echoes","gm_fx_echoes"
]

SOUND_IMPROVEMENT_MAPS = {
    "gm_piano": "piano",
    "gm_lead_1_square": "square",
    "gm_lead_2_sawtooth": "saw"
}

SOUND_FALLBACK = "piano"

# General MIDI 标准打击乐 (Channel 10) 映射到 Strudel 鼓采样
GM_DRUM_MAP = {
    35: "bd",      # Acoustic Bass Drum
    36: "bd",      # Bass Drum 1
    37: "rim",     # Side Stick
    38: "sd",      # Acoustic Snare
    39: "cp",      # Hand Clap
    40: "sd:1",    # Electric Snare
    41: "lt",      # Low Floor Tom
    42: "hh",      # Closed Hi-Hat
    43: "ht",      # High Floor Tom
    44: "hh",      # Pedal Hi-Hat
    45: "lt",      # Low Tom
    46: "oh",      # Open Hi-Hat
    47: "mt",      # Low-Mid Tom
    48: "mt",      # Hi-Mid Tom
    49: "cr",      # Crash Cymbal 1
    50: "ht",      # High Tom
    51: "rd",      # Ride Cymbal 1
    52: "cr:1",    # Chinese Cymbal
    53: "rd:1",    # Ride Bell
    54: "tb",      # Tambourine
    55: "cr:2",    # Splash Cymbal
    56: "cb",      # Cowbell
    57: "cr",      # Crash Cymbal 2
    58: "misc",    # Vibraslap
    59: "rd:2",    # Ride Cymbal 2
    60: "bongo",   # Hi Bongo
    61: "bongo",   # Low Bongo
    62: "conga",   # Mute Hi Conga
    63: "conga",   # Open Hi Conga
    64: "conga",   # Low Conga
    65: "timpani", # High Timbale
    66: "timpani", # Low Timbale
    67: "agogo",   # High Agogo
    68: "agogo",   # Low Agogo
    69: "cabasa",  # Cabasa
    70: "shaker_small", # Maracas
    71: "ballwhistle",  # Short Whistle
    72: "ballwhistle",  # Long Whistle
    73: "guiro",   # Short Guiro
    74: "guiro",   # Long Guiro
    75: "clave",   # Claves
    76: "woodblock", # Hi Wood Block
    77: "woodblock", # Low Wood Block
    80: "triangle",  # Mute Triangle
    81: "triangles", # Open Triangle
}

def get_sound_name(program_number):
    if not isinstance(program_number, int) or program_number < 0 or program_number > len(MIDI_SOUNDS) - 1:
        return SOUND_FALLBACK

    sound_name = MIDI_SOUNDS[program_number]

    if sound_name in SOUND_IMPROVEMENT_MAPS:
        return SOUND_IMPROVEMENT_MAPS[sound_name]

    stripped_sound_name = sound_name.replace("gm_", "")
    if stripped_sound_name in STRUDEL_SOUNDS:
        return stripped_sound_name

    if sound_name in STRUDEL_SOUNDS:
        return sound_name

    return SOUND_FALLBACK

def get_instrument_sound_and_chain(program_number, enhance_sound=True, tab_size=2):
    """
    根据 General MIDI Program 编号智能匹配最佳音色与声学 DSP 链。
    Strudel 原生合成器与 Soundfont 默认 release=0.01s 且缺乏混响，极易发生突兀干瘪的“断音”。
    本函数为不同乐器大类注入定制的连奏 (legato)、包络 (decay/sustain/release)、低通滤波 (lpf) 与空间混响 (room)。
    """
    indent = get_indent(tab_size, 1)
    if not isinstance(program_number, int) or program_number < 0 or program_number > len(MIDI_SOUNDS) - 1:
        if enhance_sound:
            return SOUND_FALLBACK, [f"{indent}.decay(2)", f"{indent}.room(0.2)"]
        return SOUND_FALLBACK, []

    sound_name = get_sound_name(program_number)
    if not enhance_sound:
        return sound_name, []

    # 1. 钢琴与键盘乐器 (0-7)
    if 0 <= program_number <= 3:
        # 大钢琴声学采样具备自然泛音衰减
        return "piano", [f"{indent}.decay(2)", f"{indent}.room(0.2)"]
    elif 4 <= program_number <= 5:
        # 电钢琴 (Rhodes / FM Epiano)
        return sound_name, [f"{indent}.decay(1.5)", f"{indent}.release(0.4)", f"{indent}.room(0.25)"]
    elif 6 <= program_number <= 7:
        # 大键琴 / 击弦古钢琴 (Harpsichord / Clavinet)
        return sound_name, [f"{indent}.decay(0.8)", f"{indent}.release(0.3)", f"{indent}.room(0.2)"]

    # 2. 色彩打击乐 (8-15: 钟琴、钢片琴、八音盒、颤音琴、马林巴、木琴、管钟)
    elif 8 <= program_number <= 15:
        return sound_name, [f"{indent}.decay(1.2)", f"{indent}.release(0.35)", f"{indent}.room(0.28)"]

    # 3. 风琴类 (16-23: 抽拉风琴、打击风琴、摇滚风琴、管风琴、手风琴)
    elif 16 <= program_number <= 23:
        return sound_name, [f"{indent}.legato(1.15)", f"{indent}.decay(1.0)", f"{indent}.sustain(0.85)", f"{indent}.release(0.3)", f"{indent}.room(0.28)"]

    # 4. 吉他类 (24-31: 尼龙吉他、钢弦民谣、爵士电吉他、清音电吉他、失真吉他)
    elif 24 <= program_number <= 28:
        return sound_name, [f"{indent}.decay(1.2)", f"{indent}.sustain(0.5)", f"{indent}.release(0.35)", f"{indent}.room(0.25)"]
    elif 29 <= program_number <= 31:
        # 过载与失真吉他
        return sound_name, [f"{indent}.legato(1.1)", f"{indent}.decay(0.8)", f"{indent}.sustain(0.7)", f"{indent}.release(0.3)", f"{indent}.room(0.3)"]

    # 5. 贝斯类 (32-39: 原声低音提琴、指弹电贝斯、拨片贝斯、无品贝斯、Slap贝斯、合成贝斯)
    elif 32 <= program_number <= 37:
        # 原声与电贝斯：适度释放防断音，同时不过长引起浑浊
        return sound_name, [f"{indent}.decay(0.5)", f"{indent}.sustain(0.7)", f"{indent}.release(0.2)"]
    elif 38 <= program_number <= 39:
        # 合成贝斯 (Synth Bass 1 & 2)：使用 LPF 900Hz 过滤高频毛刺，聚焦纯净低频
        return sound_name, [f"{indent}.lpf(900)", f"{indent}.decay(0.35)", f"{indent}.sustain(0.65)", f"{indent}.release(0.18)"]

    # 6. 独奏弦乐 (40-47: 小提琴、中提琴、大提琴、倍大低音提琴、颤音弦乐、拨弦、竖琴、定音鼓)
    elif 40 <= program_number <= 44:
        return sound_name, [f"{indent}.legato(1.3)", f"{indent}.attack(0.05)", f"{indent}.decay(0.8)", f"{indent}.sustain(0.85)", f"{indent}.release(0.5)", f"{indent}.room(0.4)"]
    elif program_number == 45:
        # 拨弦 Pizzicato
        return sound_name, [f"{indent}.decay(0.6)", f"{indent}.release(0.3)", f"{indent}.room(0.25)"]
    elif program_number == 46:
        # 竖琴 Harp
        return "harp" if "harp" in STRUDEL_SOUNDS else sound_name, [f"{indent}.decay(1.6)", f"{indent}.release(0.5)", f"{indent}.room(0.35)"]
    elif program_number == 47:
        # 定音鼓 Timpani
        return sound_name, [f"{indent}.decay(1.0)", f"{indent}.release(0.4)", f"{indent}.room(0.3)"]

    # 7. 弦乐合奏群与合唱人声 (48-55: 弦乐群1/2、合成弦乐1/2、Choir Aahs、Voice Oohs、铜管齐奏打击)
    elif 48 <= program_number <= 51:
        # 弦乐群是断音重灾区，注入平滑淡入包络与超长释放残响
        return sound_name, [f"{indent}.legato(1.4)", f"{indent}.attack(0.08)", f"{indent}.decay(1.0)", f"{indent}.sustain(0.9)", f"{indent}.release(0.7)", f"{indent}.room(0.45)"]
    elif 52 <= program_number <= 54:
        # 人声合唱 Choir
        return sound_name, [f"{indent}.legato(1.4)", f"{indent}.attack(0.1)", f"{indent}.decay(1.2)", f"{indent}.sustain(0.9)", f"{indent}.release(0.8)", f"{indent}.room(0.5)"]
    elif program_number == 55:
        # Orchestra Hit
        return sound_name, [f"{indent}.decay(0.8)", f"{indent}.release(0.4)", f"{indent}.room(0.35)"]

    # 8. 铜管乐器 (56-63: 小号、长号、大号、弱音小号、法国圆号、铜管组、合成铜管)
    elif 56 <= program_number <= 63:
        return sound_name, [f"{indent}.legato(1.2)", f"{indent}.attack(0.03)", f"{indent}.decay(0.6)", f"{indent}.sustain(0.8)", f"{indent}.release(0.35)", f"{indent}.room(0.35)"]

    # 9. 簧管与木管 (64-79: 萨克斯、双簧管、英国管、大管、单簧管、短笛、长笛、笛子、排箫、陶笛)
    elif 64 <= program_number <= 71:
        return sound_name, [f"{indent}.legato(1.2)", f"{indent}.attack(0.03)", f"{indent}.decay(0.6)", f"{indent}.sustain(0.8)", f"{indent}.release(0.3)", f"{indent}.room(0.35)"]
    elif 72 <= program_number <= 79:
        return sound_name, [f"{indent}.legato(1.25)", f"{indent}.attack(0.05)", f"{indent}.decay(0.7)", f"{indent}.sustain(0.85)", f"{indent}.release(0.4)", f"{indent}.room(0.4)"]

    # 10. 合成主音 (80-87: 方波主音、锯齿波主音、风琴主音、声音主音、五度音、贝斯主音)
    elif 80 <= program_number <= 87:
        if sound_name == "saw":
            # 现代锯齿波主音：3200Hz LPF 平滑刺耳毛刺，带连奏与 250ms 释放与 30% 空间混响
            return "saw", [f"{indent}.lpf(3200)", f"{indent}.legato(1.15)", f"{indent}.decay(0.4)", f"{indent}.sustain(0.7)", f"{indent}.release(0.25)", f"{indent}.room(0.3)"]
        elif sound_name == "square":
            return "square", [f"{indent}.lpf(2800)", f"{indent}.legato(1.15)", f"{indent}.decay(0.4)", f"{indent}.sustain(0.7)", f"{indent}.release(0.25)", f"{indent}.room(0.3)"]
        elif program_number == 87:
            # Bass + Lead
            return sound_name, [f"{indent}.lpf(2600)", f"{indent}.legato(1.1)", f"{indent}.decay(0.35)", f"{indent}.sustain(0.7)", f"{indent}.release(0.2)", f"{indent}.room(0.25)"]
        else:
            return sound_name, [f"{indent}.legato(1.2)", f"{indent}.decay(0.5)", f"{indent}.sustain(0.75)", f"{indent}.release(0.3)", f"{indent}.room(0.35)"]

    # 11. 合成铺底 (88-95: 新世纪、温暖、多复音、合唱、弓弦、金属、光晕、扫频 Pad)
    elif 88 <= program_number <= 95:
        # Pad 最忌讳断音，赋予 1.5 倍时值连奏、0.8秒平滑释放与大空间混响
        return sound_name, [f"{indent}.legato(1.5)", f"{indent}.attack(0.12)", f"{indent}.decay(1.2)", f"{indent}.sustain(0.9)", f"{indent}.release(0.8)", f"{indent}.room(0.5)"]

    # 12. 音效与民族乐器 (96-127: 西塔尔、班卓琴、三味线、日本筝、卡林巴等)
    elif 96 <= program_number <= 103:
        return sound_name, [f"{indent}.legato(1.3)", f"{indent}.decay(1.5)", f"{indent}.release(0.7)", f"{indent}.room(0.45)"]
    elif 104 <= program_number <= 111:
        return sound_name, [f"{indent}.decay(1.0)", f"{indent}.release(0.4)", f"{indent}.room(0.3)"]
    else:
        return sound_name, [f"{indent}.decay(0.8)", f"{indent}.release(0.3)", f"{indent}.room(0.25)"]

def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    file_handler = logging.FileHandler("log.log", encoding="utf-8", mode="a")
    file_handler.setFormatter(logging.Formatter(
        "[{asctime}][{levelname}]: {message}",
        datefmt="%Y-%m-%d %H:%M:%S",
        style="{"
    ))

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(logging.Formatter(
        "[{levelname}]: {message}",
        style="{"
    ))

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    return logger

logger = setup_logging()

def main():
    args = parse_args()
    mid = load_midi_file(args.midi)
    tempo, bpm, cycle_len = get_timing_values(mid)
    auto_drums = getattr(args, 'auto_drums', True)
    octave_shift = getattr(args, 'octave_shift', 0)
    events, instruments, drum_keys, mix_info = collect_note_events(mid, tempo, auto_drums=auto_drums, octave_shift=octave_shift)
    tracks = build_tracks(events, cycle_len, args)
    output = build_output(tracks, bpm, instruments, args, drum_keys=drum_keys, mix_info=mix_info)

    print(output)
    with open('result.txt', 'w', encoding='utf-8') as f:
        f.write(output + '\n')

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--midi', type=str, help='Path to the Midi file. (default: Uses first .mid in folder)')
    parser.add_argument('-b', '--bar-limit', type=int, default=0, help='The amount of bars to convert. 0 means no limit. (default: %(default)s)')
    parser.add_argument('-n', '--notes-per-bar', type=int, default=64, help='The resolution. Usually in steps of 4 (4, 8, 16...).' \
        ' Higher gives better note placement but can get big. (default: %(default)s)')
    parser.add_argument('-t', '--tab-size', type=int, default=2, help='How many spaces to use for indentation in the output. (default: %(default)s)')
    parser.add_argument('-g', '--guess-instrument', action='store_true', help='Use the sounds closest to the instruments mentioned in the MIDI. (default: off)')
    parser.add_argument('-f', '--flat-sequences', action='store_true', help='No complex timing or chords. (default: off)')
    parser.add_argument('-s', '--small-print', action='store_true', help='Put all notes on a single line.' \
        ' Makes it harder to make changes, but takes up less space for a drop & forget. (default: off)')
    parser.add_argument('-d', '--no-auto-drums', action='store_false', dest='auto_drums', help='Do not auto-convert MIDI channel 10 to Strudel drum samples. (default: on)')
    parser.add_argument('-o', '--octave-shift', type=int, default=0, choices=[-2, -1, 0, 1, 2], help='Shift melodic notes up or down by N octaves. (default: 0)')
    parser.add_argument('-e', '--no-enhance', action='store_false', dest='enhance_sound', help='Do not apply smart DSP chains (legato, ADSR, lpf, room) to matched instruments. (default: on)')
    parser.add_argument('-v', '--no-auto-gain', action='store_false', dest='auto_gain', help='Do not auto-balance track volumes based on MIDI velocity and CC 7. (default: on)')

    args = parser.parse_args()
    parser.print_help()
    print()

    return args

def load_midi_file(midi_path):
    if midi_path:
        if not os.path.exists(midi_path):
            print(f"MIDI file not found: {midi_path}")
            sys.exit(1)
        return mido.MidiFile(midi_path)
    
    midi_files = glob.glob("*.mid") + glob.glob("*.midi")
    if not midi_files:
        print("No MIDI files found")
        sys.exit(1)
    return mido.MidiFile(midi_files[0])

def get_timing_values(mid):
    tempo = 500000
    for msg in mid.tracks[0]:
        if msg.type == 'set_tempo':
            tempo = msg.tempo
            break
    
    bpm = mido.tempo2bpm(tempo)
    cycle_len = 60 / bpm * 4
    return tempo, bpm, cycle_len

def collect_note_events(mid, tempo, auto_drums=True, octave_shift=0):
    events = defaultdict(list)
    instruments = {}
    programs = {}
    drum_keys = set()
    track_velocities = defaultdict(list)
    track_volumes = {}
    track_pans = {}

    for track_index, track in enumerate(mid.tracks):
        time_sec = 0
        for msg in track:
            time_sec += mido.tick2second(msg.time, mid.ticks_per_beat, tempo)

            if msg.type == 'program_change':
                programs[(track_index, msg.channel)] = msg.program

            if msg.type == 'control_change':
                key = (track_index, msg.channel)
                if msg.control == 7:  # Main Volume (CC 7)
                    track_volumes[key] = msg.value
                elif msg.control == 10:  # Pan (CC 10)
                    track_pans[key] = msg.value

            if msg.type == 'note_on' and msg.velocity > 0:
                key = (track_index, msg.channel)
                track_velocities[key].append(msg.velocity)
                # MIDI 规范中 Channel 10 (索引为 9) 专用于非音高打击乐鼓组
                is_drum = auto_drums and (msg.channel == 9)
                if is_drum:
                    drum_keys.add(key)
                    drum_name = GM_DRUM_MAP.get(msg.note, "sd")
                    events[key].append((time_sec, drum_name))
                else:
                    shifted_note = msg.note + octave_shift * 12
                    shifted_note = max(0, min(127, shifted_note))
                    events[key].append((time_sec, note_num_to_str(shifted_note)))

                if key not in instruments:
                    instruments[key] = programs.get(key)

    mix_info = {
        'velocities': track_velocities,
        'volumes': track_volumes,
        'pans': track_pans
    }
    return events, instruments, drum_keys, mix_info

def note_num_to_str(n):
    return NOTE_NAMES[n % 12].lower() + str(n // 12 - 1)

def build_tracks(events, cycle_len, args):
    tracks = []
    for track_key in sorted(events):
        evs = adjust_near_cycle_end(events[track_key], cycle_len)
        if not evs:
            continue

        max_time = max(t for t, _ in evs)
        num_cycles = min((int(max_time / cycle_len) + 1), args.bar_limit if args.bar_limit > 0 else float('inf'))
        bars = []

        for c in range(num_cycles):
            start = c * cycle_len
            end = start + cycle_len
            notes_in_cycle = [(t, n) for t, n in evs if start <= t < end]

            if not notes_in_cycle:
                bars.append('-')
                continue

            bar = get_flat_mode_bar(notes_in_cycle) if args.flat_sequences \
                else get_poly_mode_bar(notes_in_cycle, start, cycle_len, args.notes_per_bar)

            bars.append(bar)

        if bars and any(bar != '-' for bar in bars):
            tracks.append((track_key, bars))

    return tracks

def adjust_near_cycle_end(events, cycle_len):
    adjusted = []
    for t, note in events:
        rel = (t % cycle_len) / cycle_len
        if rel > 0.95:
            adjusted.append((math.ceil(t / cycle_len) * cycle_len, note))
        else:
            adjusted.append((t, note))
    return adjusted

def get_flat_mode_bar(events):
    notes = [n for _, n in sorted(events)]
    return notes[0] if len(notes) == 1 else f"[{' '.join(notes)}]"

def get_poly_mode_bar(events, cycle_start, cycle_len, notes_per_bar):
    time_groups = defaultdict(list)
    for t, n in events:
        pos = quantize_time(t, cycle_start, cycle_len, notes_per_bar)
        for existing in time_groups:
            if abs(pos - existing) < 1 / notes_per_bar:
                time_groups[existing].append(n)
                break
        else:
            time_groups[pos].append(n)

    if not time_groups:
        return '-'

    subdivisions = ['-'] * notes_per_bar
    for pos in sorted(time_groups):
        i = int(round(pos * notes_per_bar))
        if i < notes_per_bar:
            group = time_groups[pos]
            subdivisions[i] = group[0] if len(group) == 1 else f"[{','.join(group)}]"

    if all(x == '-' for x in subdivisions):
        return '-'

    simplified = simplify_subdivisions(subdivisions)
    return simplified[0] if len(simplified) == 1 else f"[{' '.join(simplified)}]"

def quantize_time(timestamp, cycle_start, cycle_len, notes_per_bar):
    rel_time = (timestamp - cycle_start) / cycle_len
    quantized = round(rel_time * notes_per_bar) / notes_per_bar
    return min(quantized, 1.0 - 1e-9)

def simplify_subdivisions(subdivs):
    current = subdivs
    while len(current) % 2 == 0:
        pairs = list(zip(current[::2], current[1::2]))
        if any(second != '-' for _, second in pairs):
            break

        current = [first for first, _ in pairs]
    
    return current

def calculate_bars_per_row(tracks, max_chars=160, min_bars=2, max_bars=8):
    longest_bar = 0
    for _, bars in tracks:
        for bar in bars:
            longest_bar = max(longest_bar, len(bar))

    if longest_bar == 0:
        return max_bars

    bars_fit = (max_chars + 1) // (longest_bar + 1)
    return max(min_bars, min(max_bars, bars_fit))

def compute_track_gains(tracks, mix_info):
    """
    基于各轨道 MIDI Note Velocity 平均力度与 CC 7 (Track Volume) 主音量，
    自适应计算多轨平衡增益，防止乐器音量混乱、彼此覆盖或总线爆音失真。
    """
    if not mix_info:
        return {}
    velocities = mix_info.get('velocities', {})
    volumes = mix_info.get('volumes', {})
    raw_levels = {}
    for track_key, _ in tracks:
        vels = velocities.get(track_key, [])
        avg_vel = (sum(vels) / len(vels)) if vels else 85.0
        cc7 = volumes.get(track_key, 100.0)
        raw_levels[track_key] = max(0.1, (avg_vel / 100.0) * (cc7 / 100.0))

    max_level = max(raw_levels.values()) if raw_levels else 1.0
    gains = {}
    for track_key in raw_levels:
        ratio = raw_levels[track_key] / max_level
        # 映射到最佳混音动态区间 [0.45, 0.95]，保持各轨清晰可辨且动态层次分明
        gains[track_key] = round(0.45 + 0.50 * (ratio ** 0.8), 2)
    return gains

def build_output(tracks, bpm, instruments, args, drum_keys=None, mix_info=None):
    drum_keys = drum_keys or set()
    mix_info = mix_info or {}
    output = [f"setcpm({int(bpm)}/4)\n"]

    enhance_sound = getattr(args, 'enhance_sound', True)
    auto_gain = getattr(args, 'auto_gain', True)
    track_gains = compute_track_gains(tracks, mix_info) if auto_gain else {}
    pans = mix_info.get('pans', {})

    bars_per_row = calculate_bars_per_row(tracks)
    for track_key, bars in tracks:
        is_drum = track_key in drum_keys
        func_name = "s" if is_drum else "note"
        if (args.small_print):
            output.append(f"$: {func_name}(`<{''.join(bars)}>`)")
        else:
            output.append(f"$: {func_name}(`<")
            for i in range(0, len(bars), bars_per_row):
                chunk = bars[i:i + bars_per_row]
                output.append(f"{get_indent(args.tab_size, 2)}{' '.join(chunk)}")
            
            output[-1] += '>`)'

        if is_drum:
            # 鼓组轨道使用标准的 909 鼓机采样库
            output.append(f"{get_indent(args.tab_size, 1)}.bank(\"RolandTR909\")")
        else:
            if args.guess_instrument:
                prog = instruments.get(track_key)
                sound_name, dsp_chain = get_instrument_sound_and_chain(prog, enhance_sound=enhance_sound, tab_size=args.tab_size)
                output.append(f"{get_indent(args.tab_size, 1)}.sound(\"{sound_name}\")")
                for dsp in dsp_chain:
                    output.append(dsp)
            else:
                fallback_sound = SOUND_FALLBACK
                output.append(f"{get_indent(args.tab_size, 1)}.sound(\"{fallback_sound}\")")
                if enhance_sound:
                    output.append(f"{get_indent(args.tab_size, 1)}.decay(2)")
                    output.append(f"{get_indent(args.tab_size, 1)}.room(0.2)")

        # 智能分轨音量与声像定位
        if auto_gain and track_key in track_gains:
            output.append(f"{get_indent(args.tab_size, 1)}.gain({track_gains[track_key]})")

        pan_val = pans.get(track_key, 64)
        if abs(pan_val - 64) >= 8:
            norm_pan = round(pan_val / 127.0, 2)
            output.append(f"{get_indent(args.tab_size, 1)}.pan({norm_pan})")

        output.append("")
    
    return '\n'.join(output)

def get_indent(tab_size, tabs=1):
    return ' ' * (tab_size * tabs)

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        logger.error(e, exc_info=True)
        sys.exit(1)
