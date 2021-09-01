import os


def executeSiegfried(input_dir, output_dir):
    try:
        os.system("sf -update")
        os.system("sf -json " + input_dir + " >> /tmp/input_sf.json")
        os.system("sf -json " + output_dir + " >> /tmp/output_sf.json")
    except Exception as e:
        print("Error when executing Siegfried:", e)


if __name__ == '__main__':
    executeSiegfried("/tmp/testDirInput", "/tmp/testDirOutput")