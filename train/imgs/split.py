import random
import shutil
import math
import os


def copy_files(source_dir, dest_dir, file_list):
    for file in file_list:
        file_name = file.rpartition("/")[-1]
        shutil.copy(file, os.path.join(dest_dir, file_name))


def split_data(file_list, train_percentage):
    random.shuffle(file_list)
    train_count = math.ceil(len(file_list) * train_percentage)
    train_files = file_list[:train_count]
    validate_files = file_list[train_count:]
    return train_files, validate_files


if __name__ == "__main__":
    img_dir = os.getcwd()
    pooping = os.path.join(img_dir, "train/pooping")
    not_pooping = os.path.join(img_dir, "train/not_pooping")

    train_pooping = os.path.join(img_dir, "split/train/pooping")
    train_not_pooping = os.path.join(img_dir, "split/train/not_pooping")

    validate_pooping = os.path.join(img_dir, "split/validate/popping")
    validate_not_pooping = os.path.join(img_dir, "split/validate/not_popping")

    pooping_files = [os.path.join(pooping, f) for f in os.listdir(pooping)]
    not_pooping_files = [os.path.join(not_pooping, f) for f in os.listdir(not_pooping)]

    shutil.rmtree(train_pooping, ignore_errors=True)
    shutil.rmtree(train_not_pooping, ignore_errors=True)

    shutil.rmtree(validate_pooping, ignore_errors=True)
    shutil.rmtree(validate_not_pooping, ignore_errors=True)

    os.makedirs(train_pooping)
    os.makedirs(train_not_pooping)
    os.makedirs(validate_pooping)
    os.makedirs(validate_not_pooping)

    pooping_train_split, pooping_validate_split = split_data(pooping_files, 0.8)
    copy_files(pooping, train_pooping, pooping_train_split)
    copy_files(pooping, validate_pooping, pooping_validate_split)

    not_pooping_train_split, not_pooping_validate_split = split_data(
        not_pooping_files, 0.8
    )
    copy_files(pooping, train_not_pooping, not_pooping_train_split)
    copy_files(pooping, validate_not_pooping, not_pooping_validate_split)
