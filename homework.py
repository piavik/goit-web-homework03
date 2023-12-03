import sys
from pathlib import Path
from threading import Thread
import shutil
import re


CATEGORIES = {"Images": [".jpg", ".gif", ".png", ".svg"],
              "Audio": [".mp3", ".wav", ".flac", ".wma", ".ogg", ".amr"],
              "Docs": [".doc", ".docx", ".txt", ".rtf", ".pdf", ".epub", ".xls", ".xlsx", ".ppt", ".pptx"],
              "Video": [".avi", ".mp4", ".wmv", ".mov", ".mkv"],
              "Archives": [".zip", ".tar", ".gztar", ".bztar", ".xztar"]
              }

TRANS = {}




def initialize_translation_table() -> None:
    CYRILLIC_SYMBOLS = "абвгдеёжзийклмнопрстуфхцчшщъыьэюяєіїґ"
    TRANSLATION = ("a", "b", "v", "g", "d", "e", "e", "j", "z", "y", "j", "k", "l", "m", "n", "o", "p", "r", "s", "t", "u",
                "f", "h", "ts", "ch", "sh", "sch", "", "y", "", "e", "yu", "ya", "je", "i", "ji", "g")

    for c, l in zip(CYRILLIC_SYMBOLS, TRANSLATION):
        TRANS[ord(c)] = l
        TRANS[ord(c.upper())] = l.upper()

def normalize(name:str ) -> str:
    '''
    + проводить транслітерацію кирилічних символів на латиницю;
    замінює всі символи, крім літер латинського алфавіту та цифр, на символ '_';
    транслітерація може не відповідати стандарту, але бути читабельною;
    великі літери залишаються великими, а маленькі — маленькими після транслітерації.   
    '''
    # TODO: спробувати обійтися без 're'
    return re.sub('\W', '_', name.translate(TRANS))

def get_category(entry:Path) -> str:
    '''
    Get file category based on file extension from global const CATEGORIES
    '''
    extension = entry.suffix.lower()
    for cat, ext in CATEGORIES.items():
        if extension in ext:
            return cat
    return 'Unknown'
    # ^^^ hadrcode ??

# will run it in threads
def move_file(file, category, base_dir) -> None:
    '''
    Move file to a directory named by a category (create if not exists)), with base_dir
    '''
    category_dir = base_dir.joinpath(category)
    if not category_dir.exists():
        category_dir.mkdir()
    new_name = normalize(file.stem) + file.suffix
    new_file = category_dir.joinpath(new_name)
    if not new_file.exists():
        file.replace(new_file)
    # else:
    # TODO: use another destination file name 

def process_dir(directory: Path) -> None:
    '''
    Process all files in the given directory
    '''
    for entry in directory.glob("**/*"):
        # skip directories
        if entry.is_file():
            category = get_category(entry)
            # move_file(entry, category, directory)
            # run in multiple threads
            move = Thread(target=move_file, args=(entry, category, directory))
            move.start()

#unpack in threads
def process_archives(directory: Path) -> None:
    '''
    Unpack archives to archive_name_dir/
    NB: arch.zip and arch.tar.gz will use the same destination directory
    '''
    archive_base_name = directory.joinpath([k for k,v in CATEGORIES.items() if '.zip' in v][0])
    threads = []
    for archive_name in archive_base_name.glob("*"):
        handle_arch = Thread(target=unpack_each_archive, args=(archive_base_name, archive_name))
        handle_arch.start()
        threads.append(handle_arch)
    [th.join() for th in threads]
    

def unpack_each_archive(archive_base_name, archive_name):
    ''' unpack archive in thread '''
    archive_dir = archive_base_name.joinpath(archive_name.stem)
    if not archive_dir.exists:
        archive_dir.mkdir()
    shutil.unpack_archive(archive_name, archive_dir, archive_name.suffix[1:])
    archive_name.unlink()

def remove_empty_dirs(directory: Path) -> None:
    '''
    Clean up empty directories
    '''
    for entry in directory.glob("*"):
        # костиль ?
        if entry.is_dir() and entry.name not in list(CATEGORIES.keys())+['Unknown']:
        # if entry.is_dir() and not entry.name in list(CATEGORIES.keys()).append('Unknown'):
            shutil.rmtree(entry)

def main() -> str:
    if len(sys.argv) == 1:
        return 'ERROR: dir argument is needed. Terminating...'
    else:
        # dir_name must exist !!!
        path = Path(sys.argv[1])

    if not path.exists():
        return f'directory {path} does not exist. Terminating...'

    initialize_translation_table()

    process_dir(path)

    process_archives(path)

    remove_empty_dirs(path)

    return 'All done'


if __name__ == "__main__":
    print(main())
