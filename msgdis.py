import argparse
import os

import msg_decode
import find_text_table




def main():
    description = ""
    epilog = ""

    parser = argparse.ArgumentParser(description=description, epilog=epilog, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("code", help="code file to read.")
    parser.add_argument("region", choices=["n", "p"], help="code file to read.")
    
    args = parser.parse_args()

    find_text_table.findTextTablesMMap(args.code)
    find_text_table.read_tables(args.code)

    # start = int(args.start, 0) if args.start else 0
    # end = int(args.end, 0) if args.end else 0

    jpn_message_data_static = os.path.join(os.path.split(args.code)[0], "jpn_message_data_static")
    nes_message_data_static = os.path.join(os.path.split(args.code)[0], "nes_message_data_static")

    # i = 0
    for i in range(len(find_text_table.jpn_message_entry_table)):
        curEntry = find_text_table.jpn_message_entry_table[i]
        if curEntry[0] == 0xFFFF:
            continue

        start = find_text_table.segmented_to_offset(curEntry[3])
        nextEntry = find_text_table.jpn_message_entry_table[i+1]
        end = find_text_table.segmented_to_offset(nextEntry[3])
        # print("{:X},{},{},{:X}".format(*curEntry))
        # print("{:X},{},{},{:X}".format(*nextEntry))
        # print(f"{start:X},{end:X}")


        print("char jpn_message_{:04X}[] = ".format(curEntry[0]))
        data = msg_decode.read_data(jpn_message_data_static, start, end)
        msg_decode.decode_msg(data, "jpn")
        print(";\n")
        # print("{:X}".format(len(data)))

    for i in range(len(find_text_table.nes_message_entry_table)):
        curEntry = find_text_table.nes_message_entry_table[i]
        if curEntry[0] == 0xFFFF:
            continue

        start = find_text_table.segmented_to_offset(curEntry[3])
        nextEntry = find_text_table.nes_message_entry_table[i+1]
        end = find_text_table.segmented_to_offset(nextEntry[3])
        # print("{:X},{},{},{:X}".format(*curEntry))
        # print("{:X},{},{},{:X}".format(*nextEntry))
        # print(f"{start:X},{end:X}")


        print("char nes_message_{:04X}[] = ".format(curEntry[0]))
        data = msg_decode.read_data(nes_message_data_static, start, end)
        msg_decode.decode_msg(data, "nes")
        print(";\n")
        # print("{:X}".format(len(data)))


if __name__ == "__main__":
    main()
