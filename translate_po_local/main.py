import argparse
import os

import polib
from googletrans import Translator
from deep_translator import (GoogleTranslator,
                             ChatGptTranslator,
                             MicrosoftTranslator,
                             PonsTranslator,
                             LingueeTranslator,
                             MyMemoryTranslator,
                             YandexTranslator,
                             PapagoTranslator,
                             DeeplTranslator,
                             QcriTranslator,
                             single_detection,
                             batch_detection
                             )

from .utilities.constants import UNTRANSLATED_PATH, TRANSLATED_PATH, LANGUAGE_SOURCE, LANGUAGE_DESTINATION
from .utilities.io import read_lines, save_lines
from .utilities.match import recognize_po_file


def translate(source: str, lang_src, lang_dest) -> str:
    """ Translates a single string into target language. """
    if not source:
        return ""
    translated = GoogleTranslator(source='auto', target=lang_dest).translate(text=source)

    #translated2 = DeeplTranslator(api_key="8c08a89-82ee-4831-80f3-ea95cb1aca34:fx", source='auto', target=lang_dest, use_free_api=True).translate(text=source)
    if source == translated:
        translated = GoogleTranslator(source=lang_src, target=lang_dest).translate(text=source)
    return translated


def create_close_string(line: str) -> str:
    """ Creates single .po file translation target sting. """
    return r"msgstr " + '"' + line + '"' + "\n"


def solve(new_file: str, old_file: str, arguments):
    """ Translates single file. """
    lines = read_lines(old_file)
    for line in lines:
        line.msgstr = polib.unescape(translate(polib.escape(line.msgid), arguments))
        print(f"Translated {lines.percent_translated()}% of the lines.")
    save_lines(new_file, lines)


def solve_new(new_file: str, old_file: str, lang_src, lang_dest):
    """ Translates single file. """
    lines = read_lines(old_file)
    for line in lines:
        try:
            line.msgstr = polib.unescape(translate(polib.escape(line.msgid), lang_src=lang_src, lang_dest=lang_dest))
            print(f"Translated {lines.percent_translated()}% of the lines.")
        except Exception as e:
            print (str(e))
            line.msgstr = ""
    save_lines(new_file, lines)

def traduireFichiersDossier(lang_src, lang_dest, dossier_src, dossier_dest, ):
    """ Core process that translates all files in a directory.
     :parameter fro:
     :parameter to:
     :parameter src:
     :parameter dest:
     """
    found_files = False

    for file in os.listdir(dossier_src):
        if recognize_po_file(file):
            found_files = True
            solve_new(new_file=os.path.join(dossier_dest, file), old_file=os.path.join(dossier_src, file), lang_src=lang_src, lang_dest=lang_dest)

    if not found_files:
        raise Exception(f"Couldn't find any .po files at: '{dossier_src}'")

def run(**kwargs):
    """ Core process that translates all files in a directory.
     :parameter fro:
     :parameter to:
     :parameter src:
     :parameter dest:
     """
    found_files = False

    parser = argparse.ArgumentParser(description='Automatically translate PO files using Google translate.')
    parser.add_argument('--fro', type=str, help='Source language you want to translate from to (Default: en)',
                        default=kwargs.get('fro', LANGUAGE_SOURCE))
    parser.add_argument('--to', type=str, help='Destination language you want to translate to (Default: et)',
                        default=kwargs.get('to', LANGUAGE_DESTINATION))
    parser.add_argument('--src', type=str, help='Source directory or the files you want to translate',
                        default=kwargs.get('src', UNTRANSLATED_PATH))
    parser.add_argument('--dest', type=str, help='Destination directory you want to translated files to end up in',
                        default=kwargs.get('dest', TRANSLATED_PATH))
    arguments = parser.parse_args()

    for file in os.listdir(arguments.src):
        if recognize_po_file(file):
            found_files = True
            solve(os.path.join(arguments.dest, file), os.path.join(arguments.src, file), arguments)

    if not found_files:
        raise Exception(f"Couldn't find any .po files at: '{arguments.src}'")


#if __name__ == '__main__':
#    run()
