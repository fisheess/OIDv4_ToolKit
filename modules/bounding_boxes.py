import os
from textwrap import dedent
import cv2

import modules.utils as utils
from modules.utils import bcolors as bc
from modules.downloader import download
import modules.csv_downloader as csvdl
from modules.show import show


def bounding_boxes_images(args, DEFAULT_OID_DIR):

    if not args.Dataset:
        dataset_dir = os.path.join(DEFAULT_OID_DIR, 'Dataset')
        csv_dir = os.path.join(DEFAULT_OID_DIR, 'csv_folder')
    else:
        dataset_dir = os.path.join(DEFAULT_OID_DIR, args.Dataset)
        csv_dir = os.path.join(DEFAULT_OID_DIR, 'csv_folder')

    name_file_class = 'class-descriptions-boxable.csv'
    CLASSES_CSV = os.path.join(csv_dir, name_file_class)

    if args.command == 'downloader':

        utils.logo(args.command)

        if args.type_csv is None:
            print(bc.FAIL + 'Missing type_csv argument.' + bc.ENDC)
            exit(1)
        if args.classes is None:
            print(bc.FAIL + 'Missing classes argument.' + bc.ENDC)
            exit(1)
        if args.multiclasses is None:
            args.multiclasses = 0

        folder = ['train', 'validation', 'test']
        file_list = {'train':'train-annotations-bbox.csv',
                     'validation':'validation-annotations-bbox.csv',
                     'test':'test-annotations-bbox.csv'}

        if args.classes[0].endswith('.txt'):
            with open(args.classes[0]) as f:
                args.classes = f.readlines()
                args.classes = [x.strip() for x in args.classes]
        else:
            args.classes = [arg.replace('_', ' ') for arg in args.classes]

        if args.additional_label_classes[0].endswith('.txt'):
            with open(args.additional_label_classes[0]) as f:
                args.additional_label_classes = f.readlines
                args.additional_label_classes = [x.strip() for x in args.classes]
        else:
            args.additional_label_classes =  [arg.replace('_', ' ') for arg in args.additional_label_classes ]

        if args.multiclasses == '0':

            utils.mkdirs(dataset_dir, csv_dir, args.classes, args.type_csv)

            for classes in args.classes:

                print(bc.INFO + 'Downloading {}.'.format(classes) + bc.ENDC)
                class_name = classes

                csvdl.error_csv(name_file_class, csv_dir)
                df_classes = csvdl.pd.read_csv(CLASSES_CSV, header=None)

                class_code = df_classes.loc[df_classes[1] == class_name].values[0][0]

                if args.type_csv in folder:
                    name_file = file_list[args.type_csv]
                    df_val = csvdl.TTV(csv_dir, name_file)
                    if not args.n_threads:
                        download(args, df_classes, df_val, args.type_csv, dataset_dir, class_name, class_code)
                    else:
                        download(args, df_classes, df_val, args.type_csv, dataset_dir, class_name, class_code, threads=int(args.n_threads))

                elif args.type_csv == 'all':
                    for i in folder:
                        name_file = file_list[i]
                        df_val = csvdl.TTV(csv_dir, name_file)
                        if not args.n_threads:
                            download(args, df_classes, df_val, folder[i], dataset_dir, class_name, class_code)
                        else:
                            download(args, df_classes, df_val, folder[i], dataset_dir, class_name, class_code, threads=int(args.n_threads))
                else:
                    print(bc.FAIL + 'csv file not specified' + bc.ENDC)
                    exit(1)

        elif args.multiclasses == '1':

            class_list = args.classes
            print(bc.INFO + 'Downloading {} together.'.format(class_list) + bc.ENDC)
            multiclass_name = ['_'.join(class_list)]
            utils.mkdirs(dataset_dir, csv_dir, multiclass_name, args.type_csv)

            csvdl.error_csv(name_file_class, csv_dir)
            df_classes = csvdl.pd.read_csv(CLASSES_CSV, header=None)

            class_dict = {}
            for class_name in class_list:
                class_dict[class_name] = df_classes.loc[df_classes[1] == class_name].values[0][0]

            for class_name in class_list:

                if args.type_csv in folder:
                    name_file = file_list[args.type_csv]
                    df_val = csvdl.TTV(csv_dir, name_file)
                    if not args.n_threads:
                        download(args, df_classes, df_val, args.type_csv, dataset_dir, class_name, class_dict[class_name], class_list)
                    else:
                        download(args, df_classes, df_val, args.type_csv, dataset_dir, class_name, class_dict[class_name], class_list, threads=int(args.n_threads))

                elif args.type_csv == 'all':
                    for i in folder:
                        name_file = file_list[i]
                        df_val = csvdl.TTV(csv_dir, name_file)
                        if not args.n_threads:
                            download(args, df_classes, df_val, folder[i], dataset_dir, class_name, class_dict[class_name], class_list)
                        else:
                            download(args, df_classes, df_val, folder[i], dataset_dir, class_name, class_dict[class_name], class_list, threads=int(args.n_threads))


    elif args.command == 'visualizer':

        utils.logo(args.command)

        flag = 0

        while True:
            if flag == 0:
                print("Which folder do you want to visualize (train, test, validation)? <exit>")
                image_dir = input("> ")
                flag = 1

                if image_dir == 'exit':
                    exit(1)

                class_image_dir = os.path.join(dataset_dir, image_dir)

                print("Which class? <exit>")
                utils.show_classes(os.listdir(class_image_dir))

                class_name = input("> ")
                if class_name == 'exit':
                    exit(1)

            download_dir = os.path.join(dataset_dir, image_dir, class_name)
            label_dir = os.path.join(dataset_dir, image_dir, class_name, 'Label')

            if not os.path.isdir(download_dir):
                print("[ERROR] Images folder not found")
                exit(1)
            if not os.path.isdir(label_dir):
                print("[ERROR] Labels folder not found")
                exit(1)

            index = 0

            print(dedent("""
                --------------------------------------------------------
                INFO:
                        - Press 'd' to select next image
                        - Press 'a' to select previous image
                        - Press 'e' to select a new class
                        - Press 'w' to select a new folder
                        - Press 'q' to exit
                  You can resize the window if it's not optimal
                --------------------------------------------------------
                """))

            show(class_name, download_dir, label_dir, len(os.listdir(download_dir))-1, index)

            while True:

                utils.progression_bar(len(os.listdir(download_dir))-1, index+1)

                k = cv2.waitKey(0) & 0xFF

                if k == ord('d'):
                    cv2.destroyAllWindows()
                    if index < (len(os.listdir(download_dir)) - 2):
                        index += 1
                    show(class_name, download_dir, label_dir, len(os.listdir(download_dir))-1, index)
                elif k == ord('a'):
                    cv2.destroyAllWindows()
                    if index > 0:
                        index -= 1
                    show(class_name, download_dir, label_dir, len(os.listdir(download_dir))-1, index)
                elif k == ord('e'):
                    cv2.destroyAllWindows()
                    break
                elif k == ord('w'):
                    flag = 0
                    cv2.destroyAllWindows()
                    break
                elif k == ord('q'):
                    cv2.destroyAllWindows()
                    exit(1)
                    break
